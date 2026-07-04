"""Fast deterministic Gate 2-3P-3 validation harness.

The harness mirrors the frozen M4 contextual-shrinkage contract while avoiding
object construction for every synthetic draw. It evaluates blockwise exact
6-of-45 probabilities and preserves one result row per seed.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass
from functools import lru_cache
from statistics import fmean
from typing import Any, Iterable, Mapping, Sequence

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.distributions import FixedSizeDistribution

FIELD_NAMES = (
    "machine.machine_id",
    "ball_set.ball_set_id",
    "regime.machine_regime_id",
    "regime.ball_regime_id",
    "interaction.machine_ball_set_id",
    "environment.temperature_band",
    "pre_draw_tests.condition_id",
)
REQUIRED_FIELD_INDEXES = (0, 1, 2, 3)
EFFECT_SIZES = (1.05, 1.10, 1.25, 1.50)


@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    family: str
    lift: float = 1.0
    missing_rate: float = 0.0
    misclassification_rate: float = 0.0
    confidence: float = 0.95
    change_point: int = 615
    signal_start: int | None = None
    signal_end: int | None = None
    post_draw_error_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FastDraw:
    numbers: tuple[int, ...]
    contexts: tuple[int | None, ...]
    confidences: tuple[float, ...]
    favored: tuple[int, ...]
    signal_active: bool


@dataclass(frozen=True)
class SeriesSummary:
    category: str
    scenario: str
    effect_size: float
    seed: int
    mean_delta_log_loss: Mapping[str, float]
    mean_delta_brier: Mapping[str, float]
    positive_macro_blocks: Mapping[str, int]
    strict_winner: str | None
    direction_accuracy: float | None
    first_positive_origin: int | None
    calibration_error_m4: float
    m4_strength_by_origin: tuple[tuple[int, float], ...]
    adaptation_delay: int | None
    return_delay: int | None
    m3_diagnostic_maxima: tuple[float, float, float, float] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "scenario": self.scenario,
            "effect_size": self.effect_size,
            "seed": self.seed,
            "mean_delta_log_loss": dict(self.mean_delta_log_loss),
            "mean_delta_brier": dict(self.mean_delta_brier),
            "positive_macro_blocks": dict(self.positive_macro_blocks),
            "strict_winner": self.strict_winner,
            "direction_accuracy": self.direction_accuracy,
            "first_positive_origin": self.first_positive_origin,
            "calibration_error_m4": self.calibration_error_m4,
            "m4_strength_by_origin": [list(item) for item in self.m4_strength_by_origin],
            "adaptation_delay": self.adaptation_delay,
            "return_delay": self.return_delay,
            "m3_diagnostic_maxima": (
                None if self.m3_diagnostic_maxima is None else list(self.m3_diagnostic_maxima)
            ),
        }


def null_scenarios() -> tuple[ScenarioSpec, ...]:
    return (
        ScenarioSpec("n0_uniform", "null_no_metadata"),
        ScenarioSpec("n1_irrelevant_metadata", "null_irrelevant"),
        ScenarioSpec("n2_missing_dependency", "null_missing_dependency"),
        ScenarioSpec("n3_measurement_noise", "null_measurement_noise"),
        ScenarioSpec("n4_wrong_ids", "null_wrong_ids", misclassification_rate=0.15),
        ScenarioSpec("n5_regime_only", "null_regime_only"),
    )


def positive_scenarios(lift: float) -> tuple[ScenarioSpec, ...]:
    return (
        ScenarioSpec("p1_ball_set", "ball_set", lift=lift),
        ScenarioSpec("p2_machine", "machine", lift=lift),
        ScenarioSpec("p3_machine_ball_interaction", "interaction", lift=lift),
        ScenarioSpec("p4_regime_reversal", "regime_reversal", lift=lift),
        ScenarioSpec(
            "p5_temporary_environment",
            "temporary_environment",
            lift=lift,
            signal_start=500,
            signal_end=800,
        ),
        ScenarioSpec("p6_pretest_shared", "pretest_shared", lift=lift),
    )


def robustness_scenarios() -> tuple[ScenarioSpec, ...]:
    return (
        ScenarioSpec("r_missing_10", "ball_set", lift=1.25, missing_rate=0.10),
        ScenarioSpec("r_missing_30", "ball_set", lift=1.25, missing_rate=0.30),
        ScenarioSpec("r_missing_50", "ball_set", lift=1.25, missing_rate=0.50),
        ScenarioSpec("r_confidence_over_10", "ball_set", lift=1.25, misclassification_rate=0.10),
        ScenarioSpec("r_confidence_over_30", "ball_set", lift=1.25, misclassification_rate=0.30),
        ScenarioSpec("r_id_misclass_05", "ball_set", lift=1.25, misclassification_rate=0.05),
        ScenarioSpec("r_id_misclass_15", "ball_set", lift=1.25, misclassification_rate=0.15),
        ScenarioSpec("r_observed_after_draw", "ball_set", lift=1.25, post_draw_error_rate=0.20),
        ScenarioSpec("r_new_regime_low_support", "late_regime", lift=1.25, change_point=1100),
        ScenarioSpec(
            "r_signal_decay",
            "ball_set",
            lift=1.25,
            signal_start=1,
            signal_end=800,
        ),
        ScenarioSpec("r_direction_reversal", "regime_reversal", lift=1.25, change_point=615),
        ScenarioSpec("r_pretest_independent", "pretest_independent", lift=1.25),
    )


@lru_cache(maxsize=None)
def _favored_count_cdf(favored_count: int, lift: float, pick_count: int = 6) -> tuple[float, ...]:
    weights: list[float] = []
    lower = max(0, pick_count - (45 - favored_count))
    upper = min(pick_count, favored_count)
    for selected_favored in range(lower, upper + 1):
        weights.append(
            math.comb(favored_count, selected_favored)
            * math.comb(45 - favored_count, pick_count - selected_favored)
            * (lift ** selected_favored)
        )
    total = sum(weights)
    cumulative = 0.0
    cdf: list[float] = []
    for value in weights:
        cumulative += value / total
        cdf.append(cumulative)
    cdf[-1] = 1.0
    return tuple(cdf)


def _sample_group_weighted(
    rng: random.Random,
    favored: Sequence[int],
    lift: float,
    *,
    pick_count: int = 6,
) -> tuple[int, ...]:
    favored_values = tuple(sorted(set(favored)))
    if lift <= 1.0 or not favored_values:
        return tuple(sorted(rng.sample(range(1, 46), pick_count)))
    favored_set = set(favored_values)
    other = tuple(number for number in range(1, 46) if number not in favored_set)
    lower = max(0, pick_count - len(other))
    cdf = _favored_count_cdf(len(favored_values), round(lift, 8), pick_count)
    draw = rng.random()
    offset = next(index for index, value in enumerate(cdf) if draw <= value)
    selected_favored = lower + offset
    selected = rng.sample(favored_values, selected_favored)
    selected.extend(rng.sample(other, pick_count - selected_favored))
    return tuple(sorted(selected))


def _cyclic_group(start: int, size: int) -> tuple[int, ...]:
    return tuple(sorted(((start + offset) % 45) + 1 for offset in range(size)))


def _true_favored(
    spec: ScenarioSpec,
    *,
    draw_no: int,
    machine: int,
    ball_set: int,
    environment: int,
    pretest: int,
) -> tuple[int, ...]:
    if spec.signal_start is not None and draw_no < spec.signal_start:
        return ()
    if spec.signal_end is not None and draw_no > spec.signal_end:
        return ()
    if spec.family == "ball_set":
        return tuple(range(ball_set * 9 + 1, ball_set * 9 + 10))
    if spec.family == "machine":
        return tuple(range(1, 11)) if machine == 0 else tuple(range(36, 46))
    if spec.family == "interaction":
        return _cyclic_group((machine * 5 + ball_set) * 4, 6)
    if spec.family in {"regime_reversal", "late_regime"}:
        return tuple(range(1, 11)) if draw_no < spec.change_point else tuple(range(36, 46))
    if spec.family == "temporary_environment":
        return _cyclic_group(environment * 15, 15)
    if spec.family == "pretest_shared":
        return _cyclic_group(pretest * 15, 15)
    return ()


def generate_fast_series(
    spec: ScenarioSpec,
    *,
    draw_count: int,
    seed: int,
) -> tuple[FastDraw, ...]:
    rng = random.Random(seed)
    output: list[FastDraw] = []
    for draw_no in range(1, draw_count + 1):
        machine = draw_no % 2
        ball_set = rng.randrange(5)
        machine_regime = 0 if draw_no < spec.change_point else 1
        ball_regime = 0 if draw_no < spec.change_point else 1
        environment = (draw_no // 13 + rng.randrange(3)) % 3
        pretest = rng.randrange(3)
        interaction = machine * 5 + ball_set

        favored = _true_favored(
            spec,
            draw_no=draw_no,
            machine=machine,
            ball_set=ball_set,
            environment=environment,
            pretest=pretest,
        )
        signal_active = bool(favored) and spec.family not in {
            "null_no_metadata",
            "null_irrelevant",
            "null_missing_dependency",
            "null_measurement_noise",
            "null_wrong_ids",
            "null_regime_only",
            "pretest_independent",
        }
        numbers = _sample_group_weighted(rng, favored if signal_active else (), spec.lift)

        observed_machine = machine
        observed_ball_set = ball_set
        if rng.random() < spec.misclassification_rate:
            observed_machine = 1 - machine
        if rng.random() < spec.misclassification_rate:
            observed_ball_set = rng.choice(tuple(value for value in range(5) if value != ball_set))
        observed_interaction = observed_machine * 5 + observed_ball_set

        if spec.family == "null_no_metadata":
            values: list[int | None] = [None] * len(FIELD_NAMES)
        else:
            values = [
                observed_machine,
                observed_ball_set,
                machine_regime,
                ball_regime,
                observed_interaction,
                environment,
                pretest,
            ]

        confidences = [spec.confidence if value is not None else 0.0 for value in values]
        for index in range(len(values)):
            missing_probability = spec.missing_rate
            if spec.family == "null_missing_dependency":
                missing_probability = 0.10 if machine == 0 else 0.50
            if rng.random() < missing_probability or rng.random() < spec.post_draw_error_rate:
                values[index] = None
                confidences[index] = 0.0

        if spec.family == "null_measurement_noise":
            values[5] = rng.randrange(12)
        if spec.family == "pretest_independent":
            favored = ()
            signal_active = False

        output.append(
            FastDraw(
                numbers=numbers,
                contexts=tuple(values),
                confidences=tuple(confidences),
                favored=tuple(favored),
                signal_active=signal_active,
            )
        )
    return tuple(output)


def _quality_active(draw: FastDraw, config: EngineConfig) -> bool:
    present = [draw.contexts[index] is not None for index in REQUIRED_FIELD_INDEXES]
    completeness = sum(present) / len(REQUIRED_FIELD_INDEXES)
    reliability = sum(
        draw.confidences[index] if draw.contexts[index] is not None else 0.0
        for index in REQUIRED_FIELD_INDEXES
    ) / len(REQUIRED_FIELD_INDEXES)
    traceability = completeness
    pre_draw_rate = 1.0 if any(present) else 0.0
    return (
        completeness >= config.physical_min_completeness
        and reliability >= config.physical_min_weighted_reliability
        and traceability >= config.physical_min_source_traceability
        and pre_draw_rate >= config.physical_required_pre_draw_rate
    )


def _logit(probability: float) -> float:
    clipped = min(1.0 - 1e-12, max(1e-12, probability))
    return math.log(clipped / (1.0 - clipped))


def _brier(marginals: Sequence[float], numbers: Sequence[int]) -> float:
    selected = set(numbers)
    return fmean(
        (probability - (1.0 if index + 1 in selected else 0.0)) ** 2
        for index, probability in enumerate(marginals)
    )


def _macro_block(draw_no: int) -> int:
    if draw_no <= 609:
        return 0
    if draw_no <= 919:
        return 1
    return 2


def _context_key(draw: FastDraw) -> tuple[tuple[int | None, ...], tuple[float, ...]]:
    return draw.contexts, tuple(round(value, 6) for value in draw.confidences)


class _ContextStats:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.exposure: list[dict[int, float]] = [dict() for _ in FIELD_NAMES]
        self.hits: list[dict[int, list[float]]] = [dict() for _ in FIELD_NAMES]

    def update(self, draw: FastDraw) -> None:
        for field_index, value in enumerate(draw.contexts):
            confidence = draw.confidences[field_index]
            if value is None or confidence <= 0.0:
                continue
            self.exposure[field_index][value] = self.exposure[field_index].get(value, 0.0) + confidence
            values = self.hits[field_index].setdefault(value, [0.0] * self.config.number_count)
            for number in draw.numbers:
                values[number - 1] += confidence

    def logits(self, target: FastDraw) -> tuple[float, ...]:
        if not _quality_active(target, self.config):
            return tuple(0.0 for _ in range(self.config.number_count))
        p0 = self.config.uniform_number_probability
        prior = self.config.physical_prior_concentration
        base = _logit(p0)
        contributions: list[tuple[float, tuple[float, ...]]] = []
        for field_index, value in enumerate(target.contexts):
            confidence = target.confidences[field_index]
            if value is None or confidence <= 0.0:
                continue
            exposure = self.exposure[field_index].get(value, 0.0)
            if exposure < self.config.physical_min_context_support:
                continue
            hits = self.hits[field_index][value]
            deltas = tuple(
                max(
                    -self.config.physical_effect_clip,
                    min(
                        self.config.physical_effect_clip,
                        _logit((prior * p0 + hits[index]) / (prior + exposure)) - base,
                    ),
                )
                for index in range(self.config.number_count)
            )
            contributions.append((confidence, deltas))
        if not contributions:
            return tuple(0.0 for _ in range(self.config.number_count))
        denominator = sum(weight for weight, _ in contributions)
        raw = [
            sum(weight * values[index] for weight, values in contributions) / denominator
            for index in range(self.config.number_count)
        ]
        center = fmean(raw)
        return tuple(
            max(
                -self.config.physical_effect_clip,
                min(self.config.physical_effect_clip, value - center),
            )
            for value in raw
        )


def _prefix_counts(series: Sequence[FastDraw], number_count: int = 45) -> list[list[int]]:
    prefix: list[list[int]] = [[0] * number_count]
    for draw in series:
        current = prefix[-1].copy()
        for number in draw.numbers:
            current[number - 1] += 1
        prefix.append(current)
    return prefix


def _baseline_distributions(
    prefix: Sequence[Sequence[int]],
    origin: int,
    config: EngineConfig,
) -> dict[str, FixedSizeDistribution]:
    p0 = config.uniform_number_probability
    base = _logit(p0)
    cumulative = prefix[origin]
    prior = config.prior_concentration
    m1_logits = []
    for count in cumulative:
        rate = (prior * p0 + count) / (prior + origin)
        m1_logits.append(max(-0.35, min(0.35, _logit(rate) - base)))

    recent_start = max(0, origin - 52)
    previous_start = max(0, origin - 104)
    recent = [cumulative[index] - prefix[recent_start][index] for index in range(45)]
    previous = [prefix[recent_start][index] - prefix[previous_start][index] for index in range(45)]
    se = math.sqrt(p0 * (1.0 - p0) / 52.0)
    shift_se = math.sqrt(2.0 * p0 * (1.0 - p0) / 52.0)
    m2_logits = [max(-0.35, min(0.35, -0.10 * ((count / 52.0 - p0) / se))) for count in recent]
    m3_logits = [
        max(-0.35, min(0.35, 0.10 * (((recent[index] - previous[index]) / 52.0) / shift_se)))
        for index in range(45)
    ]
    return {
        "M1": FixedSizeDistribution(tuple(m1_logits), config.pick_count),
        "M2": FixedSizeDistribution(tuple(m2_logits), config.pick_count),
        "M3": FixedSizeDistribution(tuple(m3_logits), config.pick_count),
    }


def _calibration_error(bin_counts: Sequence[int], bin_pred: Sequence[float], bin_obs: Sequence[float]) -> float:
    total = sum(bin_counts)
    if total <= 0:
        return 0.0
    return sum(
        count / total * abs(bin_pred[index] / count - bin_obs[index] / count)
        for index, count in enumerate(bin_counts)
        if count
    )


def _m3_diagnostic_maxima(series: Sequence[FastDraw], config: EngineConfig) -> tuple[float, float, float, float]:
    p0 = config.uniform_number_probability
    prefix = _prefix_counts(series, config.number_count)
    drift = 0.25 * math.sqrt(p0 * (1.0 - p0))
    cplus = [0.0] * config.number_count
    cminus = [0.0] * config.number_count
    maxima = [0.0, 0.0, 0.0, 0.0]
    origin_set = set(range(config.min_history, len(series), 52))
    for draw_no, draw in enumerate(series, start=1):
        selected = {number - 1 for number in draw.numbers}
        for index in range(config.number_count):
            centered = (1.0 if index in selected else 0.0) - p0
            cplus[index] = max(0.0, cplus[index] + centered - drift)
            cminus[index] = min(0.0, cminus[index] + centered + drift)
        if draw_no not in origin_set:
            continue
        current = prefix[draw_no]
        for slot, window in enumerate((52, 104)):
            recent_start = draw_no - window
            prior_start = draw_no - 2 * window
            recent = [current[index] - prefix[recent_start][index] for index in range(45)]
            previous = [prefix[recent_start][index] - prefix[prior_start][index] for index in range(45)]
            se = math.sqrt(2.0 * p0 * (1.0 - p0) / window)
            maxima[slot] = max(
                maxima[slot],
                max(abs(((recent[index] - previous[index]) / window) / se) for index in range(45)),
            )
        mean_cusum = fmean(cplus[index] + cminus[index] for index in range(45))
        variance = fmean(((cplus[index] + cminus[index]) - mean_cusum) ** 2 for index in range(45))
        sd = math.sqrt(variance)
        if sd > 0:
            maxima[2] = max(
                maxima[2],
                max(abs(((cplus[index] + cminus[index]) - mean_cusum) / sd) for index in range(45)),
            )
        counts52 = [current[index] - prefix[draw_no - 52][index] for index in range(45)]
        probabilities = [count / (6.0 * 52.0) for count in counts52 if count]
        entropy = -sum(value * math.log(value) for value in probabilities) / math.log(45)
        maxima[3] = max(maxima[3], 1.0 - entropy)
    return tuple(maxima)  # type: ignore[return-value]


def evaluate_series(
    spec: ScenarioSpec,
    *,
    category: str,
    draw_count: int,
    seed: int,
    include_m3_diagnostics: bool,
    config: EngineConfig = DEFAULT_CONFIG,
) -> SeriesSummary:
    series = generate_fast_series(spec, draw_count=draw_count, seed=seed)
    prefix = _prefix_counts(series, config.number_count)
    stats = _ContextStats(config)
    uniform = FixedSizeDistribution(tuple(0.0 for _ in range(45)), config.pick_count)
    uniform_loss = -uniform.joint_log_probability(series[0].numbers)
    uniform_marginals = tuple(uniform.marginal_probabilities().values())

    losses = {name: [] for name in ("M1", "M2", "M3", "M4")}
    briers = {name: [] for name in ("M1", "M2", "M3", "M4")}
    macro_losses = {name: [[], [], []] for name in losses}
    first_positive_origin: int | None = None
    strengths: list[tuple[int, float]] = []
    direction_hits = 0
    direction_trials = 0
    calibration_bins = [0] * 10
    calibration_pred = [0.0] * 10
    calibration_obs = [0.0] * 10

    next_origin = config.min_history
    for draw_index, draw in enumerate(series, start=1):
        if draw_index <= config.min_history:
            stats.update(draw)
            continue
        if draw_index != next_origin + 1:
            continue

        origin = next_origin
        block_end = min(draw_count, origin + 52)
        baselines = _baseline_distributions(prefix, origin, config)
        m4_cache: dict[tuple[tuple[int | None, ...], tuple[float, ...]], tuple[FixedSizeDistribution, tuple[float, ...]]] = {}
        block_deltas = {name: [] for name in losses}
        origin_strengths: list[float] = []

        for target_no in range(origin + 1, block_end + 1):
            target = series[target_no - 1]
            key = _context_key(target)
            if key not in m4_cache:
                logits = stats.logits(target)
                distribution = FixedSizeDistribution(logits, config.pick_count)
                marginals = tuple(distribution.marginal_probabilities().values())
                m4_cache[key] = distribution, marginals
            m4_distribution, m4_marginals = m4_cache[key]
            origin_strengths.append(max(m4_distribution.logits) - min(m4_distribution.logits))

            model_distributions = {**baselines, "M4": m4_distribution}
            model_marginals = {
                "M1": tuple(baselines["M1"].marginal_probabilities().values()),
                "M2": tuple(baselines["M2"].marginal_probabilities().values()),
                "M3": tuple(baselines["M3"].marginal_probabilities().values()),
                "M4": m4_marginals,
            }
            uniform_brier = _brier(uniform_marginals, target.numbers)
            for name, distribution in model_distributions.items():
                model_loss = -distribution.joint_log_probability(target.numbers)
                delta_loss = uniform_loss - model_loss
                delta_brier = uniform_brier - _brier(model_marginals[name], target.numbers)
                losses[name].append(delta_loss)
                briers[name].append(delta_brier)
                block_deltas[name].append(delta_loss)
                macro_losses[name][_macro_block(target_no)].append(delta_loss)

            if target.signal_active and target.favored:
                favored_set = set(target.favored)
                favored_mean = fmean(m4_marginals[number - 1] for number in favored_set)
                other_mean = fmean(
                    probability
                    for number, probability in enumerate(m4_marginals, start=1)
                    if number not in favored_set
                )
                direction_hits += int(favored_mean > other_mean)
                direction_trials += 1

            selected = set(target.numbers)
            for index, probability in enumerate(m4_marginals):
                bin_index = min(9, int(probability * 10.0))
                calibration_bins[bin_index] += 1
                calibration_pred[bin_index] += probability
                calibration_obs[bin_index] += 1.0 if index + 1 in selected else 0.0

        if first_positive_origin is None and fmean(block_deltas["M4"]) > 0:
            first_positive_origin = origin
        strengths.append((origin, fmean(origin_strengths) if origin_strengths else 0.0))
        for target_no in range(origin + 1, block_end + 1):
            stats.update(series[target_no - 1])
        next_origin += 52
        if next_origin >= draw_count:
            break

    mean_ll = {name: fmean(values) if values else 0.0 for name, values in losses.items()}
    mean_brier = {name: fmean(values) if values else 0.0 for name, values in briers.items()}
    positive_blocks = {
        name: sum((fmean(values) if values else 0.0) > 0 for values in macro_losses[name])
        for name in losses
    }
    ordered = sorted(((score, name) for name, score in mean_ll.items()), reverse=True)
    strict_winner = ordered[0][1] if ordered[0][0] > 0 and ordered[0][0] > ordered[1][0] + 1e-15 else None

    adaptation_delay: int | None = None
    if spec.family in {"regime_reversal", "late_regime"}:
        for origin, strength in strengths:
            if origin >= spec.change_point and strength > 0.0:
                adaptation_delay = origin - spec.change_point
                break
    return_delay: int | None = None
    if spec.signal_end is not None:
        post = [(origin, strength) for origin, strength in strengths if origin >= spec.signal_end]
        if post:
            baseline_strength = strengths[0][1] if strengths else 0.0
            for origin, strength in post:
                if strength <= max(0.02, baseline_strength):
                    return_delay = origin - spec.signal_end
                    break

    return SeriesSummary(
        category=category,
        scenario=spec.name,
        effect_size=spec.lift,
        seed=seed,
        mean_delta_log_loss=mean_ll,
        mean_delta_brier=mean_brier,
        positive_macro_blocks=positive_blocks,
        strict_winner=strict_winner,
        direction_accuracy=(direction_hits / direction_trials if direction_trials else None),
        first_positive_origin=first_positive_origin,
        calibration_error_m4=_calibration_error(calibration_bins, calibration_pred, calibration_obs),
        m4_strength_by_origin=tuple(strengths),
        adaptation_delay=adaptation_delay,
        return_delay=return_delay,
        m3_diagnostic_maxima=(
            _m3_diagnostic_maxima(series, config) if include_m3_diagnostics else None
        ),
    )


def assigned_null_scenario(global_index: int, total: int) -> ScenarioSpec:
    scenarios = null_scenarios()
    if total == 4000:
        counts = (670, 666, 666, 666, 666, 666)
    elif total == 5000:
        counts = (835, 833, 833, 833, 833, 833)
    else:
        return scenarios[global_index % len(scenarios)]
    cursor = 0
    for scenario, count in zip(scenarios, counts, strict=True):
        if cursor <= global_index < cursor + count:
            return scenario
        cursor += count
    raise IndexError(global_index)


def summarize_rows(rows: Iterable[SeriesSummary]) -> list[dict[str, Any]]:
    return [row.to_dict() for row in rows]
