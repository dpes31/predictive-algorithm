"""Frozen configuration for research-ensemble-implementation-1.0.0."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from engine.config import EngineConfig
from engine.hashing import sha256_value

ABLATION_IDS = (
    "CONTROL_M0",
    "HISTORICAL_ONLY",
    "HYPOTHESIS_ONLY",
    "PHYSICAL_ONLY",
    "ENSEMBLE_FULL",
    "ENSEMBLE_MINUS_M1",
    "ENSEMBLE_MINUS_M2",
    "ENSEMBLE_MINUS_M3",
    "ENSEMBLE_MINUS_HYPOTHESES",
    "ENSEMBLE_MINUS_PHYSICAL",
)


@dataclass(frozen=True)
class ResearchEnsembleConfig:
    integration_contract_version: str = "research-ensemble-spec-1.0.0"
    implementation_contract_version: str = "research-ensemble-implementation-1.0.0"
    model_version: str = "6.0.0-research"
    score_contract_version: str = "score-45-1.0.0"
    hypothesis_registry_contract: str = "hypothesis-registry-1.0.0"
    user_input_registry_contract: str = "user-input-registry-1.0.0"
    physical_adapter_contract: str = "user-physical-adapter-1.0.0"
    output_schema_version: str = "research-ensemble-output-1.0.0"
    number_count: int = 45
    pick_count: int = 6
    min_history: int = 299
    prior_concentration: float = 90.0
    recent_windows: tuple[int, ...] = (10, 30, 52, 104)
    ewma_half_life: float = 26.0
    winsor_limit: float = 3.0
    weight_decay: float = 0.995
    learning_rate: float = 0.10
    loss_difference_clip: float = 5.0
    minimum_weight: float = 0.01
    candidate_count: int = 5
    candidate_universe_per_component: int = 300
    uniform_candidate_pool: int = 3000
    near_tie_ratio: float = 0.99
    crowd_avoidance_max_share: float = 0.05
    historical_budget: float = 0.60
    single_hypothesis_cap: float = 0.10
    hypothesis_total_cap: float = 0.25
    single_physical_field_cap: float = 0.05
    physical_total_cap: float = 0.15
    final_logit_abs_cap: float = 0.35
    uncertainty_abs_cap: float = 0.75
    historical_weight_support_draws: int = 52

    @property
    def config_hash(self) -> str:
        return sha256_value(asdict(self))

    @property
    def engine_config(self) -> EngineConfig:
        return EngineConfig(
            model_version=self.model_version,
            feature_contract_version=self.score_contract_version,
            number_count=self.number_count,
            pick_count=self.pick_count,
            min_history=self.min_history,
            prior_concentration=self.prior_concentration,
            recent_windows=self.recent_windows,
            ewma_half_life=self.ewma_half_life,
            winsor_limit=self.winsor_limit,
            weight_decay=self.weight_decay,
            learning_rate=self.learning_rate,
            loss_difference_clip=self.loss_difference_clip,
            minimum_weight=self.minimum_weight,
            candidate_count=self.candidate_count,
            candidate_universe_per_component=self.candidate_universe_per_component,
            uniform_candidate_pool=self.uniform_candidate_pool,
            near_tie_ratio=self.near_tie_ratio,
            crowd_avoidance_max_share=self.crowd_avoidance_max_share,
        )

DEFAULT_INTEGRATION_CONFIG = ResearchEnsembleConfig()
