# Configuration, state, and privacy

Status: proposed ownership and persistence model.

## Configuration layers

Use human-readable configuration with a versioned schema: packaged defaults, administrator policy, and user preferences. Define precedence per field. User preferences must not override an administrator restriction merely by appearing later. Reject unknown critical fields and invalid types; preserve the last valid configuration when an edited file fails validation.

Proposed areas: activation controls; dictation/command mode; microphone; recognition engine/artifact; language; mapping packs; AI engine/artifact; resource budget; authorized folders/applications; retention; appearance/accessibility; diagnostics. A configuration editor and CLI must operate on the same model.

Separate non-secret configuration from credentials. The core must not require proprietary service credentials. Any future optional integration should store secrets through an appropriate secret facility, never inline in committed examples or model prompts.

## Location strategy

Follow XDG conventions for user configuration, persistent state, reusable data, caches, and runtime files, rather than hard-coding `/home/mike`. The XDG specification distinguishes these categories and defines environment-based locations. [XDG Base Directory specification](https://specifications.freedesktop.org/basedir/latest/).

Proposed project subdirectory: `vplinuxai` under each relevant XDG location. Exact file formats remain open. Runtime IPC endpoints belong in the user's runtime directory with peer identity and restrictive permissions, not an unauthenticated network listener exposed to other users.

## Data lifetime proposal

| Data | Default lifetime | Rationale |
| --- | --- | --- |
| Audio frames | In memory for the active request; released after completion/cancel | Dictation does not imply archival recording |
| Raw/processed transcript | Active session only | Enables correction without permanent history by default |
| Action journal | Bounded durable operational records | Supports recovery and duplicate suppression |
| Model cache | Until user removes/replaces it | Large artifacts should not download on every launch |
| Search/context cache | Bounded; invalidated on source changes/revocation | Avoid stale references and excessive retention |
| Diagnostic export | Explicitly generated, previewable | Prevent accidental publication of speech or paths |

Action records can reveal sensitive filenames even without transcript text. Retention, access, and deletion must cover those metadata too. Exact retention periods are open; release configuration must make them explicit.

## Recovery journal minimum

Store request/revision IDs, operation IDs, capability/version, a bounded target reference, authorization reference, execution state, timestamps, and verification evidence sufficient for the adapter's reconciliation. Persist intent before effects and completion after evidence. Keep model reasoning traces out of the recovery journal; they are not needed to prove a file operation occurred.

If the journal cannot durably record a mutation's intent, do not start that mutation. Reads may continue if they do not rely on durable recovery. On startup, reconcile incomplete operations before resuming dependent steps; do not automatically replay old user requests.

## Privacy controls and observability

Show when the microphone stream is actually open and when audio is being retained for recognition. Do not label a continuously active capture stream as fully disconnected. Expose effective configuration and granted scopes through both UI and CLI.

Proposed default network behavior: no telemetry and no request-content egress; model acquisition/update is a separately visible activity. A future self-hosted remote engine may be evaluated, but its connection and data boundary must be explicit. “Open source” and “local processing” are different properties and should be described separately.

## Configuration changes in flight

Increment a configuration epoch on accepted changes. Requests record the epoch used to plan; the executor rechecks current policy before effects. Tightening permissions revokes pending operations. Changing models affects new inference jobs; existing jobs either finish under a named version or are cancelled explicitly. Never silently reinterpret an approved request after a backend change.
