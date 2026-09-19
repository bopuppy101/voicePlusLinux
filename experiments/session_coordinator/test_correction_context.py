"""QA contract for bounded request-local correction context; no model calls."""

import json
import unittest

from coordinator import Sandbox, SessionCoordinator, TransitionError


def proposal(name="Garden"):
    return {"kind": "proposal", "actions": [{"capability": "directory.create",
            "arguments": {"root_id": "documents", "name": name}}]}


class CorrectionContextTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.sandbox.__enter__()
        self.addCleanup(self.sandbox.__exit__, None, None, None)
        self.coordinator = SessionCoordinator(self.sandbox, confirmation_required=True)

    def request(self, text="Create a folder called Garden"):
        return self.coordinator.submit(text)

    def interpret(self, request, output=None):
        job = self.coordinator.begin_interpretation(request)
        if output is not None:
            self.assertTrue(self.coordinator.accept_interpretation(job["ticket"], output))
        return job

    def assert_turns(self, job, expected):
        self.assertEqual(job["context"].get("pending_request"), {"turns": expected})

    def test_initial_request_has_no_prior_context(self):
        job = self.interpret(self.request())
        self.assertIsNone(job["context"].get("pending_request"))

    def test_revision_preserves_admitted_proposal_without_host_authority(self):
        request = self.request()
        self.interpret(request, proposal())
        old_digest = self.coordinator.snapshot(request)["confirmation_digest"]
        self.coordinator.revise(request, "Call it Orchard instead")
        job = self.interpret(request)
        self.assertEqual(job["utterance"], "Call it Orchard instead")
        self.assert_turns(job, [{"utterance": "Create a folder called Garden",
                                 "interpretation": proposal()}])
        serialized = json.dumps(job["context"]["pending_request"])
        for value in (request, self.coordinator.session_id, old_digest):
            self.assertNotIn(value, serialized)
        self.assertFalse(self.coordinator.approve(request, old_digest))
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_clarification_is_available_when_next_turn_supplies_missing_name(self):
        request = self.request("Create a folder")
        clarify = {"kind": "clarify", "missing": ["name"]}
        self.interpret(request, clarify)
        self.coordinator.revise(request, "Garden")
        job = self.interpret(request)
        self.assertEqual(job["utterance"], "Garden")
        self.assert_turns(job, [{"utterance": "Create a folder", "interpretation": clarify}])

    def test_unfinished_jobs_preserve_user_turns_but_cannot_supply_late_interpretations(self):
        request = self.request("Create Garden")
        first = self.interpret(request)
        self.coordinator.revise(request, "Use Orchard instead")
        second = self.interpret(request)
        self.coordinator.revise(request, "Actually use Meadow")
        self.assertFalse(self.coordinator.accept_interpretation(first["ticket"], proposal()))
        self.assertFalse(self.coordinator.accept_interpretation(second["ticket"], proposal("Orchard")))
        self.assert_turns(self.interpret(request), [{"utterance": "Create Garden"},
                                                   {"utterance": "Use Orchard instead"}])

    def test_partial_activation_and_finalization_archive_previous_turn_once(self):
        request = self.request("Create Garden")
        self.interpret(request, proposal())
        self.coordinator.revise(request, "Create Garden", input_final=False)
        with self.assertRaises(TransitionError):
            self.coordinator.begin_interpretation(request)
        self.coordinator.finalize_input(request, "Use Orchard instead")
        job = self.interpret(request)
        self.assertEqual(job["ticket"]["request_revision"], 2)
        self.assertEqual(job["utterance"], "Use Orchard instead")
        self.assert_turns(job, [{"utterance": "Create Garden", "interpretation": proposal()}])

    def test_repeated_partial_revisions_never_archive_unfinalized_text(self):
        request = self.request("Create Garden")
        self.coordinator.revise(request, "unfinished replacement", input_final=False)
        self.coordinator.revise(request, "another preview", input_final=False)
        self.coordinator.finalize_input(request, "Use Meadow")
        self.assert_turns(self.interpret(request), [{"utterance": "Create Garden"}])

    def test_histories_are_request_local(self):
        first = self.request("First private utterance")
        self.coordinator.revise(first, "First correction")
        second = self.request("Second independent request")
        self.assertIsNone(self.interpret(second)["context"].get("pending_request"))
        self.assert_turns(self.interpret(first), [{"utterance": "First private utterance"}])

    def test_history_is_deep_copied_at_output_boundary(self):
        request = self.request("Create Garden")
        original = proposal()
        self.interpret(request, original)
        self.coordinator.revise(request, "Use Orchard")
        job = self.interpret(request)
        job["context"]["pending_request"]["turns"][0]["interpretation"]["actions"][0]["arguments"]["name"] = "MUTATED"
        original["actions"][0]["arguments"]["name"] = "ALSO MUTATED"
        self.coordinator.revise(request, "Use Meadow")
        self.assert_turns(self.interpret(request), [
            {"utterance": "Create Garden", "interpretation": proposal()},
            {"utterance": "Use Orchard"}])

    def test_policy_change_retains_utterances_and_discards_all_prior_interpretations(self):
        request = self.request("Create Garden")
        self.interpret(request, proposal())
        self.coordinator.revise(request, "Use Orchard")
        self.interpret(request, proposal("Orchard"))
        self.coordinator.revise(request, "Use Meadow")
        old = self.interpret(request)
        self.coordinator.set_grants([{"capability": "file.search", "root_id": "documents"}])
        self.assertFalse(self.coordinator.accept_interpretation(old["ticket"], proposal("Meadow")))
        self.assert_turns(self.interpret(request), [{"utterance": "Create Garden"},
                                                  {"utterance": "Use Orchard"}])

    def test_policy_change_does_not_archive_current_invalidated_proposal(self):
        request = self.request("Create Garden")
        self.interpret(request, proposal())
        self.coordinator.set_grants([{"capability": "file.search", "root_id": "documents"}])
        self.coordinator.revise(request, "Find Garden instead")
        self.assert_turns(self.interpret(request), [{"utterance": "Create Garden"}])

    def test_four_previous_finalized_turns_are_retained_in_order(self):
        request = self.request("Turn 0")
        for number in range(1, 5):
            self.coordinator.revise(request, f"Turn {number}")
        job = self.interpret(request)
        self.assertEqual(job["utterance"], "Turn 4")
        self.assert_turns(job, [{"utterance": f"Turn {number}"} for number in range(4)])

    def test_fifth_previous_turn_fails_closed_instead_of_silently_dropping_context(self):
        request = self.request("Turn 0")
        for number in range(1, 5):
            self.coordinator.revise(request, f"Turn {number}")
        old = self.interpret(request, proposal())
        digest = self.coordinator.snapshot(request)["confirmation_digest"]
        with self.assertRaises(TransitionError):
            self.coordinator.revise(request, "Turn 5")
        view = self.coordinator.snapshot(request)
        self.assertEqual(view["state"], "failed")
        self.assertEqual(view["result"]["reason"], "correction_context_limit")
        self.assertIsNone(view["proposal"])
        self.assertFalse(self.coordinator.accept_interpretation(old["ticket"], proposal()))
        self.assertFalse(self.coordinator.approve(request, digest))
        with self.assertRaises(TransitionError):
            self.coordinator.execute(request)
        self.assertIsNone(self.interpret(self.request("A complete new request"))["context"].get("pending_request"))
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_unicode_escape_bytes_are_counted_not_python_characters(self):
        # 1,400 emoji are only 5,600 UTF-8 bytes, but exceed 16 KiB after
        # ensure_ascii=True renders each character as two surrogate escapes.
        text = "\U0001f331" * 1400
        self.assertLess(len(text.encode("utf-8")), 16384)
        self.assertGreater(len(json.dumps({"turns": [{"utterance": text}]}, ensure_ascii=True).encode()), 16384)
        request = self.request(text)
        with self.assertRaises(TransitionError):
            self.coordinator.revise(request, "Replacement")
        self.assertEqual(self.coordinator.snapshot(request)["result"]["reason"], "correction_context_limit")

    @staticmethod
    def exact_context_text(size):
        seed = "\U0001f331" * 1300
        used = len(json.dumps({"turns": [{"utterance": seed}]}, ensure_ascii=True,
                              allow_nan=False).encode("utf-8"))
        return seed + "x" * (size - used)

    def test_exact_16_kib_context_is_accepted(self):
        text = self.exact_context_text(16384)
        self.assertLess(len(text), 8192)
        request = self.request(text)
        self.coordinator.revise(request, "Replacement")
        job = self.interpret(request)
        history = job["context"]["pending_request"]
        self.assertEqual(len(json.dumps(history, ensure_ascii=True, allow_nan=False).encode("utf-8")), 16384)

    def test_one_byte_over_context_limit_fails_closed(self):
        request = self.request(self.exact_context_text(16385))
        with self.assertRaises(TransitionError):
            self.coordinator.revise(request, "Replacement")
        snapshot = self.coordinator.snapshot(request)
        self.assertEqual(snapshot["result"]["reason"], "correction_context_limit")
        self.assertIsNone(snapshot["pending_context"])

    def test_interpretations_contribute_to_byte_limit(self):
        request = self.request("a" * 8100)
        self.interpret(request, proposal("b" * 255))
        self.coordinator.revise(request, "c" * 8100)
        with self.assertRaises(TransitionError):
            self.coordinator.revise(request, "Replacement")
        self.assertEqual(self.coordinator.snapshot(request)["result"]["reason"], "correction_context_limit")

    def test_snapshot_history_is_copied(self):
        request = self.request("Create Garden")
        self.coordinator.revise(request, "Use Orchard")
        view = self.coordinator.snapshot(request)
        self.assertEqual(view["pending_context"], {"turns": [{"utterance": "Create Garden"}]})
        view["pending_context"]["turns"][0]["utterance"] = "MUTATED"
        self.assert_turns(self.interpret(request), [{"utterance": "Create Garden"}])

    def test_terminal_outcomes_release_retained_correction_context(self):
        for ending in ("cancel", "lock", "unsupported", "invalid_proposal", "success", "unknown"):
            with self.subTest(ending=ending):
                request = self.request(f"Initial request for {ending}")
                self.coordinator.revise(request, "Replacement")
                self.assertIsNotNone(self.coordinator.snapshot(request)["pending_context"])
                if ending == "cancel":
                    self.coordinator.cancel(request)
                elif ending == "lock":
                    self.coordinator.set_active(False)
                    self.coordinator.set_active(True)
                elif ending == "unsupported":
                    self.interpret(request, {"kind": "unsupported"})
                elif ending == "invalid_proposal":
                    self.interpret(request, proposal("../invalid"))
                else:
                    self.interpret(request, proposal(f"Fixture-{ending}"))
                    digest = self.coordinator.snapshot(request)["confirmation_digest"]
                    self.assertTrue(self.coordinator.approve(request, digest))
                    self.coordinator.execute(request, interrupt_after_effect=ending == "unknown")
                terminal = self.coordinator.snapshot(request)
                self.assertIn(terminal["state"], {"succeeded", "failed", "cancelled", "outcome_unknown"})
                self.assertIsNone(terminal["pending_context"])


if __name__ == "__main__":
    unittest.main()
