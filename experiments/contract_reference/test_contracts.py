"""Boundary checks beyond the readable admission fixtures."""

import copy
import json
from pathlib import Path
import unittest

from check_contracts import reject_constant, strict_object, validate


class ContractBoundaries(unittest.TestCase):
    def setUp(self):
        fixtures = json.loads(Path(__file__).with_name("fixtures.json").read_text())
        self.base = next(case for case in fixtures if case["name"] == "valid-create")

    def decide(self, case):
        return validate(case["session"], case["proposal"], case["grants"])

    def test_validation_does_not_change_input(self):
        before = copy.deepcopy(self.base)
        self.assertEqual(self.decide(self.base)["decision"], "allow")
        self.assertEqual(self.base, before)

    def test_untrusted_top_level_types_fail_without_crashing(self):
        for section in ("session", "proposal", "grants"):
            for value in (None, True, 0, 1.0, "value", [], {}):
                case = copy.deepcopy(self.base)
                case[section] = value
                with self.subTest(section=section, value=value):
                    self.assertEqual(self.decide(case)["decision"], "deny")

    def test_missing_or_extra_fields_fail(self):
        for section in ("session", "proposal"):
            for key in self.base[section]:
                case = copy.deepcopy(self.base)
                del case[section][key]
                with self.subTest(section=section, missing=key):
                    self.assertEqual(self.decide(case)["decision"], "deny")
            case = copy.deepcopy(self.base)
            case[section]["model_claims_authorized"] = True
            self.assertEqual(self.decide(case)["decision"], "deny")

    def test_multibyte_name_limit_is_bytes(self):
        for name, allowed in (("x" * 255, True), ("x" * 256, False),
                              ("é" * 127, True), ("é" * 128, False)):
            case = copy.deepcopy(self.base)
            case["proposal"]["steps"][0]["arguments"]["name"] = name
            with self.subTest(length=len(name.encode("utf-8"))):
                self.assertEqual(self.decide(case)["decision"] == "allow", allowed)

    def test_identity_and_policy_are_rechecked_each_time(self):
        self.assertEqual(self.decide(self.base)["decision"], "allow")
        for field in ("request_revision", "policy_epoch"):
            case = copy.deepcopy(self.base)
            case["session"][field] += 1
            self.assertEqual(self.decide(case)["decision"], "deny")
        self.base["grants"] = []
        self.assertEqual(self.decide(self.base)["code"], "missing_grant")

    def test_no_permission_for_similar_scope(self):
        for root in ("documents-old", "Documents", "documents.private"):
            case = copy.deepcopy(self.base)
            case["proposal"]["steps"][0]["arguments"]["root_id"] = root
            self.assertEqual(self.decide(case)["code"], "missing_grant")

    def test_duplicate_json_keys_are_rejected_at_any_depth(self):
        for payload in ('{"x":1,"x":2}', '{"x":{"allow":false,"allow":true}}'):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                json.loads(payload, object_pairs_hook=strict_object)

    def test_non_json_numeric_constants_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                json.loads(value, parse_constant=reject_constant)


if __name__ == "__main__":
    unittest.main()
