import copy
import threading
import time
import unittest

from coordinator import Sandbox, SessionCoordinator
from inference import InferenceError
from worker import InferenceWorker, deliver


PROPOSAL = {"kind": "proposal", "actions": [{"capability": "directory.create",
             "arguments": {"root_id": "documents", "name": "Garden"}}]}


class ControlledInterpreter:
    name = "controlled_fixture_not_ai"

    def __init__(self, output=PROPOSAL):
        self.output = output
        self.started = threading.Event()
        self.release = threading.Event()
        self.jobs = []

    def interpret(self, job):
        self.jobs.append(copy.deepcopy(job))
        self.started.set()
        if not self.release.wait(timeout=2):
            raise RuntimeError("Test did not release interpreter")
        if isinstance(self.output, BaseException):
            raise self.output
        return copy.deepcopy(self.output)


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.sandbox.__enter__()
        self.addCleanup(self.sandbox.__exit__, None, None, None)
        self.coordinator = SessionCoordinator(self.sandbox)
        self.interpreter = ControlledInterpreter()
        self.workers = []
        self.addCleanup(self.cleanup_workers)

    def cleanup_workers(self):
        self.interpreter.release.set()
        for worker in self.workers:
            worker.close(wait_seconds=1)

    def worker(self, capacity=4):
        worker = InferenceWorker(self.interpreter, capacity=capacity)
        self.workers.append(worker)
        return worker

    def job(self):
        request = self.coordinator.submit("Create Garden")
        return request, self.coordinator.begin_interpretation(request)

    def results(self, worker, count=1):
        output = []
        until = time.monotonic() + 2
        while len(output) < count and time.monotonic() < until:
            output.extend(worker.drain())
            if len(output) < count:
                time.sleep(0.002)
        self.assertEqual(len(output), count)
        return output

    def test_owner_delivers_result_and_execution_is_separate(self):
        worker = self.worker()
        request, job = self.job()
        self.assertTrue(worker.submit(job))
        self.assertTrue(self.interpreter.started.wait(1))
        self.interpreter.release.set()
        result = self.results(worker)[0]
        self.assertEqual(self.coordinator.snapshot(request)["state"], "interpreting")
        self.assertNotIn("ticket", self.interpreter.jobs[0])
        self.assertTrue(deliver(self.coordinator, result))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "ready")
        self.assertFalse((self.sandbox.documents / "Garden").exists())
        self.coordinator.execute(request)
        self.assertTrue((self.sandbox.documents / "Garden").is_dir())

    def test_running_cancel_is_prompt_and_suppresses_delivery(self):
        worker = self.worker()
        request, job = self.job()
        worker.submit(job)
        self.assertTrue(self.interpreter.started.wait(1))
        self.assertTrue(self.coordinator.cancel(request))
        self.assertTrue(worker.cancel(job["ticket"]))
        self.assertFalse(self.interpreter.release.is_set())
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")
        self.interpreter.release.set()
        result = self.results(worker)[0]
        self.assertTrue(result["cancelled"])
        self.assertFalse(deliver(self.coordinator, result))
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_queued_cancellation_skips_interpreter_call(self):
        worker = self.worker()
        _, first = self.job()
        _, second = self.job()
        worker.submit(first)
        self.assertTrue(self.interpreter.started.wait(1))
        worker.submit(second)
        worker.cancel(second["ticket"])
        self.interpreter.release.set()
        results = self.results(worker, 2)
        self.assertEqual(len(self.interpreter.jobs), 1)
        self.assertTrue(results[1]["cancelled"])

    def test_stale_revision_is_rejected_without_worker_cancel(self):
        worker = self.worker()
        request, job = self.job()
        worker.submit(job)
        self.coordinator.revise(request, "Find garden notes")
        self.interpreter.release.set()
        self.assertFalse(deliver(self.coordinator, self.results(worker)[0]))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "received")

    def test_policy_change_rejects_delayed_output(self):
        worker = self.worker()
        request, job = self.job()
        worker.submit(job)
        self.coordinator.set_grants([])
        self.interpreter.release.set()
        self.assertFalse(deliver(self.coordinator, self.results(worker)[0]))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "received")

    def test_capacity_includes_running_and_undrained_results(self):
        worker = self.worker(capacity=1)
        _, first = self.job()
        _, second = self.job()
        self.assertTrue(worker.submit(first))
        self.assertFalse(worker.submit(second))
        self.interpreter.release.set()
        until = time.monotonic() + 1
        while worker._results.empty() and time.monotonic() < until:
            time.sleep(0.002)
        self.assertFalse(worker._results.empty())
        self.assertFalse(worker.submit(second))
        self.results(worker)
        self.assertTrue(worker.submit(second))
        self.results(worker)

    def test_cancel_after_completion_before_drain_discards_output(self):
        worker = self.worker()
        _, job = self.job()
        worker.submit(job)
        self.interpreter.release.set()
        until = time.monotonic() + 1
        while worker._results.empty() and time.monotonic() < until:
            time.sleep(0.002)
        worker.cancel(job["ticket"])
        self.assertTrue(self.results(worker)[0]["cancelled"])

    def test_interpreter_exception_is_sanitized(self):
        self.interpreter.output = RuntimeError("sensitive error text")
        worker = self.worker()
        request, job = self.job()
        worker.submit(job)
        self.interpreter.release.set()
        result = self.results(worker)[0]
        self.assertEqual(result["error"], "inference_invalid_response")
        self.assertNotIn("sensitive", str(result))
        self.assertTrue(deliver(self.coordinator, result))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "failed")

    def test_known_timeout_code_is_preserved(self):
        self.interpreter.output = InferenceError("inference_timeout")
        worker = self.worker()
        _, job = self.job()
        worker.submit(job)
        self.interpreter.release.set()
        self.assertEqual(self.results(worker)[0]["error"], "inference_timeout")

    def test_input_is_copied_and_duplicate_ticket_is_rejected(self):
        worker = self.worker()
        _, job = self.job()
        worker.submit(job)
        with self.assertRaises(ValueError):
            worker.submit(job)
        job["utterance"] = "Mutated after submission"
        self.interpreter.release.set()
        self.results(worker)
        self.assertEqual(self.interpreter.jobs[0]["utterance"], "Create Garden")

    def test_close_does_not_wait_for_running_call_and_rejects_new_work(self):
        worker = self.worker()
        _, job = self.job()
        worker.submit(job)
        self.assertTrue(self.interpreter.started.wait(1))
        self.assertFalse(worker.close())
        with self.assertRaises(ValueError):
            worker.submit(self.job()[1])
        self.interpreter.release.set()
        self.assertTrue(worker.close(wait_seconds=1))
        self.assertTrue(self.results(worker)[0]["cancelled"])


if __name__ == "__main__":
    unittest.main()
