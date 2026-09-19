"""Single-threaded lifecycle experiment around a disposable action sandbox.

Controller methods are trusted in-process APIs, not authenticated IPC endpoints.
Interpretation outputs are untrusted structured data. No inference runs here.
"""

from dataclasses import dataclass, field
import copy
import hashlib
import hmac
import json
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.sandbox_workflow.demo import Coordinator as Executor, Sandbox
from experiments.contract_reference.check_contracts import validate
from experiments.intent_evaluation.score import valid_outcome


TERMINAL = {"succeeded", "failed", "cancelled", "outcome_unknown"}
EDITABLE = {"received", "interpreting", "needs_clarification", "proposed", "awaiting_confirmation", "ready"}
MAX_PRIOR_TURNS = 4
MAX_PRIOR_CONTEXT_BYTES = 16_384


class TransitionError(ValueError):
    pass


@dataclass
class Request:
    request_id: str
    text: str
    mode: str
    input_final: bool = True
    revision: int = 1
    state: str = "received"
    job: dict | None = None
    proposal: dict | None = None
    confirmation_digest: str | None = None
    approved_digest: str | None = None
    result: dict | None = None
    live_session: dict | None = None
    cancel_requested: bool = False
    events: list = field(default_factory=list)
    sequence: int = 0
    prior_turns: list = field(default_factory=list)


class SessionCoordinator:
    def __init__(self, sandbox, *, confirmation_required=False):
        if type(confirmation_required) is not bool:
            raise ValueError("confirmation_required must be boolean")
        self.executor = Executor(sandbox)
        self.session_id = uuid4().hex
        self.active = True
        self.input_epoch = 1
        self.policy_epoch = 1
        self.confirmation_required = confirmation_required
        self.grants = [{"capability": "directory.create", "root_id": "documents"},
                       {"capability": "file.search", "root_id": "documents"}]
        self._requests = {}
        self._executing = False

    @staticmethod
    def _text(value):
        if type(value) is not str or not value.strip() or len(value) > 8192:
            raise ValueError("Text must be nonblank and at most 8192 characters")
        return value

    def _get(self, request_id):
        if type(request_id) is not str or request_id not in self._requests:
            raise TransitionError("Unknown request")
        return self._requests[request_id]

    def _event(self, request, state, event):
        request.state = state
        request.sequence += 1
        request.events.append({"sequence": request.sequence, "revision": request.revision,
                               "state": state, "event": event})
        request.events = request.events[-128:]

    def _session(self, request):
        return {"session_id": self.session_id, "request_id": request.request_id,
                "request_revision": request.revision, "policy_epoch": self.policy_epoch,
                "active": self.active, "cancelled": request.cancel_requested,
                "input_final": request.input_final, "mode": request.mode}

    def _fail(self, request, reason):
        request.job = None
        request.prior_turns = []
        request.result = {"status": "failed", "reason": reason, "steps": []}
        self._event(request, "failed", reason)

    def submit(self, text, *, mode="command"):
        text = self._text(text)
        if type(mode) is not str or mode not in {"command", "dictation"}:
            raise ValueError("Unknown mode")
        if not self.active:
            raise TransitionError("Session is inactive")
        if len(self._requests) >= 32:
            removable = next((key for key, value in self._requests.items() if value.state in TERMINAL), None)
            if removable is None:
                raise TransitionError("Too many pending requests")
            del self._requests[removable]
        request = Request(uuid4().hex, text, mode)
        self._requests[request.request_id] = request
        self._event(request, "received", "submitted")
        if mode == "dictation":
            request.result = {"status": "succeeded", "kind": "dictation", "text": text,
                              "delivery": "panel_only", "steps": []}
            self._event(request, "succeeded", "dictation_ready")
        return request.request_id

    def revise(self, request_id, text, *, input_final=True):
        request = self._get(request_id)
        text = self._text(text)
        if type(input_final) is not bool:
            raise ValueError("input_final must be boolean")
        if request.state not in EDITABLE or not self.active:
            raise TransitionError("Only a pending request can be revised")
        prior = copy.deepcopy(request.prior_turns)
        if request.input_final:
            turn = {"utterance": request.text}
            if request.state in {"ready", "awaiting_confirmation"}:
                # Historical interpretations describe the pending intent, not
                # execution authority. Remove every host envelope/operation ID.
                admission = validate(self._session(request), request.proposal, self.grants)
                if admission["decision"] == "allow":
                    turn["interpretation"] = {"kind": "proposal", "actions": [
                        {"capability": step["capability"], "arguments": copy.deepcopy(step["arguments"])}
                        for step in request.proposal["steps"]]}
            elif request.state == "needs_clarification":
                turn["interpretation"] = copy.deepcopy(request.result)
            prior.append(turn)
        request.text = text
        request.input_final = input_final
        request.revision += 1
        request.job = request.proposal = request.confirmation_digest = request.approved_digest = None
        request.result = None
        # Overflow still invalidates the old executable revision; never silently
        # drop an antecedent or leave the prior approval usable after correction.
        if len(prior) > MAX_PRIOR_TURNS or len(json.dumps(
                {"turns": prior}, ensure_ascii=True, allow_nan=False).encode("utf-8")) > MAX_PRIOR_CONTEXT_BYTES:
            self._fail(request, "correction_context_limit")
            raise TransitionError("Correction context limit reached; start a new complete request")
        request.prior_turns = prior
        self._event(request, "received", "revised")

    def finalize_input(self, request_id, text):
        request = self._get(request_id)
        text = self._text(text)
        if request.state != "received" or request.input_final or not self.active:
            raise TransitionError("Request is not awaiting final input")
        request.text = text
        request.input_final = True
        self._event(request, "received", "input_finalized")

    def begin_interpretation(self, request_id):
        request = self._get(request_id)
        if request.state != "received" or request.mode != "command" or not request.input_final or not self.active:
            raise TransitionError("Request is not ready for interpretation")
        request.job = {"job_id": uuid4().hex, "session_id": self.session_id,
                       "request_id": request.request_id, "request_revision": request.revision,
                       "policy_epoch": self.policy_epoch}
        self._event(request, "interpreting", "interpretation_started")
        context = {"roots": {"documents": "Disposable Documents"},
                   "default_root_id": "documents", "capabilities": ["directory.create", "file.search"]}
        if request.prior_turns:
            context["pending_request"] = {"turns": copy.deepcopy(request.prior_turns)}
        return {"ticket": copy.deepcopy(request.job), "mode": request.mode, "utterance": request.text,
                "context": context}

    def _current_job(self, ticket):
        keys = {"job_id", "session_id", "request_id", "request_revision", "policy_epoch"}
        if type(ticket) is not dict or set(ticket) != keys:
            return None
        if not all(type(ticket[key]) is str for key in ("job_id", "session_id", "request_id")):
            return None
        if not all(type(ticket[key]) is int for key in ("request_revision", "policy_epoch")):
            return None
        request = self._requests.get(ticket["request_id"])
        if request is None or request.state != "interpreting" or not self.active:
            return None
        if request.job != ticket:
            return None
        return request

    def fail_interpretation(self, ticket, reason):
        if reason not in ("inference_timeout", "inference_unavailable", "inference_invalid_response"):
            raise ValueError("Unknown inference failure")
        request = self._current_job(ticket)
        if request is None:
            return False
        self._fail(request, reason)
        return True

    def accept_interpretation(self, ticket, output):
        request = self._current_job(ticket)
        if request is None:
            return False
        request.job = None
        if not valid_outcome(output) or output["kind"] == "dictation":
            self._fail(request, "interpretation_invalid")
            return True
        if output["kind"] == "clarify":
            if len(output["missing"]) > 3 or any(item not in {"name", "root_id", "query"} for item in output["missing"]):
                self._fail(request, "interpretation_invalid")
                return True
            request.result = {"kind": "clarify", "missing": copy.deepcopy(output["missing"])}
            self._event(request, "needs_clarification", "clarification_required")
        elif output["kind"] == "unsupported":
            self._fail(request, "unsupported_request")
        else:
            request.proposal = {"schema_version": 1, "session_id": self.session_id,
                                "request_id": request.request_id, "request_revision": request.revision,
                                "policy_epoch": self.policy_epoch,
                                "steps": [{"operation_id": f"step-{index + 1}", **copy.deepcopy(action)}
                                          for index, action in enumerate(output["actions"])]}
            self._event(request, "proposed", "proposal_received")
            admission = validate(self._session(request), request.proposal, self.grants)
            if admission["decision"] != "allow":
                self._fail(request, admission["code"])
                return True
            digest = self._digest(request.proposal)
            requires = self.confirmation_required and any(
                step["capability"] == "directory.create" for step in request.proposal["steps"])
            request.confirmation_digest = digest if requires else None
            self._event(request, "awaiting_confirmation" if requires else "ready",
                        "confirmation_required" if requires else "admitted")
        return True

    @staticmethod
    def _digest(proposal):
        return hashlib.sha256(json.dumps(proposal, sort_keys=True, separators=(",", ":"),
                                         ensure_ascii=False).encode("utf-8")).hexdigest()

    def approve(self, request_id, digest):
        request = self._get(request_id)
        if request.state != "awaiting_confirmation" or type(digest) is not str or not self.active:
            return False
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            return False
        if not hmac.compare_digest(digest, request.confirmation_digest):
            return False
        admission = validate(self._session(request), request.proposal, self.grants)
        if admission["decision"] != "allow":
            self._fail(request, admission["code"])
            return False
        request.approved_digest = digest
        self._event(request, "ready", "confirmed")
        return True

    def cancel(self, request_id):
        request = self._get(request_id)
        if request.state in TERMINAL:
            return False
        request.cancel_requested = True
        request.prior_turns = []
        request.job = None
        if request.live_session is not None:
            request.live_session["cancelled"] = True
        if request.state in {"executing", "cancellation_pending"}:
            self._event(request, "cancellation_pending", "cancellation_requested")
        else:
            request.proposal = None
            request.result = {"status": "cancelled", "steps": []}
            self._event(request, "cancelled", "cancelled_before_execution")
        return True

    def set_active(self, active):
        if type(active) is not bool:
            raise ValueError("active must be boolean")
        if self.active and not active:
            self.input_epoch += 1
        self.active = active
        if not active:
            for request in self._requests.values():
                if request.live_session is not None:
                    request.live_session["active"] = False
                if request.state not in TERMINAL:
                    self.cancel(request.request_id)

    def set_grants(self, grants):
        if type(grants) is not list or len(grants) > 2:
            raise ValueError("Only the two sandbox grants are supported")
        pairs = []
        for grant in grants:
            if type(grant) is not dict or set(grant) != {"capability", "root_id"}:
                raise ValueError("Invalid grant")
            if grant["root_id"] != "documents" or grant["capability"] not in ("directory.create", "file.search"):
                raise ValueError("Unknown sandbox grant")
            pairs.append((grant["capability"], grant["root_id"]))
        if len(set(pairs)) != len(pairs):
            raise ValueError("Duplicate grant")
        updated = [{"capability": cap, "root_id": root} for cap, root in sorted(pairs)]
        if updated == self.grants:
            return
        self.grants[:] = updated
        self.policy_epoch += 1
        for request in self._requests.values():
            # A policy change cannot preserve a model-derived action suggestion
            # as authority. User utterances remain reference data for replanning.
            request.prior_turns = [{"utterance": turn["utterance"]} for turn in request.prior_turns]
            if request.live_session is not None:
                request.live_session["policy_epoch"] = self.policy_epoch
            elif request.state in EDITABLE:
                request.job = request.proposal = request.confirmation_digest = request.approved_digest = None
                request.result = None
                self._event(request, "received", "policy_invalidated")

    def execute(self, request_id, *, before_step=None, interrupt_after_effect=False):
        request = self._get(request_id)
        if request.state != "ready" or self._executing:
            raise TransitionError("Request is not ready, or another request is executing")
        if request.confirmation_digest is not None and request.approved_digest != self._digest(request.proposal):
            self._fail(request, "approval_invalid")
            return self.snapshot(request_id)
        request.live_session = self._session(request)
        self._executing = True
        self._event(request, "executing", "dispatch_started")
        try:
            outcome = self.executor.run(request.live_session, request.proposal, self.grants,
                                        before_step=before_step, interrupt_after_effect=interrupt_after_effect)
        except Exception as exc:
            # The experiment treats dispatch failures conservatively; effects may exist.
            known = []
            for step in request.proposal["steps"]:
                record = self.executor.records.get(self.executor._key(request.proposal, step))
                if record is not None and record["state"] == "completed":
                    known.append({"operation_id": step["operation_id"], **copy.deepcopy(record["result"]),
                                  "observed_before_exception": True})
            request.result = {"status": "outcome_unknown", "reason": "dispatch_exception",
                              "error_type": type(exc).__name__, "steps": known}
            self._event(request, "outcome_unknown", "dispatch_uncertain")
        else:
            request.result = copy.deepcopy(outcome)
            if outcome["status"] == "outcome_unknown":
                state = "outcome_unknown"
            elif request.cancel_requested:
                state = "cancelled"
            elif outcome["status"] == "succeeded":
                state = "succeeded"
            else:
                state = "failed"
            self._event(request, state, "dispatch_settled")
        finally:
            self._executing = False
            request.live_session = None
            if request.state in TERMINAL:
                request.prior_turns = []
        return self.snapshot(request_id)

    def snapshot(self, request_id):
        request = self._get(request_id)
        return copy.deepcopy({"request_id": request.request_id, "revision": request.revision,
                              "mode": request.mode, "text": request.text, "state": request.state,
                              "input_final": request.input_final,
                              "pending_context": {"turns": request.prior_turns} if request.prior_turns else None,
                              "proposal": request.proposal, "confirmation_digest": request.confirmation_digest,
                              "result": request.result, "events": request.events})
