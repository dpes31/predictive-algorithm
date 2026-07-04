from __future__ import annotations

from typing import Mapping

from ..config import EngineConfig
from ..contracts import FeatureSnapshot
from ..distributions import FixedSizeDistribution, MixtureDistribution

REGIME_FEATURES = (
    "z_shift_52",
    "z_shift_104",
    "z_ewma_minus_long",
    "signed_cusum_score",
)


def build_regime_change_subexperts(
    snapshot: FeatureSnapshot,
    config: EngineConfig,
) -> Mapping[str, FixedSizeDistribution]:
    change_gate = float(snapshot.global_features.get("change_gate", 0.0))
    return {
        feature: FixedSizeDistribution(
            tuple(
                change_gate * snapshot.number_features[number][feature]
                for number in range(1, config.number_count + 1)
            ),
            config.pick_count,
        )
        for feature in REGIME_FEATURES
    }


def build_regime_change_model(
    snapshot: FeatureSnapshot,
    config: EngineConfig,
    weights: Mapping[str, float] | None = None,
) -> MixtureDistribution:
    experts = build_regime_change_subexperts(snapshot, config)
    selected = weights or {name: 1.0 for name in experts}
    return MixtureDistribution(
        tuple(experts[name] for name in experts),
        tuple(float(selected.get(name, 0.0)) for name in experts),
    )
