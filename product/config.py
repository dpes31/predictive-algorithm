"""Frozen Product Gate P1 constants."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from engine.hashing import sha256_value


PRODUCT_CONTRACT_VERSION = "product-release-candidate-1.0.0"
MODEL_VERSION = "5.0.0-research-m0-product"
ENGINE_CORE_VERSION = "2.0.0-research"
FEATURE_CONTRACT_VERSION = "1.0.0"
CANDIDATE_CONTRACT_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
DATASET_VERSION = "draws-2026.06.27-r1"
EXPECTED_DATA_HASH = "57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1"


@dataclass(frozen=True)
class ProductConfig:
    number_count: int = 45
    pick_count: int = 6
    candidate_count: int = 5
    uniform_candidate_pool: int = 3000
    final_distribution: str = "M0_ONLY"

    @property
    def effective_payload(self) -> dict[str, int | str]:
        return {
            "candidate_count": self.candidate_count,
            "final_distribution": self.final_distribution,
            "number_count": self.number_count,
            "pick_count": self.pick_count,
            "uniform_candidate_pool": self.uniform_candidate_pool,
        }

    @property
    def config_hash(self) -> str:
        return sha256_value(self.effective_payload)


DEFAULT_PRODUCT_CONFIG = ProductConfig()
PRODUCT_WEIGHTS = {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0}


def product_config_dict() -> dict[str, object]:
    return asdict(DEFAULT_PRODUCT_CONFIG)
