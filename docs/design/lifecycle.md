# Request lifecycle and event ordering

Status: refined coordinator specification. The current admission checker covers some eligibility checks, not this full lifecycle.

## States

| State | Meaning | Allowed next work |
| --- | --- | --- |
| `received` | Input exists but is not yet planned | Finalize/correct input, begin interpretation, cancel |
| `interpreting` | A model job is attached to this revision | Accept bounded output, clarify, fail, cancel |
| `needs_clarification` | Required intent/target information is missing | Collect one answer, revise request, cancel |
| `proposed` | Structured steps exist; not yet ready to execute | Validate, resolve, obtain required authorization, revise, cancel |
| `awaiting_confirmation` | A concrete proposal needs a user decision | Confirm unchanged proposal, deny/cancel, revise |
| `ready` | Current proposal passed checks | Recheck and dispatch, invalidate, or cancel |
| `executing` | At least one step may produce effects | Observe results, request cancellation, reconcile |
| `cancellation_pending` | Stop requested while an effect may be in progress | Observe/reconcile current step; do not start later steps |
| `succeeded` | All required steps verified | Display result; a new request can refer to it |
| `failed` | A definite failure occurred | Display completed/failed/skipped steps; explicit new retry request |
| `cancelled` | No further work will run and in-flight effects are resolved | Display any effects completed before cancellation |
| `outcome_unknown` | Evidence cannot settle an operation | Stop dependent steps and expose uncertainty |

Partial success is represented in step results even when the request ends `failed` or `cancelled`. It is never collapsed into “nothing happened.”

## Identity and ordering

Every event identifies session, request, request revision, and event/operation ID. The coordinator uses a monotonic sequence within the request to order accepted events; wall-clock time is diagnostic, not a correctness ordering mechanism.

Only the active revision can produce a newly executable proposal. Old model responses are discarded after correction, cancellation, or session invalidation. Repeated result/event IDs must not duplicate effects or duplicate UI completion messages. The actual IPC protocol must authenticate the sender; IDs in JSON alone do not authenticate anything.

## Corrections

Before dispatch, a correction increments the revision and returns to `received` or `interpreting`, clearing readiness and approval. During execution, correction first requests cancellation of remaining steps; the current step reaches a known or unknown outcome before planning a new request against actual state.

Avoid changing an executing proposal in place. Otherwise the journal could record one target while the adapter affects another.

## Confirmation

Confirmation refers to a frozen human-readable effect summary and its canonical proposal digest. Include capabilities, resolved objects, material arguments, request revision, policy epoch, and scope. Formatting-only changes need not alter semantics; define canonical serialization before implementing the digest.

A confirmation event is accepted only for the currently displayed proposal. Expiry, cancellation, target changes, grant changes, or session changes invalidate it. The production UI must defend against an old dialog confirming a newer request. Confirmation is not needed when an existing valid grant already authorizes the action.

## Timeouts

Separate capture limit, recognition deadline, interpretation deadline, clarification wait, confirmation expiry, adapter deadline, and verification/reconciliation deadline. Values remain configuration choices pending measurement. A timeout during execution can mean uncertainty, not proof that the operation failed before making changes.

When the deadline expires, prevent further dependent work, request cancellation where supported, and reconcile. Do not claim that terminating an inference worker terminated an already dispatched OS operation.

## Backpressure

Allow a bounded queue with visible busy state. Recordings that exceed declared limits stop with an explicit incomplete-input state. Prioritize cancellation/control events over queued inference work. The initial implementation may serialize mutations per request/session; cross-request concurrency requires object/conflict rules before being enabled.

## Test obligations

Inject reordered proposal/result messages; send an old approval after a correction; cancel before dispatch and during dispatch; change a grant while ready; lock the session while queued; restart after a mutation but before acknowledgement. Verify that no later event can revive a terminal cancelled request and no “success” appears without the required evidence.
