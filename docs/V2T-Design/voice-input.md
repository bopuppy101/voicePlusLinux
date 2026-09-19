# Voice input and V2T reuse

Status: proposed pipeline and evaluation scope, grounded in inspected V2T source. No microphone capture or model execution has been performed for this project.

The [transcript boundary experiment](transcript-boundary.md) now checks partial
preview, finality, mode authority, and correction/cancellation ordering using
synthetic events. It does not yet connect a microphone or recognizer.

## Preserve useful existing behavior

V2T already has recording control, buffering, model loading, transcription, mappings, formatting, and platform-specific text delivery. Reuse should preserve attribution and isolate useful modules rather than copying an entire launcher and its environment assumptions unchanged. See the [source review](v2t-source-review.md).

On the reviewed `develop` commit, the Ubuntu Wayland launcher disables CUDA visibility and runs as the desktop user. Its source comments describe a particular local resource-sharing reason. This illustrates why launcher behavior must be inspected separately from the Python code's CPU/CUDA autodetection. It is not a proposed VPLinuxAI device policy. [Reviewed launcher](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/ubuntu-26.04/run-dbdude-v2t.bash).

## Logical pipeline

```text
Explicit activation → Device capture → Bounded audio buffer
 → Optional segmentation → Recognition → Final transcript
 → Mode-specific processing → Text delivery or command interpretation
```

Keep raw recognition text and processed text distinct. Store which mappings changed an utterance while it is in use. Dictation punctuation rules must not accidentally rewrite a filename or command argument without a visible trace. A proposal for commands is to supply both raw and normalized text to interpretation, with transformation metadata, rather than permanently replacing the only record.

## Recognition adapter contract

Accept an audio reference, declared sample format/rate, language setting, request ID, and cancellation signal. Return transcript revisions with final/partial status, segment timing where available, and an error category when capture or recognition fails. Include model/artifact version in diagnostic metadata. Model-specific confidence values are optional and must not be treated as universally calibrated probabilities.

A final transcript means recognition is finished for that revision, not that its contents are correct. In the first slice partial output may update a visible preview, but cannot start a system mutation.

## Capture design questions

Keep the audio callback short; enqueue frames and perform heavier work elsewhere. Define maximum buffered duration/bytes and behavior on overflow. Do not silently drop samples and then execute a command reconstructed from incomplete audio. Select sample rate/channel conversion explicitly and test device-native formats.

Compare the existing `sounddevice` path with a PipeWire integration spike only if it addresses a measured problem. PipeWire provides a graph-oriented multimedia framework and low-latency processing facilities; that makes it relevant to evaluate, not a reason to rewrite functioning capture before measurement. [PipeWire documentation](https://pipewire.pages.freedesktop.org/pipewire/).

## Activation and mode proposal

Mike named the OS voice service **Lanzo** and supplied **“Yo Lonzo”** as its spoken wake phrase. **“Yo”** is an attention cue like “Hey,” not part of the service name. Preserve the supplied phrase and service spelling separately; pronunciation and spelling normalization have not yet been specified.

Wake-phrase activation is part of the intended OS experience. The detector, listening behavior, and handling of false activations remain design questions; no wake detector has been implemented or tested. Waking the voice service and resuming a suspended computer are separate capabilities; hardware-level wake from sleep has not been specified.

The default prototype uses explicit single-key toggle activation, avoiding hold duration and key chords. A configurable dedicated key must not take the ordinary space key away from applications globally. In the VPLinuxAI panel, a large focused control can be activated with one key. Test accidental repeats and tremor-related double activation.

Dictation and command modes have visible persistent labels. The user can change mode by a simple control before recording. Automatic mode inference and the implementation of the requested wake phrase need their own evidence and settings; they are not implemented in the current prototype.

Stop/cancel must be available without depending on the speech recognizer. On lock, logout, explicit stop, permission loss, or device removal, stop capture and clear pending delivery. Whether to keep a capture stream warm while inactive is an explicit privacy/power/latency choice, not an invisible implementation detail.

## Delivery behavior

Capture the intended target at activation if the desktop allows it, then revalidate before insertion. If the target changed or cannot be verified, keep the transcript in the VPLinuxAI panel for explicit delivery. Never insert unexpectedly into a new focused terminal or password field. Prevent accidental newline/Enter submission in terminals; distinguish text insertion from invoking a command.

A text-injection process returning zero does not prove the application received all text. Mark the level of evidence accurately. Do not blindly retry partial insertion and duplicate the utterance.

## Candidate comparison

Use V2T's current faster-whisper path as the initial baseline. Evaluate another engine only on the same audio, hardware, mappings, and warm/cold conditions. Do not transfer upstream speed claims into VPLinuxAI performance claims. [faster-whisper upstream](https://github.com/SYSTRAN/faster-whisper).

The benchmark should separate recognition quality, postprocessing quality, and delivery reliability. The complete system must meet the baseline; replacing a recognizer while losing phrase mappings is not automatically an improvement.
