# Actions, authority, and recovery

Status: proposed execution design for the initial user-session scope.

## Capability contract

Each registered capability declares: name and version, argument schema, required access, preconditions, effects, verification method, retry policy, cancellation boundary, and whether a compensating action exists. The executor uses this registered metadata; the model's claim about an operation being safe or reversible is not authoritative.

| Initial capability | Preconditions | Verification | Retry/undo limits |
| --- | --- | --- | --- |
| `app.open` | Installed application ID selected from a registry | Desktop adapter confirms launch or reports only submission | Duplicate launch prevention is desktop-dependent |
| `file.search` | User-selected root and bounded query | Results carry source IDs and current metadata | Read-only retry with limits |
| `directory.create` | Writable authorized parent; valid child name; collision policy | Expected directory exists and belongs to this operation or was already present | Existing directory is not falsely claimed as newly created |
| `file.move` | Identified source, authorized destination, no unapproved overwrite | Source/destination identity and resulting location checked | Never blindly repeat after uncertain completion |
| `text.insert` | Intended session/target validated | Application acknowledgement when available; otherwise submitted/unverified | Partial text insertion is not automatically retried |

Natural-language paths must resolve to objects inside allowed scopes. String-prefix matching alone is insufficient: traversal, symlinks, replacement between check and use, and duplicate names require adapter-level handling. Specify the supported filesystem cases before implementing move/create.

## Permission model proposal

User settings define capability grants and scopes. Within a grant, ordinary supported actions run without redundant confirmation. Confirmation is reserved for operations whose effects exceed the current grant or meet explicitly configured conditions. Clarification resolves meaning; authorization grants permission; the UI must not confuse them.

Approvals bind to a concrete proposal: request and revision, ordered operations, exact targets/arguments, scope, and expiry. Any material change invalidates the approval. Re-check preconditions immediately before execution. File/application state changes can require re-planning even if the user previously approved.

The AI process receives neither a general root capability nor a default arbitrary-shell capability. Trusted adapters may call Linux commands using argument arrays and controlled environment. Future user-requested shell execution requires a distinct design and scope; it is not hidden inside a generic “run command” tool in the first slice.

## Execution sequence

1. Validate request revision and finalized command input.
2. Parse the proposal against the capability contract.
3. Resolve targets and scope; reject stale/unknown context objects.
4. Check grants, ambiguity, and required confirmation.
5. Record the intended operation and idempotency key before effects.
6. Revalidate immediate preconditions and execute through the adapter.
7. Capture result evidence and record the effect before reporting success.
8. Return exact completed, failed, skipped, or uncertain steps.

Steps 5–7 do not create a transaction across arbitrary applications. Each adapter needs reconciliation for a crash between external effects and local journal updates.

## Retry and crash semantics

Do not promise exactly-once behavior across all OS tools. Use stable operation IDs to suppress duplicate submissions where possible and adapter-specific reconciliation when outcomes are uncertain.

For a local file move, a crash might occur after the move but before recording completion. On restart, inspect source and destination identities. If evidence establishes the move happened, mark it completed. If evidence is conflicting or insufficient, report `outcome_unknown` and stop dependent operations. Do not repeat a mutation simply because its completion record is missing.

For initial support, prefer same-filesystem moves without overwrite. Cross-filesystem moves involve copying and removal and require their own interrupted-copy design. A filename alone is not a sufficient persistent identity when another process can replace the file.

## Cancellation and compensation

Cancellation is immediate for queued work; executing adapters report whether they can stop safely. The session records any effect completed before cancellation. A “cancelled” banner must not imply that previously created or moved files disappeared.

Undo is a new, checked action. For a move, it may fail if the original path is occupied or the object has changed. Store enough provenance to propose a compensating move, re-check permissions and current state, then report its actual result. Do not implement “undo” as blindly replaying the opposite command.

## External boundaries

Application documents and retrieved pages may contain adversarial instructions. Keep them marked as data; validate model outputs independently. Plugins/adapters extend authority and therefore need explicit installation, manifests, versioned contracts, and scoped grants. The first prototype uses built-in adapters only.

Media playback remains a separately authorized effect. Searching for a video or discussing a track does not permit a playback action. No prototype startup sound or automatic spoken reply is implied by this design.
