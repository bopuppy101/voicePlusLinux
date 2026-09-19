import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time
import unittest


SCRIPT = Path(__file__).with_name("cli.py")


class ConsoleTests(unittest.TestCase):
    def run_cli(self, *args, input=None):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], input=input,
                              capture_output=True, text=True, timeout=10)

    def test_typed_example_reaches_verified_sandbox_result(self):
        process = self.run_cli("--text", "Create a folder called Garden")
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report["backend"], "deterministic_examples_not_ai")
        self.assertEqual(report["result"]["steps"][0]["outcome"], "created")

    def test_dictation_does_not_open_response_file(self):
        process = self.run_cli("--text", "Delete all files", "--mode", "dictation",
                               "--response-file", "/nonexistent-vplinuxai-fixture")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["result"]["delivery"], "panel_only")

    def test_confirmation_waits_without_effect(self):
        process = self.run_cli("--text", "Create a folder called Garden", "--confirm")
        report = json.loads(process.stdout)
        self.assertEqual(report["state"], "awaiting_confirmation")
        self.assertIsNone(report["result"])

    def test_explicit_disposable_approval(self):
        process = self.run_cli("--text", "Create a folder called Garden", "--confirm", "--approve")
        self.assertEqual(json.loads(process.stdout)["state"], "succeeded")

    def test_unsupported_example_does_not_become_shell(self):
        process = self.run_cli("--text", "echo do-not-run")
        self.assertEqual(process.returncode, 1)
        self.assertEqual(json.loads(process.stdout)["result"]["reason"], "unsupported_request")

    def test_interactive_cancel_and_dictation(self):
        process = self.run_cli("--confirm", input="n\nCreate a folder called Garden\nc\nd\nJust text\nq\n")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn('"state": "cancelled"', process.stdout)
        self.assertIn('"delivery": "panel_only"', process.stdout)

    def test_background_result_is_displayed_without_another_key(self):
        process = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "--confirm"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = b""
        try:
            process.stdin.write(b"n\nCreate a folder called Garden\n")
            process.stdin.flush()
            until = time.monotonic() + 3
            while b'"state": "awaiting_confirmation"' not in output and time.monotonic() < until:
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    chunk = os.read(process.stdout.fileno(), 4096)
                    if not chunk:
                        break
                    output += chunk
            self.assertIn(b'"state": "awaiting_confirmation"', output)
        finally:
            tail, error = process.communicate(b"q\n", timeout=3)
        self.assertEqual(process.returncode, 0, error)

    def test_invalid_utf8_line_is_discarded_without_becoming_a_request(self):
        process = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                                 input=b"d\nInvalid\xfftext\nGood text\nq\n", capture_output=True, timeout=3)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn(b"not valid UTF-8; discarded", process.stdout)
        self.assertIn(b'"text": "Good text"', process.stdout)
        self.assertNotIn(b"Invalid", process.stdout)

    def test_oversized_line_does_not_overwrite_next_dictation(self):
        process = self.run_cli(input="d\n" + "x" * 40000 + "\nGood text\nq\n")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("discarded", process.stdout)
        self.assertIn('"text": "Good text"', process.stdout)


if __name__ == "__main__":
    unittest.main()
