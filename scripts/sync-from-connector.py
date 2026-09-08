#!/usr/bin/env python3
"""Regenerate this power's tool tables from the Native MCP connector.

Source of truth: ``docs/tool-inventory.json`` in a checkout of
rocksteady-cloud/native-mcp-connector (written by ``make tool-inventory``
there). This script rewrites the generated blocks in every
``skills/*/SKILL.md`` and in ``README.md``, refreshes the tool counts, and
records the synced connector commit in ``.connector-sync.json``.

Hand-written prose outside the generated blocks is never touched. Doctrine
changes in the connector (skill pack, prompts, content JSON) are *reported*
in the summary so a human folds them into the skills.

Usage:
    scripts/sync-from-connector.py --connector ../native-mcp-connector --write
    scripts/sync-from-connector.py --connector ../native-mcp-connector --check
    scripts/sync-from-connector.py --connector ../native-mcp-connector --write \
        --summary-out sync-summary.md
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MAP_PATH = ROOT / "scripts" / "skill-map.json"
SYNC_STATE_PATH = ROOT / ".connector-sync.json"
README_PATH = ROOT / "README.md"

BEGIN = "<!-- BEGIN GENERATED: tools (scripts/sync-from-connector.py) -->"
END = "<!-- END GENERATED: tools -->"
NEEDS_PLACEMENT = "New tools (needs placement)"
DOCTRINE_PATHS = [
    "connector-skill",
    "pkg/connector/content/prompts",
    "pkg/connector/content/terminology.json",
    "pkg/connector/content/cnapp-sources.json",
    "pkg/connector/content/parameter-semantics.json",
    "pkg/connector/content/capability-matrix.json",
    "pkg/connector/content/install-snippets.json",
]
NUMBER_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
}
MAX_DESCRIPTION = 230


# --------------------------------------------------------------------------
# Inventory
# --------------------------------------------------------------------------

def load_inventory(connector: Path) -> tuple[dict, list[dict]]:
    path = connector / "docs" / "tool-inventory.json"
    if not path.exists():
        sys.exit(
            f"error: {path} not found. Run `make tool-inventory` in the "
            "connector checkout first (it writes both the .md and the .json)."
        )
    doc = json.loads(path.read_text())
    tools = doc.get("tools")
    if not isinstance(tools, list) or not tools:
        sys.exit(f"error: {path} has no `tools` array")
    for t in tools:
        for key in ("name", "group", "intent"):
            if key not in t:
                sys.exit(f"error: tool record missing `{key}`: {t}")
    return doc, sorted(tools, key=lambda t: (t["group"], t["name"]))


def describe(tool: dict, default_off: set[str]) -> str:
    """One table cell from the connector's Intent string plus markers."""
    text = " ".join(tool["intent"].split())
    text = text.replace("|", "\\|")
    # Keep whole sentences up to the cap; the Intent strings are written as
    # prose and the first sentence is the summary by convention.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for s in sentences:
        candidate = (out + " " + s).strip()
        if out and len(candidate) > MAX_DESCRIPTION:
            break
        out = candidate
        if len(out) >= 60:
            break
    if len(out) > MAX_DESCRIPTION:
        out = out[: MAX_DESCRIPTION - 1].rstrip() + "…"
    markers = []
    if tool.get("destructive"):
        markers.append("**destructive**, confirmation phrase")
    elif tool.get("mutating"):
        markers.append("write")
    flag = tool.get("featureFlag") or ""
    if flag in default_off:
        markers.append(f"flagged: `{flag}`")
    if markers:
        out = f"{out} ({'; '.join(markers)})"
    return out


# --------------------------------------------------------------------------
# Placement
# --------------------------------------------------------------------------

def place_tools(tools: list[dict], skill_map: dict) -> tuple[dict, list[dict]]:
    """Return {skill: [(section_title, [tool,...]), ...]} and unassigned tools."""
    by_name = {t["name"]: t for t in tools}
    listed: set[str] = set()
    placed: dict[str, list[tuple[dict, list[dict]]]] = {}
    for skill, spec in skill_map["skills"].items():
        sections = []
        for section in spec["sections"]:
            rows = []
            for name in section["tools"]:
                if name in by_name:
                    rows.append(by_name[name])
                    listed.add(name)
                # A listed tool the connector no longer registers is simply
                # dropped; the summary reports it as removed.
            if rows:
                sections.append((section, rows))
        placed[skill] = sections
    # Tools in a mapped group that no section lists.
    group_to_skill = {}
    for skill, spec in skill_map["skills"].items():
        for g in spec["groups"]:
            group_to_skill[g] = skill
    unassigned = []
    for t in tools:
        if t["name"] in listed:
            continue
        skill = group_to_skill.get(t["group"])
        if skill is None:
            unassigned.append(t)
            continue
        sections = placed[skill]
        if sections and sections[-1][0].get("title") == NEEDS_PLACEMENT:
            sections[-1][1].append(t)
        else:
            sections.append(({"title": NEEDS_PLACEMENT, "auto": True}, [t]))
    return placed, unassigned


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_table(rows: list[dict], default_off: set[str], header: str) -> str:
    lines = [f"| Tool | {header} |", "|---|---|"]
    for t in rows:
        lines.append(f"| `{t['name']}` | {describe(t, default_off)} |")
    return "\n".join(lines)


def render_skill_block(sections, default_off: set[str]) -> str:
    parts = []
    for section, rows in sections:
        title = section["title"]
        if section.get("auto"):
            parts.append(
                f"### {title}\n\n"
                "> The connector registered these tools after this skill was "
                "last curated. Move each into the right section of "
                "`scripts/skill-map.json` and describe its workflow above; "
                "`scripts/validate.py` fails while this section exists.\n\n"
                + render_table(rows, default_off, "What it does")
            )
        else:
            parts.append(f"### {title}\n\n{render_table(rows, default_off, 'What it does')}")
    return "\n\n".join(parts)


def render_readme_block(placed, skill_map: dict, default_off: set[str], unassigned) -> str:
    parts = []
    for skill, sections in placed.items():
        spec = skill_map["skills"][skill]
        skill_title = spec.get("readmeTitle", skill)
        pending_title = None
        pending_rows: list[dict] = []
        for section, rows in sections:
            merge = section.get("readmeMergeWithPrevious") or (spec.get("readmeMerged") and not section.get("auto"))
            if merge and pending_title:
                # One README table for several skill sections (or the whole skill).
                pending_rows.extend(rows)
                continue
            if pending_title:
                parts.append(f"**{pending_title}**\n\n{render_table(pending_rows, default_off, 'Description')}")
            if section.get("auto"):
                pending_title = f"{skill_title}: {NEEDS_PLACEMENT}"
            elif section.get("readmeTitle"):
                pending_title = section["readmeTitle"]
            elif len(sections) == 1 or spec.get("readmeMerged"):
                pending_title = skill_title
            else:
                pending_title = f"{skill_title}: {section['title']}"
            pending_rows = list(rows)
        if pending_title:
            parts.append(f"**{pending_title}**\n\n{render_table(pending_rows, default_off, 'Description')}")
    if unassigned:
        parts.append(
            "**Unassigned tools**\n\n"
            "> These tools belong to a connector group that `scripts/skill-map.json` "
            "does not map to any skill. Add the group to a skill.\n\n"
            + render_table(unassigned, default_off, "Description")
        )
    return "\n\n".join(parts)


def splice(doc: str, block: str, path: Path) -> str:
    b = doc.find(BEGIN)
    if b < 0:
        sys.exit(f"error: {path}: marker {BEGIN!r} not found")
    e = doc.find(END, b)
    if e < 0:
        sys.exit(f"error: {path}: marker {END!r} not found after BEGIN")
    return doc[:b] + BEGIN + "\n" + block + "\n" + doc[e:]


def number_word(n: int) -> str:
    return NUMBER_WORDS.get(n, str(n))


def refresh_counts(text: str, total: int, groups: int, destructive: int, per_group: dict[str, int],
                   per_skill: int | None) -> str:
    text = re.sub(r"\b\d+ tools in \d+ groups\b", f"{total} tools in {groups} groups", text)
    text = re.sub(r"\b\d+ tools / \d+ groups\b", f"{total} tools / {groups} groups", text)
    text = re.sub(r"\b\d+ of the \d+ tools\b", f"{total - destructive} of the {total} tools", text)
    text = re.sub(r"\bAll \d+ tools of the Native MCP connector\b",
                  f"All {total} tools of the Native MCP connector", text)
    text = re.sub(r"\bThe (\w+) destructive operations\b",
                  f"The {number_word(destructive)} destructive operations", text)
    text = re.sub(r"\b(\w+) tools are \*\*destructive\*\* and require\b",
                  f"{number_word(destructive).capitalize()} tools are **destructive** and require", text)
    text = re.sub(r"\b(\w+) are destructive and sit behind\b",
                  f"{number_word(destructive).capitalize()} are destructive and sit behind", text)

    def fix_source_line(m: re.Match) -> str:
        line = m.group(0)
        line = re.sub(r"([a-z_.]+) group \((\d+) tools\)",
                      lambda mm: f"{mm.group(1)} group ({per_group.get(mm.group(1), mm.group(2))} tools)", line)
        line = re.sub(r"\b([a-z_]+) \((\d+)\)",
                      lambda mm: f"{mm.group(1)} ({per_group.get(mm.group(1), mm.group(2))})", line)
        return line

    text = re.sub(r"^  source: .*$", fix_source_line, text, flags=re.M)
    return text


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

def existing_tool_names(paths: list[Path]) -> set[str]:
    names: set[str] = set()
    for p in paths:
        if not p.exists():
            continue
        doc = p.read_text()
        b, e = doc.find(BEGIN), doc.find(END)
        if b < 0 or e < 0:
            continue
        names.update(re.findall(r"^\| `([a-z_]+)` \|", doc[b:e], re.M))
    return names


def git(connector: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(connector), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def doctrine_changes(connector: Path, since: str | None) -> str:
    if not since:
        return "_No previously synced connector commit recorded; doctrine diff skipped._"
    head = git(connector, "rev-parse", "HEAD")
    if not head:
        return "_Connector checkout is not a git repository; doctrine diff skipped._"
    if not git(connector, "cat-file", "-e", f"{since}^{{commit}}"):
        # cat-file -e prints nothing on success; distinguish by exit status
        pass
    stat = git(connector, "diff", "--stat", f"{since}..HEAD", "--", *DOCTRINE_PATHS)
    if stat == "":
        return f"_No doctrine files changed between `{since[:7]}` and `{head[:7]}`._"
    log = git(connector, "log", "--oneline", f"{since}..HEAD", "--", *DOCTRINE_PATHS)
    return (
        f"Doctrine files changed between `{since[:7]}` and `{head[:7]}`. "
        "Read each and fold the change into the affected skill's prose (the "
        "generated tables do not carry doctrine):\n\n"
        f"```\n{stat}\n```\n\nCommits:\n\n```\n{log}\n```"
    )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--connector", required=True, type=Path, help="path to a native-mcp-connector checkout")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="rewrite the generated blocks in place")
    mode.add_argument("--check", action="store_true", help="exit 1 if the generated blocks are stale")
    ap.add_argument("--connector-sha", help="connector commit to record (default: git HEAD of --connector)")
    ap.add_argument("--summary-out", type=Path, help="write a Markdown summary here (also printed)")
    args = ap.parse_args()

    connector = args.connector.resolve()
    skill_map = json.loads(SKILL_MAP_PATH.read_text())
    default_off = set(skill_map.get("defaultOffFlags", []))
    inventory_doc, tools = load_inventory(connector)
    sha = args.connector_sha or git(connector, "rev-parse", "HEAD") or None

    previous_state = json.loads(SYNC_STATE_PATH.read_text()) if SYNC_STATE_PATH.exists() else {}
    skill_paths = [ROOT / "skills" / s / "SKILL.md" for s in skill_map["skills"]]
    before = existing_tool_names(skill_paths)

    placed, unassigned = place_tools(tools, skill_map)
    total = len(tools)
    groups = sorted({t["group"] for t in tools})
    destructive = sum(1 for t in tools if t.get("destructive"))
    per_group = {g: sum(1 for t in tools if t["group"] == g) for g in groups}

    changes: dict[Path, str] = {}
    for skill, sections in placed.items():
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.exists():
            sys.exit(f"error: {path} missing but listed in skill-map.json")
        doc = path.read_text()
        new = splice(doc, render_skill_block(sections, default_off), path)
        skill_total = sum(len(rows) for _, rows in sections)
        new = refresh_counts(new, total, len(groups), destructive, per_group, skill_total)
        if new != doc:
            changes[path] = new

    readme = README_PATH.read_text()
    new_readme = splice(readme, render_readme_block(placed, skill_map, default_off, unassigned), README_PATH)
    new_readme = refresh_counts(new_readme, total, len(groups), destructive, per_group, None)
    if new_readme != readme:
        changes[README_PATH] = new_readme

    state = {
        "connectorRepo": "rocksteady-cloud/native-mcp-connector",
        "connectorCommit": sha,
        "inventoryVersion": inventory_doc.get("version"),
        "toolCount": total,
        "groups": per_group,
        "destructiveTools": sorted(t["name"] for t in tools if t.get("destructive")),
    }
    new_state = json.dumps(state, indent=2) + "\n"
    if not SYNC_STATE_PATH.exists() or SYNC_STATE_PATH.read_text() != new_state:
        changes[SYNC_STATE_PATH] = new_state

    after = {t["name"] for t in tools}
    added, removed = sorted(after - before), sorted(before - after)
    needs_placement = {
        skill: [t["name"] for sec, rows in sections if sec.get("auto") for t in rows]
        for skill, sections in placed.items()
        if any(sec.get("auto") for sec, _ in sections)
    }

    lines = ["## Kiro power sync from native-mcp-connector", ""]
    lines.append(f"- Connector commit: `{(sha or 'unknown')[:12]}` (previous: `{str(previous_state.get('connectorCommit') or 'none')[:12]}`)")
    lines.append(f"- Tools: **{total}** in {len(groups)} groups; destructive: {destructive}")
    lines.append(f"- Added tools: {', '.join(f'`{n}`' for n in added) if added else 'none'}")
    lines.append(f"- Removed tools: {', '.join(f'`{n}`' for n in removed) if removed else 'none'}")
    if needs_placement:
        lines.append("- **Needs placement** (moved into an auto section; `validate.py` fails until placed): "
                     + "; ".join(f"{s}: {', '.join(f'`{n}`' for n in ns)}" for s, ns in needs_placement.items()))
    if unassigned:
        lines.append("- **Unassigned groups** (no skill maps them): "
                     + ", ".join(sorted({f'`{t["group"]}`' for t in unassigned})))
    changed_files = sorted(str(p.relative_to(ROOT)) for p in changes)
    lines.append(f"- Files changed: {', '.join(f'`{f}`' for f in changed_files) if changed_files else 'none'}")
    lines += ["", "### Doctrine changes to fold in by hand", "", doctrine_changes(connector, previous_state.get("connectorCommit"))]
    summary = "\n".join(lines) + "\n"
    print(summary)
    if args.summary_out:
        args.summary_out.write_text(summary)

    if args.check:
        if changes:
            print(f"STALE: {len(changes)} file(s) would change. Run with --write.", file=sys.stderr)
            return 1
        print("up to date")
        return 0

    for path, content in changes.items():
        path.write_text(content)
    print(f"wrote {len(changes)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
