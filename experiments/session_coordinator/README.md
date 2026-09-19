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
Pressing `r` immediately suspends the current request and invalidates its old job
and approval, before replacement text arrives. Invalid replacement text leaves
it suspended; type a new replacement, or use `c` to cancel or `q` to quit at the
replacement prompt. These two single-letter lines are controls in that prompt.
Only one current pending request is exposed: revise or cancel it before starting
another. Inference runs in a worker, so the console can process these controls
while awaiting a response. Results appear without another keypress. EOF and quit
cancel pending requests. Input lines are bounded and invalid UTF-8 is discarded.
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

`--endpoint http://127.0.0.1:8080/v1/chat/completions --model MODEL_ID`
uses an explicitly configured local chat server instead of the examples. This
does not install, download, launch, or select a model. The protocol targets the
JSON chat interface documented by [llama.cpp's server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md);
compatibility with a real server remains untested. Replace `MODEL_ID` with the
identifier configured on a server you have independently admitted. A numeric
loopback address, exact endpoint path, and explicit model are required. The
adapter ignores proxy environment variables and does not follow redirects.

Requests and responses are bounded to 64 KiB. Responses must contain one finished
assistant JSON outcome, with no duplicate keys, Markdown fences, authority
fields, or tool calls. Invalid or truncated output fails without action. The
adapter never retries. The model receives utterance/mode/context, not job tickets
or evaluation answers. The coordinator independently validates every proposal.
Loopback restricts this client's destination; it does not prove that the server
keeps data local or that its model is open source. Those are admission decisions.

HTTP framing is checked independently of JSON validity: a short declared body or
an unfinished chunked body is rejected even if the received prefix is valid JSON.
Ambiguous transfer-encoding/content-length combinations are rejected. Unexpected
interpreter error codes become a bounded `inference_invalid_response` failure.

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

Corrections and clarification replies retain bounded context for this same
pending request. `context.pending_request.turns` contains up to four previous
finalized user utterances and, where available, a sanitized admitted proposal or
clarification. The current replacement remains the job's `utterance`. History
contains no job IDs, operation IDs, grants, approvals, or execution results.
It helps a real model interpret “Gardening instead” or an answer such as “Garden”;
the deterministic example interpreter still recognizes only its three phrases.

Starting correction captures history once; partial input and finalization do not
duplicate it. Earlier outputs remain invalid and every new proposal is checked
under current permissions. Policy changes remove historical model interpretations
while retaining user text; cancellation and terminal results clear the context.
The history envelope is limited to 16 KiB of ASCII-escaped JSON, in addition to
the full HTTP body's 64 KiB bound. Overflow fails the request with
`correction_context_limit` and requires a new complete request. It never truncates
an antecedent or leaves an older plan executable. This is pending-request context,
not general conversation memory or evidence of model comprehension.

Each component has focused tests linked from the [architecture map](../../docs/High-Level-Design/architecture.md#implemented-prototype-map).
They cover controller states, console controls and subprocess behavior, fake HTTP,
worker cancellation, and the [synthetic transcript boundary](test_transcripts.py).
Independent [QA regressions](test_boundary_regressions.py) cover response framing,
error handling, and results arriving while correction text is being entered.
[Correction-context tests](test_correction_context.py) cover isolation, cleanup,
ordering, and exact turn/byte limits. Current counts and results live in
[progress](../../docs/High-Level-Design/progress.md), so this README describes behavior rather
than duplicating a changing test count. No microphone or recognizer is connected,
and no model has been evaluated. Sandbox effect/recovery tests remain separate.

## Limits

The controller is owned by one thread, with a separate inference worker and a
Linux console event pump. These are trusted in-process APIs, not an authenticated
service, general concurrent controller, production persistence layer, or model
process supervisor. Request states are in memory; the underlying
sandbox journal does not persist an entire session. Exceptions during dispatch
are conservatively reported as uncertain, with known earlier effects retained.
Request history is bounded, but the disposable executor's journal retains prior
operations for the session and can grow during long runs. Production retention
and storage limits remain unimplemented.

The worker receives copied bounded data, never a controller/executor reference.
Only the console's owner thread delivers outcomes and dispatches admitted plans.
Its default capacity is four jobs, including running calls and undrained results;
there is one worker thread and no automatic pool expansion. Cancelling queued
work skips inference when possible. Cancelling running work suppresses delivery,
but cannot stop its HTTP server or forcibly terminate a Python call. Its slot is
retained until the call settles and the result is drained. A stuck call can block
later inference; the console remains responsive and reports saturation. Closing
does not wait indefinitely and never turns a late result into an action.

The one-shot `--text` path remains synchronous. Sandbox action dispatch also
remains synchronous: responsive inference does not establish bounded action
cancellation latency. A separate process supervisor and real desktop event loop
remain production work. No microphone, audio output, desktop injection, or live
user-file access is implemented.

`--timeout` is a socket inactivity timeout (default 10 seconds, maximum 30), with
additional elapsed-time checks while reading the body. It is not a hard total
deadline: a server trickling HTTP headers can occupy the synchronous call longer.
Hard worker termination needs a separate process supervisor. Test timings
describe fake-server transport only, not model speed, quality, or OS performance.
