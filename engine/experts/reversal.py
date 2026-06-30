from __future__ import annotations

from typing import Mapping

from ..config import EngineConfig
from ..contracts import FeatureSnapshot
from ..distributions import FixedSizeDistribution, MixtureDistribution

REVERSAL_FEATURES: tuple[tuple[str, float], ...] = (
    ("z_recent_10", -1.0),
    ("z_recent_30", -1.0),
    ("z_recent_52", -1.0),
    ("z_recent_104", -1.0),
    ("z_trend_10_52", -1.0),
    ("z_trend_30_104", -1.0),
    ("z_gap", 1.0),
)


def build_reversal_subexperts(
    snapshot: FeatureSnapshot,
    config: EngineConfig,
) -> Mapping[str, FixedSizeDistribution]:
    return {
        feature: FixedSizeDistribution(
            tuple(sign * snapshot.number_features[number][feature] for number in range(1, config.number_count + 1)),
            config.pick_count,
        )
        for feature, sign in REVERSAL_FEATURES
    }


def build_reversal_model(
    snapshot: FeatureSnapshot,
    config: EngineConfig,
    weights: Mapping[str, float] | None = None,
) -> MixtureDistribution:
    experts = build_reversal_subexperts(snapshot, config)
    selected = weights or {name: 1.0 for name in experts}
    return MixtureDistribution(
        tuple(experts[name] for name in experts),
        tuple(float(selected.get(name, 0.0)) for name in experts),
    )
