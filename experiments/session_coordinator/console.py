"""Sequential-key Linux console with inference results delivered on its owner thread."""

import json
import os
import select
import sys

from coordinator import TERMINAL, TransitionError
from worker import InferenceWorker, deliver


def report(coordinator, request_id, interpreter):
    view = coordinator.snapshot(request_id)
    return {"backend": interpreter.name, "workspace": "disposable",
            **{key: view[key] for key in ("request_id", "revision", "state", "text", "proposal",
                                         "input_final", "confirmation_digest", "result")}}


class Console:
    def __init__(self, coordinator, interpreter, worker):
        self.coordinator, self.interpreter, self.worker = coordinator, interpreter, worker
        self.current = None
        self.entering = None
        self.closed = False
        self.tickets = {}
        self.presented_digest = None

    @property
    def prompt(self):
        return "Replacement request (c cancel, q quit): " if self.entering == "revision" else "Text: " if self.entering else "> "

    def show(self, request):
        view = report(self.coordinator, request, self.interpreter)
        if request == self.current:
            self.presented_digest = view["confirmation_digest"]
        return view

    def schedule(self):
        view = self.coordinator.snapshot(self.current)
        if view["state"] != "received" or not view["input_final"]:
            return []
        job = self.coordinator.begin_interpretation(self.current)
        try:
            accepted = self.worker.submit(job)
        except (ValueError, TypeError):
            accepted = False
        if not accepted:
            self.coordinator.fail_interpretation(job["ticket"], "inference_unavailable")
            return ["Inference worker is busy or unavailable. Start a new request after pending work settles."]
        self.tickets[self.current] = job["ticket"]
        return []

    def handle_line(self, line):
        if self.closed:
            return []
        try:
            if self.entering == "revision" and line.strip().casefold() in {"c", "q"}:
                self.entering = None  # Single-key escape without submitting text.
            elif self.entering:
                purpose = self.entering
                if purpose == "revision":
                    self.coordinator.finalize_input(self.current, line)
                else:
                    self.current = self.coordinator.submit(line, mode=purpose)
                self.entering = None
                self.presented_digest = None
                return [*self.schedule(), self.show(self.current)]
            action = line.strip().casefold()
            if action == "q":
                self.close()
                return []
            if action in {"n", "d"}:
                if self.current is not None and self.coordinator.snapshot(self.current)["state"] not in TERMINAL:
                    return ["Current request is still pending. Use r to revise, c to cancel, or s for status."]
                self.entering = "command" if action == "n" else "dictation"
                return []
            if self.current is None:
                return ["No current request. Use n or d."]
            if action == "r":
                view = self.coordinator.snapshot(self.current)
                self.coordinator.revise(self.current, view["text"], input_final=False)
                old = self.tickets.pop(self.current, None)
                if old:
                    self.worker.cancel(old)
                self.presented_digest = None
                self.entering = "revision"
                return [self.show(self.current)]
            if action == "c":
                self.coordinator.cancel(self.current)
                ticket = self.tickets.get(self.current)
                if ticket:
                    self.worker.cancel(ticket)
            elif action == "a":
                if not self.coordinator.approve(self.current, self.presented_digest):
                    return ["No displayed proposal awaiting confirmation."]
                self.coordinator.execute(self.current)
            elif action != "s":
                return ["Use n, d, r, a, c, s, or q."]
            return [self.show(self.current)]
        except (ValueError, TransitionError) as exc:
            return [f"Cannot complete this control operation: {exc}"]

    def tick(self):
        views = []
        for result in self.worker.drain():
            request = result["ticket"]["request_id"]
            if self.tickets.get(request) == result["ticket"]:
                self.tickets.pop(request)
            if not self.closed and deliver(self.coordinator, result):
                if self.coordinator.snapshot(request)["state"] == "ready":
                    self.coordinator.execute(request)
                views.append(self.show(request))
        return views

    def close(self):
        self.closed = True
        self.coordinator.set_active(False)
        self.worker.close()


def interactive(coordinator, interpreter):
    worker = InferenceWorker(interpreter)
    console = Console(coordinator, interpreter, worker)
    print("Disposable VPLinuxAI prototype. Backend:", interpreter.name)
    print("One letter then Enter: n command, d dictation, r revise, a approve, c cancel, s status, q quit.")
    print("Inference runs in the background. Controls affect the most recent request.")
    print("Example commands: Create a folder called Garden / Find garden notes / Create a folder")
    print(console.prompt, end="", flush=True)
    partial, dropping = bytearray(), False

    def display(items):
        for item in items:
            print("\n" + (json.dumps(item, indent=2, ensure_ascii=True) if isinstance(item, dict) else item))

    try:
        while not console.closed:
            # Raw descriptor reads avoid text-buffer/select disagreement for piped
            # input. This is a Linux terminal prototype, not a portable GUI.
            ready, _, _ = select.select([sys.stdin], [], [], 0.05)
            if ready:
                data = os.read(sys.stdin.fileno(), 4096)
                if not data:
                    break  # EOF cancels pending work; it never implies approval.
                for char in data:
                    if char == 10:
                        if dropping:
                            display(["Input line exceeds 8192 characters; discarded."])
                        else:
                            try:
                                line = partial.decode("utf-8").rstrip("\r")
                            except UnicodeDecodeError:
                                display(["Input line is not valid UTF-8; discarded."])
                            else:
                                display(console.handle_line(line) if len(line) <= 8192 else
                                        ["Input line exceeds 8192 characters; discarded."])
                        partial, dropping = bytearray(), False
                        if console.closed:
                            break
                        print(console.prompt, end="", flush=True)
                    elif not dropping:
                        partial.append(char)
                        if len(partial) > 32768:
                            partial, dropping = bytearray(), True
            if not console.closed:
                updates = console.tick()
                if updates:
                    display(updates)
                    print(console.prompt, end="", flush=True)
        return 0
    finally:
        console.close()
