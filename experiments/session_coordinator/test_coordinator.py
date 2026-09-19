import copy
import unittest

from coordinator import Sandbox, SessionCoordinator, TransitionError


def create(name="Garden"):
    return {"kind": "proposal", "actions": [{"capability": "directory.create",
                                             "arguments": {"root_id": "documents", "name": name}}]}


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox._temporary.cleanup)
        self.coordinator = SessionCoordinator(self.sandbox)

    def pending(self, output=None):
        request = self.coordinator.submit("Create Garden")
        job = self.coordinator.begin_interpretation(request)
        if output is not None:
            self.assertTrue(self.coordinator.accept_interpretation(job["ticket"], output))
        return request, job

    def test_normal_request_and_monotonic_events(self):
        request, _ = self.pending(create())
        result = self.coordinator.execute(request)
        self.assertEqual(result["state"], "succeeded")
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())
        self.assertEqual([e["sequence"] for e in result["events"]], list(range(1, len(result["events"]) + 1)))

    def test_dictation_bypasses_interpretation_and_effects(self):
        request = self.coordinator.submit("Delete all files", mode="dictation")
        result = self.coordinator.snapshot(request)
        self.assertEqual(result["result"]["text"], "Delete all files")
        self.assertEqual(result["result"]["delivery"], "panel_only")
        self.assertIsNone(result["proposal"])
        self.assertEqual(self.coordinator.executor.records, {})
        with self.assertRaises(TransitionError):
            self.coordinator.begin_interpretation(request)

    def test_old_response_cannot_override_revision(self):
        request, old = self.pending()
        self.coordinator.revise(request, "Create Other")
        current = self.coordinator.begin_interpretation(request)
        self.assertFalse(self.coordinator.accept_interpretation(old["ticket"], create()))
        self.assertTrue(self.coordinator.accept_interpretation(current["ticket"], create("Other")))
        self.coordinator.execute(request)
        self.assertFalse((self.sandbox.documents / "Garden").exists())
        self.assertTrue((self.sandbox.documents / "Other").is_dir())

    def test_cancelled_request_cannot_be_revived(self):
        request, job = self.pending()
        self.coordinator.cancel(request)
        self.assertFalse(self.coordinator.accept_interpretation(job["ticket"], create()))
        with self.assertRaises(TransitionError):
            self.coordinator.execute(request)
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")

    def test_job_ticket_type_confusion_is_rejected(self):
        request, job = self.pending()
        forged = copy.deepcopy(job["ticket"])
        forged["request_revision"] = True
        self.assertFalse(self.coordinator.accept_interpretation(forged, create()))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "interpreting")

    def test_wrong_job_identity_is_rejected(self):
        request, job = self.pending()
        forged = copy.deepcopy(job["ticket"])
        forged["job_id"] = "different"
        self.assertFalse(self.coordinator.accept_interpretation(forged, create()))
        self.assertTrue(self.coordinator.accept_interpretation(job["ticket"], create()))

    def test_duplicate_response_is_ignored(self):
        request, job = self.pending(create())
        self.assertFalse(self.coordinator.accept_interpretation(job["ticket"], create("Other")))
        self.coordinator.execute(request)
        self.assertFalse((self.sandbox.documents / "Other").exists())

    def test_confirmation_is_bound_to_revision(self):
        self.coordinator = SessionCoordinator(self.sandbox, confirmation_required=True)
        request, _ = self.pending(create())
        old_digest = self.coordinator.snapshot(request)["confirmation_digest"]
        with self.assertRaises(TransitionError):
            self.coordinator.execute(request)
        self.coordinator.revise(request, "Create Other")
        job = self.coordinator.begin_interpretation(request)
        self.coordinator.accept_interpretation(job["ticket"], create("Other"))
        self.assertFalse(self.coordinator.approve(request, old_digest))
        digest = self.coordinator.snapshot(request)["confirmation_digest"]
        self.assertTrue(self.coordinator.approve(request, digest))
        self.assertEqual(self.coordinator.execute(request)["state"], "succeeded")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_policy_change_invalidates_pending_inference(self):
        request, job = self.pending()
        self.coordinator.set_grants([])
        self.assertFalse(self.coordinator.accept_interpretation(job["ticket"], create()))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "received")

    def test_policy_change_invalidates_ready_proposal(self):
        request, _ = self.pending(create())
        self.coordinator.set_grants([])
        with self.assertRaises(TransitionError):
            self.coordinator.execute(request)
        job = self.coordinator.begin_interpretation(request)
        self.coordinator.accept_interpretation(job["ticket"], create())
        self.assertEqual(self.coordinator.snapshot(request)["result"]["reason"], "missing_grant")

    def test_identical_policy_does_not_invalidate_request(self):
        request, _ = self.pending(create())
        self.coordinator.set_grants(copy.deepcopy(self.coordinator.grants))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "ready")

    def test_session_lock_invalidates_request_and_late_output(self):
        request, job = self.pending()
        self.coordinator.set_active(False)
        self.coordinator.set_active(True)
        self.assertFalse(self.coordinator.accept_interpretation(job["ticket"], create()))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")

    def test_cancel_during_dispatch_prevents_next_effect(self):
        output = create()
        output["actions"].extend(create("Second")["actions"])
        request, _ = self.pending(output)
        def stop(index):
            if index == 1:
                self.coordinator.cancel(request)
        result = self.coordinator.execute(request, before_step=stop)
        self.assertEqual(result["state"], "cancelled")
        self.assertEqual(len(result["result"]["steps"]), 1)
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())
        self.assertFalse((self.sandbox.documents / "Second").exists())

    def test_exception_after_first_step_preserves_known_effect(self):
        output = create()
        output["actions"].extend(create("Second")["actions"])
        request, _ = self.pending(output)
        def interrupt(index):
            if index == 1:
                raise OSError("Synthetic interruption")
        result = self.coordinator.execute(request, before_step=interrupt)
        self.assertEqual(result["state"], "outcome_unknown")
        self.assertEqual(len(result["result"]["steps"]), 1)
        self.assertEqual(result["result"]["steps"][0]["outcome"], "created")

    def test_revoke_during_dispatch_stops_later_steps(self):
        output = create()
        output["actions"].extend(create("Second")["actions"])
        request, _ = self.pending(output)
        def revoke(index):
            if index == 1:
                self.coordinator.set_grants([])
        result = self.coordinator.execute(request, before_step=revoke)
        self.assertEqual(result["state"], "failed")
        self.assertFalse((self.sandbox.documents / "Second").exists())

    def test_snapshot_and_model_output_cannot_mutate_proposal(self):
        output = create()
        request, _ = self.pending(output)
        output["actions"][0]["arguments"]["name"] = "Changed"
        view = self.coordinator.snapshot(request)
        view["proposal"]["steps"][0]["arguments"]["name"] = "AlsoChanged"
        self.coordinator.execute(request)
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())

    def test_clarification_then_revised_input(self):
        request, _ = self.pending({"kind": "clarify", "missing": ["name"]})
        self.assertEqual(self.coordinator.snapshot(request)["state"], "needs_clarification")
        self.coordinator.revise(request, "Create Garden")
        job = self.coordinator.begin_interpretation(request)
        self.coordinator.accept_interpretation(job["ticket"], create())
        self.assertEqual(self.coordinator.execute(request)["state"], "succeeded")

    def test_model_cannot_supply_host_permission_fields(self):
        output = create()
        output["approved"] = True
        request, _ = self.pending(output)
        self.assertEqual(self.coordinator.snapshot(request)["result"]["reason"], "interpretation_invalid")
        self.assertEqual(self.coordinator.executor.records, {})

    def test_late_inference_error_cannot_fail_new_revision(self):
        request, job = self.pending()
        self.coordinator.revise(request, "Create Other")
        self.assertFalse(self.coordinator.fail_interpretation(job["ticket"], "inference_timeout"))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "received")

    def test_request_limit_does_not_evict_pending_work(self):
        requests = [self.coordinator.submit(f"Request {index}") for index in range(32)]
        with self.assertRaises(TransitionError):
            self.coordinator.submit("Too many")
        self.assertEqual(self.coordinator.snapshot(requests[0])["state"], "received")
