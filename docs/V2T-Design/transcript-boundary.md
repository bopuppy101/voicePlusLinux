# Transcript events and correction boundaries

Status: implemented as a synthetic in-process experiment in
[transcripts.py](../../experiments/session_coordinator/transcripts.py), with 17
tests. No audio is recorded or decoded, no recognizer is imported, and no V2T
code is copied. This isolates the input-to-request behavior that any recognition
engine must satisfy.

## Activation owns the mode and identity

A trusted input controller explicitly begins a capture in `command` or
`dictation` mode and obtains a fresh capture ID. The gate records session ID,
input epoch, policy epoch, and optional correction request/revision. Recognition
events cannot set mode, grants, approvals, or request identity. Capture IDs are
correlation values, not authentication credentials; production IPC still needs
sender authentication and scope checks.

The prototype has one active capture. Beginning a second requires finalizing or
cancelling the first. A session lock increments the host's input epoch. Thus a
final transcript arriving after lock and unlock still belongs to obsolete input
and cannot revive it. Policy changes also invalidate in-progress input. This is
separate from stopping an actual microphone stream, which remains capture-adapter
work.

## Recognition events

Each text event contains exactly:

```json
{
  "schema_version": 1,
  "capture_id": "ID_RETURNED_BY_BEGIN",
  "sequence": 1,
  "kind": "partial",
  "text": "Create a folder called"
}
```

`kind` is `partial` or `final`. Text is a complete replacement for the capture's
preview, not a fragment to append. A final is a complete utterance, not the final
segment alone. An ASR adapter with segment-level output must assemble the complete
utterance before emitting it. Recognition errors replace the `text` field with
`code` and use `kind: error`; codes are `recognition_failed`, `input_incomplete`,
`device_removed`, or `permission_lost`.

The experimental limits are 8192 text characters and 1024 sequenced events per
capture. Sequence starts at one and must be contiguous. Exact repeats of the
latest event are ignored; a conflicting latest event fails the capture. Earlier
events are ignored. A gap fails closed rather than interpreting incomplete input.
Unknown capture IDs are ignored so an old worker cannot poison new input. These
are bounded reliable-channel rules for the experiment, not a negotiated network
protocol or a universal ASR streaming requirement.

A partial can update only the preview. It does not create a new command request,
start inference, or dispatch an action. A valid nonblank final creates exactly
one request. Command input enters `received`; its interpretation/authorization
pipeline still must run. Dictation enters the existing panel-only text path and
cannot begin interpretation. Duplicate or late finals do not create another
request. Invalid, oversized, cancelled, and incomplete events never release text
for execution.

## Spoken correction suspends the old request immediately

Waiting for a corrected final transcript before invalidating a proposal would
leave the old command executable while the user is correcting it. The experiment
therefore treats correction activation as a state change:

1. Check that the target is a pending command, not an executing/finished action.
2. Increment its request revision immediately; clear the old job, proposal, and
   approval. Preserve prior text only as context and mark `input_final: false`.
3. Show recognition partials as preview. `begin_interpretation` rejects this
   unfinalized revision, even though prior text is still present.
4. The valid final replaces text and finalizes that same revision. Only then may
   interpretation begin.
5. Cancelling or failing this correction cancels the unfinalized request. The old
   proposal is never restored automatically.

If a later typed correction supersedes the capture, its new revision wins. The
old recognition result is discarded without cancelling the newer request.
Correcting an executing action remains a separate cancel/reconcile/new-request
workflow; this gate deliberately rejects that shortcut.

## Raw and processed text

The gate records raw and processed final text separately, but currently applies
identity processing: both are equal and `transformations` is empty. This is
explicitly not V2T mapping parity. A future mapping adapter must preserve version,
rules applied, changed spans, and mode. It must not turn a recognizer's guessed
word into an invisible filename change. The initial AI job still receives the
final text through the existing model contract; adding dual raw/processed context
needs a versioned change and evaluation cases.

## Evidence and remaining work

Tests cover preview-only partials, final replay, mode authority, immediate
correction invalidation, stale model responses, cancelled corrections, later
typed revisions, policy/lock changes, unlock behavior, event gaps, duplicate
conflicts, errors, bounds, and a synthetic final through the disposable create
adapter. These tests establish gate behavior only; they do not measure recognition
accuracy, V2T parity, microphone latency, background listening, or desktop delivery.

The next recognition adapter must declare whether it emits segments or full
replacement text, map its cancellation/errors into these outcomes, and prove it
stops capture independently of recognition. Actual device capture, buffer
overflow detection, recognition deadlines, model provenance, and end-to-end audio
benchmarks remain unimplemented. No action is allowed from speculative partial
text in this first slice.
