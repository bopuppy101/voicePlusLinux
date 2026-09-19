import copy
import json
from pathlib import Path
import tempfile
import unittest

from run_inference import InferenceError, digest, run


class RecordingInterpreter:
    name = "synthetic_test_not_ai"
    model = "test-fixture"
    last_metadata = None

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.jobs = []

    def interpret(self, job):
        self.jobs.append(copy.deepcopy(job))
        value = next(self.outputs)
        if isinstance(value, BaseException):
            raise value
        return value


class EvaluationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="vplinuxai-evaluation-test-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.cases_file = self.root / "cases.jsonl"
        self.run_dir = self.root / "run"
        self.cases = [
            {"id": "unsupported", "category": "unsupported", "mode": "command",
             "utterance": "Play a song", "context": {}, "acceptable": [{"kind": "unsupported"}]},
            {"id": "dictation", "category": "routing", "mode": "dictation",
             "utterance": "Create a folder called Garden", "context": {},
             "acceptable": [{"kind": "dictation", "text": "Create a folder called Garden"}]},
        ]
        self.write_cases()

    def write_cases(self):
        self.cases_file.write_text("".join(json.dumps(case) + "\n" for case in self.cases), encoding="utf-8")

    def read(self, name):
        return json.loads((self.run_dir / name).read_text())

    def test_outputs_hashes_and_separate_routing_report(self):
        interpreter = RecordingInterpreter([{"kind": "unsupported"}])
        report = run(self.cases_file, self.run_dir, interpreter)
        self.assertTrue(report["complete_match"])
        self.assertEqual(report["by_route"]["model"]["total"], 1)
        self.assertEqual(report["by_route"]["dictation_bypass"]["total"], 1)
        manifest = self.read("manifest.json")
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(manifest["completed_cases"], 2)
        self.assertFalse(manifest["action_execution"])
        for key, file in (("cases_sha256", "cases.snapshot.jsonl"),
                          ("system_prompt_sha256", "system-prompt.txt"),
                          ("predictions_sha256", "predictions.jsonl")):
            self.assertEqual(manifest[key], digest((self.run_dir / file).read_bytes()))
        self.assertEqual(len(interpreter.jobs), 1)
        self.assertEqual(set(interpreter.jobs[0]), {"mode", "utterance", "context"})
        self.assertNotIn("acceptable", interpreter.jobs[0])

    def test_transport_failure_is_not_an_unsupported_pass(self):
        report = run(self.cases_file, self.run_dir, RecordingInterpreter([InferenceError("inference_timeout")]))
        self.assertEqual(report["invalid_outputs"], ["unsupported"])
        self.assertEqual(report["by_route"]["model"]["matched"], 0)
        self.assertFalse(report["complete_match"])
        metadata = [json.loads(line) for line in (self.run_dir / "case-metadata.jsonl").read_text().splitlines()]
        self.assertEqual(metadata[0]["error_code"], "inference_timeout")

    def test_existing_directory_preserved_without_inference(self):
        self.run_dir.mkdir()
        marker = self.run_dir / "preserve.txt"
        marker.write_text("existing evidence")
        interpreter = RecordingInterpreter([])
        with self.assertRaises(FileExistsError):
            run(self.cases_file, self.run_dir, interpreter)
        self.assertEqual(marker.read_text(), "existing evidence")
        self.assertEqual(interpreter.jobs, [])

    def test_interruption_keeps_completed_case_and_manifest(self):
        self.cases[1]["mode"] = "command"
        self.write_cases()
        interpreter = RecordingInterpreter([{"kind": "unsupported"}, KeyboardInterrupt()])
        with self.assertRaises(KeyboardInterrupt):
            run(self.cases_file, self.run_dir, interpreter)
        manifest = self.read("manifest.json")
        self.assertEqual(manifest["status"], "interrupted")
        self.assertEqual(manifest["completed_cases"], 1)
        self.assertEqual(len((self.run_dir / "predictions.jsonl").read_text().splitlines()), 1)
        self.assertFalse((self.run_dir / "report.json").exists())

    def test_unexpected_failure_marks_run_failed_without_secret_message(self):
        interpreter = RecordingInterpreter([RuntimeError("private-server-message")])
        with self.assertRaises(RuntimeError):
            run(self.cases_file, self.run_dir, interpreter)
        manifest = self.read("manifest.json")
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["error_type"], "RuntimeError")
        self.assertNotIn("private-server-message", json.dumps(manifest))

    def test_invalid_cases_fail_before_output_directory_or_inference(self):
        self.cases.append(copy.deepcopy(self.cases[0]))
        self.write_cases()
        interpreter = RecordingInterpreter([])
        with self.assertRaises(ValueError):
            run(self.cases_file, self.run_dir, interpreter)
        self.assertFalse(self.run_dir.exists())
        self.assertEqual(interpreter.jobs, [])

    def test_proposal_is_recorded_without_filesystem_effect(self):
        proposal = {"kind": "proposal", "actions": [{"capability": "directory.create",
                     "arguments": {"root_id": "documents", "name": "MustNotExist"}}]}
        self.cases = [{**self.cases[0], "utterance": "Make MustNotExist", "acceptable": [proposal]}]
        self.write_cases()
        report = run(self.cases_file, self.run_dir, RecordingInterpreter([proposal]))
        self.assertTrue(report["complete_match"])
        self.assertIsNone(report["by_route"]["dictation_bypass"])
        self.assertFalse((self.root / "MustNotExist").exists())


if __name__ == "__main__":
    unittest.main()
