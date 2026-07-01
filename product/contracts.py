"""Product Gate P1 output contracts and invariant checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ProductCandidate:
    rank: int
    numbers: tuple[int, ...]
    joint_probability: float
    lift_vs_uniform: float

    def validate(self) -> None:
        if self.rank not in range(1, 6):
            raise ValueError("candidate rank must be in 1..5")
        if len(self.numbers) != 6 or len(set(self.numbers)) != 6:
            raise ValueError("candidate must contain six unique numbers")
        if tuple(sorted(self.numbers)) != self.numbers:
            raise ValueError("candidate numbers must be ascending")
        if not all(1 <= number <= 45 for number in self.numbers):
            raise ValueError("candidate number outside 1..45")
        if self.joint_probability <= 0:
            raise ValueError("candidate probability must be positive")
        if self.lift_vs_uniform != 1.0:
            raise ValueError("M0 product lift must equal 1.0")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "rank": self.rank,
            "numbers": list(self.numbers),
            "joint_probability": self.joint_probability,
            "lift_vs_uniform": self.lift_vs_uniform,
        }


@dataclass(frozen=True)
class ProductPrediction:
    schema_version: str
    contract_version: str
    target_draw_no: int
    input_last_draw: int
    generated_at: str
    research_only: bool
    public_release_allowed: bool
    statistical_edge: bool
    reason: str
    advantage_status: str
    final_distribution: str
    product_weights: Mapping[str, float]
    candidate_sets: Sequence[ProductCandidate]
    versions: Mapping[str, str]
    hashes: Mapping[str, str]
    seed: str
    diagnostics: Mapping[str, Any]
    limitations: Sequence[str]

    def validate(self) -> None:
        if self.target_draw_no < 2:
            raise ValueError("target_draw_no must be at least 2")
        if self.input_last_draw != self.target_draw_no - 1:
            raise ValueError("input_last_draw must equal target_draw_no - 1")
        if self.research_only is not True:
            raise ValueError("research_only must be true")
        if self.public_release_allowed is not False:
            raise ValueError("public_release_allowed must be false")
        if self.statistical_edge is not False:
            raise ValueError("statistical_edge must be false")
        if self.reason != "no_validated_nonuniform_signal":
            raise ValueError("unexpected reason")
        if self.advantage_status != "통계적 우위 없음":
            raise ValueError("unexpected advantage status")
        if self.final_distribution != "M0_ONLY":
            raise ValueError("final_distribution must be M0_ONLY")
        if dict(self.product_weights) != {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0}:
            raise ValueError("product weights must be exactly M0-only")
        if len(self.candidate_sets) != 5:
            raise ValueError("exactly five candidate sets are required")
        for candidate in self.candidate_sets:
            candidate.validate()
        ranks = [candidate.rank for candidate in self.candidate_sets]
        if sorted(ranks) != [1, 2, 3, 4, 5]:
            raise ValueError("candidate ranks must be exactly 1..5")
        combinations = [candidate.numbers for candidate in self.candidate_sets]
        if len(combinations) != len(set(combinations)):
            raise ValueError("candidate sets must be distinct")
        for value in self.hashes.values():
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise ValueError("hashes must be lowercase SHA-256 hex")
        if len(self.seed) != 64 or any(character not in "0123456789abcdef" for character in self.seed):
            raise ValueError("seed must be lowercase SHA-256 hex")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "contract_version": self.contract_version,
            "target_draw_no": self.target_draw_no,
            "input_last_draw": self.input_last_draw,
            "generated_at": self.generated_at,
            "research_only": self.research_only,
            "public_release_allowed": self.public_release_allowed,
            "statistical_edge": self.statistical_edge,
            "reason": self.reason,
            "advantage_status": self.advantage_status,
            "final_distribution": self.final_distribution,
            "product_weights": dict(self.product_weights),
            "candidate_sets": [candidate.to_dict() for candidate in self.candidate_sets],
            "versions": dict(self.versions),
            "hashes": dict(self.hashes),
            "seed": self.seed,
            "diagnostics": dict(self.diagnostics),
            "limitations": list(self.limitations),
        }
