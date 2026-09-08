#!/usr/bin/env python3
"""Self-contained structural checks for this power. No network, no connector
checkout needed. Run in CI on every PR and locally before pushing.

Checks:
  * plugin.json / mcp.json parse and carry the Agent Plugins schema ids.
  * every skills/<dir>/SKILL.md has front matter; `name` == <dir> and matches
    the Agent Skills pattern; `description` is 1..1024 chars; file <= 500 lines.
  * every SKILL.md and README.md contains the generated-tools block markers.
  * every tool appears in exactly one skill table; README tables equal the
    union of skill tables; no "needs placement" or "Unassigned" sections.
  * .connector-sync.json exists and its toolCount equals the number of tools.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- BEGIN GENERATED: tools (scripts/sync-from-connector.py) -->"
END = "<!-- END GENERATED: tools -->"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_SKILL_LINES = 500

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def generated(doc: str, label: str) -> str | None:
    b, e = doc.find(BEGIN), doc.find(END)
    if b < 0 or e < 0 or e < b:
        err(f"{label}: generated block markers missing or out of order")
        return None
    return doc[b:e]


def table_tools(block: str) -> list[str]:
    return re.findall(r"^\| `([a-z_]+)` \|", block, re.M)


def main() -> int:
    # Manifests
    for name, schema in (("plugin.json", "plugin.schema.json"), ("mcp.json", "mcp.schema.json")):
        p = ROOT / name
        try:
            doc = json.loads(p.read_text())
        except Exception as e:  # noqa: BLE001
            err(f"{name}: does not parse: {e}")
            continue
        if not str(doc.get("$schema", "")).endswith(schema):
            err(f"{name}: $schema should end with {schema}")
    plugin = json.loads((ROOT / "plugin.json").read_text())
    if not re.fullmatch(r"(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", plugin.get("name", "")):
        err("plugin.json: name violates the Agent Plugins pattern")

    # Skills
    skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    if not skill_dirs:
        err("skills/: no skill directories")
    owner: dict[str, list[str]] = {}
    for d in skill_dirs:
        label = f"skills/{d.name}/SKILL.md"
        p = d / "SKILL.md"
        if not p.exists():
            err(f"{label}: missing")
            continue
        doc = p.read_text()
        m = re.match(r"---\n(.*?)\n---\n", doc, re.S)
        if not m:
            err(f"{label}: no YAML front matter")
            continue
        fm = m.group(1)
        name = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc = re.search(r"^description:\s*(.+)$", fm, re.M)
        if not name or name.group(1).strip() != d.name:
            err(f"{label}: front matter name must equal directory name {d.name!r}")
        elif not NAME_RE.fullmatch(name.group(1).strip()) or len(name.group(1).strip()) > 64:
            err(f"{label}: name violates the Agent Skills pattern")
        if not desc or not (1 <= len(desc.group(1).strip()) <= 1024):
            err(f"{label}: description must be 1..1024 chars")
        lines = doc.count("\n") + 1
        if lines > MAX_SKILL_LINES:
            err(f"{label}: {lines} lines, limit {MAX_SKILL_LINES} (move detail to references/)")
        block = generated(doc, label)
        if block is None:
            continue
        if "needs placement" in block.lower():
            err(f"{label}: contains a 'needs placement' section; place the new tools in scripts/skill-map.json")
        for t in table_tools(block):
            owner.setdefault(t, []).append(d.name)

    for t, skills in sorted(owner.items()):
        if len(skills) > 1:
            err(f"tool `{t}` is owned by more than one skill: {', '.join(skills)}")
    all_tools = set(owner)
    if not all_tools:
        err("no tools found in any skill table")

    # README
    readme = (ROOT / "README.md").read_text()
    block = generated(readme, "README.md")
    if block is not None:
        readme_tools = table_tools(block)
        if "unassigned tools" in block.lower():
            err("README.md: contains an 'Unassigned tools' section; map the group in scripts/skill-map.json")
        dup = {t for t in readme_tools if readme_tools.count(t) > 1}
        if dup:
            err(f"README.md: duplicate tool rows: {sorted(dup)}")
        missing = all_tools - set(readme_tools)
        extra = set(readme_tools) - all_tools
        if missing:
            err(f"README.md: tools present in skills but not in README: {sorted(missing)}")
        if extra:
            err(f"README.md: tools present in README but in no skill: {sorted(extra)}")

    # Sync state
    state_path = ROOT / ".connector-sync.json"
    if not state_path.exists():
        err(".connector-sync.json: missing (run scripts/sync-from-connector.py --write)")
    else:
        state = json.loads(state_path.read_text())
        if state.get("toolCount") != len(all_tools):
            err(f".connector-sync.json: toolCount {state.get('toolCount')} != {len(all_tools)} tools in skill tables")

    if errors:
        print("validate: FAILED")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"validate: OK ({len(skill_dirs)} skills, {len(all_tools)} tools)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
