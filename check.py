#!/usr/bin/env python3
"""Run the established prototype checks without a model, microphone, or installation."""

import argparse
import ast
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent
COMPONENTS = {
    "admission": ROOT / "experiments/contract_reference",
    "intent": ROOT / "experiments/intent_evaluation",
    "executor": ROOT / "experiments/sandbox_workflow",
    "session": ROOT / "experiments/session_coordinator",
}


def run_suite(name):
    # Each component runs in its own process to isolate these experimental module
    # imports. Never let discovery silently report success with zero tests.
    suite = unittest.TestLoader().discover(str(COMPONENTS[name]), pattern="test_*.py")
    if suite.countTestCases() == 0:
        print(f"FAIL {name}: no tests discovered", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


def check_files():
    paths = [Path(__file__), *(p for folder in COMPONENTS.values() for p in folder.glob("*.py"))]
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    documents = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "docs").rglob("*.md")),
                 *(folder / "README.md" for folder in COMPONENTS.values())]
    links = 0
    for document in documents:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = (document.parent / target.split("#", 1)[0]).resolve()
            if not destination.exists():
                raise ValueError(f"Broken local link in {document.relative_to(ROOT)}: {target}")
            links += 1
    print(f"Parsed {len(paths)} Python files; checked {links} local links across {len(documents)} documents.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=COMPONENTS, help="Run one component's tests only")
    parser.add_argument("--_suite", choices=COMPONENTS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args._suite:
        return run_suite(args._suite)
    commands = []
    if args.component is None:
        check_files()
        commands.extend([
            ("Admission fixtures", ["experiments/contract_reference/check_contracts.py"]),
            ("Intent case validation", ["experiments/intent_evaluation/score.py", "--validate-cases"]),
        ])
    for name in ([args.component] if args.component else COMPONENTS):
        commands.append((f"{name} tests", [str(Path(__file__).resolve()), "--_suite", name]))
    failed = []
    for label, arguments in commands:
        print(f"\n{label}", flush=True)
        try:
            outcome = subprocess.run([sys.executable, "-B", *arguments], cwd=ROOT, timeout=60)
        except subprocess.TimeoutExpired:
            print(f"FAIL {label}: exceeded the 60-second check limit", file=sys.stderr)
            failed.append(label)
        else:
            if outcome.returncode != 0:
                failed.append(label)
    if failed:
        print("Checks failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    print("\nAll selected checks passed. This is synthetic software evidence, not a model or voice benchmark.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, SyntaxError) as exc:
        print(f"Check error: {exc}", file=sys.stderr)
        sys.exit(2)
