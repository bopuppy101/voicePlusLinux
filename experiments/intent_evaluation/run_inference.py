#!/usr/bin/env python3
"""Record a development evaluation through an explicitly configured loopback model.

Never creates an executor or dispatches proposed actions. Each completed case is
flushed to disk; an interrupted run is evidence, not a resumable job queue.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/session_coordinator"))
from inference import InferenceError, LocalChatInterpreter, SYSTEM_PROMPT, decode_json
from experiments.intent_evaluation.score import index_cases, score


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_cases(path):
    with path.open("rb") as source:
        raw = source.read(10_000_001)
    if len(raw) > 10_000_000:
        raise ValueError("Cases exceed the 10 MB experiment limit")
    cases = [decode_json(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    index_cases(cases)
    return raw, cases


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def append_record(stream, value):
    stream.write(json.dumps(value, ensure_ascii=True, allow_nan=False) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


def run(cases_path, output_dir, interpreter, *, provenance=None):
    raw, cases = read_cases(cases_path)
    # Fails before contacting an interpreter when the destination already exists.
    output_dir.mkdir(parents=False, exist_ok=False)
    (output_dir / "cases.snapshot.jsonl").write_bytes(raw)
    (output_dir / "system-prompt.txt").write_text(SYSTEM_PROMPT, encoding="utf-8")
    source_files = [Path(__file__), Path(__file__).with_name("score.py"),
                    ROOT / "experiments/session_coordinator/inference.py"]
    manifest = {
        "schema_version": 1, "status": "running", "started_at": timestamp(),
        "purpose": "public_development_evaluation_not_held_out", "action_execution": False,
        "backend": interpreter.name, "case_count": len(cases), "completed_cases": 0,
        "cases_sha256": digest(raw), "system_prompt_sha256": digest(SYSTEM_PROMPT.encode()),
        "source_sha256": {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in source_files},
        "requested_model": getattr(interpreter, "model", None),
        "provenance": provenance or {},
        "provenance_verification": "caller_supplied_not_independently_verified",
        "generation": {"temperature": 0, "max_tokens": 512, "stream": False,
                       "response_format": {"type": "json_object"}},
        "retries": 0, "prediction_files": ["predictions.jsonl", "case-metadata.jsonl"],
    }
    manifest_path = output_dir / "manifest.json"
    write_json(manifest_path, manifest)
    predictions = []
    try:
        with (output_dir / "predictions.jsonl").open("x", encoding="utf-8") as outputs, \
                (output_dir / "case-metadata.jsonl").open("x", encoding="utf-8") as metadata:
            for case in cases:
                started = time.monotonic()
                details = {"id": case["id"], "route": "model", "status": "returned"}
                if case["mode"] == "dictation":
                    output = {"kind": "dictation", "text": case["utterance"]}
                    details["route"] = "dictation_bypass"
                else:
                    # Construct a fresh allowlisted prompt payload, never pass a case
                    # wholesale. Reference answers, case IDs, categories stay local.
                    job = {key: case[key] for key in ("mode", "utterance", "context")}
                    try:
                        output = interpreter.interpret(job)
                    except InferenceError as exc:
                        # Deliberately invalid to the scorer. A transport failure must
                        # not accidentally match an expected unsupported outcome.
                        output = {"kind": "error", "code": exc.code}
                        details.update(status="inference_failed", error_code=exc.code)
                    else:
                        details["transport"] = getattr(interpreter, "last_metadata", None)
                details["elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
                prediction = {"id": case["id"], "output": output}
                append_record(outputs, prediction)
                append_record(metadata, details)
                predictions.append(prediction)
                manifest["completed_cases"] = len(predictions)
                write_json(manifest_path, manifest)
        report = score(cases, predictions)
        report["by_route"] = {}
        for mode, route in (("command", "model"), ("dictation", "dictation_bypass")):
            subset = [case for case in cases if case["mode"] == mode]
            ids = {case["id"] for case in subset}
            report["by_route"][route] = score(subset, [p for p in predictions if p["id"] in ids]) if subset else None
        write_json(output_dir / "report.json", report)
        manifest.update(status="completed", ended_at=timestamp(), report="report.json",
                        predictions_sha256=digest((output_dir / "predictions.jsonl").read_bytes()))
        write_json(manifest_path, manifest)
        return report
    except BaseException as exc:
        manifest.update(status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                        ended_at=timestamp(), error_type=type(exc).__name__)
        write_json(manifest_path, manifest)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory with an existing parent")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--engine-revision", help="Caller-supplied engine revision, if known")
    parser.add_argument("--model-artifact-sha256", help="Caller-supplied weight artifact digest, if known")
    args = parser.parse_args(argv)
    if args.model_artifact_sha256 is not None and (len(args.model_artifact_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in args.model_artifact_sha256)):
        parser.error("Artifact SHA-256 must contain 64 lowercase hexadecimal characters")
    interpreter = LocalChatInterpreter(args.endpoint, args.model, timeout=args.timeout)
    report = run(args.cases, args.output_dir, interpreter, provenance={
        "endpoint": args.endpoint, "socket_timeout_seconds": args.timeout,
        "engine_revision": args.engine_revision, "model_artifact_sha256": args.model_artifact_sha256,
        "hardware": "not_recorded", "artifact_admission": "not_verified_by_runner"})
    print(json.dumps({"run_directory": str(args.output_dir.resolve()), "matched": report["matched"],
                      "total": report["total"], "complete_match": report["complete_match"]}, indent=2))
    return 0 if report["complete_match"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, TypeError) as exc:
        print(f"Evaluation setup failed: {type(exc).__name__}", file=sys.stderr)
        sys.exit(2)
