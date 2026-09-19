import time
import unittest

from console import Console
from coordinator import Sandbox, SessionCoordinator
from test_worker import ControlledInterpreter
from worker import InferenceWorker


class ResponsiveConsoleTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.sandbox.__enter__()
        self.addCleanup(self.sandbox.__exit__, None, None, None)
        self.coordinator = SessionCoordinator(self.sandbox, confirmation_required=True)
        self.interpreter = ControlledInterpreter()
        self.worker = InferenceWorker(self.interpreter)
        self.console = Console(self.coordinator, self.interpreter, self.worker)
        self.addCleanup(self.finish)

    def finish(self):
        self.console.close()
        self.interpreter.release.set()
        self.worker.close(wait_seconds=1)

    def start_request(self):
        self.console.handle_line("n")
        self.console.handle_line("Create Garden")
        self.assertTrue(self.interpreter.started.wait(1))
        return self.console.current

    def wait_for_state(self, state):
        until = time.monotonic() + 2
        views = []
        while time.monotonic() < until:
            views.extend(self.console.tick())
            if self.coordinator.snapshot(self.console.current)["state"] == state:
                return views
            time.sleep(0.002)
        self.fail(f"Request did not reach {state}")

    def test_cancel_control_works_while_inference_is_blocked(self):
        request = self.start_request()
        view = self.console.handle_line("c")[-1]
        self.assertFalse(self.interpreter.release.is_set())
        self.assertEqual(view["state"], "cancelled")
        self.interpreter.release.set()
        self.worker.close(wait_seconds=1)
        self.console.tick()
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_approval_needs_displayed_proposal(self):
        request = self.start_request()
        self.assertIn("No displayed proposal", self.console.handle_line("a")[0])
        self.interpreter.release.set()
        self.wait_for_state("awaiting_confirmation")
        self.assertFalse((self.sandbox.documents / "Garden").exists())
        view = self.console.handle_line("a")[-1]
        self.assertEqual(view["state"], "succeeded")
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())

    def test_revision_cancels_old_job_and_uses_new_revision(self):
        request = self.start_request()
        self.console.handle_line("r")
        view = self.console.handle_line("Please make Garden in Documents")[-1]
        self.assertEqual(view["revision"], 2)
        self.interpreter.release.set()
        self.wait_for_state("awaiting_confirmation")
        self.assertEqual(self.coordinator.snapshot(request)["proposal"]["request_revision"], 2)
        self.assertEqual(self.interpreter.jobs[-1]["utterance"], "Please make Garden in Documents")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_new_request_does_not_hide_pending_request(self):
        request = self.start_request()
        self.assertIn("still pending", self.console.handle_line("n")[0])
        self.assertEqual(self.console.current, request)
        self.assertIsNone(self.console.entering)

    def test_dictation_after_cancel_bypasses_still_running_interpreter(self):
        self.start_request()
        self.console.handle_line("c")
        self.console.handle_line("d")
        view = self.console.handle_line("Delete all files")[-1]
        self.assertEqual(view["result"]["delivery"], "panel_only")
        self.assertEqual(view["result"]["text"], "Delete all files")
        self.assertEqual(len(self.interpreter.jobs), 1)

    def test_quit_cancels_inference_without_waiting(self):
        request = self.start_request()
        self.console.handle_line("q")
        self.assertTrue(self.console.closed)
        self.assertFalse(self.interpreter.release.is_set())
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")
        self.assertFalse((self.sandbox.documents / "Garden").exists())


if __name__ == "__main__":
    unittest.main()
