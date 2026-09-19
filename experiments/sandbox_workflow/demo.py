#!/usr/bin/env python3
"""Disposable fixture-only workflow; no real AI, media, or desktop control."""

import copy
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "contract_reference"))
from check_contracts import validate  # noqa: E402


class InterruptedAfterEffect(RuntimeError):
    """Controlled fault injection, not an actual process crash."""


class Sandbox:
    def __init__(self):
        self._temporary = tempfile.TemporaryDirectory(prefix="vplinuxai-fixture-")
        self.root = Path(self._temporary.name)
        self.documents = self.root / "documents"
        self.documents.mkdir()
        (self.documents / "garden notes.txt").write_text("Synthetic gardening note.\n")
        (self.documents / "other.txt").write_text("Unrelated synthetic note.\n")
        self.journal_path = self.root / "journal.json"

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._temporary.cleanup()


def entry_type(path):
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return "absent"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    return "other"


class Coordinator:
    def __init__(self, sandbox):
        if type(sandbox) is not Sandbox:
            raise TypeError("Only a generated Sandbox is supported")
        self.sandbox = sandbox
        self.records = (json.loads(sandbox.journal_path.read_text())
                        if sandbox.journal_path.exists() else {})

    def _save(self):
        target = self.sandbox.journal_path
        pending = target.with_suffix(".pending")
        with pending.open("w", encoding="utf-8") as stream:
            json.dump(self.records, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, target)

    @staticmethod
    def _key(proposal, step):
        return json.dumps([proposal["session_id"], proposal["request_id"],
                           proposal["request_revision"], step["operation_id"]])

    def _search(self, query):
        matches = []
        with os.scandir(self.sandbox.documents) as entries:
            for entry in entries:
                if entry.is_file(follow_symlinks=False) and query.casefold() in entry.name.casefold():
                    matches.append(entry.name)
        return {"status": "succeeded", "outcome": "search_complete", "matches": sorted(matches)}

    def _recover(self, step):
        if step["capability"] == "file.search":
            return self._search(step["arguments"]["query"])
        kind = entry_type(self.sandbox.documents / step["arguments"]["name"])
        if kind == "directory":
            return {"status": "succeeded", "outcome": "satisfied_observed", "provenance": "unknown"}
        return {"status": "outcome_unknown", "outcome": "reconciliation_required", "observed": kind}

    def _effect(self, step):
        args = step["arguments"]
        if step["capability"] == "file.search":
            return self._search(args["query"])
        path = self.sandbox.documents / args["name"]
        try:
            path.mkdir()
        except FileExistsError:
            kind = entry_type(path)
            if kind == "directory":
                return {"status": "succeeded", "outcome": "already_present"}
            return {"status": "failed", "outcome": "target_conflict", "observed": kind}
        if entry_type(path) != "directory":
            return {"status": "outcome_unknown", "outcome": "verification_failed"}
        return {"status": "succeeded", "outcome": "created"}

    def run(self, session, proposal, grants, *, interrupt_after_effect=False, before_step=None):
        admission = validate(session, proposal, grants)
        if admission["decision"] != "allow":
            return {"status": "denied", "reason": admission["code"], "steps": []}
        # Freeze model-supplied operations; trusted policy/session remain live.
        proposal = copy.deepcopy(proposal)
        # Check every operation identity and root before allowing any effects.
        for step in proposal["steps"]:
            if step["arguments"]["root_id"] != "documents":
                return {"status": "denied", "reason": "unknown_root", "steps": []}
            existing = self.records.get(self._key(proposal, step))
            if existing is not None and existing["step"] != step:
                return {"status": "denied", "reason": "operation_identity_conflict", "steps": []}
        results = []
        for index, step in enumerate(proposal["steps"]):
            if before_step is not None:
                before_step(index)
            admission = validate(session, proposal, grants)
            if admission["decision"] != "allow":
                return {"status": "stopped", "reason": admission["code"], "steps": results}
            key = self._key(proposal, step)
            existing = self.records.get(key)
            if existing is not None and existing["state"] == "completed":
                outcome = copy.deepcopy(existing["result"])
                outcome["replayed"] = True
            elif existing is not None:
                outcome = self._recover(step)
                self.records[key] = {"step": copy.deepcopy(step), "state": "completed", "result": outcome}
                self._save()
            else:
                self.records[key] = {"step": copy.deepcopy(step), "state": "executing"}
                self._save()
                try:
                    outcome = self._effect(step)
                except OSError as exc:
                    # A low-level error does not prove that no effect happened.
                    outcome = {"status": "outcome_unknown", "outcome": "adapter_error", "errno": exc.errno}
                if interrupt_after_effect:
                    raise InterruptedAfterEffect("Effect may have happened; journal result not recorded")
                self.records[key] = {"step": copy.deepcopy(step), "state": "completed", "result": outcome}
                self._save()
            results.append({"operation_id": step["operation_id"], **outcome})
            if outcome["status"] != "succeeded":
                return {"status": outcome["status"], "steps": results}
        return {"status": "succeeded", "steps": results}


def fixture_request():
    session = {"session_id": "fixture-session", "request_id": "fixture-request",
               "request_revision": 1, "policy_epoch": 1, "active": True,
               "cancelled": False, "input_final": True, "mode": "command"}
    proposal = {"schema_version": 1, "session_id": "fixture-session",
                "request_id": "fixture-request", "request_revision": 1, "policy_epoch": 1,
                "steps": [{"operation_id": "create-1", "capability": "directory.create",
                           "arguments": {"root_id": "documents", "name": "Garden"}}]}
    grants = [{"capability": "directory.create", "root_id": "documents"},
              {"capability": "file.search", "root_id": "documents"}]
    return session, proposal, grants


def main():
    with Sandbox() as sandbox:
        session, proposal, grants = fixture_request()
        coordinator = Coordinator(sandbox)
        print("Synthetic request: Create a Garden folder in Documents")
        print(json.dumps(coordinator.run(session, proposal, grants), indent=2))
        session["request_id"] = proposal["request_id"] = "fixture-search"
        proposal["steps"] = [{"operation_id": "search-1", "capability": "file.search",
                              "arguments": {"root_id": "documents", "query": "garden"}}]
        print("Synthetic request: Find filenames containing garden")
        print(json.dumps(coordinator.run(session, proposal, grants), indent=2))
    print("Temporary workspace removed. No model was used.")


if __name__ == "__main__":
    main()
