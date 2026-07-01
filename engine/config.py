"""Frozen Gate 2-3P-R3 development constants."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .hashing import sha256_value


@dataclass(frozen=True)
class EngineConfig:
    model_version: str = "4.0.0-research"
    feature_contract_version: str = "3.0.0"
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

    # Legacy 3.0 maxT settings are retained for report reproducibility only.
    maxt_alpha: float = 0.001
    maxt_min_calibration_series: int = 10_000

    # Physical metadata quality contract.
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
        "environment.humidity_band",
        "environment.air_pressure_band",
        "environment.mixing_duration_band",
        "pre_draw_tests.condition_id",
    )
    physical_min_completeness: float = 0.70
    physical_min_weighted_reliability: float = 0.70
    physical_min_source_traceability: float = 0.90
    physical_required_pre_draw_rate: float = 1.00

    # Gate 2-3P-R correction architecture. R3 may select only registered grid values.
    correction_k_global: float = 1040.0
    correction_k_context: float = 520.0
    correction_effect_clip: float = 0.10
    correction_interaction_prior: float = 1040.0
    correction_interaction_effect_clip: float = 0.05
    correction_interaction_min_support: float = 52.0
    correction_activation_e: float = 1000.0
    correction_deactivation_e: float = 100.0
    correction_forced_return_draws: int = 52
    correction_single_field_weight_cap: float = 0.50
    correction_interaction_field_weight_cap: float = 0.25
    correction_transient_family_weight_cap: float = 0.40
    correction_transient_windows: tuple[int, ...] = (13, 26, 52, 104)
    correction_change_max_life: int = 208
    correction_m3_restart_interval: int = 13
    correction_m3_max_restarts: int = 104
    correction_m3_lambda_grid: tuple[float, ...] = (
        -0.20,
        -0.10,
        -0.05,
        -0.02,
        0.02,
        0.05,
        0.10,
        0.20,
    )
    correction_k_m3: float = 520.0
    correction_m3_effect_clip: float = 0.20
    correction_m3_min_support: int = 20
    correction_m3_candidate_weight_cap: float = 0.10
    correction_stable_fields: tuple[str, ...] = (
        "machine.machine_id",
        "machine.machine_generation",
        "ball_set.ball_set_id",
        "ball_set.ball_generation",
        "regime.machine_regime_id",
        "regime.ball_regime_id",
        "regime.operating_procedure_regime_id",
    )
    correction_transient_fields: tuple[str, ...] = (
        "environment.temperature_band",
        "environment.humidity_band",
        "environment.air_pressure_band",
        "environment.mixing_duration_band",
        "pre_draw_tests.condition_id",
    )
    correction_seed_namespaces: tuple[str, ...] = ("DEV", "CAL", "SEALED")

    @property
    def uniform_number_probability(self) -> float:
        return self.pick_count / self.number_count

    @property
    def config_hash(self) -> str:
        return sha256_value(asdict(self))


DEFAULT_CONFIG = EngineConfig()
