# Worked workflows and failure branches

Status: detailed behavior proposals. Application names and paths below are fixtures, not commands to execute on Mike's machine.

## A. Dictate a note

1. User focuses a supported editor and activates dictation with the configured single key.
2. The system records the mode, intended target, session, and request ID. A visible listening indicator appears.
3. User stops recording. Capture closes or returns to the explicitly configured inactive state; recognition produces a final transcript.
4. Mappings/formatting produce text while preserving the raw transcript for session correction.
5. The delivery adapter rechecks session and target. If valid, it inserts once and reports the available level of acknowledgement.
6. If focus changed, the transcript stays in the panel awaiting explicit delivery. No inferred command runs even if the text is “delete the file.”

Failure cases: microphone removal marks input incomplete; model timeout preserves a retryable recording only if retention policy permits; partial insertion is shown as uncertain rather than retried automatically. After cancellation, late recognition output is discarded.

## B. Create a folder from an English request

Fixture: `documents` is an authorized root and `Garden` does not exist.

1. Final command text arrives: “I need a Garden folder in Documents.”
2. Interpretation proposes `directory.create` with root ID `documents` and leaf `Garden`.
3. Static checks validate shape, current revision, session, policy epoch, and grant.
4. The real adapter resolves the root and checks current filesystem state. It records intent and uses the appropriate bounded operation.
5. Verification establishes the directory result. The user receives a concrete result with its location.

Variations: no root grant triggers permission handling; “over there” without context triggers clarification; an existing file named Garden is a conflict; an existing directory can satisfy the desired state without claiming a new creation. A malformed model response never reaches execution.

## C. Find and move a note

1. Search within a selected root returns `note-a` and `note-b`, each with path and freshness metadata.
2. The user selects one using single-key navigation. Selection becomes a context reference, not a guessed filename.
3. “Move this into Garden” resolves the selected object and destination to a concrete proposal.
4. The executor rechecks both immediately before the effect. A stale selection prompts re-resolution, not a move of whatever now occupies the path.
5. The same-filesystem, no-overwrite adapter executes and verifies. The UI reports the final location.

If the process restarts after the effect, use the [recovery table](recovery-cases.md). If another file occupies the destination, stop with a conflict. If “the other note” arrives before execution, revise and invalidate the old proposal. If it arrives after completion, treat it as a new request with visible prior effects.

## D. Request correction and approval binding

Initial proposal: move `note-a` to `Garden`. The user changes the destination to `Archive`. The coordinator increments the request revision, cancels inference/jobs for the old revision, discards any old approval, and builds a new proposal. An old model response or UI click arriving late cannot authorize the revised action.

Once execution starts, a correction is not a retroactive edit. Request cancellation of remaining work, reconcile the current step, then interpret the new request against actual state.

## E. Model unavailable

The model fails to load or exceeds its memory budget. The panel reports that command interpretation is unavailable and shows a diagnostic path. Dictation can continue if its recognizer is healthy. Typed commands through ordinary Linux tools remain usable. The system never falls back to executing raw recognized text as shell commands.

## F. Lock, logout, and restart

Lock invalidates pending dictation delivery and stops listening. A queued command that has not started an effect is suspended/cancelled according to the session policy and cannot execute under a newly active user. An operation already in progress must be reconciled; session loss does not erase effects.

After restart, show recovered outcomes from bounded journal metadata, but do not replay old utterances. Model warm-up or update failure must not prevent access to the ordinary desktop.

## G. Unsupported but reasonable request

“Send this note to Alex” is outside the initial capability registry. Interpretation should say the action is unsupported or explain the available next step. It must not invent a messaging capability or use shell access to bypass the registry. Later adding messaging requires its own recipient resolution, permission, and verification contract.

## H. Audio output request

“Find a video about gardening” may return text results. It does not imply playback permission. A deliberate “play this video” request can be evaluated by a future playback capability. Voice input, app startup, and reading an article never automatically enable spoken output or autoplay.

## Traceability

A/B exercise R02–R07 and U01/U04; C/D exercise R03/R07 and U03/U05/U06; E/F exercise R04/R06 and U07/U08; G/H define capability and playback boundaries. See [requirements](requirements.md). None of these scenario descriptions counts as a passing end-to-end test.
