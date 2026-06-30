"""Frozen Gate 2-3P engine constants."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .hashing import sha256_value


@dataclass(frozen=True)
class EngineConfig:
    model_version: str = "3.0.0-research"
    feature_contract_version: str = "2.0.0"
    physical_data_schema_version: str = "1.0.0"
    backtest_protocol_version: str = "1.0.0"
    number_count: int = 45
    pick_count: int = 6
    min_history: int = 299
    prior_concentration: float = 90.0
    recent_windows: tuple[int, ...] = (10, 30, 52, 104)
    ewma_half_life: float = 26.0
    winsor_limit: float = 3.0
    temperature_grid: tuple[float, ...] = (0.05, 0.10, 0.20, 0.50, 1.00)
    weight_decay: float = 0.995
    learning_rate: float = 0.10
    loss_difference_clip: float = 5.0
    minimum_weight: float = 0.01
    candidate_count: int = 5
    candidate_universe_per_component: int = 300
    uniform_candidate_pool: int = 3000
    near_tie_ratio: float = 0.99
    crowd_avoidance_max_share: float = 0.05
    maxt_alpha: float = 0.001
    maxt_min_calibration_series: int = 10_000
    physical_prior_concentration: float = 260.0
    physical_effect_clip: float = 0.35
    physical_candidate_weight_cap: float = 0.10
    physical_min_context_support: float = 20.0
    physical_required_fields: tuple[str, ...] = (
        "machine.machine_id",
        "ball_set.ball_set_id",
        "regime.machine_regime_id",
        "regime.ball_regime_id",
    )
    physical_context_fields: tuple[str, ...] = (
        "machine.machine_id",
        "machine.machine_generation",
        "ball_set.ball_set_id",
        "ball_set.ball_generation",
        "regime.machine_regime_id",
        "regime.ball_regime_id",
        "regime.operating_procedure_regime_id",
        "interaction.machine_ball_set_id",
        "environment.temperature_band",
        "pre_draw_tests.condition_id",
    )
    physical_min_completeness: float = 0.70
    physical_min_weighted_reliability: float = 0.70
    physical_min_source_traceability: float = 0.90
    physical_required_pre_draw_rate: float = 1.00

    @property
    def uniform_number_probability(self) -> float:
        return self.pick_count / self.number_count

    @property
    def config_hash(self) -> str:
        return sha256_value(asdict(self))


DEFAULT_CONFIG = EngineConfig()
