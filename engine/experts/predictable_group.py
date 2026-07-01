"""Past-only predictable-group learner for Gate 2-3P-R3M-3-2.

The learner is fully deterministic and implements contract version 1.0.0.
It ranks numbers from a fixed trailing window, selects group size through
chronological internal validation, freezes the selected group for 52 draws,
and abstains when no size is eligible.
"""

from __future__ import annotations

import bisect
import functools
import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from .oracle_group_eprocess import ExactGroupAlternative

NUMBER_COUNT = 45
PICK_COUNT = 6
OUTER_WINDOW = 520
HALF_LIFE = 104
PRIOR_STRENGTH = 52.0
INITIAL_FIT = 260
FOLD_COUNT = 5
FOLD_LENGTH = 52
GROUP_SIZES = (6, 10, 15)
LIFT = 1.25
TIE_TOLERANCE = 1e-12
UNIFORM_PROBABILITY = PICK_COUNT / NUMBER_COUNT
_DECAY = 2.0 ** (-1.0 / HALF_LIFE)


def numbers_to_mask(numbers: Sequence[int]) -> int:
    values = tuple(int(number) for number in numbers)
    if len(values) != PICK_COUNT or len(set(values)) != PICK_COUNT:
        raise ValueError("draw must contain exactly six unique numbers")
    if any(number < 1 or number > NUMBER_COUNT for number in values):
        raise ValueError("draw number outside 1..45")
    mask = 0
    for number in values:
        mask |= 1 << (number - 1)
    return mask


def validate_draw_mask(mask: int) -> None:
    if not isinstance(mask, int) or mask < 0 or mask >> NUMBER_COUNT:
        raise ValueError("draw mask outside 45-number universe")
    if mask.bit_count() != PICK_COUNT:
        raise ValueError("draw mask must contain exactly six numbers")


def group_to_mask(numbers: Sequence[int]) -> int:
    values = tuple(sorted(set(int(number) for number in numbers)))
    if not values or any(number < 1 or number > NUMBER_COUNT for number in values):
        raise ValueError("invalid group")
    mask = 0
    for number in values:
        mask |= 1 << (number - 1)
    return mask


@dataclass(frozen=True)
class OccurrenceIndex:
    """Sparse per-number occurrence index for weighted trailing-window queries."""

    draw_masks: tuple[int, ...]
    times: tuple[tuple[int, ...], ...]
    inverse_weight_prefix: tuple[tuple[float, ...], ...]
    decay_powers: tuple[float, ...]

    @classmethod
    def build(cls, draw_masks: Sequence[int]) -> "OccurrenceIndex":
        masks = tuple(int(mask) for mask in draw_masks)
        occurrence_times: list[list[int]] = [[] for _ in range(NUMBER_COUNT)]
        occurrence_prefix: list[list[float]] = [[0.0] for _ in range(NUMBER_COUNT)]
        decay_powers = [1.0]
        inverse = 1.0
        for draw_no, mask in enumerate(masks, start=1):
            validate_draw_mask(mask)
            decay_powers.append(decay_powers[-1] * _DECAY)
            inverse /= _DECAY
            value = mask
            while value:
                lowest = value & -value
                index = lowest.bit_length() - 1
                occurrence_times[index].append(draw_no)
                occurrence_prefix[index].append(
                    occurrence_prefix[index][-1] + inverse
                )
                value ^= lowest
        return cls(
            draw_masks=masks,
            times=tuple(tuple(values) for values in occurrence_times),
            inverse_weight_prefix=tuple(
                tuple(values) for values in occurrence_prefix
            ),
            decay_powers=tuple(decay_powers),
        )

    @property
    def draw_count(self) -> int:
        return len(self.draw_masks)

    def weighted_count(self, number: int, start: int, end: int) -> float:
        if not 1 <= number <= NUMBER_COUNT:
            raise ValueError("number outside 1..45")
        if not 1 <= start <= end <= self.draw_count:
            raise ValueError("invalid training interval")
        times = self.times[number - 1]
        prefix = self.inverse_weight_prefix[number - 1]
        left = bisect.bisect_left(times, start)
        right = bisect.bisect_right(times, end)
        return self.decay_powers[end] * (prefix[right] - prefix[left])


def _logit(probability: float) -> float:
    return math.log(probability / (1.0 - probability))


def score_numbers(
    index: OccurrenceIndex,
    *,
    start: int,
    end: int,
) -> Mapping[int, float]:
    if not 1 <= start <= end <= index.draw_count:
        raise ValueError("invalid score interval")
    length = end - start + 1
    total_weight = (1.0 - _DECAY**length) / (1.0 - _DECAY)
    denominator = PRIOR_STRENGTH + total_weight
    baseline_logit = _logit(UNIFORM_PROBABILITY)
    output: dict[int, float] = {}
    for number in range(1, NUMBER_COUNT + 1):
        weighted = index.weighted_count(number, start, end)
        posterior = (
            PRIOR_STRENGTH * UNIFORM_PROBABILITY + weighted
        ) / denominator
        output[number] = _logit(posterior) - baseline_logit
    return output


def rank_numbers(scores: Mapping[int, float]) -> tuple[int, ...]:
    if set(scores) != set(range(1, NUMBER_COUNT + 1)):
        raise ValueError("scores must contain numbers 1..45 exactly once")

    def compare(left: int, right: int) -> int:
        difference = scores[left] - scores[right]
        if abs(difference) <= TIE_TOLERANCE:
            return -1 if left < right else (1 if left > right else 0)
        return -1 if difference > 0.0 else 1

    return tuple(sorted(scores, key=functools.cmp_to_key(compare)))


@dataclass(frozen=True)
class PredictableGroupDecision:
    block_start: int
    selected_size: int | None
    group: tuple[int, ...]
    cv_scores: Mapping[int, float]
    positive_folds: Mapping[int, int]
    eligible_sizes: tuple[int, ...]
    abstain: bool

    @property
    def group_mask(self) -> int:
        return 0 if self.abstain else group_to_mask(self.group)


def _validation_log_lr(
    index: OccurrenceIndex,
    *,
    start: int,
    end: int,
    group: Sequence[int],
) -> float:
    alternative = ExactGroupAlternative(tuple(sorted(group)), LIFT)
    mask = group_to_mask(group)
    return sum(
        alternative.log_likelihood_ratio_from_count(
            (index.draw_masks[draw_no - 1] & mask).bit_count()
        )
        for draw_no in range(start, end + 1)
    )


def select_predictable_group(
    index: OccurrenceIndex,
    *,
    block_start: int,
) -> PredictableGroupDecision:
    outer_start = block_start - OUTER_WINDOW
    if outer_start < 1 or block_start - 1 > index.draw_count:
        raise ValueError("a complete 520-draw learning window is required")

    cv_scores = {size: 0.0 for size in GROUP_SIZES}
    positive_folds = {size: 0 for size in GROUP_SIZES}

    for fold in range(FOLD_COUNT):
        validation_start = block_start - INITIAL_FIT + fold * FOLD_LENGTH
        validation_end = validation_start + FOLD_LENGTH - 1
        training_end = validation_start - 1
        ranked = rank_numbers(
            score_numbers(index, start=outer_start, end=training_end)
        )
        for size in GROUP_SIZES:
            value = _validation_log_lr(
                index,
                start=validation_start,
                end=validation_end,
                group=ranked[:size],
            )
            cv_scores[size] += value
            if value > 0.0:
                positive_folds[size] += 1

    eligible = tuple(
        size
        for size in GROUP_SIZES
        if cv_scores[size] > 0.0 and positive_folds[size] >= 3
    )
    if not eligible:
        return PredictableGroupDecision(
            block_start=block_start,
            selected_size=None,
            group=(),
            cv_scores=cv_scores,
            positive_folds=positive_folds,
            eligible_sizes=(),
            abstain=True,
        )

    selected = eligible[0]
    for size in eligible[1:]:
        difference = cv_scores[size] - cv_scores[selected]
        if difference > TIE_TOLERANCE:
            selected = size
        elif abs(difference) <= TIE_TOLERANCE and size < selected:
            selected = size

    final_ranked = rank_numbers(
        score_numbers(index, start=outer_start, end=block_start - 1)
    )
    group = tuple(sorted(final_ranked[:selected]))
    return PredictableGroupDecision(
        block_start=block_start,
        selected_size=selected,
        group=group,
        cv_scores=cv_scores,
        positive_folds=positive_folds,
        eligible_sizes=eligible,
        abstain=False,
    )
