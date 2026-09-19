# Typed-request lifecycle prototype

This experiment extends the disposable sandbox with real typed input, request
identity/revisions, correlated interpretation jobs, cancellation, policy
invalidation, and optional proposal-bound confirmation. All action effects stay
inside generated temporary files. Python remains an experimental choice.

## Run

From the repository root:

```bash
python3 -B experiments/session_coordinator/cli.py --text 'Create a folder called Garden'
python3 -B experiments/session_coordinator/cli.py --text 'Find garden notes'
python3 -B experiments/session_coordinator/cli.py --text 'Just dictated text' --mode dictation
python3 -B experiments/session_coordinator/cli.py --confirm
python3 -B -m unittest discover -s experiments/session_coordinator -p 'test_*.py'
```

Without `--text`, the console accepts a single letter followed by Enter for new
command, dictation, revision, approval, cancellation, status, and quit. This is
an experimental sequential-key console, not a validated accessible desktop UI.
Completed requests require a new request; revision applies to pending requests.
`--confirm` is optional policy for testing proposal binding, not a requirement to
confirm every ordinary granted action.

## Interpretation sources

The default interpreter recognizes exactly three example inputs (ignoring case):
“Create a folder called Garden,” “Find garden notes,” and “Create a folder.”
Other text is reported unsupported. This is deterministic plumbing, **not AI**.
Dictation bypasses interpretation and returns text to the panel only.

`--response-file PATH` supplies a structured interpretation JSON object for an
arbitrary typed request. The object must match the intent evaluator's outcome
shape; it cannot contain host grants, approval fields, or request identity.
Files are read only for command interpretation, are limited to 64 KiB, and reject
duplicate keys/non-JSON constants. The experiment never executes supplied shell
text. The only action adapters remain folder creation and filename search.

## Controller lifecycle

`submit` returns a request ID. `begin_interpretation` produces a correlated ticket
plus model input. `accept_interpretation` consumes an output only for the active
job/revision/session; its Boolean return indicates delivery, not successful
admission. `revise` invalidates prior jobs/proposals/approvals. `execute` only
accepts ready requests and rechecks current state through the sandbox executor.

Optional confirmation uses a digest of the exact host-generated proposal,
including request revision and policy epoch. A corrected proposal cannot reuse
an earlier approval. Changing grants invalidates pending planning and stops
later execution steps. Locking a session cancels pending work; unlocking does
not revive it. Cancellation during execution preserves known completed effects.

Twenty-one controller tests and six subprocess console tests cover these paths.
No model was evaluated. The existing 11 sandbox tests still cover adapter effects
and simulated journal recovery separately.

## Limits

This is a single-threaded, in-process trusted controller API. It is not an
authenticated service, thread-safe event loop, production persistence layer,
or model process supervisor. Request states are in memory; the underlying
sandbox journal does not persist an entire session. Exceptions during dispatch
are conservatively reported as uncertain, with known earlier effects retained.

The synchronous console cannot accept a cancellation key while a blocking
interpreter call is running. The controller APIs support invalidation of late
responses; an event-driven UI/worker boundary remains necessary for responsive
real inference. No microphone, audio output, desktop injection, or live user-file
access is implemented.
