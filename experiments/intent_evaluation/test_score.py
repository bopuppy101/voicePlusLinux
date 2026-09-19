"""Scorer integrity tests; synthetic predictions are not AI evaluation."""

import copy
from pathlib import Path
import tempfile
import unittest

from score import load_jsonl, score


class ScorerIntegrity(unittest.TestCase):
    def setUp(self):
        self.cases = load_jsonl(Path(__file__).with_name("cases.jsonl"))
        self.predictions = [{"id": c["id"], "output": copy.deepcopy(c["acceptable"][0])}
                            for c in self.cases]

    def test_reference_echo_only_checks_scorer(self):
        report = score(self.cases, self.predictions)
        self.assertTrue(report["complete_match"])
        self.assertEqual(report["matched"], len(self.cases))

    def test_missing_result_keeps_full_denominator(self):
        report = score(self.cases, self.predictions[1:])
        self.assertEqual(report["total"], len(self.cases))
        self.assertEqual(report["matched"], len(self.cases) - 1)
        self.assertEqual(report["missing"], [self.predictions[0]["id"]])
        self.assertFalse(report["complete_match"])

    def test_extra_id_cannot_produce_complete_match(self):
        extra = {"id": "invented-case", "output": {"kind": "unsupported"}}
        report = score(self.cases, self.predictions + [extra])
        self.assertFalse(report["complete_match"])
        self.assertEqual(report["unexpected"], ["invented-case"])

    def test_duplicate_result_is_rejected(self):
        with self.assertRaises(ValueError):
            score(self.cases, self.predictions + self.predictions[:1])

    def test_wrong_argument_is_not_a_match(self):
        self.predictions[0]["output"]["actions"][0]["arguments"]["name"] = "Other"
        report = score(self.cases, self.predictions)
        self.assertEqual(report["matched"], len(self.cases) - 1)
        self.assertEqual(report["mismatched"], [self.predictions[0]["id"]])

    def test_boolean_cannot_replace_string_argument(self):
        self.predictions[0]["output"]["actions"][0]["arguments"]["name"] = True
        report = score(self.cases, self.predictions)
        self.assertEqual(report["invalid_outputs"], [self.predictions[0]["id"]])

    def test_object_key_order_is_irrelevant(self):
        output = self.predictions[0]["output"]
        self.predictions[0]["output"] = dict(reversed(list(output.items())))
        self.assertTrue(score(self.cases, self.predictions)["complete_match"])

    def test_strict_loader_rejects_ambiguous_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "predictions.jsonl"
            for invalid in ('{"id":"a","id":"b"}\n', '{"x":NaN}\n', ''):
                path.write_text(invalid)
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    load_jsonl(path)


if __name__ == "__main__":
    unittest.main()
