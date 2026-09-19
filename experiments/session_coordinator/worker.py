"""Bounded background interpretation; the owner thread alone mutates requests.

Cancellation suppresses delivery and can skip queued work. It cannot terminate a
running Python call or prove that an inference server stopped computing.
"""

import copy
import json
import queue
import threading

from inference import InferenceError, MAX_BYTES


class InferenceWorker:
    def __init__(self, interpreter, *, capacity=4):
        if type(capacity) is not int or not 1 <= capacity <= 16:
            raise ValueError("Worker capacity must be an integer from 1 to 16")
        self.interpreter = interpreter
        self.capacity = capacity
        self._jobs = queue.Queue(maxsize=capacity)
        self._results = queue.Queue(maxsize=capacity)
        self._lock = threading.Lock()
        self._entries = {}
        self._closed = threading.Event()
        self._thread = threading.Thread(target=self._run, name="vplinuxai-inference", daemon=True)
        self._thread.start()

    @staticmethod
    def _ticket(ticket):
        keys = {"job_id", "session_id", "request_id", "request_revision", "policy_epoch"}
        return (type(ticket) is dict and set(ticket) == keys
                and all(type(ticket[k]) is str and ticket[k] for k in ("job_id", "session_id", "request_id"))
                and all(type(ticket[k]) is int and ticket[k] >= 1 for k in ("request_revision", "policy_epoch")))

    def submit(self, job):
        if type(job) is not dict or not self._ticket(job.get("ticket")):
            raise ValueError("A correlated job is required")
        # Copy before sharing; reject non-JSON and excessive payloads at the boundary.
        raw = json.dumps(job, ensure_ascii=True, allow_nan=False)
        if len(raw.encode()) > MAX_BYTES:
            raise ValueError("Job exceeds worker limit")
        job = json.loads(raw)
        key = job["ticket"]["job_id"]
        with self._lock:
            if self._closed.is_set():
                raise ValueError("Worker is closed")
            if key in self._entries:
                raise ValueError("Job already submitted")
            if len(self._entries) >= self.capacity:
                return False
            self._entries[key] = {"ticket": job["ticket"], "cancelled": False}
            self._jobs.put_nowait(job)
        return True

    def cancel(self, ticket):
        if not self._ticket(ticket):
            return False
        with self._lock:
            entry = self._entries.get(ticket["job_id"])
            if entry is None or entry["ticket"] != ticket:
                return False
            entry["cancelled"] = True
            return True

    def _cancelled(self, key):
        with self._lock:
            return self._closed.is_set() or self._entries[key]["cancelled"]

    def _run(self):
        while not self._closed.is_set():
            try:
                job = self._jobs.get(timeout=0.05)
            except queue.Empty:
                continue
            key = job["ticket"]["job_id"]
            result = {"ticket": job["ticket"]}
            if not self._cancelled(key):
                try:
                    payload = {k: job[k] for k in ("mode", "utterance", "context")}
                    output = self.interpreter.interpret(payload)
                    raw = json.dumps(output, ensure_ascii=True, allow_nan=False)
                    if len(raw.encode()) > MAX_BYTES:
                        raise ValueError("Output exceeds worker limit")
                    result["output"] = json.loads(raw)
                except InferenceError as exc:
                    result["error"] = exc.code
                except Exception:
                    # Do not print potentially sensitive interpreter exception text.
                    result["error"] = "inference_invalid_response"
            if self._cancelled(key):
                result = {"ticket": job["ticket"], "cancelled": True}
            # Capacity counts jobs until drain, so every accepted job has room for
            # exactly one result. No worker callback touches controller/executor.
            self._results.put_nowait(result)
            self._jobs.task_done()

    def drain(self):
        results = []
        while True:
            try:
                result = self._results.get_nowait()
            except queue.Empty:
                break
            with self._lock:
                entry = self._entries.pop(result["ticket"]["job_id"])
                if entry["cancelled"] or self._closed.is_set():
                    result = {"ticket": result["ticket"], "cancelled": True}
            results.append(copy.deepcopy(result))
        return results

    def close(self, *, wait_seconds=0):
        if type(wait_seconds) not in (int, float) or not 0 <= wait_seconds <= 1:
            raise ValueError("Close wait must be from zero to one second")
        self._closed.set()
        self._thread.join(timeout=wait_seconds)
        return not self._thread.is_alive()


def deliver(coordinator, result):
    """Call only on the controller's owner thread. Never dispatches actions."""
    if result.get("cancelled"):
        return False
    if "error" in result:
        return coordinator.fail_interpretation(result["ticket"], result["error"])
    return coordinator.accept_interpretation(result["ticket"], result["output"])
