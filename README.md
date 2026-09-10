# Native Security Kiro Power

A [Kiro](https://kiro.dev) power that connects your IDE directly to the [Native](https://native.security) cloud-security platform. Explore your cloud estate, understand and enforce security policies, route changes through peer review, verify that an apply did not break anything, investigate blocked actions and scanner findings, and locate sensitive data across AWS, Azure, Google Cloud and OCI. All through natural language in your editor, with your own Native identity.

Native turns security architecture into enforced guardrails. Instead of scanning for misconfigurations after the fact, Native deploys preventive controls (SCPs, Azure Policy, GCP Organization Policy, OCI policies and reactive controls) at the account, OU and organization level, simulates their blast radius before they go live, and keeps them healthy afterwards. This power brings that whole workflow into Kiro.

## What It Does

This power gives Kiro the ability to operate on your Native tenant through the [Native MCP connector](https://docs.native.security/integrations/ai-agents), and brings in operational guidance through seven skills derived from the connector's own doctrine. Instead of switching between your IDE, the Native console and four cloud consoles, you can ask Kiro things like:

- "Summarize my Native tenant and flag any organization with drift"
- "Which policies are effective on the production OU, and what regions do they allow?"
- "What would break if I enforced encryption at rest on our GCP organization? Give me the evidence report"
- "Prepare the change, get it reviewed by the security contacts, and tell me when it is approved"
- "Did yesterday's apply break anything? Keep or revert?"
- "Why was my deploy role blocked in eu-west-1 in the last 24 hours?"
- "How many CNAPP findings do we have, and from which scanner?"
- "Where is our sensitive data, and are those accounts protected?"

Kiro will call the right tools in the right order, respect Native's tenant-default scope rule, and never apply a destructive change without you typing the confirmation phrase back. Everything is grounded in [7 skills](#skills-7-operational-guidance-modules) that mirror the connector's shipped surface: 81 tools in 9 groups.

## Quick Start

### Prerequisites

- [Kiro IDE](https://kiro.dev) installed
- A Native account with at least one cloud organization onboarded
- Outbound HTTPS to `mcp.native.security` (port 443)

No API keys, tokens or environment variables. The MCP server is remote and signs you in with OAuth 2.1.

### 1. Install the Power

Open Kiro's Powers panel, choose **Add Custom Power**, then **Import power from GitHub**, and paste:

```
https://github.com/native-security/native-security-kiro-power
```

Or clone this repository and import the directory as a local power.

### 2. Sign In

The first time Kiro calls a Native tool, a browser tab opens for the Native sign-in (OAuth 2.1 via Descope). Sign in with your Native account. Kiro receives a token bound to your user and tenant; nothing is stored in the power.

### 3. Verify and Start Exploring

A natural entry point is to confirm who you are and what this session can do:

```
> "Who am I in Native?"
> "Run the Native connector self-test"
> "Which Native tool groups are enabled for me?"
```

Then explore, check, and change:

```
> "Show me my AWS organization tree"
> "What does the restrict-AI-models policy allow in account 123456789012?"
> "Simulate block-inbound-public-access on our Azure management group"
> "What is drifting right now, grouped by plan?"
```

## What's Included

### MCP Tools

All 81 tools of the Native MCP connector. Read-only unless marked. Five tools are **destructive** and require a confirmation phrase that you type back; Kiro is instructed never to auto-fill it. Three groups are feature-flagged on the Native side and may be absent from your session; ask Kiro to check `list_capabilities`.

**Connector & Session**

| Tool | Description |
|---|---|
| `who_am_i` | Identify the current user: name, email, selected tenant, permissions, roles, and tenant logo. |
| `list_organizations` | List the tenant's onboarded organizations the user has a role in. |
| `list_capabilities` | Enumerate the tool groups, curated prompts and resources available to this session (filtered by granted scopes). |
| `get_prompt` | Fetch the body of one of the connector's curated MCP prompts (drift-triage, prepare-change, recommend-next, …). |
| `read_resource` | Read the content of one of the connector's published MCP resources (terminology map, capability matrix, troubleshooting playbooks, policy-kinds catalogue). |
| `get_console_link` | Return a Native console deep link for any task or resource the user wants to see in the UI. |
| `get_whats_new` | Surface Native's published 'What's New' posts (new policies, capabilities, integrations, incidents). |
| `self_test` | Probe every section of the connector (auth, environment, policy, policy_coverage, plan, apply) in parallel, report per-section status + remediation, and name the MCP revision this session negotiated. |
| `revoke_session` | Revoke this MCP session immediately so subsequent calls require a new sign-in. (write) |

**Environment**

| Tool | Description |
|---|---|
| `environment_summarize` | Summarize the tenant's cloud footprint or one organization in a single call. |
| `environment_list_cloud_units` | Enumerate cloud units across the tenant or within one organization. |
| `environment_get_cloud_unit_details` | Return one cloud unit's services, regions, cost, owners, third parties, policy installation counts, recent Blocked Actions, CNAPP digest and account data-sensitivity block. |
| `environment_get_organization_tree` | Return the full cloud organization hierarchy for one Native organization. |
| `environment_list_zones` | List zones across the tenant or in one organization. |
| `environment_get_zone_overview` | Return one zone's topology (derived booleans + connectivity headline), CNAPP digest, data sensitivity, cost-by-category, used services / regions, owners, and policy counts. |
| `environment_get_zone_inventory` | Return zone-level used services, used regions, and resource statistics. |
| `environment_triage_inventory_item` | Look up a cloud unit by its cloud-unit-level external id and return its details. |
| `environment_list_effective_policies` | List policies effective on a tenant / organization / zone / cloud unit, with totals and (zone-only) direct vs inherited source. |
| `environment_explain_coverage_risks` | For each policy whose coverage is missing or partial in scope, explain why the policy matters (sourced from PolicyDetailsV2.whyThisPolicyMatters). |
| `environment_show_sync_status` | Per-organization sync status: current status, last sync time, most recent workflow, onboarding template freshness. |
| `environment_get_zone_connectivity` | Return one zone's external connections — dedicated circuits, private endpoints and site-to-site VPNs — with the derived booleans, optional network hubs and zone peers, and one connection in full detail. (flagged: `FLAG_MCP_CONNECTOR_CONNECTIVITY_TOOLS`) |
| `environment_summarize_connectivity` | Roll up the estate's external connections, network hubs and zone peers in one call: counts by kind, provider, state and risk flag, hubs folded by union, each peer edge once, and which risk flags have a producer. (flagged: `FLAG_MCP_CONNECTOR_CONNECTIVITY_TOOLS`) |
| `environment_get_zone_relationships` | Return one zone's structural relationships — parents, children, siblings, intersections and identical zones — so scope overlap can be reasoned about before a policy install. (flagged: `FLAG_MCP_CONNECTOR_CONNECTIVITY_TOOLS`) |
| `environment_summarize_data_sensitivity` | Count sensitive resources by rating, sensitivity type, source and resource type for a tenant, organization, zone or cloud unit, with a coverage block naming what was scanned. (flagged: `FLAG_MCP_CONNECTOR_DSPM_TOOLS`) |
| `environment_list_sensitive_resources` | List the resources carrying a sensitivity rating in one organization, cloud unit or zone, each attributed to the scanner that rated it. (flagged: `FLAG_MCP_CONNECTOR_DSPM_TOOLS`) |

**Policy: Discover & Explain**

| Tool | Description |
|---|---|
| `policy_list_catalog` | Paginated listing of every policy template in the Native catalog (the agent's discovery surface for policy_explain / policy_recommend_next / policy_suggest_intention). |
| `policy_explain` | Explain a policy template in plain language: title, why it matters, implementation description, supported cloud providers and target scopes, plus a deployment summary (Intention counts by status state per the canonical Draft/Acti… |
| `policy_list_controls` | List enforcement mechanisms (SCP, Azure Policy, GCP Org Policy, native reactive controls) per policy template, grouped by enforcement vs native + per-cloud-provider counts. |
| `policy_search_parameters` | Search every managed policy template's declared parameters in one call — the cross-template discovery surface for "which policy can configure X?" questions. |
| `policy_get_parameter_definitions` | Return the backend-authored parameter schema, defaults, curated options, provider applicability, and optionally resolved region/service values for one managed policy template. |
| `policy_list_vocabulary` | List the canonical value universe for one vocabulary kind (cloud services, AI models, or regions) on one cloud provider — the ids that policy parameter allowedValues join against. |
| `policy_get_effective_parameters` | Return the effective parameter values (allowed regions, encryption flags, etc.) for one policy template across the intentions deployed in a scope. |
| `policy_get_history` | Read the revision history of a policy template (template-rollup) or drill into one revision's coverage (revision mode). |

**Policy: State, Coverage & Drift**

| Tool | Description |
|---|---|
| `policy_list_intentions` | List deployed Intentions in a scope (tenant by default; or organization / zone / cloudUnit when specified) with their status state, derived health, coverage, recent violation counts, target scope UUIDs, plan memberships, and anno… |
| `policy_inspect_cloud_object` | Inspect one cloud object (account, project, OU, …): which policy templates cover it, per-template coverage (installed/partial/missing/notInstalled), and an optional per-template drill-down into the live policy state. |
| `policy_check_drift` | List drifting Intentions in a scope (status.state="drift" — Intentions whose desired state has diverged from the actual cloud state). |
| `policy_compliance_coverage` | Roll up regulatory-framework coverage (CIS, NIST, SOC 2, HIPAA, …) by composing the policy catalog's complianceStandards tags with the per-template enforcement-mechanism counts. |
| `policy_cross_org_coverage` | Compare policy coverage across all organizations in the tenant in one call. |
| `policy_get_org_settings` | Read the org-level policy defaults: drift recovery, auto-import tracking, review requirements, attachment limits, plus the breakglass identity list. |
| `policy_get_breakglass_roles` | List the org's breakglass identities (emergency-bypass IAM principals that escape policy enforcement). |

**Policy: Recommend & Tune**

| Tool | Description |
|---|---|
| `policy_recommend_next` | Recommend the next policy to deploy by walking Getting Started -> AI Guardrails -> Multi-Cloud Alignment, falling back to a structured guidance prompt when no plan applies. |
| `policy_list_recommendations` | Full paginated listing of every attention-worthy Intention across every plan (Draft / drift / error). |
| `policy_suggest_intention` | Pre-fill the parameters object for a new Intention before calling policy_prepare_change. |
| `policy_get_optimization` | Fetch the backend's optimization suggestion for one Intention. |
| `policy_dismiss_optimization` | Mark an optimization as dismissed so the reconciler stops re-suggesting it for this Intention. (write) |
| `policy_update_annotations` | Merge user-supplied metadata.annotations into an Intention's desired-state document. (write) |

**Policy: Preview, IaC & Change**

| Tool | Description |
|---|---|
| `policy_simulate` | Read-only preview of a policy's impact on an environment, WITHOUT creating a Draft Intention. |
| `policy_show_implementation_steps` | Compute the concrete per-cloud-object steps the backend would execute to apply a PolicyAction to the given targets. |
| `policy_generate_iac` | Render a PolicyAction + targets directly as Infrastructure-as-Code (Terraform today). |
| `policy_prepare_change` | Create a Draft Intention on the backend (status.state=pending) AFTER the user has confirmed the parameters policy_suggest_intention proposed. (write) |
| `policy_apply_change` | Flip the Draft Intention created by policy_prepare_change to enforcing. (**destructive**, confirmation phrase) |
| `policy_revert_to_revision` | Rewrite an Intention's desired state to a prior revision. DESTRUCTIVE — gated by FLAG_MCP_CONNECTOR_APPLY_CHANGE and a deterministic confirmation phrase the user must echo back. (**destructive**, confirmation phrase) |
| `policy_abort_execution` | Abort an in-progress execution on an Intention (only valid while statusState is in-progress / deleting). (**destructive**, confirmation phrase) |
| `policy_set_drift_recovery` | Toggle automatic drift recovery on a single Intention. ENABLING is destructive (Native will auto-remediate cloud state on drift); DISABLING reverts to manual remediation. (**destructive**, confirmation phrase) |
| `policy_delete_intention` | Permanently delete an Intention (its desired-state document and any associated drafts). (**destructive**, confirmation phrase) |

**Policy: Exceptions & Plans**

| Tool | Description |
|---|---|
| `policy_search_exceptions` | Search the tenant's configured policy exceptions — the exclusions declared on intentions plus organization break-glass identities — with typed filters, KPI facet counts and a reverse lookup answering "which policies exclude this… |
| `policy_list_exception_subjects` | List the distinct values actually excluded on one subject dimension (identity, resource, tag, cloudUnitId, cidr) so a policy_search_exceptions reverse lookup is offered real choices instead of a guessed ARN. |
| `plan_list` | List tenant-visible plans (Getting Started, AI Guardrails, Multi-Cloud Alignment, user-created, shared-target-list). |
| `plan_get_status` | Fetch one plan's per-status-state intention breakdown, progress percentage, and the agent's recommended next action (highest-priority attention-worthy intention in the plan: Draft > drift > error). |

**Intention Review**

| Tool | Description |
|---|---|
| `intention_get_suggested_reviewers` | Fetch the org's suggested reviewers for this Intention. Backend computes the list from intention owners, scope stakeholders, and security contacts. |
| `intention_start_review` | Open a peer-review on a Draft Intention before applying it. Sends invites to the reviewer emails the user provided (or to suggested reviewers from intention_get_suggested_reviewers). (write) |
| `intention_get_review_status` | Read the current ReviewState of the Intention's open review: reviewStatus, approval count vs. |
| `intention_record_decision` | Record the calling user's approve/reject decision on a review. (write) |
| `intention_add_note` | Append a comment to a review without recording a decision. The note shows up in ReviewState.history for every participant. (write) |
| `intention_add_reviewer` | Invite additional reviewers to an existing review. Useful when the initial invitees haven't acted, or the user wants additional sign-off. (write) |
| `intention_remove_reviewer` | Remove an invited reviewer who hasn't yet acted. Returns 409 if the reviewer already recorded a decision (the audit trail is immutable). (write) |
| `intention_resend_reviewer_notification` | Re-send the review notification to a single reviewer who hasn't yet acted (e.g. (write) |
| `intention_cancel_review` | Cancel an in-progress review. Returns 409 if the review is already approved (the audit trail is immutable past approval). (write) |

**Deployment Health**

| Tool | Description |
|---|---|
| `deployment_health_check` | Answer "did this policy's recent apply break anything — keep it or revert?" for one intention, or inspect an organization's health at a point in time. |
| `deployment_health_deny_series` | Blocked-action (denial) trend over time for an intention or an organization — the attributed and unattributed layers plus a spike-vs-baseline summary. |
| `deployment_health_get_metrics` | Fetch specific health-metric series (by id) plus anomalies for an intention or organization. |
| `deployment_health_list_metrics` | Browse the available health metrics (the catalog the dashboard's "Add health metric" picker uses), with title and description per metric. |
| `deployment_health_apply_events` | When did this intention apply? Returns the apply-relevant lifecycle transitions (markers) for one intention over the recent past. |
| `deployment_health_scope_search` | Find an OU or account (a scopeId) within an organization by free-text. |

**CNAPP (flagged)**

| Tool | Description |
|---|---|
| `cnapp_get_posture` | Report CNAPP findings and Risks by finding source for a tenant, organization, zone or cloud unit, with a coverage block that says which sources could have reported at all. (flagged: `FLAG_MCP_CONNECTOR_CNAPP_TOOLS`) |
| `cnapp_list_findings` | List one cloud unit's open CNAPP findings per managed policy, by severity and finding source, so an agent can say which Native policy would remove the most of them. (flagged: `FLAG_MCP_CONNECTOR_CNAPP_TOOLS`) |

**Blocked Actions & Custom Policies**

| Tool | Description |
|---|---|
| `blocked_actions_search` | Search blocked-action (denial) events with friendly filters — action/identity substring, region, policy template or intention, identity type, and a relative or ISO time window. |
| `blocked_actions_get` | Fetch one blocked-action event by id with full forensic detail — the raw provider audit event plus connector-enriched links to the Native intentions that produced the denial. |
| `blocked_actions_filter_values` | List the distinct values present for one filterable field (identityType, identityName, region, policyIds, actionType, policyType, thirdParty) in a scope/window, so you can offer concrete choices before calling blocked_actions_sea… |
| `custom_policy_list` | List user-authored custom policies. Composes GET /v2/policy-management/policies with type=Custom; paginates client-side because the endpoint has no page cursor. |
| `custom_policy_explain` | Read one user-authored custom policy in full: metadata, per-provider statement bodies (AWS / Azure / GCP / OCI), security domains. |

### Skills: 7 Operational Guidance Modules

Six skills wrap one connector tool group each, and one (Secure-by-Design IaC) sequences tools across groups; all teach Kiro the workflows, vocabulary and honesty rules the connector expects. Content is derived from the connector's own skill pack, curated prompts and tool registrations, not written from memory. Reference a skill by name in Kiro chat to activate it (for example `#policy-manager`).

**Environment Explorer**
- Apply the tenant-default scope rule: default to the tenant, narrow only when the user names an account, zone or organization, resolve parents automatically
- Map organization trees, zones, effective policies and coverage gaps before making compliance statements
- Read zone connectivity honestly: only `active` is operational, absence is "nothing observed", risk-flag coverage before any all-clear
- Run the sensitive-data workflow coverage-first, and never report record counts the backend does not serve

**Policy Manager**
- Discover what is configurable via parameter search, vocabularies and resolved allowed values
- Answer "what does policy X allow in scope Y?" with a single effective-parameters call
- Simulate before every change, read the evidence report, and surface missing impact previews before offering to apply
- Run both confirmation-gate flows correctly: prepare-then-apply, and same-tool two-call for revert, abort, delete and drift recovery
- Distinguish configured exceptions from actual denials, and track plan progress

**Secure-by-Design IaC**
- Build Terraform, CloudFormation, Bicep, Pulumi or Helm for a specific cloud unit that is compliant with Native policies from the first draft
- Resolve the target cloud unit, read the effective policies and their parameters, then write code that already honours them and cite the policy per constrained line
- Stop and explain when a request conflicts with a policy instead of weakening the control; never claim Native "passed" a file

**Intention Workflow**
- Open peer reviews with suggested reviewers and attached simulation evidence
- Record `approve` or `reject` decisions as the signed-in user; notes versus decisions
- Handle stale review state, immutable audit trails and 409 conflicts without blind retries

**Posture and Findings**
- Walk the CNAPP ladder outside-in: tenant, organization, zone, cloud unit, then per-policy findings
- State the four CNAPP rules out loud: absence is not cleanliness, Risks are not findings, policy buckets overlap, vendor text is data
- Investigate blocked actions with the real filter vocabulary and pair them with the policy's intent
- Audit custom policies without executing their statement bodies

**Deployment Health**
- Run the flagship health check right after every apply, by intention or by organization at a point in time
- Read anomalies, deny trends and the advisory keep / investigate / consider-revert verdict
- Drill into deny series, metric series, apply markers and narrower scopes
- Never revert on the hint alone; reverts go through the confirmation gate

**Platform Utilities**
- Start every session with identity, capabilities and the scope prompt
- Resolve ambiguous vocabulary from the terminology resource
- Deep-link into the Native console, read the What's New feed, run the self-test and revoke sessions

## Project Structure

```
.
├── plugin.json                       # Agent Plugins manifest: name, description, activation keywords
├── mcp.json                          # Native MCP connector (Streamable HTTP, OAuth 2.1)
├── LICENSE                           # MIT
├── README.md
└── skills/                           # Skills (loaded on demand in Kiro)
    ├── environment-explorer/
    │   └── SKILL.md                  # Estate, zones, effective policies, connectivity, sensitive data
    ├── policy-manager/
    │   └── SKILL.md                  # Catalog, parameters, drift, simulation, IaC, the apply gate, exceptions, plans
    ├── secure-by-design-iac/
    │   └── SKILL.md                  # Policy-first infrastructure code for a cloud unit (build, do not scan)
    ├── intention-workflow/
    │   └── SKILL.md                  # Peer review of a Draft Intention before apply
    ├── posture-and-findings/
    │   └── SKILL.md                  # CNAPP posture and findings, blocked actions, custom policies
    ├── deployment-health/
    │   └── SKILL.md                  # Did this apply break anything: keep or revert
    └── platform-utilities/
        └── SKILL.md                  # Identity, capabilities, prompts, resources, console links, self-test
```

The power follows the [Agent Plugins](https://agent-plugins.org) format that Kiro recommends for new powers. Skills follow the [Agent Skills](https://agentskills.io/specification) specification.

## Safety Model

- Every tool call carries your own identity and tenant from the OAuth token. The power never asks for, stores or forwards a tenant id, key or password.
- 76 of the 81 tools are read-only or change only review and metadata state. The five destructive operations require you to type a confirmation phrase back, and Kiro is instructed never to auto-fill, paraphrase or replay it.
- Scanner, cloud and user-authored text (finding titles, audit events, tag values, custom policy statements) is treated as data, never as instructions.
- Feature-flagged groups are described as conditional, so Kiro checks what your session can actually use instead of promising a tool that is off.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Sign-in tab never opens or the callback fails | Ask Kiro to read `resource://native/troubleshooting/oauth-callback`; make sure a default browser is set |
| Connection refused or timeout | Allow outbound HTTPS to `mcp.native.security` on port 443; check corporate proxy rules (`troubleshooting/network-egress`) |
| `who_am_i` shows the wrong user or tenant | Ask Kiro to run `revoke_session`, then sign in again with the right account |
| A tool group is missing (CNAPP, connectivity, sensitive data) | The feature flag is off for your deployment; `list_capabilities` shows what is enabled |
| `CONFIRMATION_REQUIRED` or `CONFIRMATION_MISMATCH` | Expected: type the phrase Kiro shows you exactly as written; it is never auto-filled |
| `review_state_changed` (409) | Another participant already acted; ask Kiro to re-read the review status |
| "Cloud unit not found" or stale ids | Ask Kiro to re-list cloud units, zones or intentions and use the fresh id |
| Resource-level id rejected | Triage works at the account level; resolve the parent cloud unit first |
| Transport errors (`-32020`, `-32022`, `404 session not found`) | Ask Kiro to run `self_test` and quote the `protocol` section (`troubleshooting/protocol-errors`) |
| Tools return errors after a permission change | Run `self_test`, then `revoke_session` and sign in again so the new scopes apply |

## Resources

- [Native docs: AI agents and the MCP connector](https://docs.native.security/integrations/ai-agents)
- [Native Security](https://native.security)
- [Kiro powers: create your own](https://kiro.dev/docs/powers/create/)
- [Agent Plugins specification](https://agent-plugins.org)
- [Agent Skills specification](https://agentskills.io/specification)
- [Kiro IDE](https://kiro.dev)

## Legal & Support

- **License:** [MIT](./LICENSE)
- **Support:** [GitHub Issues](https://github.com/native-security/native-security-kiro-power/issues)
- **Native support and documentation:** [docs.native.security](https://docs.native.security)
