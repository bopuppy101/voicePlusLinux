import json
from pathlib import Path
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
