"""Frozen Gate 2 engine constants."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .hashing import sha256_value


@dataclass(frozen=True)
class EngineConfig:
    model_version: str = "2.1.0-research"
    feature_contract_version: str = "1.1.0"
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

    @property
    def uniform_number_probability(self) -> float:
        return self.pick_count / self.number_count

    @property
    def config_hash(self) -> str:
        return sha256_value(asdict(self))


DEFAULT_CONFIG = EngineConfig()
