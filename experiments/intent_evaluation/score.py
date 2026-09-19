#!/usr/bin/env python3
"""Strict offline scoring of structured intent outcomes; no model execution."""

import argparse
import json
from pathlib import Path
import sys


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def load_jsonl(path):
    if path.stat().st_size > 10_000_000:
        raise ValueError("Input exceeds this experiment's 10 MB limit")
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line, object_pairs_hook=strict_object,
                                      parse_constant=reject_constant))
        except ValueError as exc:
            raise ValueError(f"Line {number}: {exc}") from exc
    if not records:
        raise ValueError("Input must contain records")
    return records


def exact(value, keys):
    return type(value) is dict and set(value) == keys


def text(value):
    return type(value) is str and bool(value.strip())


def valid_outcome(value):
    if type(value) is not dict or type(value.get("kind")) is not str:
        return False
    kind = value["kind"]
    if kind == "unsupported":
        return exact(value, {"kind"})
    if kind == "dictation":
        return exact(value, {"kind", "text"}) and type(value["text"]) is str
    if kind == "clarify":
        return (exact(value, {"kind", "missing"})
                and type(value["missing"]) is list and bool(value["missing"])
                and all(text(item) for item in value["missing"]))
    if kind != "proposal" or not exact(value, {"kind", "actions"}):
        return False
    if type(value["actions"]) is not list or not 1 <= len(value["actions"]) <= 8:
        return False
    for action in value["actions"]:
        if not exact(action, {"capability", "arguments"}):
            return False
        if action["capability"] == "directory.create":
            keys = {"root_id", "name"}
        elif action["capability"] == "file.search":
            keys = {"root_id", "query"}
        else:
            return False
        if not exact(action["arguments"], keys):
            return False
        if not all(text(item) for item in action["arguments"].values()):
            return False
    return True


def index_cases(cases):
    result = {}
    for case in cases:
        if not exact(case, {"id", "category", "mode", "utterance", "context", "acceptable"}):
            raise ValueError("Invalid case shape")
        if not text(case["id"]) or case["id"] in result:
            raise ValueError("Case IDs must be nonempty and unique")
        if not text(case["category"]) or not text(case["utterance"]):
            raise ValueError("Case category and utterance are required")
        if type(case["mode"]) is not str or case["mode"] not in {"command", "dictation"}:
            raise ValueError("Invalid case mode")
        if type(case["context"]) is not dict:
            raise ValueError("Case context must be an object")
        if type(case["acceptable"]) is not list or not case["acceptable"]:
            raise ValueError("Case requires acceptable outcomes")
        if not all(valid_outcome(item) for item in case["acceptable"]):
            raise ValueError(f"Invalid expected outcome in {case['id']}")
        result[case["id"]] = case
    if not result:
        raise ValueError("No cases")
    return result


def score(cases, predictions):
    expected = index_cases(cases)
    observed = {}
    for prediction in predictions:
        if not exact(prediction, {"id", "output"}) or not text(prediction["id"]):
            raise ValueError("Invalid prediction record")
        if prediction["id"] in observed:
            raise ValueError(f"Duplicate prediction: {prediction['id']}")
        observed[prediction["id"]] = prediction["output"]
    report = {"total": len(expected), "matched": 0, "missing": [],
              "unexpected": sorted(set(observed) - set(expected)),
              "mismatched": [], "invalid_outputs": [], "by_category": {}}
    for case_id, case in expected.items():
        group = report["by_category"].setdefault(case["category"], {"total": 0, "matched": 0})
        group["total"] += 1
        if case_id not in observed:
            report["missing"].append(case_id)
        elif not valid_outcome(observed[case_id]):
            report["invalid_outputs"].append(case_id)
        elif observed[case_id] not in case["acceptable"]:
            report["mismatched"].append(case_id)
        else:
            report["matched"] += 1
            group["matched"] += 1
    report["complete_match"] = report["matched"] == report["total"] and not report["unexpected"]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", nargs="?", type=Path)
    parser.add_argument("--validate-cases", action="store_true")
    args = parser.parse_args()
    cases = load_jsonl(Path(__file__).with_name("cases.jsonl"))
    index_cases(cases)
    if args.validate_cases:
        if args.predictions is not None:
            parser.error("Use either --validate-cases or a predictions file")
        print(f"Validated {len(cases)} development cases; no model was evaluated")
        return 0
    if args.predictions is None:
        parser.error("Provide predictions or use --validate-cases")
    report = score(cases, load_jsonl(args.predictions))
    print(json.dumps(report, indent=2))
    return 0 if report["complete_match"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, TypeError) as exc:
        print(f"Evaluation input error: {exc}", file=sys.stderr)
        sys.exit(2)
