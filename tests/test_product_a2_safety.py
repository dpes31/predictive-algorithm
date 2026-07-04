from __future__ import annotations
import json
import pathlib
import unittest
from research_ensemble.config import ABLATION_IDS
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import synthetic_records

ROOT = pathlib.Path(__file__).resolve().parents[1]


class A2SafetyTests(unittest.TestCase):
    def test_ablation_manifest_is_complete_and_deterministic(self) -> None:
        records = synthetic_records()
        first = build_score_bundle(records, target_draw_no=len(records) + 1, data_version="synthetic-a2")
        second = build_score_bundle(records, target_draw_no=len(records) + 1, data_version="synthetic-a2")
        self.assertEqual(set(first["ablations"]), set(ABLATION_IDS))
        self.assertEqual(first["ablation_manifest_hash"], second["ablation_manifest_hash"])
        self.assertTrue(first["ablations"]["CONTROL_M0"]["run_abstained"])

    def test_no_network_client_dependency(self) -> None:
        forbidden = ("import requests", "import httpx", "import urllib", "import socket")
        for path in (ROOT / "research_ensemble").glob("*.py"):
            source = path.read_text(encoding="utf-8")
            self.assertFalse(any(token in source for token in forbidden), path.name)

    def test_frozen_predictable_group_lock_is_unchanged(self) -> None:
        value = json.loads((ROOT / "reports/gate2_3p_r3m3_predictable_group_dev_lock.json").read_text(encoding="utf-8"))
        self.assertEqual(value["decision"], "PREDICTABLE_GROUP_FAIL")
        self.assertEqual(value["implementation_commit"], "156f286db9242f0e8f45c0bda9246e57d22d57da")
        self.assertEqual(value["report_hash"], "9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37")
        self.assertEqual(value["lock_hash"], "e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04")


if __name__ == "__main__":
    unittest.main()
