#!/usr/bin/env python3
"""Typed input for the disposable coordinator experiment. No microphone/audio."""

import argparse
import copy
import json
from pathlib import Path
import sys

from coordinator import Sandbox, SessionCoordinator
from inference import InferenceError, LocalChatInterpreter
from console import interactive, report
from experiments.contract_reference.check_contracts import strict_object, reject_constant


EXAMPLES = {
    "create a folder called garden": {"kind": "proposal", "actions": [
        {"capability": "directory.create", "arguments": {"root_id": "documents", "name": "Garden"}}]},
    "find garden notes": {"kind": "proposal", "actions": [
        {"capability": "file.search", "arguments": {"root_id": "documents", "query": "garden"}}]},
    "create a folder": {"kind": "clarify", "missing": ["name"]},
}


class ExampleInterpreter:
    name = "deterministic_examples_not_ai"

    def interpret(self, job):
        return copy.deepcopy(EXAMPLES.get(job["utterance"].strip().casefold(), {"kind": "unsupported"}))


class FileInterpreter:
    name = "supplied_json_not_ai"

    def __init__(self, path):
        self.path = path

    def interpret(self, job):
        with self.path.open("rb") as stream:
            raw = stream.read(65_537)
        if len(raw) > 65_536:
            raise ValueError("Response exceeds 64 KiB")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_object, parse_constant=reject_constant)


def prepare(coordinator, request_id, interpreter):
    if coordinator.snapshot(request_id)["state"] != "received":
        return
    job = coordinator.begin_interpretation(request_id)
    try:
        output = interpreter.interpret(job)
    except InferenceError as exc:
        coordinator.fail_interpretation(job["ticket"], exc.code)
    except (OSError, ValueError):
        coordinator.fail_interpretation(job["ticket"], "inference_invalid_response")
    else:
        coordinator.accept_interpretation(job["ticket"], output)


def dispatch_ready(coordinator, request_id):
    if coordinator.snapshot(request_id)["state"] == "ready":
        coordinator.execute(request_id)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="A single typed request; omit for the experimental console")
    parser.add_argument("--mode", choices=("command", "dictation"), default="command")
    parser.add_argument("--response-file", type=Path, help="Supply a JSON interpretation instead of deterministic examples")
    parser.add_argument("--endpoint", help="Explicit numeric-loopback HTTP /v1/chat/completions endpoint")
    parser.add_argument("--model", help="Model identifier served by the configured local endpoint")
    parser.add_argument("--timeout", type=float, default=10.0, help="Inference socket timeout in seconds (maximum 30)")
    parser.add_argument("--confirm", action="store_true", help="Require confirmation for folder creation")
    parser.add_argument("--approve", action="store_true", help="Explicitly approve this one-shot disposable proposal")
    args = parser.parse_args(argv)
    if args.approve and (args.text is None or not args.confirm):
        parser.error("--approve requires both --text and --confirm")
    if bool(args.endpoint) != bool(args.model):
        parser.error("--endpoint and --model must be supplied together")
    if args.endpoint and args.response_file:
        parser.error("Choose an endpoint or a response file")
    if args.endpoint:
        interpreter = LocalChatInterpreter(args.endpoint, args.model, timeout=args.timeout)
    else:
        interpreter = FileInterpreter(args.response_file) if args.response_file else ExampleInterpreter()
    with Sandbox() as sandbox:
        coordinator = SessionCoordinator(sandbox, confirmation_required=args.confirm)
        if args.text is None:
            return interactive(coordinator, interpreter)
        request = coordinator.submit(args.text, mode=args.mode)
        prepare(coordinator, request, interpreter)
        if args.approve:
            coordinator.approve(request, coordinator.snapshot(request)["confirmation_digest"])
        dispatch_ready(coordinator, request)
        print(json.dumps(report(coordinator, request, interpreter), indent=2, ensure_ascii=True))
        state = coordinator.snapshot(request)["state"]
        return 0 if state in {"succeeded", "awaiting_confirmation", "needs_clarification"} else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        sys.exit(2)
