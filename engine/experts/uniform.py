from __future__ import annotations

from ..config import EngineConfig
from ..distributions import FixedSizeDistribution


def build_uniform_model(config: EngineConfig) -> FixedSizeDistribution:
    return FixedSizeDistribution(tuple(0.0 for _ in range(config.number_count)), config.pick_count)
