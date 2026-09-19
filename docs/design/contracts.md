# Initial request/proposal contract

Status: executable design experiment, version 1. This is a preflight admission contract, not an authorization service or execution engine.

## Trust boundaries

The coordinator supplies trusted session state and grants. The model supplies only a proposal. Never let a model populate the session or grant objects in production. The JSON fixture format puts all three in one document solely to express test cases.

An `allow` result from the reference checker means the proposal passes these illustrative static checks. It does not mean the filesystem targets exist, that desktop identity is valid, that the requester has been authenticated, or that execution should begin. Real adapters must recheck authority and immediate preconditions.

## Session object

Required fields: `session_id`, `request_id`, `request_revision`, `policy_epoch`, `active`, `cancelled`, `input_final`, and `mode`. IDs are bounded ASCII identifiers; revisions and epochs are integers from 0 through 2^53−1 for exact interchange with common JSON consumers. Boolean values are not accepted as integers. The only modes are `dictation` and `command`.

Session state comes from the coordinator at validation time. A request is eligible only when active, not cancelled, finalized, and in command mode. This version has no execution or confirmation-state model.

## Proposal object

Required fields: `schema_version`, `session_id`, `request_id`, `request_revision`, `policy_epoch`, and `steps`. Version is exactly integer 1. Session, request, revision, and epoch must match the current coordinator state. Unknown fields are rejected.

`steps` contains 1–8 entries in this experiment. Each contains a unique `operation_id`, a capability name, and exact capability-specific arguments. Limits here are provisional defensive bounds, not measured product limits.

Operation IDs are unique within a proposal. A future durable executor must namespace them by session/request/revision (or use globally unique IDs), preserve the same identity for a retry of the same operation, and avoid reusing it for changed arguments. The static checker implements no cross-request deduplication.

Initial supported capabilities:

| Capability | Arguments | Scope lookup |
| --- | --- | --- |
| `directory.create` | `root_id`, `name` | Exact capability/root grant |
| `file.search` | `root_id`, `query` | Exact capability/root grant |

`root_id` is an opaque identifier mapped by a trusted adapter, not a model-provided absolute path. A directory name must be one nonempty leaf, at most 255 UTF-8 bytes, excluding separators, `.` and `..`. Queries are nonblank text up to 2,048 characters. This initial checker rejects all Unicode category C characters in names/queries (including control, format, surrogate, private-use, and unassigned characters); that conservative experimental rule must be reviewed for language support before production. All such limits can be revised with compatibility tests.

The experiment excludes `file.move`, `text.insert`, app launch, and shell execution even though the design backlog includes some of them. An unsupported capability is denied rather than simulated as implemented.

## Grants

Each grant contains exactly `capability` and `root_id`. A match admits only that capability for that named scope. No wildcard grants or path-prefix logic exist. Confirmation-required capabilities will need a separate approval object bound to a proposal digest; this fixture version does not model them.

## Result

The checker returns `decision` (`allow` or `deny`) and a stable `code`. Validation errors, unsupported version, ineligible input, stale proposal, unknown capability, invalid arguments, duplicate operation IDs, and missing grants have distinguishable codes. The whole proposal is checked before allowing any step. There is no partial execution.

## Executable examples

See [contract reference experiment](../../experiments/contract_reference/README.md). It uses Python's standard library as a small verification tool, not as a production-language decision. Fixtures demonstrate static invariants and explicitly do not demonstrate AI quality, voice quality, live authentication, filesystem confinement, or recovery after effects.
