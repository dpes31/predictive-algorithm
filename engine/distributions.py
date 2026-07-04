"""Exact fixed-size product distributions and finite mixtures."""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from .elementary_symmetric import elementary_symmetric, inclusion_probabilities


class CombinationDistribution(Protocol):
    pick_count: int

    def joint_probability(self, numbers: Sequence[int]) -> float: ...
    def joint_log_probability(self, numbers: Sequence[int]) -> float: ...
    def marginal_probabilities(self) -> Mapping[int, float]: ...
    def top_combinations(self, limit: int) -> list[tuple[int, ...]]: ...


@dataclass(frozen=True)
class FixedSizeDistribution:
    logits: tuple[float, ...]
    pick_count: int = 6
    labels: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if not self.logits:
            raise ValueError("logits must not be empty")
        if not 0 < self.pick_count <= len(self.logits):
            raise ValueError("invalid pick_count")
        if not all(math.isfinite(logit) for logit in self.logits):
            raise ValueError("all logits must be finite")
        labels = self.labels or tuple(range(1, len(self.logits) + 1))
        if len(labels) != len(self.logits) or len(set(labels)) != len(labels):
            raise ValueError("labels must be unique and match logits")
        object.__setattr__(self, "labels", labels)

    @property
    def shifted_weights(self) -> tuple[float, ...]:
        maximum = max(self.logits)
        return tuple(math.exp(logit - maximum) for logit in self.logits)

    @property
    def log_normalizer(self) -> float:
        maximum = max(self.logits)
        normalizer = elementary_symmetric(self.shifted_weights, self.pick_count)
        return self.pick_count * maximum + math.log(normalizer)

    @property
    def is_uniform(self) -> bool:
        return max(self.logits) - min(self.logits) <= 1e-15

    def _indices(self, numbers: Sequence[int]) -> tuple[int, ...]:
        values = tuple(int(number) for number in numbers)
        if len(values) != self.pick_count or len(set(values)) != self.pick_count:
            raise ValueError("combination must have pick_count unique labels")
        label_to_index = {label: index for index, label in enumerate(self.labels or ())}
        try:
            return tuple(label_to_index[number] for number in values)
        except KeyError as exc:
            raise ValueError(f"unknown label: {exc.args[0]}") from exc

    def joint_log_probability(self, numbers: Sequence[int]) -> float:
        return sum(self.logits[index] for index in self._indices(numbers)) - self.log_normalizer

    def joint_probability(self, numbers: Sequence[int]) -> float:
        return math.exp(self.joint_log_probability(numbers))

    def marginal_probabilities(self) -> Mapping[int, float]:
        probabilities = inclusion_probabilities(self.shifted_weights, self.pick_count)
        return {label: probability for label, probability in zip(self.labels or (), probabilities, strict=True)}

    def top_combinations(self, limit: int) -> list[tuple[int, ...]]:
        if limit <= 0:
            return []
        ranked = sorted(range(len(self.logits)), key=lambda index: (-self.logits[index], self.labels[index]))
        start = tuple(range(self.pick_count))
        heap: list[tuple[float, tuple[int, ...]]] = [
            (-sum(self.logits[ranked[position]] for position in start), start)
        ]
        visited = {start}
        output: list[tuple[int, ...]] = []

        while heap and len(output) < limit:
            _, positions = heapq.heappop(heap)
            output.append(tuple(sorted(self.labels[ranked[position]] for position in positions)))
            for slot in range(self.pick_count - 1, -1, -1):
                candidate = list(positions)
                candidate[slot] += 1
                if candidate[slot] >= len(ranked):
                    continue
                if slot < self.pick_count - 1 and candidate[slot] >= candidate[slot + 1]:
                    continue
                candidate_tuple = tuple(candidate)
                if candidate_tuple in visited:
                    continue
                visited.add(candidate_tuple)
                score = sum(self.logits[ranked[position]] for position in candidate_tuple)
                heapq.heappush(heap, (-score, candidate_tuple))
        return output


@dataclass(frozen=True)
class MixtureDistribution:
    components: tuple[CombinationDistribution, ...]
    weights: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.components or len(self.components) != len(self.weights):
            raise ValueError("components and weights must be non-empty and aligned")
        if any(weight < 0 or not math.isfinite(weight) for weight in self.weights):
            raise ValueError("mixture weights must be finite and non-negative")
        total = sum(self.weights)
        if total <= 0:
            raise ValueError("mixture weight total must be positive")
        object.__setattr__(self, "weights", tuple(weight / total for weight in self.weights))
        if len({component.pick_count for component in self.components}) != 1:
            raise ValueError("all components must share pick_count")

    @property
    def pick_count(self) -> int:
        return self.components[0].pick_count

    @property
    def is_uniform(self) -> bool:
        active = [component for component, weight in zip(self.components, self.weights, strict=True) if weight > 0]
        return bool(active) and all(getattr(component, "is_uniform", False) for component in active)

    def joint_probability(self, numbers: Sequence[int]) -> float:
        return sum(
            weight * component.joint_probability(numbers)
            for component, weight in zip(self.components, self.weights, strict=True)
        )

    def joint_log_probability(self, numbers: Sequence[int]) -> float:
        return math.log(self.joint_probability(numbers))

    def marginal_probabilities(self) -> Mapping[int, float]:
        component_marginals = [component.marginal_probabilities() for component in self.components]
        labels = component_marginals[0].keys()
        return {
            label: sum(weight * marginals[label] for marginals, weight in zip(component_marginals, self.weights, strict=True))
            for label in labels
        }

    def top_combinations(self, limit: int) -> list[tuple[int, ...]]:
        universe: set[tuple[int, ...]] = set()
        per_component = max(limit, 50)
        for component in self.components:
            universe.update(component.top_combinations(per_component))
        return sorted(universe, key=lambda combination: (-self.joint_probability(combination), combination))[:limit]
