"""Independent QA regressions: fake HTTP, controlled workers, disposable files only."""

import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
import unittest

from console import Console
from coordinator import Sandbox, SessionCoordinator
from inference import InferenceError, LocalChatInterpreter
from transcripts import TranscriptGate
from worker import InferenceWorker, deliver


CREATE = {"kind": "proposal", "actions": [{"capability": "directory.create",
          "arguments": {"root_id": "documents", "name": "Garden"}}]}


def completion(content=None):
    return json.dumps({"choices": [{"finish_reason": "stop", "message": {
        "role": "assistant", "content": json.dumps(CREATE) if content is None else content}}]}).encode()


class ResponseFixture(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        body, declared_length, *framing = self.server.fixture
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        if framing and framing[0] == "chunked":
            self.send_header("Transfer-Encoding", "chunked")
        else:
            self.send_header("Content-Length", str(len(body) if declared_length is None else declared_length))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def log_message(self, *_):
        pass


class InferenceBoundaryRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ResponseFixture)
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      kwargs={"poll_interval": 0.01}, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=1)

    def setUp(self):
        self.server.fixture = (completion(), None)
        endpoint = f"http://127.0.0.1:{self.server.server_port}/v1/chat/completions"
        self.adapter = LocalChatInterpreter(endpoint, "synthetic-fixture", timeout=1)
        self.job = {"mode": "command", "utterance": "Create Garden", "context": {}}

    def assert_rejected(self):
        with self.assertRaises(InferenceError) as caught:
            self.adapter.interpret(self.job)
        self.assertIn(caught.exception.code, {"inference_invalid_response", "inference_unavailable"})
        self.assertIsNone(self.adapter.last_metadata)

    def test_valid_json_in_incomplete_http_entity_is_rejected(self):
        # The JSON itself is complete; the HTTP entity is not. read1() can return
        # EOF without raising IncompleteRead, so framing must also be checked.
        body = completion()
        self.server.fixture = (body, len(body) + 10)
        self.assert_rejected()

    def test_deep_outer_json_becomes_typed_failure(self):
        self.server.fixture = (b"[" * 2000 + b"0" + b"]" * 2000, None)
        self.assert_rejected()

    def test_deep_model_json_becomes_typed_failure(self):
        self.server.fixture = (completion("[" * 2000 + "0" + "]" * 2000), None)
        self.assert_rejected()

    def test_outer_duplicate_keys_cannot_select_a_different_completion(self):
        original = completion().decode()
        self.server.fixture = ((original[:-1] + ',"choices":[]}').encode(), None)
        self.assert_rejected()

    def test_invalid_utf8_is_rejected(self):
        self.server.fixture = (b'{"choices": "\xff"}', None)
        self.assert_rejected()

    def test_metadata_from_success_is_cleared_on_next_failure(self):
        self.assertEqual(self.adapter.interpret(self.job), CREATE)
        self.assertIsNotNone(self.adapter.last_metadata)
        self.server.fixture = (b"not-json", None)
        self.assert_rejected()

    def test_complete_chunked_completion_is_accepted(self):
        body = completion()
        midpoint = len(body) // 2
        chunks = [body[:midpoint], body[midpoint:]]
        framed = b"".join(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n" for chunk in chunks)
        self.server.fixture = (framed + b"0\r\n\r\n", None, "chunked")
        self.assertEqual(self.adapter.interpret(self.job), CREATE)
        self.assertEqual(self.adapter.last_metadata["response_bytes"], len(body))

    def test_valid_json_without_chunk_terminator_is_rejected(self):
        body = completion()
        framed = f"{len(body):x}\r\n".encode() + body + b"\r\n"
        self.server.fixture = (framed, None, "chunked")
        self.assert_rejected()


class GateBoundaryRegressions(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.sandbox.__enter__()
        self.addCleanup(self.sandbox.__exit__, None, None, None)
        self.coordinator = SessionCoordinator(self.sandbox)
        self.gate = TranscriptGate(self.coordinator)

    @staticmethod
    def event(capture, sequence=1, kind="final", text="Create Garden"):
        return {"schema_version": 1, "capture_id": capture,
                "sequence": sequence, "kind": kind, "text": text}

    def test_cancel_request_before_correction_final_prevents_delivery(self):
        request = self.coordinator.submit("Old request")
        capture = self.gate.begin(request_id=request)
        self.coordinator.cancel(request)
        self.assertFalse(self.gate.accept(self.event(capture)))
        self.assertEqual(self.gate.snapshot()["state"], "cancelled")
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_mutating_accepted_partial_does_not_rewrite_duplicate_history(self):
        capture = self.gate.begin()
        event = self.event(capture, kind="partial", text="Create")
        self.assertTrue(self.gate.accept(event))
        event["text"] = "Delete"
        self.assertFalse(self.gate.accept(event))
        self.assertEqual(self.gate.snapshot()["reason"], "conflicting_transcript_event")
        self.assertEqual(self.coordinator._requests, {})

    def test_finalized_capture_cannot_be_replayed_after_new_activation(self):
        old_capture = self.gate.begin(mode="dictation")
        old_final = self.event(old_capture)
        self.assertTrue(self.gate.accept(old_final))
        new_capture = self.gate.begin(mode="command")
        self.assertFalse(self.gate.accept(old_final))
        self.assertEqual(self.gate.snapshot()["capture_id"], new_capture)
        self.assertEqual(self.gate.snapshot()["state"], "receiving")
        self.assertEqual(len(self.coordinator._requests), 1)

    def test_boolean_sequence_cannot_be_used_as_first_event(self):
        capture = self.gate.begin()
        self.assertFalse(self.gate.accept(self.event(capture, sequence=True)))
        self.assertEqual(self.gate.snapshot()["reason"], "invalid_transcript_event")
        self.assertEqual(self.coordinator._requests, {})


class ControlledInterpreter:
    name = "qa_fixture_not_ai"

    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.output = CREATE

    def interpret(self, _job):
        self.started.set()
        if not self.release.wait(timeout=2):
            raise RuntimeError("Fixture was not released")
        if isinstance(self.output, BaseException):
            raise self.output
        return copy.deepcopy(self.output)


class WorkerBoundaryRegressions(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.sandbox.__enter__()
        self.addCleanup(self.sandbox.__exit__, None, None, None)
        self.coordinator = SessionCoordinator(self.sandbox)
        self.interpreter = ControlledInterpreter()
        self.worker = InferenceWorker(self.interpreter)
        self.addCleanup(self.close_worker)

    def close_worker(self):
        self.interpreter.release.set()
        self.worker.close(wait_seconds=1)

    def start(self):
        request = self.coordinator.submit("Create Garden")
        job = self.coordinator.begin_interpretation(request)
        self.assertTrue(self.worker.submit(job))
        return request, job

    def result(self):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            results = self.worker.drain()
            if results:
                self.assertEqual(len(results), 1)
                return results[0]
            time.sleep(0.002)
        self.fail("Accepted worker job did not produce a result")

    def test_unknown_interpreter_error_code_is_sanitized_before_delivery(self):
        self.interpreter.output = InferenceError("private server error /secret/location")
        request, _ = self.start()
        self.interpreter.release.set()
        result = self.result()
        self.assertEqual(result["error"], "inference_invalid_response")
        self.assertTrue(deliver(self.coordinator, result))
        self.assertEqual(self.coordinator.snapshot(request)["state"], "failed")

    def test_worker_continues_after_a_failed_interpreter_call(self):
        self.interpreter.output = RuntimeError("private detail")
        first, _ = self.start()
        self.interpreter.release.set()
        result = self.result()
        self.assertTrue(deliver(self.coordinator, result))
        self.assertEqual(self.coordinator.snapshot(first)["state"], "failed")
        self.interpreter.output = CREATE
        second, _ = self.start()
        self.assertTrue(deliver(self.coordinator, self.result()))
        self.assertEqual(self.coordinator.snapshot(second)["state"], "ready")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_beginning_typed_correction_blocks_old_inference_before_next_line(self):
        console = Console(self.coordinator, self.interpreter, self.worker)
        console.handle_line("n")
        console.handle_line("Create Garden")
        request = console.current
        self.assertTrue(self.interpreter.started.wait(timeout=1))
        console.handle_line("r")
        self.interpreter.release.set()
        deadline = time.monotonic() + 2
        while self.worker._results.empty() and time.monotonic() < deadline:
            time.sleep(0.002)
        self.assertFalse(self.worker._results.empty())
        console.tick()
        self.assertFalse((self.sandbox.documents / "Garden").exists(),
                         "Old request executed while its replacement was being entered")
        self.assertNotEqual(self.coordinator.snapshot(request)["state"], "succeeded")

    def test_invalid_replacement_keeps_original_suspended_and_cancel_reachable(self):
        console = Console(self.coordinator, self.interpreter, self.worker)
        console.handle_line("n")
        console.handle_line("Create Garden")
        request = console.current
        console.handle_line("r")
        console.handle_line("   ")
        suspended = self.coordinator.snapshot(request)
        self.assertEqual(suspended["revision"], 2)
        self.assertFalse(suspended["input_final"])
        self.assertIsNone(suspended["proposal"])
        self.assertEqual(console.entering, "revision")
        console.handle_line("c")
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")
        self.assertFalse((self.sandbox.documents / "Garden").exists())

    def test_quit_remains_reachable_after_rejected_replacement(self):
        console = Console(self.coordinator, self.interpreter, self.worker)
        console.handle_line("n")
        console.handle_line("Create Garden")
        request = console.current
        console.handle_line("r")
        console.handle_line("")
        console.handle_line("q")
        self.assertTrue(console.closed)
        self.assertEqual(self.coordinator.snapshot(request)["state"], "cancelled")
        self.assertFalse((self.sandbox.documents / "Garden").exists())


if __name__ == "__main__":
    unittest.main()
