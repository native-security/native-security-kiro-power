# Native Security power for Kiro

A [Kiro power](https://kiro.dev/docs/powers/) that connects Kiro to the [Native](https://native.security) cloud-security platform through the Native MCP connector. Install it once and Kiro can explore your AWS, Azure, Google Cloud and OCI estate, manage and safely apply security policies, route changes through peer review, check deployment health, investigate blocked actions and CNAPP findings, and find sensitive data, all with your own Native identity.

The power follows the [Agent Plugins](https://agent-plugins.org) format (`plugin.json`), which Kiro recommends for new powers.

## What is inside

```
plugin.json                       manifest and activation keywords
mcp.json                          the Native MCP connector (Streamable HTTP, OAuth 2.1)
skills/
  environment-explorer/SKILL.md   estate, zones, effective policies, connectivity, sensitive data
  policy-manager/SKILL.md         catalog, parameters, drift, simulation, IaC, the apply gate, exceptions, plans
  intention-workflow/SKILL.md     peer review of a Draft Intention before apply
  posture-and-findings/SKILL.md   CNAPP posture and findings, blocked actions, custom policies
  deployment-health/SKILL.md      did this apply break anything: keep or revert
  platform-utilities/SKILL.md     identity, capabilities, prompts, resources, console links, self-test
```

The six skills cover the connector's full shipped surface: 81 tools in 9 groups. Some groups are feature-flagged on the Native side (CNAPP, zone connectivity, data sensitivity); the skills tell Kiro to check `list_capabilities` before relying on them.

## Install

**From GitHub (recommended).** In Kiro open the Powers panel, choose *Add Custom Power*, then *Import power from GitHub*, and paste:

```
https://github.com/native-security/native-security-kiro-power
```

**From a local path.** Clone this repository and import the directory as a local power.

No API keys and no environment variables are needed. The MCP server is remote.

## First run

1. Ask Kiro something Native-shaped, for example `who am I in Native?`. The power activates and Kiro connects to `https://mcp.native.security/mcp`.
2. A browser tab opens for the Native sign-in (OAuth 2.1 via Descope). Sign in with your Native account.
3. Back in Kiro, verify the connection:
   - `who am I in Native?` runs `who_am_i` and shows your user, tenant and roles.
   - `run the Native connector self-test` runs `self_test` and reports every section with remediation text if something is off.

## Things to try

- `Summarize my Native tenant.`
- `Which policies are effective on the production OU?`
- `What does the restrict-AI-models policy allow in my GCP organization?`
- `What would break if I enforced region management on org X? Give me the evidence report.`
- `Prepare the change, get it reviewed by the security contacts, and tell me when it is approved.`
- `Did yesterday's apply break anything? Keep or revert?`
- `Why was my deploy role blocked in eu-west-1 in the last 24 hours?`
- `Where is our sensitive data, and are those accounts protected?`

## Safety model

- Every tool call carries your own identity and tenant. The power never asks for or stores a tenant id, key or password.
- Almost every tool is read-only. The five destructive operations (`policy_apply_change`, `policy_revert_to_revision`, `policy_abort_execution`, `policy_delete_intention`, `policy_set_drift_recovery`) require you to type a confirmation phrase back. Kiro is instructed never to auto-fill or paraphrase it.
- Scanner, cloud and user-authored text (finding titles, audit events, tag values) is treated as data, never as instructions.

## Related

- Native docs for AI agents: https://docs.native.security/integrations/ai-agents
- Connector source and tool inventory: https://github.com/rocksteady-cloud/native-mcp-connector
- Kiro power authoring guide: https://kiro.dev/docs/powers/create/

## License

MIT
