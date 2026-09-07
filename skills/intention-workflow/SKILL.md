---
name: intention-workflow
description: Run the peer-review lifecycle for a Native Draft Intention before it is applied - open a review, pick or invite reviewers, record approve or reject decisions, add notes, resend notifications, read review status and history, and cancel a review. Use when the user says "get this reviewed", "who has to approve this", "approve", "reject", "loop in someone", or asks how a review is going.
license: MIT
metadata:
  author: Native Security
  version: "1.0.0"
  source: native-mcp-connector intention.review group (9 tools)
---

# Intention Workflow

## Overview

A **Draft Intention** is the `changeId` (also the `desiredStateId`) returned by `policy_prepare_change`. It can be peer-reviewed before `policy_apply_change` runs. Review tools change review state only, never cloud state, so they carry **no confirmation phrase**. Approval applies nothing: the change still goes through `policy_apply_change` and its gate in the policy-manager skill.

Identity comes from the user's token. Decisions and notes are recorded for the calling user; you cannot record someone else's decision.

## Prerequisites

- A Draft Intention created with `policy_prepare_change`.
- `policy.review.read` for status and suggested reviewers; `policy.review.write` for the other seven tools.
- Whether a template *requires* review before apply is an organization setting (`policy_get_org_settings`).

## Tools

| Tool | What it does |
|---|---|
| `intention_get_suggested_reviewers` | The organization's suggested reviewers for this intention, computed from intention owners, scope stakeholders and security contacts. Use it to pre-fill `reviewerEmails`. |
| `intention_start_review` | Opens the review on a Draft (`desiredStateId` + `organizationId`; optional `reviewerEmails`, `message`, and `simulationHasImpact` / `simulationSummary` from `policy_simulate`). One open review per Draft. |
| `intention_get_review_status` | The `ReviewState`: `reviewStatus`, `currentApprovalCount` versus `minApprovalsRequired`, each participant's decision, and the `history` audit trail. |
| `intention_record_decision` | Records the calling user's decision. `decision` is `approve` or `reject` (anything else is `VALIDATION_FAILED`), with an optional `note`. |
| `intention_add_note` | A comment without a decision. Appears in `history` for every participant. |
| `intention_add_reviewer` | Invites more reviewers to an existing review. |
| `intention_remove_reviewer` | Removes an invitee who has not acted yet. Returns 409 once they have decided. |
| `intention_resend_reviewer_notification` | Re-sends the invitation to one reviewer who has not acted. |
| `intention_cancel_review` | Withdraws an in-progress review. Returns 409 if already approved; undo an approved change with a new review on a reverse change. |

Related tools owned by the policy-manager skill: `policy_prepare_change` (creates the Draft), `policy_list_intentions` (find Drafts and their state), `policy_delete_intention` (remove an abandoned Draft, gated).

## Review semantics

- `reviewStatus` is `pending`, `approved`, `rejected`, `cancelled` or `expired`. The set is open-ended: report an unknown value as-is.
- "I'll approve later" is a **note**; "I approve" is a **decision**.
- A reviewer can only be removed before they have decided. The audit trail is immutable past a decision or an approval.
- Stale state returns `BACKEND_PARTIAL` with `details.reason = "review_state_changed"` (HTTP 409): another participant already moved the review. Re-fetch with `intention_get_review_status` and retry only if the operation still applies. Never retry blindly.
- Poll `intention_get_review_status` for progress; never guess at approval counts.

## Step-by-step

### 1. Find what needs review

```
policy_list_intentions                     # Drafts show status.state = pending
intention_get_review_status                # is there an open review, and where is it?
```

### 2. Open a review

1. `policy_simulate` (policy-manager skill) if not already done, so reviewers see evidence.
2. `intention_get_suggested_reviewers` for the invite list.
3. `intention_start_review` with `desiredStateId`, `organizationId`, `reviewerEmails`, a short `message`, and `simulationHasImpact` / `simulationSummary`.
4. `intention_add_note` with the business reason or ticket reference.

### 3. Track and unblock

- `intention_get_review_status` for approvals versus `minApprovalsRequired`.
- `intention_resend_reviewer_notification` for a reviewer who has not responded.
- `intention_remove_reviewer` then `intention_add_reviewer` to swap an unavailable reviewer (only before they decide).

### 4. Decide

`intention_record_decision` with `approve` or `reject` and an optional `note`. The decision is recorded for the signed-in user only.

### 5. After approval

Return to the policy-manager skill and run `policy_apply_change` with the Draft's `changeId` and the user-typed confirmation phrase. Then `deployment_health_check` (deployment-health skill).

### 6. Withdraw

`intention_cancel_review` while the review is pending. To drop the Draft itself, use `policy_delete_intention` through its two-call gate.

## Common workflows

**Standard change approval.** prepare, simulate, suggested reviewers, start review, note, decision, apply, health check.

**Audit trail for compliance.** `intention_get_review_status` for `history`, `intention_add_note` for context, `intention_record_decision` with a reason, and after apply `policy_get_history`.

**Stalled review.** status, resend notification, swap reviewer if needed, status again.

## Troubleshooting

- **Reviewer never got the email.** `intention_resend_reviewer_notification`; if still nothing, confirm the account is active in the Native console.
- **`VALIDATION_FAILED` on decision.** `decision` must be exactly `approve` or `reject`.
- **409 on remove or cancel.** The reviewer already decided, or the review is already approved. The trail is immutable; start a new review on a reverse change instead.
- **`review_state_changed`.** Re-read status; someone else acted first.
- **Intention not found.** Ids go stale; re-list with `policy_list_intentions`.

## Best practices

- Add a note with the business reason before starting the review so the trail is meaningful.
- Attach simulation evidence to every review; reviewers should never approve a change whose impact was not previewed.
- Prefer `intention_get_suggested_reviewers` over hand-picked reviewers.
- Do not delete intentions after they are applied; their history is audit evidence. Delete only abandoned Drafts.
