from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
import time
import unittest
from unittest.mock import patch

from coordinator import Sandbox, SessionCoordinator
from inference import InferenceError, LocalChatInterpreter, MAX_BYTES, build_messages


OUTCOME = {"kind": "proposal", "actions": [{"capability": "directory.create",
                                           "arguments": {"root_id": "documents", "name": "Garden"}}]}


def completion(content=None, finish="stop"):
    return json.dumps({"choices": [{"finish_reason": finish, "message": {
        "role": "assistant", "content": json.dumps(OUTCOME) if content is None else content}}]}).encode()


class FakeChat(BaseHTTPRequestHandler):
    def do_POST(self):
        plan = dict(self.server.plan)
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.server.requests.append({"path": self.path, "json": json.loads(raw)})
        time.sleep(plan.get("delay", 0))
        body = plan.get("body", completion())
        try:
            self.send_response(plan.get("status", 200))
            self.send_header("Content-Type", plan.get("type", "application/json"))
            self.send_header("Content-Length", str(plan.get("length", len(body))))
            self.send_header("Location", "http://192.0.2.1/should-not-follow")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *_):
        pass


class LoopbackAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeChat)
        cls.thread = threading.Thread(target=cls.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        cls.thread.start()
        cls.endpoint = f"http://127.0.0.1:{cls.server.server_port}/v1/chat/completions"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.server.plan = {}
        self.server.requests = []
        self.job = {"mode": "command", "utterance": "Create Garden", "context": {
            "roots": {"documents": "Documents"}, "default_root_id": "documents"}}
        self.adapter = LocalChatInterpreter(self.endpoint, "fake-model", timeout=1)

    def assert_failure(self, code):
        with self.assertRaises(InferenceError) as failure:
            self.adapter.interpret(self.job)
        self.assertEqual(failure.exception.code, code)
        self.assertIsNone(self.adapter.last_metadata)

    def test_valid_response_and_no_reference_answer_leakage(self):
        self.job["acceptable"] = ["secret-reference-answer"]
        self.job["ticket"] = {"job_id": "private-correlation-ticket"}
        self.assertEqual(self.adapter.interpret(self.job), OUTCOME)
        request = self.server.requests[0]
        self.assertEqual(request["path"], "/v1/chat/completions")
        self.assertFalse(request["json"]["stream"])
        self.assertEqual(request["json"]["model"], "fake-model")
        serialized = json.dumps(request)
        self.assertNotIn("secret-reference-answer", serialized)
        self.assertNotIn("private-correlation-ticket", serialized)

    def test_numeric_loopback_only(self):
        endpoints = ["https://127.0.0.1/v1/chat/completions", "http://localhost/v1/chat/completions",
                     "http://192.0.2.1/v1/chat/completions", "http://user:secret@127.0.0.1/v1/chat/completions",
                     "http://127.0.0.1/v1/chat/completions?key=secret", "http://127.0.0.1:0/v1/chat/completions",
                     "http://127.0.0.1/other", "http://127.0.0.1/v1/chat/completions#fragment"]
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                LocalChatInterpreter(endpoint, "fake-model")

    def test_redirect_is_not_followed(self):
        self.server.plan = {"status": 302}
        self.assert_failure("inference_unavailable")
        self.assertEqual(len(self.server.requests), 1)

    def test_http_failure_body_is_not_exposed(self):
        self.server.plan = {"status": 500, "body": b"sensitive-server-detail"}
        self.assert_failure("inference_unavailable")

    def test_proxy_environment_is_not_used(self):
        with patch.dict(os.environ, {"http_proxy": "http://192.0.2.1:9", "HTTP_PROXY": "http://192.0.2.1:9"}):
            self.assertEqual(self.adapter.interpret(self.job), OUTCOME)

    def test_idle_timeout(self):
        self.server.plan = {"delay": 0.1}
        self.adapter = LocalChatInterpreter(self.endpoint, "fake", timeout=0.02)
        self.assert_failure("inference_timeout")

    def test_length_truncation_is_not_accepted(self):
        self.server.plan = {"body": completion(finish="length")}
        self.assert_failure("inference_invalid_response")

    def test_duplicate_keys_in_model_output_rejected(self):
        self.server.plan = {"body": completion('{"kind":"unsupported","kind":"proposal"}')}
        self.assert_failure("inference_invalid_response")

    def test_markdown_fences_are_not_silently_stripped(self):
        self.server.plan = {"body": completion('```json\n{"kind":"unsupported"}\n```')}
        self.assert_failure("inference_invalid_response")

    def test_model_cannot_add_permission_fields(self):
        output = {**OUTCOME, "approved": True}
        self.server.plan = {"body": completion(json.dumps(output))}
        self.assert_failure("inference_invalid_response")

    def test_oversized_response_is_rejected(self):
        self.server.plan = {"body": b"x", "length": MAX_BYTES + 1}
        self.assert_failure("inference_invalid_response")

    def test_non_json_content_type(self):
        self.server.plan = {"type": "text/html"}
        self.assert_failure("inference_invalid_response")

    def test_large_request_does_not_reach_server(self):
        self.job["context"]["extra"] = "x" * MAX_BYTES
        self.assert_failure("inference_invalid_response")
        self.assertEqual(self.server.requests, [])

    def test_dictation_cannot_be_sent_to_model(self):
        self.job["mode"] = "dictation"
        self.assert_failure("inference_invalid_response")
        self.assertEqual(self.server.requests, [])

    def test_adapter_to_coordinator_to_fixture_effect(self):
        with Sandbox() as sandbox:
            coordinator = SessionCoordinator(sandbox)
            request = coordinator.submit("Create Garden")
            job = coordinator.begin_interpretation(request)
            output = self.adapter.interpret(job)
            self.assertTrue(coordinator.accept_interpretation(job["ticket"], output))
            self.assertEqual(coordinator.execute(request)["state"], "succeeded")
            self.assertTrue((sandbox.documents / "Garden").is_dir())


if __name__ == "__main__":
    unittest.main()
