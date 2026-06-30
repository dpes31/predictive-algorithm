"""Blockwise exact probability probe for Gate 2-3R synthetic controls."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean
from typing import Mapping, Sequence

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.contracts import DrawRecord
from engine.distributions import FixedSizeDistribution
from engine.experts.persistence import PERSISTENCE_FEATURES
from engine.experts.regime_change import REGIME_FEATURES
from engine.experts.reversal import REVERSAL_FEATURES
from engine.weights import uniform_weights, update_weights

from .calibration import NullCalibration
from .diagnostics import OriginSnapshot


@dataclass(frozen=True)
class ModelProbeSummary:
    mean_delta_log_loss: float
    mean_delta_brier: float
    positive_macro_blocks: int
    block_delta_log_loss: tuple[float, ...]
    final_weight: float


@dataclass(frozen=True)
class ProbeResult:
    model_summaries: Mapping[str, ModelProbeSummary]
    winning_model: str | None
    first_positive_origin: Mapping[str, int | None]
    m3_significant_origins: int
    exploratory_pair_significant_origins: int
    target_pair_significant_origins: int
    final_shadow_weights: Mapping[str, float]
    final_subexpert_weights: Mapping[str, Mapping[str, float]]

    def to_dict(self) -> dict[str, object]:
        return {
            "model_summaries": {
                name: {
                    "mean_delta_log_loss": summary.mean_delta_log_loss,
                    "mean_delta_brier": summary.mean_delta_brier,
                    "positive_macro_blocks": summary.positive_macro_blocks,
                    "block_delta_log_loss": list(summary.block_delta_log_loss),
                    "final_weight": summary.final_weight,
                }
                for name, summary in self.model_summaries.items()
            },
            "winning_model": self.winning_model,
            "first_positive_origin": dict(self.first_positive_origin),
            "m3_significant_origins": self.m3_significant_origins,
            "exploratory_pair_significant_origins": self.exploratory_pair_significant_origins,
            "target_pair_significant_origins": self.target_pair_significant_origins,
            "final_shadow_weights": dict(self.final_shadow_weights),
            "final_subexpert_weights": {
                model: dict(weights) for model, weights in self.final_subexpert_weights.items()
            },
        }


def _temperature_name(feature: str, temperature: float) -> str:
    return f"{feature}@T{temperature:.2f}"


def _expert_names(config: EngineConfig) -> dict[str, tuple[str, ...]]:
    return {
        "M1": tuple(
            _temperature_name(feature, temperature)
            for feature in PERSISTENCE_FEATURES
            for temperature in config.temperature_grid
        ),
        "M2": tuple(
            _temperature_name(feature, temperature)
            for feature, _ in REVERSAL_FEATURES
            for temperature in config.temperature_grid
        ),
        "M3": tuple(REGIME_FEATURES),
    }


def _expert_distributions(
    snapshot: OriginSnapshot,
    change_gate: float,
    config: EngineConfig,
) -> dict[str, dict[str, FixedSizeDistribution]]:
    m1 = {
        _temperature_name(feature, temperature): FixedSizeDistribution(
            tuple(temperature * value for value in snapshot.number_features[feature]),
            config.pick_count,
        )
        for feature in PERSISTENCE_FEATURES
        for temperature in config.temperature_grid
    }
    m2 = {
        _temperature_name(feature, temperature): FixedSizeDistribution(
            tuple(sign * temperature * value for value in snapshot.number_features[feature]),
            config.pick_count,
        )
        for feature, sign in REVERSAL_FEATURES
        for temperature in config.temperature_grid
    }
    m3 = {
        feature: FixedSizeDistribution(
            tuple(change_gate * value for value in snapshot.number_features[feature]),
            config.pick_count,
        )
        for feature in REGIME_FEATURES
    }
    return {"M1": m1, "M2": m2, "M3": m3}


def _mixture_probability(
    distributions: Mapping[str, FixedSizeDistribution],
    weights: Mapping[str, float],
    numbers: Sequence[int],
) -> tuple[float, dict[str, float]]:
    probabilities = {
        name: distribution.joint_probability(numbers)
        for name, distribution in distributions.items()
    }
    mixture = sum(weights[name] * probability for name, probability in probabilities.items())
    return mixture, probabilities


def _mixture_marginals(
    marginals: Mapping[str, Sequence[float]],
    weights: Mapping[str, float],
) -> list[float]:
    names = tuple(marginals)
    return [
        sum(weights[name] * marginals[name][index] for name in names)
        for index in range(len(next(iter(marginals.values()))))
    ]


def _brier(probabilities: Sequence[float], numbers: Sequence[int]) -> float:
    selected = set(numbers)
    return fmean(
        (probability - (1.0 if index + 1 in selected else 0.0)) ** 2
        for index, probability in enumerate(probabilities)
    )


def _macro_block(draw_no: int) -> int:
    if draw_no <= 609:
        return 0
    if draw_no <= 919:
        return 1
    return 2


def _strict_winner(summaries: Mapping[str, ModelProbeSummary]) -> str | None:
    names = ("M1", "M2", "M3")
    ordered = sorted(
        ((summaries[name].mean_delta_log_loss, name) for name in names),
        reverse=True,
    )
    best_score, best_name = ordered[0]
    second_score = ordered[1][0]
    if best_score <= 0 or best_score <= second_score + 1e-15:
        return None
    return best_name


def run_blockwise_probe(
    records: Sequence[DrawRecord],
    snapshots: Sequence[OriginSnapshot],
    calibration: NullCalibration,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
) -> ProbeResult:
    if not snapshots:
        raise ValueError("snapshots must not be empty")
    by_draw = {record.draw_no: record for record in records}
    uniform_joint = 1.0 / math.comb(config.number_count, config.pick_count)
    uniform_loss = -math.log(uniform_joint)
    uniform_marginals = [config.uniform_number_probability] * config.number_count

    names = _expert_names(config)
    subweights = {model: uniform_weights(expert_names) for model, expert_names in names.items()}
    shadow_weights = {"M0": 0.25, "M1": 0.25, "M2": 0.25, "M3": 0.25}
    delta_losses = {name: [] for name in ("M1", "M2", "M3", "SHADOW")}
    delta_briers = {name: [] for name in ("M1", "M2", "M3", "SHADOW")}
    macro_losses = {name: [[], [], []] for name in delta_losses}
    first_positive_origin: dict[str, int | None] = {name: None for name in ("M1", "M2", "M3")}
    m3_significant_origins = 0
    exploratory_pair_significant_origins = 0
    target_pair_significant_origins = 0

    for snapshot in snapshots:
        gate_result = calibration.evaluate(snapshot)
        if gate_result.significant:
            m3_significant_origins += 1
        if gate_result.exploratory_pair_tail_probability <= calibration.alpha:
            exploratory_pair_significant_origins += 1
        if gate_result.target_pair_tail_probability <= calibration.alpha:
            target_pair_significant_origins += 1

        expert_groups = _expert_distributions(snapshot, gate_result.change_gate, config)
        expert_marginals: dict[str, dict[str, list[float]]] = {}
        for model_name, distributions in expert_groups.items():
            expert_marginals[model_name] = {
                name: list(distribution.marginal_probabilities().values())
                for name, distribution in distributions.items()
            }

        block_model_deltas = {name: [] for name in ("M1", "M2", "M3")}
        for draw_no in range(snapshot.forecast_start, snapshot.forecast_end + 1):
            record = by_draw[draw_no]
            model_probabilities: dict[str, float] = {}
            model_losses: dict[str, float] = {}
            model_marginals: dict[str, list[float]] = {}
            expert_losses: dict[str, dict[str, float]] = {}

            for model_name, distributions in expert_groups.items():
                probability, individual = _mixture_probability(
                    distributions,
                    subweights[model_name],
                    record.numbers,
                )
                model_probabilities[model_name] = probability
                model_losses[model_name] = -math.log(probability)
                expert_losses[model_name] = {
                    name: -math.log(value) for name, value in individual.items()
                }
                model_marginals[model_name] = _mixture_marginals(
                    expert_marginals[model_name],
                    subweights[model_name],
                )

            shadow_probability = (
                shadow_weights["M0"] * uniform_joint
                + sum(shadow_weights[name] * model_probabilities[name] for name in ("M1", "M2", "M3"))
            )
            shadow_loss = -math.log(shadow_probability)
            shadow_marginals = [
                shadow_weights["M0"] * uniform_marginals[index]
                + sum(shadow_weights[name] * model_marginals[name][index] for name in ("M1", "M2", "M3"))
                for index in range(config.number_count)
            ]
            uniform_brier = _brier(uniform_marginals, record.numbers)

            for model_name in ("M1", "M2", "M3"):
                delta = uniform_loss - model_losses[model_name]
                delta_losses[model_name].append(delta)
                block_model_deltas[model_name].append(delta)
                macro_losses[model_name][_macro_block(draw_no)].append(delta)
                delta_briers[model_name].append(
                    uniform_brier - _brier(model_marginals[model_name], record.numbers)
                )
                subweights[model_name] = update_weights(
                    subweights[model_name],
                    expert_losses[model_name],
                    baseline_loss=uniform_loss,
                    config=config,
                )

            shadow_delta = uniform_loss - shadow_loss
            delta_losses["SHADOW"].append(shadow_delta)
            macro_losses["SHADOW"][_macro_block(draw_no)].append(shadow_delta)
            delta_briers["SHADOW"].append(uniform_brier - _brier(shadow_marginals, record.numbers))
            shadow_weights = update_weights(
                shadow_weights,
                {
                    "M0": uniform_loss,
                    "M1": model_losses["M1"],
                    "M2": model_losses["M2"],
                    "M3": model_losses["M3"],
                },
                baseline_loss=uniform_loss,
                config=config,
            )

        for model_name, values in block_model_deltas.items():
            if first_positive_origin[model_name] is None and values and fmean(values) > 0:
                first_positive_origin[model_name] = snapshot.origin_draw_no

    summaries: dict[str, ModelProbeSummary] = {}
    for model_name in ("M1", "M2", "M3", "SHADOW"):
        block_means = tuple(fmean(values) if values else 0.0 for values in macro_losses[model_name])
        final_weight = shadow_weights.get(model_name, 0.0) if model_name != "SHADOW" else 1.0
        summaries[model_name] = ModelProbeSummary(
            mean_delta_log_loss=fmean(delta_losses[model_name]),
            mean_delta_brier=fmean(delta_briers[model_name]),
            positive_macro_blocks=sum(value > 0 for value in block_means),
            block_delta_log_loss=block_means,
            final_weight=final_weight,
        )

    return ProbeResult(
        model_summaries=summaries,
        winning_model=_strict_winner(summaries),
        first_positive_origin=first_positive_origin,
        m3_significant_origins=m3_significant_origins,
        exploratory_pair_significant_origins=exploratory_pair_significant_origins,
        target_pair_significant_origins=target_pair_significant_origins,
        final_shadow_weights=shadow_weights,
        final_subexpert_weights=subweights,
    )
