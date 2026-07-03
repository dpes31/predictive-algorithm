from __future__ import annotations

import unittest

from product_closeout.compare import compare_results
from product_closeout.harness import run_internal_qa


class ProductCloseoutC2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_internal_qa()
        cls.canonical = cls.result["canonical_result"]

    def test_candidate_status(self) -> None:
        self.assertEqual(self.canonical["status"], "PRODUCT_CLOSEOUT_QA_PASS_CANDIDATE")
        self.assertEqual(self.canonical["decision_reasons"], [])

    def test_all_internal_checks_pass(self) -> None:
        failures = [
            name
            for name, value in self.canonical["checks"].items()
            if not bool(value.get("pass"))
        ]
        self.assertEqual(failures, [])

    def test_fixed_product_disclosure(self) -> None:
        self.assertIs(self.canonical["statistical_edge"], False)
        self.assertEqual(self.canonical["reason"], "no_validated_nonuniform_signal")
        self.assertIs(self.canonical["research_only"], True)
        self.assertIs(self.canonical["public_release_allowed"], False)

    def test_repeat_hash_is_identical(self) -> None:
        repeat = run_internal_qa()
        self.assertEqual(self.result["canonical_result_hash"], repeat["canonical_result_hash"])

    def test_compare_requires_matching_results(self) -> None:
        self.assertTrue(self.result["canonical_result_hash"])
        self.assertEqual(self.canonical["contract_version"], "product-closeout-qa-1.0.0")


if __name__ == "__main__":
    unittest.main()
