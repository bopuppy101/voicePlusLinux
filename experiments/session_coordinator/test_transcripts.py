import unittest

from coordinator import Sandbox, SessionCoordinator, TransitionError
from transcripts import TranscriptGate


CREATE = {"kind": "proposal", "actions": [{"capability": "directory.create",
          "arguments": {"root_id": "documents", "name": "Garden"}}]}


class TranscriptGateTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.sandbox.__enter__()
        self.addCleanup(self.sandbox.__exit__, None, None, None)
        self.coordinator = SessionCoordinator(self.sandbox)
        self.gate = TranscriptGate(self.coordinator)
        self.capture = self.gate.begin()

    def event(self, sequence, text="Create Garden", kind="partial", **extra):
        event = {"schema_version": 1, "capture_id": self.capture,
                 "sequence": sequence, "kind": kind, "text": text}
        event.update(extra)
        return event

    def correction(self, *, proposed=False, confirmation=False):
        self.gate.cancel()
        self.coordinator.confirmation_required = confirmation
        request = self.coordinator.submit("Create Garden")
        job = self.coordinator.begin_interpretation(request)
        if proposed:
            self.coordinator.accept_interpretation(job["ticket"], CREATE)
        view = self.coordinator.snapshot(request)
        self.capture = self.gate.begin(request_id=request)
        return request, job, view

    def test_partial_is_preview_only_and_final_creates_one_pending_request(self):
        self.assertTrue(self.gate.accept(self.event(1, "Create")))
        self.assertIsNone(self.gate.snapshot()["request_id"])
        self.assertEqual(self.coordinator._requests, {})
        final = self.event(2, kind="final")
        self.assertTrue(self.gate.accept(final))
        view = self.gate.snapshot()
        self.assertEqual(view["raw_final"], "Create Garden")
        self.assertEqual(view["processed_final"], view["raw_final"])
        self.assertEqual(view["transformations"], [])
        self.assertEqual(self.coordinator.snapshot(view["request_id"])["state"], "received")
        self.assertFalse(self.gate.accept(final))
        self.assertEqual(len(self.coordinator._requests), 1)
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_final_command_can_use_existing_policy_and_sandbox_pipeline(self):
        self.gate.accept(self.event(1, kind="final"))
        request = self.gate.snapshot()["request_id"]
        job = self.coordinator.begin_interpretation(request)
        self.assertEqual(job["utterance"], "Create Garden")
        self.coordinator.accept_interpretation(job["ticket"], CREATE)
        self.assertEqual(self.coordinator.execute(request)["state"], "succeeded")
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())

    def test_dictation_mode_never_becomes_command(self):
        self.gate.cancel()
        self.capture = self.gate.begin(mode="dictation")
        self.gate.accept(self.event(1, "Delete all files", "final"))
        request = self.gate.snapshot()["request_id"]
        view = self.coordinator.snapshot(request)
        self.assertEqual(view["result"]["delivery"], "panel_only")
        self.assertEqual(view["result"]["text"], "Delete all files")
        with self.assertRaises(TransitionError):
            self.coordinator.begin_interpretation(request)

    def test_recognizer_cannot_switch_activation_mode(self):
        self.assertFalse(self.gate.accept(self.event(1, kind="final", mode="command")))
        self.assertEqual(self.gate.snapshot()["state"], "failed")
        self.assertEqual(self.coordinator._requests, {})

    def test_beginning_correction_invalidates_old_job_before_any_transcript(self):
        request, job, _ = self.correction()
        view = self.coordinator.snapshot(request)
        self.assertEqual(view["revision"], 2)
        self.assertFalse(view["input_final"])
        self.assertFalse(self.coordinator.accept_interpretation(job["ticket"], CREATE))
        with self.assertRaises(TransitionError):
            self.coordinator.begin_interpretation(request)
        self.gate.accept(self.event(1, "Find Garden", "final"))
        self.assertEqual(self.coordinator.begin_interpretation(request)["utterance"], "Find Garden")

    def test_beginning_correction_invalidates_ready_proposal_and_approval(self):
        request, _, old = self.correction(proposed=True, confirmation=True)
        self.assertFalse(self.coordinator.approve(request, old["confirmation_digest"]))
        with self.assertRaises(TransitionError):
            self.coordinator.execute(request)
        self.assertIsNone(self.coordinator.snapshot(request)["proposal"])

    def test_cancelled_correction_cannot_revive_original_command(self):
        request, job, _ = self.correction()
        self.assertTrue(self.gate.cancel())
        self.assertFalse(self.gate.accept(self.event(1, kind="final")))
        self.assertFalse(self.coordinator.accept_interpretation(job["ticket"], CREATE))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")

    def test_typed_revision_supersedes_capture_without_being_cancelled_by_late_final(self):
        request, _, _ = self.correction()
        self.coordinator.revise(request, "Find notes instead")
        self.assertFalse(self.gate.accept(self.event(1, kind="final")))
        view = self.coordinator.snapshot(request)
        self.assertEqual(view["revision"], 3)
        self.assertEqual(view["state"], "received")
        self.assertTrue(view["input_final"])
        self.assertEqual(view["text"], "Find notes instead")

    def test_policy_change_blocks_final_text(self):
        self.coordinator.set_grants([])
        self.assertFalse(self.gate.accept(self.event(1, kind="final")))
        self.assertEqual(self.gate.snapshot()["reason"], "input_context_changed")
        self.assertEqual(self.coordinator._requests, {})

    def test_lock_blocks_final_text(self):
        self.coordinator.set_active(False)
        self.assertFalse(self.gate.accept(self.event(1, kind="final")))
        self.assertEqual(self.coordinator._requests, {})

    def test_unlock_does_not_revive_audio_from_before_lock(self):
        self.coordinator.set_active(False)
        self.coordinator.set_active(True)
        self.assertFalse(self.gate.accept(self.event(1, kind="final")))
        self.assertEqual(self.gate.snapshot()["reason"], "input_context_changed")
        self.assertEqual(self.coordinator._requests, {})

    def test_old_capture_cannot_poison_new_capture(self):
        old = self.event(1, kind="final")
        self.gate.cancel()
        self.capture = self.gate.begin()
        self.assertFalse(self.gate.accept(old))
        self.assertEqual(self.gate.snapshot()["state"], "receiving")
        self.assertTrue(self.gate.accept(self.event(1, kind="final")))

    def test_repeated_partial_is_idempotent_and_conflict_fails_closed(self):
        first = self.event(1, "Create")
        self.assertTrue(self.gate.accept(first))
        self.assertFalse(self.gate.accept(first))
        self.assertEqual(self.gate.snapshot()["state"], "receiving")
        self.assertFalse(self.gate.accept(self.event(1, "Delete")))
        self.assertEqual(self.gate.snapshot()["reason"], "conflicting_transcript_event")
        self.assertFalse(self.gate.accept(self.event(2, kind="final")))

    def test_sequence_gap_prevents_incomplete_input_dispatch(self):
        self.gate.accept(self.event(1, "Create"))
        self.assertFalse(self.gate.accept(self.event(3, kind="final")))
        self.assertEqual(self.gate.snapshot()["reason"], "transcript_event_gap")
        self.assertEqual(self.coordinator._requests, {})

    def test_error_cancels_unfinalized_correction(self):
        request, _, _ = self.correction()
        event = self.event(1, kind="error")
        del event["text"]
        event["code"] = "input_incomplete"
        self.assertTrue(self.gate.accept(event))
        self.assertEqual(self.gate.snapshot()["state"], "failed")
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")

    def test_blank_final_and_oversized_partial_fail_without_request(self):
        for text, kind in (("  ", "final"), ("x" * 8193, "partial")):
            with self.subTest(kind=kind):
                self.gate.cancel()
                self.capture = self.gate.begin()
                self.assertFalse(self.gate.accept(self.event(1, text, kind)))
                self.assertEqual(self.coordinator._requests, {})

    def test_cannot_start_second_active_capture_or_correct_finished_action(self):
        with self.assertRaises(TransitionError):
            self.gate.begin()
        self.gate.cancel()
        request = self.coordinator.submit("Only text", mode="dictation")
        with self.assertRaises(TransitionError):
            self.gate.begin(request_id=request)


if __name__ == "__main__":
    unittest.main()
