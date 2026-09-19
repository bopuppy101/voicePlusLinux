"""Synthetic recognition-event gate. No capture, audio decoding, or ASR model.

Events are complete text replacements, not incremental text fragments. The
trusted caller activates a fixed mode. Only a valid final event can release input
for interpretation; recognition supplies neither authority nor an input mode.
"""

import copy
from uuid import uuid4

from coordinator import EDITABLE, TransitionError


class TranscriptGate:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.capture = None

    def begin(self, *, mode="command", request_id=None):
        if type(mode) is not str or mode not in {"command", "dictation"}:
            raise ValueError("Unknown input mode")
        if not self.coordinator.active:
            raise TransitionError("Session is inactive")
        if self.capture is not None and self.capture["state"] == "receiving":
            raise TransitionError("Cancel or finalize the active input first")
        revision = None
        if request_id is not None:
            view = self.coordinator.snapshot(request_id)
            if mode != "command" or view["mode"] != "command" or view["state"] not in EDITABLE:
                raise TransitionError("Only a pending command can receive a spoken correction")
            # Invalidate an old model job or approval now, before recognition.
            # Keep the old text for context but make it explicitly non-final.
            self.coordinator.revise(request_id, view["text"], input_final=False)
            revision = self.coordinator.snapshot(request_id)["revision"]
        self.capture = {
            "capture_id": uuid4().hex, "session_id": self.coordinator.session_id,
            "input_epoch": self.coordinator.input_epoch,
            "policy_epoch": self.coordinator.policy_epoch, "mode": mode,
            "request_id": request_id, "request_revision": revision,
            "state": "receiving", "sequence": 0, "preview": "", "raw_final": None,
            "processed_final": None, "transformations": [], "reason": None,
        }
        self._last_event = None
        return self.capture["capture_id"]

    def _bound(self):
        if self.capture["request_id"] is None:
            return None
        try:
            view = self.coordinator.snapshot(self.capture["request_id"])
        except TransitionError:
            return None
        return view if view["revision"] == self.capture["request_revision"] else None

    def _stop(self, state, reason):
        view = self._bound()
        if view is not None and view["state"] == "received" and not view["input_final"]:
            self.coordinator.cancel(view["request_id"])
        self.capture.update(state=state, reason=reason)

    def cancel(self):
        if self.capture is None or self.capture["state"] != "receiving":
            return False
        self._stop("cancelled", "input_cancelled")
        return True

    def accept(self, event):
        if self.capture is None or self.capture["state"] != "receiving":
            return False
        # Late events from a previous capture must not cancel or alter a new one.
        if type(event) is not dict or event.get("capture_id") != self.capture["capture_id"]:
            return False
        if (not self.coordinator.active or self.capture["session_id"] != self.coordinator.session_id
                or self.capture["input_epoch"] != self.coordinator.input_epoch
                or self.capture["policy_epoch"] != self.coordinator.policy_epoch):
            self._stop("cancelled", "input_context_changed")
            return False
        if self.capture["request_id"] is not None:
            view = self._bound()
            if view is None or view["state"] != "received" or view["input_final"]:
                self._stop("cancelled", "input_context_changed")
                return False
        sequence = event.get("sequence")
        kind = event.get("kind")
        common = {"schema_version", "capture_id", "sequence", "kind"}
        keys = common | ({"code"} if kind == "error" else {"text"})
        if (set(event) != keys or type(event.get("schema_version")) is not int or event["schema_version"] != 1
                or type(sequence) is not int or not 1 <= sequence <= 1024
                or type(kind) is not str or kind not in {"partial", "final", "error"}):
            self._stop("failed", "invalid_transcript_event")
            return False
        if sequence < self.capture["sequence"]:
            return False
        if sequence == self.capture["sequence"]:
            if event != self._last_event:
                self._stop("failed", "conflicting_transcript_event")
            return False
        if sequence != self.capture["sequence"] + 1:
            self._stop("failed", "transcript_event_gap")
            return False
        if kind == "error":
            if event["code"] not in ("recognition_failed", "input_incomplete", "device_removed", "permission_lost"):
                self._stop("failed", "invalid_transcript_event")
                return False
            self.capture["sequence"] = sequence
            self._stop("failed", event["code"])
            return True
        text = event["text"]
        if type(text) is not str or len(text) > 8192 or (kind == "final" and not text.strip()):
            self._stop("failed", "invalid_transcript_event")
            return False
        self.capture.update(sequence=sequence, preview=text)
        self._last_event = copy.deepcopy(event)
        if kind == "partial":
            return True
        try:
            if self.capture["request_id"] is None:
                request = self.coordinator.submit(text, mode=self.capture["mode"])
                self.capture.update(request_id=request, request_revision=1)
            else:
                self.coordinator.finalize_input(self.capture["request_id"], text)
        except (ValueError, TransitionError):
            self._stop("failed", "input_delivery_failed")
            return False
        # Identity processing only. No V2T mappings have been imported or applied.
        self.capture.update(state="finalized", raw_final=text, processed_final=text)
        return True

    def snapshot(self):
        return copy.deepcopy(self.capture)
