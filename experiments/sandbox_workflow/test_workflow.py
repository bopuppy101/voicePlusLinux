"""Actual effects are confined to disposable fixture workspaces."""

import copy
from pathlib import Path
import tempfile
import unittest

from demo import Coordinator, InterruptedAfterEffect, Sandbox, fixture_request


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox._temporary.cleanup)
        self.session, self.proposal, self.grants = fixture_request()
        self.coordinator = Coordinator(self.sandbox)

    def run_request(self, **kwargs):
        return self.coordinator.run(self.session, self.proposal, self.grants, **kwargs)

    def test_create_verified_and_duplicate_not_repeated(self):
        first = self.run_request()
        self.assertEqual(first["steps"][0]["outcome"], "created")
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())
        again = self.run_request()
        self.assertTrue(again["steps"][0]["replayed"])
        self.assertEqual(len(self.coordinator.records), 1)

    def test_denied_later_step_prevents_all_effects(self):
        step = copy.deepcopy(self.proposal["steps"][0])
        step["operation_id"] = "create-2"
        step["arguments"]["root_id"] = "outside"
        self.proposal["steps"].append(step)
        self.assertEqual(self.run_request()["status"], "denied")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_cancel_rechecked_before_effect(self):
        def cancel(_):
            self.session["cancelled"] = True
        self.assertEqual(self.run_request(before_step=cancel)["reason"], "cancelled")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_proposal_is_frozen_after_admission(self):
        def change_caller_copy(_):
            self.proposal["steps"][0]["arguments"]["name"] = "Changed"
        result = self.run_request(before_step=change_caller_copy)
        self.assertEqual(result["status"], "succeeded")
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())
        self.assertFalse((self.sandbox.documents / "Changed").exists())

    def test_revocation_after_first_step_keeps_partial_result(self):
        second = copy.deepcopy(self.proposal["steps"][0])
        second["operation_id"] = "create-2"
        second["arguments"]["name"] = "Second"
        self.proposal["steps"].append(second)
        def revoke(index):
            if index == 1:
                self.grants.clear()
        result = self.run_request(before_step=revoke)
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(len(result["steps"]), 1)
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())
        self.assertFalse((self.sandbox.documents / "Second").exists())

    def test_interrupted_create_reconciles_without_claiming_provenance(self):
        with self.assertRaises(InterruptedAfterEffect):
            self.run_request(interrupt_after_effect=True)
        self.coordinator = Coordinator(self.sandbox)
        result = self.run_request()
        self.assertEqual(result["steps"][0]["outcome"], "satisfied_observed")
        self.assertEqual(result["steps"][0]["provenance"], "unknown")

    def test_missing_target_after_interruption_is_not_recreated(self):
        with self.assertRaises(InterruptedAfterEffect):
            self.run_request(interrupt_after_effect=True)
        (self.sandbox.documents / "Garden").rmdir()
        self.coordinator = Coordinator(self.sandbox)
        result = self.run_request()
        self.assertEqual(result["status"], "outcome_unknown")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_existing_file_is_preserved(self):
        target = self.sandbox.documents / "Garden"
        target.write_text("Keep this fixture")
        result = self.run_request()
        self.assertEqual(result["steps"][0]["outcome"], "target_conflict")
        self.assertEqual(target.read_text(), "Keep this fixture")

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.sandbox.documents / "Garden").symlink_to(outside, target_is_directory=True)
            result = self.run_request()
            self.assertEqual(result["steps"][0]["outcome"], "target_conflict")
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_operation_identity_cannot_change_arguments(self):
        self.run_request()
        self.proposal["steps"][0]["arguments"]["name"] = "Different"
        result = self.run_request()
        self.assertEqual(result["reason"], "operation_identity_conflict")
        self.assertFalse((self.sandbox.documents / "Different").exists())

    def test_filename_search_is_read_only_and_skips_symlinks(self):
        (self.sandbox.documents / "garden-link").symlink_to("other.txt")
        self.proposal["steps"] = [{"operation_id": "search-1", "capability": "file.search",
                                   "arguments": {"root_id": "documents", "query": "garden"}}]
        result = self.run_request()
        self.assertEqual(result["steps"][0]["matches"], ["garden notes.txt"])
        self.assertEqual((self.sandbox.documents / "other.txt").read_text(), "Unrelated synthetic note.\n")


if __name__ == "__main__":
    unittest.main()
