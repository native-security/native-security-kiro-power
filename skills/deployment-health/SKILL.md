---
name: deployment-health
description: Answer "did this policy apply break anything - keep it or revert?" using Native's Deployment Health surface - the flagship health check around an apply or a point in time, plus deny-trend series, health-metric series and catalog, apply markers, and scope search for narrowing. Use right after policy_apply_change, when a user reports fallout after a guardrail went live, for live triage of an organization, or when a deny spike needs explaining.
license: MIT
metadata:
  author: Native Security
  version: "1.0.0"
  source: native-mcp-connector deployment_health group (6 tools)
---

# Deployment Health

## Overview

Deployment Health mirrors the Native console's Deployment Health dashboard. The flagship tool is `deployment_health_check`; the other five are escape hatches for drill-down. The report is **advisory**: a `consider_revert` hint is a suggestion, nothing auto-reverts, and reverting still goes through the apply gate in the policy-manager skill.

Vocabulary note: the backend calls each signal a *capability*; the agent surface and the console call it a **health metric**. Use "health metric" with users.

## Prerequisites

- Native MCP connector connected and signed in; `policy.read` scope.
- At least one intention applied through Native, or an organization to inspect at a point in time.

## Tools

<!-- BEGIN GENERATED: tools (scripts/sync-from-connector.py) -->
### Tools

| Tool | What it does |
|---|---|
| `deployment_health_check` | Answer "did this policy's recent apply break anything — keep it or revert?" for one intention, or inspect an organization's health at a point in time. |
| `deployment_health_deny_series` | Blocked-action (denial) trend over time for an intention or an organization — the attributed and unattributed layers plus a spike-vs-baseline summary. |
| `deployment_health_get_metrics` | Fetch specific health-metric series (by id) plus anomalies for an intention or organization. |
| `deployment_health_list_metrics` | Browse the available health metrics (the catalog the dashboard's "Add health metric" picker uses), with title and description per metric. |
| `deployment_health_apply_events` | When did this intention apply? Returns the apply-relevant lifecycle transitions (markers) for one intention over the recent past. |
| `deployment_health_scope_search` | Find an OU or account (a scopeId) within an organization by free-text. |
<!-- END GENERATED: tools -->

## How `deployment_health_check` works

Two modes, mirroring the console:

- **Inspect by policy.** Pass an `intention` (the `policyDesiredStateId` from `policy_list_intentions`). The tool resolves the apply marker, the policy's default health metrics and a pre-apply baseline for you.
- **Inspect health.** Pass an `organizationId` (plus optional `cloudProvider`, `centerTime`) with no intention, to inspect health around a point in time. `centerTime` now is live triage.

You pass an intention or an organization and a relative window. **Never** pass health-metric ids or ISO timestamps to this tool.

The report leads with `anomalies` (metrics that moved in the bad direction after the apply), the `denyTrend` spike versus baseline, and `verdict.hint` (`keep`, `investigate`, `consider_revert`).

## Step-by-step

### 1. Post-apply check

Immediately after `policy_apply_change`:

```
policy_list_intentions            # find the policyDesiredStateId
deployment_health_check           # intention = <that id>
```

Report the verdict hint, the anomalies and the deny trend. Do not assume success.

### 2. Explain a deny spike

`deployment_health_deny_series` for the same intention or organization, then `blocked_actions_search` (posture-and-findings skill) with the `intentionId` and `cloudObjectIds` to name the specific workloads being denied.

### 3. Drill into a metric

`deployment_health_list_metrics` for the catalog, then `deployment_health_get_metrics` with explicit `healthMetricIds`. Most users should stay on `deployment_health_check`, which picks the metrics itself.

### 4. Retrieval too large

`deployment_health_scope_search` to pick a narrower OU or account, then re-run `deployment_health_check` or `deployment_health_get_metrics` with that `scopeId`.

### 5. When was it applied?

`deployment_health_apply_events` for the intention's apply, re-apply and drift-recovery markers.

### 6. Act on the verdict

- `keep`: report and stop.
- `investigate`: drill with deny series, blocked actions and `policy_inspect_cloud_object`.
- `consider_revert`: present the evidence; if the user agrees, `policy_revert_to_revision` through its two-call confirmation gate (policy-manager skill). Never revert on the hint alone.

## Common workflows

**Guarded rollout.** simulate, prepare, apply, `deployment_health_check`, decide keep or revert with the user.

**Live triage of an organization.** `deployment_health_check` with `organizationId` and `centerTime` now; spikes lead to `deployment_health_deny_series` and `blocked_actions_search`.

**Weekly trend review.** `deployment_health_list_metrics` once, then `deployment_health_get_metrics` per organization for the metrics you track; compare with the prior week.

## Troubleshooting

- **No baseline.** The apply is too recent, or no marker exists yet. `deployment_health_apply_events` shows whether the apply landed; re-check later.
- **Result too large.** Use `deployment_health_scope_search` and re-run with `scopeId`.
- **Deny series shows unattributed denials.** They did not map to a Native intention; investigate with `blocked_actions_search` before blaming the new policy.
- **Verdict says `consider_revert` but the user expected the denials.** The hint is statistical. Confirm with the user which denials are intended before proposing a revert.

## Best practices

- Run `deployment_health_check` after every apply, and again a day later.
- Quote the verdict as a hint, with the anomalies that drove it.
- Pair every deny spike with the concrete blocked actions before recommending a change.
- Keep the user's decision explicit: reverting always requires the typed confirmation phrase.
