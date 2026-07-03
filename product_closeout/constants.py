"""Frozen Product Closeout Gate C2 constants."""

from __future__ import annotations

QA_CONTRACT_VERSION = "product-closeout-qa-1.0.0"
SPEC_CONTRACT_VERSION = "product-closeout-spec-1.0.0"
BASE_COMMIT = "2f6d42fad4517b744f33132ad7ad1061678e6340"
A4_DRAFT_PR = 51
A4_CANONICAL_RESULT_HASH = "c886f07c2fa7fd01cfa49d2d0e4174d6c9802ac0856aff2fd13d54da44fde3b7"
A4_SNAPSHOT_PATH = "reports/product_closeout_c2_a4_preservation_snapshot.json"
FIXED_TARGET = 1231
FIXED_GENERATED_AT = "2026-07-03T00:00:00Z"
EXPECTED_RECORD_COUNT = 1230
EXPECTED_FIRST_DRAW = 1
EXPECTED_LAST_DRAW = 1230
EXPECTED_VERIFICATION_STATUS = "auto_checked"
EXPECTED_WEIGHTS = {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0}

MODEL_SOURCE_PATHS = (
    "engine/distributions.py",
    "engine/elementary_symmetric.py",
    "engine/candidate_optimizer.py",
    "engine/hashing.py",
    "product/config.py",
    "product/contracts.py",
    "product/run_prediction.py",
)

IMMUTABLE_BASE_PATHS = (
    "data/draws.json",
    "data/source_manifest.json",
    "data/checksums.sha256",
    "reports/data_integrity.json",
    "engine/contracts.py",
    "engine/data_loader.py",
    "engine/config.py",
    "engine/elementary_symmetric.py",
    "engine/distributions.py",
    "engine/candidate_optimizer.py",
    "engine/hashing.py",
    "product/config.py",
    "product/contracts.py",
    "product/run_prediction.py",
    "schemas/product_prediction.schema.json",
    "release/assembly_manifest.json",
    "release/rollback_manifest.json",
    "reports/product_p1_acceptance.json",
    "reports/product_p1_acceptance_lock.json",
    "docs/ALGORITHM_INTEGRATION_A1_SPEC.md",
    "docs/ALGORITHM_INTEGRATION_A1_REGISTRIES.md",
    "docs/ALGORITHM_INTEGRATION_A1_ACCEPTANCE.md",
    "reports/algorithm_integration_a1_spec_report.json",
    "reports/algorithm_integration_a1_spec_lock.json",
    "reports/ALGORITHM_INTEGRATION_A2_STATUS.md",
    "reports/algorithm_integration_a2_implementation.json",
    "reports/algorithm_integration_a2_implementation_lock.json",
    "release/algorithm_integration_a2_rollback_manifest.json",
    "docs/ALGORITHM_INTEGRATION_A3_EVALUATION_SPEC.md",
    "docs/ALGORITHM_INTEGRATION_A3_METRICS.md",
    "docs/ALGORITHM_INTEGRATION_A3_ACCEPTANCE.md",
    "reports/algorithm_integration_a3_spec_report.json",
    "reports/algorithm_integration_a3_spec_lock.json",
    "docs/PRODUCT_CLOSEOUT_M0_SPEC.md",
    "reports/product_closeout_spec_report.json",
    "reports/product_closeout_spec_lock.json",
    "reports/gate2_3p3_full_summary.md",
    "reports/gate2_3p_r3_dev_lock.json",
    "reports/gate2_3p_r3m2_oracle_dev_lock.json",
    "reports/gate2_3p_r3m3_predictable_group_dev_lock.json",
)

PROHIBITED_NETWORK_IMPORTS = {
    "aiohttp",
    "ftplib",
    "http",
    "httpx",
    "requests",
    "socket",
    "urllib",
    "urllib3",
}
