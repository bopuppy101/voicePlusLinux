#!/usr/bin/env python3
"""Pure-data contract checks. No action execution or model calls."""

import json
from pathlib import Path
import re
import sys
import unicodedata


ID = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")
SESSION_KEYS = {
    "session_id", "request_id", "request_revision", "policy_epoch",
    "active", "cancelled", "input_final", "mode",
}
PROPOSAL_KEYS = {
    "schema_version", "session_id", "request_id", "request_revision",
    "policy_epoch", "steps",
}
CAPABILITIES = {"directory.create", "file.search"}


def exact_keys(value, keys):
    return type(value) is dict and set(value) == keys


def identifier(value):
    return type(value) is str and ID.fullmatch(value) is not None


def integer(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def plain_text(value, limit):
    return (
        type(value) is str
        and 0 < len(value) <= limit
        and bool(value.strip())
        and not any(unicodedata.category(char).startswith("C") for char in value)
    )


def result(code):
    return {"decision": "allow" if code == "accepted" else "deny", "code": code}


def validate(session, proposal, grants):
    """Validate static admission only. Trusted state must come from the host."""
    if not exact_keys(session, SESSION_KEYS):
        return result("invalid_session")
    if not all(identifier(session[key]) for key in ("session_id", "request_id")):
        return result("invalid_session")
    if not all(integer(session[key]) for key in ("request_revision", "policy_epoch")):
        return result("invalid_session")
    if not all(type(session[key]) is bool for key in ("active", "cancelled", "input_final")):
        return result("invalid_session")
    if type(session["mode"]) is not str or session["mode"] not in {"dictation", "command"}:
        return result("invalid_session")

    if type(grants) is not list or len(grants) > 64:
        return result("invalid_grants")
    for grant in grants:
        if not exact_keys(grant, {"capability", "root_id"}):
            return result("invalid_grants")
        if not identifier(grant["capability"]) or grant["capability"] not in CAPABILITIES:
            return result("invalid_grants")
        if not identifier(grant["root_id"]):
            return result("invalid_grants")

    if not exact_keys(proposal, PROPOSAL_KEYS):
        return result("invalid_proposal")
    if type(proposal["schema_version"]) is not int:
        return result("invalid_proposal")
    if proposal["schema_version"] != 1:
        return result("unsupported_version")
    if not all(identifier(proposal[key]) for key in ("session_id", "request_id")):
        return result("invalid_proposal")
    if not all(integer(proposal[key]) for key in ("request_revision", "policy_epoch")):
        return result("invalid_proposal")
    if type(proposal["steps"]) is not list or not 1 <= len(proposal["steps"]) <= 8:
        return result("invalid_proposal")

    if not session["active"]:
        return result("inactive_session")
    if session["cancelled"]:
        return result("cancelled")
    if session["mode"] != "command":
        return result("not_command")
    if not session["input_final"]:
        return result("input_not_final")
    if any(proposal[key] != session[key] for key in ("session_id", "request_id")):
        return result("identity_mismatch")
    if proposal["request_revision"] != session["request_revision"]:
        return result("stale_revision")
    if proposal["policy_epoch"] != session["policy_epoch"]:
        return result("stale_policy")

    seen = set()
    for step in proposal["steps"]:
        if not exact_keys(step, {"operation_id", "capability", "arguments"}):
            return result("invalid_step")
        if not identifier(step["operation_id"]):
            return result("invalid_step")
        if step["operation_id"] in seen:
            return result("duplicate_operation")
        seen.add(step["operation_id"])
        capability = step["capability"]
        if not identifier(capability) or capability not in CAPABILITIES:
            return result("unknown_capability")
        args = step["arguments"]
        field = "name" if capability == "directory.create" else "query"
        if not exact_keys(args, {"root_id", field}) or not identifier(args["root_id"]):
            return result("invalid_arguments")
        value = args[field]
        if capability == "directory.create":
            if not plain_text(value, 255) or value in {".", ".."}:
                return result("invalid_arguments")
            if "/" in value or "\\" in value or len(value.encode("utf-8")) > 255:
                return result("invalid_arguments")
        elif not plain_text(value, 2048):
            return result("invalid_arguments")
        if {"capability": capability, "root_id": args["root_id"]} not in grants:
            return result("missing_grant")
    return result("accepted")


def strict_object(pairs):
    """Reject duplicate JSON keys instead of accepting last-key-wins input."""
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def main():
    path = Path(__file__).with_name("fixtures.json")
    cases = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if type(cases) is not list or not cases:
        raise ValueError("Expected a nonempty fixture list")
    names = set()
    failed = 0
    for case in cases:
        if not exact_keys(case, {"name", "session", "proposal", "grants", "expected"}):
            raise ValueError("Invalid fixture shape")
        if not identifier(case["name"]) or case["name"] in names:
            raise ValueError("Fixture names must be unique identifiers")
        names.add(case["name"])
        actual = validate(case["session"], case["proposal"], case["grants"])
        if actual != case["expected"]:
            failed += 1
            print(f"FAIL {case['name']}: expected {case['expected']}, got {actual}")
    print(f"Contract fixtures: {len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"Fixture error: {exc}", file=sys.stderr)
        sys.exit(2)
