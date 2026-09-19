# Protocol transport and errors

Status: proposed production requirements; the current JSON fixtures are local data and do not implement a wire protocol.

## Transport decision

Compare a user-session D-Bus service with a Unix-domain socket protocol after selecting the first desktop. Both can support process boundaries, but each needs a concrete authentication, lifecycle, and versioning design. Do not introduce an externally reachable HTTP service merely to connect two processes on the same machine.

The development reference uses JSON files to keep examples independent of transport and language. JSON is not mandatory for every production message. Audio buffers should not be repeatedly encoded into giant JSON strings; use a bounded stream or controlled reference with explicit lifetime.

## Envelope proposal

A future message envelope should identify protocol version, message kind, session ID, request ID/revision, operation/event ID, and deadline. The authenticated peer determines authority; payload fields cannot establish sender identity. Associate a model worker with a specific outstanding job so it cannot submit a proposal for another session.

Bound message bytes, nesting, collection sizes, and outstanding jobs before expensive parsing or allocation. Reject duplicate keys and ambiguous numeric forms if JSON is selected. Limits in the reference checker only cover selected fields; they are not a complete untrusted-network parser.

## Compatibility

Negotiate supported protocol and capability versions at connection. Reject unsupported major versions. An unknown optional telemetry field may be ignorable only if the schema explicitly marks it optional; unknown action arguments remain errors. Keep model output schemas narrower than internal coordinator messages.

Changing the model prompt does not grant protocol extensions. Update the capability registry, adapter, schemas, tests, and version compatibility together when adding a capability.

## Error categories and user behavior

| Category | Meaning | Proposed user-visible handling |
| --- | --- | --- |
| `input_incomplete` | Audio or text was not finalized reliably | Keep/correct text or record again; do not act |
| `recognizer_unavailable` | Voice recognition cannot run | Offer typed input and diagnostics |
| `interpretation_invalid` | Model output cannot satisfy the contract | Bounded repair or clear failure, no execution |
| `needs_clarification` | Intent/target is unresolved | One concise question with accessible selection where useful |
| `permission_required` | Operation exceeds current grant | Show concrete effect and required scope |
| `permission_denied` | Policy refuses the operation | Explain the relevant restriction without retry loops |
| `stale_proposal` | Input, policy, or target changed | Re-resolve/re-plan; never reuse stale approval |
| `target_conflict` | Destination/type/current state conflicts | Preserve existing data and request a new plan |
| `adapter_unavailable` | Desktop/capability integration missing | Explain supported alternatives |
| `resource_exhausted` | Memory, disk, queue, or compute limit reached | Stop safely; expose what can be retried |
| `cancelled` | Request is settled and further work stopped | Report any earlier effects |
| `outcome_unknown` | An effect may have happened | Show evidence and stop dependent work |

Internal diagnostics may contain syscall or engine details, while the user-facing message should explain the concrete consequence and next action. Avoid misleading errors such as “permission denied” for every model or device failure.

## Observability without transcript leakage

Emit request state transitions, component/version identifiers, elapsed stages, queue sizes, and redacted error categories. Full text, audio, paths, and model prompts require a deliberate diagnostic mode and reviewable export. Counters alone can support performance debugging; they cannot establish task correctness.

The development JSON fixtures contain synthetic text only. Do not add private corpus recordings or real transcripts to this public repository by default.
