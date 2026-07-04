"""Data contracts used by the Gate 2 research engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class DrawRecord:
    draw_no: int
    draw_date: str
    numbers: tuple[int, ...]
    bonus_number: int | None = None
    verification_status: str = "synthetic"
    locked: bool = False
    source: str = "synthetic"
    checksum: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "DrawRecord":
        record = cls(
            draw_no=int(value["draw_no"]),
            draw_date=str(value["draw_date"]),
            numbers=tuple(int(number) for number in value["numbers"]),
            bonus_number=(None if value.get("bonus_number") is None else int(value["bonus_number"])),
            verification_status=str(value.get("verification_status", "unknown")),
            locked=bool(value.get("locked", False)),
            source=str(value.get("source", "unknown")),
            checksum=(None if value.get("checksum") is None else str(value["checksum"])),
        )
        record.validate()
        return record

    def validate(self) -> None:
        if self.draw_no < 1:
            raise ValueError("draw_no must be positive")
        if len(self.numbers) != 6 or len(set(self.numbers)) != 6:
            raise ValueError(f"draw {self.draw_no}: numbers must contain six unique values")
        if tuple(sorted(self.numbers)) != self.numbers:
            raise ValueError(f"draw {self.draw_no}: numbers must be sorted")
        if not all(1 <= number <= 45 for number in self.numbers):
            raise ValueError(f"draw {self.draw_no}: number outside 1..45")
        if self.bonus_number is not None:
            if not 1 <= self.bonus_number <= 45:
                raise ValueError(f"draw {self.draw_no}: bonus outside 1..45")
            if self.bonus_number in self.numbers:
                raise ValueError(f"draw {self.draw_no}: bonus duplicates a main number")


@dataclass(frozen=True)
class FeatureSnapshot:
    target_draw_no: int
    input_last_draw: int
    data_version: str
    feature_contract_version: str
    number_features: Mapping[int, Mapping[str, float]]
    global_features: Mapping[str, float | bool | str]
    snapshot_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_draw_no": self.target_draw_no,
            "input_last_draw": self.input_last_draw,
            "data_version": self.data_version,
            "feature_contract_version": self.feature_contract_version,
            "number_features": {
                str(number): dict(features) for number, features in self.number_features.items()
            },
            "global_features": dict(self.global_features),
            "snapshot_hash": self.snapshot_hash,
        }


@dataclass(frozen=True)
class CandidateSet:
    rank: int
    numbers: tuple[int, ...]
    joint_probability: float
    lift_vs_uniform: float
    credible_interval_95: tuple[float, float] | None = None
    crowd_avoidance_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionResult:
    target_draw_no: int
    model_version: str
    data_version: str
    gate_state: str
    advantage_status: str
    model_weights: Mapping[str, float]
    shadow_weights: Mapping[str, float]
    candidate_sets: Sequence[CandidateSet]
    generated_at: str
    input_last_draw: int
    seed: str
    prediction_hash: str
    research_only: bool = True
    public_release_allowed: bool = False
    uncertainty_status: str = "pending_gate2_3"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_draw_no": self.target_draw_no,
            "model_version": self.model_version,
            "data_version": self.data_version,
            "gate_state": self.gate_state,
            "advantage_status": self.advantage_status,
            "model_weights": dict(self.model_weights),
            "shadow_weights": dict(self.shadow_weights),
            "candidate_sets": [candidate.to_dict() for candidate in self.candidate_sets],
            "generated_at": self.generated_at,
            "input_last_draw": self.input_last_draw,
            "seed": self.seed,
            "prediction_hash": self.prediction_hash,
            "research_only": self.research_only,
            "public_release_allowed": self.public_release_allowed,
            "uncertainty_status": self.uncertainty_status,
            "metadata": dict(self.metadata),
        }
