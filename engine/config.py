"""Frozen Gate 2-3P-R2 correction-engine constants."""

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

    # 4.0 M3 anytime-valid restart-mixture change e-process.
    m3_activation_evidence: float = 1000.0
    m3_deactivation_evidence: float = 100.0
    m3_betting_fractions: tuple[float, ...] = (-0.20, -0.10, -0.05, -0.02, 0.02, 0.05, 0.10, 0.20)
    m3_restart_stride: int = 13
    m3_max_restarts: int = 104
    m3_max_life: int = 208
    m3_candidate_weight_cap: float = 0.10

    # 4.0 M4 hierarchical physical-evidence contract.
    physical_k_global: float = 520.0
    physical_k_context: float = 260.0
    physical_effect_clip: float = 0.20
    physical_candidate_weight_cap: float = 0.10
    physical_interaction_weight_cap: float = 0.25
    physical_field_weight_cap: float = 0.50
    physical_transient_family_cap: float = 0.40
    physical_min_context_support: float = 20.0
    physical_min_interaction_support: float = 52.0
    physical_activation_evidence: float = 1000.0
    physical_deactivation_evidence: float = 100.0
    physical_transient_restarts: tuple[int, ...] = (13, 26, 52, 104)
    physical_transient_expiry: int = 104
    physical_hard_return_draws: int = 52
    physical_return_contract_draws: int = 208

    physical_required_fields: tuple[str, ...] = (
        "machine.machine_id",
        "ball_set.ball_set_id",
        "regime.machine_regime_id",
        "regime.ball_regime_id",
    )
    physical_stable_fields: tuple[str, ...] = (
        "machine.machine_id",
        "machine.machine_generation",
        "ball_set.ball_set_id",
        "ball_set.ball_generation",
        "regime.machine_regime_id",
        "regime.ball_regime_id",
        "interaction.machine_ball_set_id",
    )
    physical_transient_fields: tuple[str, ...] = (
        "environment.temperature_band",
        "environment.humidity_band",
        "environment.air_pressure_band",
        "environment.mixing_duration_band",
        "pre_draw_tests.condition_id",
    )
    physical_context_fields: tuple[str, ...] = physical_stable_fields + physical_transient_fields
    physical_min_completeness: float = 0.70
    physical_min_weighted_reliability: float = 0.70
    physical_min_source_traceability: float = 0.90
    physical_required_pre_draw_rate: float = 1.00

    # Seed namespace separation for development, calibration and sealed validation.
    dev_seed_namespace: str = "GATE2P-R-DEV"
    calibration_seed_namespace: str = "GATE2P-R-CAL"
    sealed_seed_namespace: str = "GATE2P-R-SEALED"

    @property
    def uniform_number_probability(self) -> float:
        return self.pick_count / self.number_count

    @property
    def config_hash(self) -> str:
        return sha256_value(asdict(self))


DEFAULT_CONFIG = EngineConfig()
