# Native Security Kiro Power

A [Kiro](https://kiro.dev) power that connects your IDE directly to the [Native](https://native.security) cloud-security platform. Explore your cloud estate, understand and enforce security policies, route changes through peer review, verify that an apply did not break anything, investigate blocked actions and scanner findings, and locate sensitive data across AWS, Azure, Google Cloud and OCI. All through natural language in your editor, with your own Native identity.

Native turns security architecture into enforced guardrails. Instead of scanning for misconfigurations after the fact, Native deploys preventive controls (SCPs, Azure Policy, GCP Organization Policy, OCI policies and reactive controls) at the account, OU and organization level, simulates their blast radius before they go live, and keeps them healthy afterwards. This power brings that whole workflow into Kiro.

## What It Does

This power gives Kiro the ability to operate on your Native tenant through the [Native MCP connector](https://github.com/rocksteady-cloud/native-mcp-connector), and brings in operational guidance through six skills derived from the connector's own doctrine. Instead of switching between your IDE, the Native console and four cloud consoles, you can ask Kiro things like:

- "Summarize my Native tenant and flag any organization with drift"
- "Which policies are effective on the production OU, and what regions do they allow?"
- "What would break if I enforced encryption at rest on our GCP organization? Give me the evidence report"
- "Prepare the change, get it reviewed by the security contacts, and tell me when it is approved"
- "Did yesterday's apply break anything? Keep or revert?"
- "Why was my deploy role blocked in eu-west-1 in the last 24 hours?"
- "How many CNAPP findings do we have, and from which scanner?"
- "Where is our sensitive data, and are those accounts protected?"

Kiro will call the right tools in the right order, respect Native's tenant-default scope rule, and never apply a destructive change without you typing the confirmation phrase back. Everything is grounded in [6 skills](#skills-6-operational-guidance-modules) that mirror the connector's shipped surface: 81 tools in 9 groups.

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
|------|-------------|
| `who_am_i` | Identify the current user: name, email, selected tenant, permissions, roles |
| `list_organizations` | List the tenant's onboarded organizations the user has a role in |
| `list_capabilities` | Enumerate the tool groups, prompts and resources available to this session |
| `get_prompt` | Fetch the body of one curated workflow prompt (scope, drift-triage, prepare-change, ...) |
| `read_resource` | Read one published resource (terminology, capability matrix, troubleshooting, CNAPP sources, policy kinds) |
| `get_console_link` | Return a Native console deep link for any task or resource |
| `get_whats_new` | Surface Native's published What's New posts, optionally by category or date |
| `self_test` | Probe auth, environment, policy, coverage, plan and apply, with remediation per section |
| `revoke_session` | Revoke this MCP session so the next call requires a fresh sign-in |

**Environment**

| Tool | Description |
|------|-------------|
| `environment_summarize` | Summarize the tenant's cloud footprint or one organization in a single call |
| `environment_list_cloud_units` | Enumerate accounts, subscriptions, projects and compartments, with hierarchy paths |
| `environment_get_cloud_unit_details` | One cloud unit in full: services, regions, cost, owners, policy counts, blocked actions, CNAPP and sensitivity digests |
| `environment_get_organization_tree` | The full OU, management-group, folder or compartment hierarchy of one organization |
| `environment_list_zones` | List zones across the tenant or in one organization |
| `environment_get_zone_overview` | One zone's topology, connectivity headline, CNAPP digest, sensitivity, cost, services, owners and policy counts |
| `environment_get_zone_inventory` | Zone-level used services, used regions and resource statistics |
| `environment_triage_inventory_item` | Look up a cloud unit by its external id (account number, subscription id, project id, OCID) |
| `environment_list_effective_policies` | Policies effective on a tenant, organization, zone or cloud unit, direct versus inherited |
| `environment_explain_coverage_risks` | For each policy with missing or partial coverage in scope, explain why it matters |
| `environment_show_sync_status` | Per-organization sync status, last sync time and template freshness |
| `environment_get_zone_connectivity` | A zone's dedicated circuits, private endpoints and site-to-site VPNs (flagged) |
| `environment_summarize_connectivity` | Estate-wide rollup of connections, network hubs and zone peers (flagged) |
| `environment_get_zone_relationships` | A zone's parents, children, siblings, intersections and identical zones (flagged) |
| `environment_summarize_data_sensitivity` | Sensitive-resource counts by rating, type and source, with a coverage block (flagged) |
| `environment_list_sensitive_resources` | The rated buckets and datastores in a scope, attributed to the scanner (flagged) |

**Policy: Discover & Explain**

| Tool | Description |
|------|-------------|
| `policy_list_catalog` | Paginated catalog of every policy template with providers, scopes, domains and deployment counts |
| `policy_explain` | Plain-language explanation of one template with its goal and deployment summary |
| `policy_list_controls` | Enforcement mechanisms per template (SCP, Azure Policy, GCP Org Policy, reactive controls) |
| `policy_search_parameters` | Search every template's declared parameters by keyword, provider or catalog |
| `policy_get_parameter_definitions` | Parameter schema, defaults, options and resolved allowed values for one template |
| `policy_list_vocabulary` | Canonical cloud services, AI models or regions for one provider |
| `policy_get_effective_parameters` | The parameter values in effect for one template across a scope |
| `policy_get_history` | Revision history of a template, or one revision's coverage |

**Policy: State, Coverage & Drift**

| Tool | Description |
|------|-------------|
| `policy_list_intentions` | Deployed intentions in a scope with status, health, coverage and recent violations |
| `policy_inspect_cloud_object` | Which templates cover one cloud object, with optional live-state drill-down and action items |
| `policy_check_drift` | Drifting intentions in a scope, freshest first |
| `policy_compliance_coverage` | Regulatory-framework rollup (CIS, NIST, SOC 2, HIPAA and others) |
| `policy_cross_org_coverage` | Per-template, per-organization installation matrix |
| `policy_get_org_settings` | Org-level defaults: drift recovery, review requirements, attachment limits, break-glass list |
| `policy_get_breakglass_roles` | The organization's break-glass identities |

**Policy: Recommend & Tune**

| Tool | Description |
|------|-------------|
| `policy_recommend_next` | The next policy to deploy, with the reason it matters now |
| `policy_list_recommendations` | Every attention-worthy intention (draft, drift, error) across plans |
| `policy_suggest_intention` | Scope-aware default parameters for a new intention |
| `policy_get_optimization` | The backend's optimization suggestion for one intention |
| `policy_dismiss_optimization` | Dismiss an optimization suggestion (preference write) |
| `policy_update_annotations` | Merge metadata annotations into an intention (write) |

**Policy: Preview, IaC & Change**

| Tool | Description |
|------|-------------|
| `policy_simulate` | Read-only impact preview with coverage attestation and a paste-ready evidence report |
| `policy_show_implementation_steps` | The concrete per-object steps the backend would execute |
| `policy_generate_iac` | Render a policy action and targets as Terraform |
| `policy_prepare_change` | Create a Draft Intention and return its change id and confirmation phrase (write) |
| `policy_apply_change` | Flip the Draft to enforcing (**destructive**, confirmation phrase) |
| `policy_revert_to_revision` | Rewrite an intention to a prior revision (**destructive**, confirmation phrase) |
| `policy_abort_execution` | Abort an in-progress execution (**destructive**, confirmation phrase) |
| `policy_set_drift_recovery` | Toggle automatic drift recovery on one intention (**destructive**, confirmation phrase) |
| `policy_delete_intention` | Permanently delete an intention (**destructive**, confirmation phrase) |

**Policy: Exceptions & Plans**

| Tool | Description |
|------|-------------|
| `policy_search_exceptions` | Configured exclusions and break-glass identities, with facets and reverse lookup |
| `policy_list_exception_subjects` | Distinct excluded values on one dimension (identity, resource, tag, cloud unit, CIDR) |
| `plan_list` | Tenant-visible plans with optional progress |
| `plan_get_status` | One plan's breakdown, progress and recommended next action |

**Intention Review**

| Tool | Description |
|------|-------------|
| `intention_get_suggested_reviewers` | The organization's suggested reviewers for an intention |
| `intention_start_review` | Open a peer review on a Draft Intention (write) |
| `intention_get_review_status` | Review status, approval count, participant decisions and history |
| `intention_record_decision` | Record the signed-in user's approve or reject decision (write) |
| `intention_add_note` | Add a comment without a decision (write) |
| `intention_add_reviewer` | Invite additional reviewers (write) |
| `intention_remove_reviewer` | Remove a reviewer who has not yet decided (write) |
| `intention_resend_reviewer_notification` | Re-send the invitation to one reviewer (write) |
| `intention_cancel_review` | Withdraw an in-progress review (write) |

**Deployment Health**

| Tool | Description |
|------|-------------|
| `deployment_health_check` | Is a policy apply, or an organization at a point in time, healthy: anomalies, deny trend, advisory verdict |
| `deployment_health_deny_series` | Blocked-action trend over time for an intention or organization |
| `deployment_health_get_metrics` | Specific health-metric series plus anomalies |
| `deployment_health_list_metrics` | The health-metric catalog |
| `deployment_health_apply_events` | When an intention was applied, re-applied or drift-recovered |
| `deployment_health_scope_search` | Find an OU or account scope by free text to narrow a retrieval |

**Blocked Actions & Custom Policies**

| Tool | Description |
|------|-------------|
| `blocked_actions_search` | Search denied attempts by action, identity, region, policy, intention and time window |
| `blocked_actions_get` | One blocked-action event in full, with the raw provider audit event |
| `blocked_actions_filter_values` | Distinct values for one filterable field |
| `custom_policy_list` | List user-authored custom policies |
| `custom_policy_explain` | One custom policy in full, with per-provider statement bodies |

**CNAPP** (flagged)

| Tool | Description |
|------|-------------|
| `cnapp_get_posture` | Findings and Risks by source for a tenant, organization, zone or cloud unit, with coverage |
| `cnapp_list_findings` | One cloud unit's open findings per managed policy, by severity and source, with optional detail |

### Skills: 6 Operational Guidance Modules

Each skill wraps one connector tool group and teaches Kiro the workflows, vocabulary and honesty rules the connector expects. Content is derived from the connector's own skill pack, curated prompts and tool registrations, not written from memory. Reference a skill by name in Kiro chat to activate it (for example `#policy-manager`).

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
- [Native MCP connector source and tool inventory](https://github.com/rocksteady-cloud/native-mcp-connector)
- [Native Security](https://native.security)
- [Kiro powers: create your own](https://kiro.dev/docs/powers/create/)
- [Agent Plugins specification](https://agent-plugins.org)
- [Agent Skills specification](https://agentskills.io/specification)
- [Kiro IDE](https://kiro.dev)

## Legal & Support

- **License:** [MIT](./LICENSE)
- **Support:** [GitHub Issues](https://github.com/native-security/native-security-kiro-power/issues)
- **Native support and documentation:** [docs.native.security](https://docs.native.security)
