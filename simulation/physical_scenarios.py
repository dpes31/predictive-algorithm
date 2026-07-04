"""Synthetic physical-context scenarios for Gate 2-3P-2 smoke validation."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Sequence

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.contracts import DrawRecord
from engine.physical_metadata import EvidenceValue, PhysicalDrawMetadata

from .sampling import sample_weighted_combination


@dataclass(frozen=True)
class PhysicalScenarioSpec:
    name: str
    family: str
    lift: float = 1.0
    missing_rate: float = 0.0
    misclassification_rate: float = 0.0
    change_point: int | None = None

    def validate(self) -> None:
        if self.family not in {"unrelated", "ball_set", "machine", "regime_reversal"}:
            raise ValueError(f"unknown physical scenario family: {self.family}")
        if self.lift < 1.0:
            raise ValueError("lift must be at least one")
        if not 0.0 <= self.missing_rate <= 1.0:
            raise ValueError("missing_rate must be in [0, 1]")
        if not 0.0 <= self.misclassification_rate <= 1.0:
            raise ValueError("misclassification_rate must be in [0, 1]")


NULL_UNRELATED = PhysicalScenarioSpec("null_unrelated", "unrelated")
BALL_SET_LIFT_125 = PhysicalScenarioSpec("ball_set_lift_125", "ball_set", lift=1.25)
MACHINE_LIFT_125 = PhysicalScenarioSpec("machine_lift_125", "machine", lift=1.25)
REGIME_REVERSAL_125 = PhysicalScenarioSpec(
    "regime_reversal_125",
    "regime_reversal",
    lift=1.25,
    change_point=615,
)
BALL_SET_LIFT_125_MISSING_30 = PhysicalScenarioSpec(
    "ball_set_lift_125_missing_30",
    "ball_set",
    lift=1.25,
    missing_rate=0.30,
)

PHYSICAL_SMOKE_SCENARIOS: tuple[PhysicalScenarioSpec, ...] = (
    NULL_UNRELATED,
    BALL_SET_LIFT_125,
    MACHINE_LIFT_125,
    REGIME_REVERSAL_125,
    BALL_SET_LIFT_125_MISSING_30,
)


def _evidence(
    value: object,
    *,
    draw_no: int,
    missing: bool,
    confidence: float = 0.95,
) -> EvidenceValue:
    if missing:
        return EvidenceValue()
    observed = datetime(2002, 12, 7, 9, 0, tzinfo=timezone(timedelta(hours=9))) + timedelta(
        weeks=draw_no - 1
    )
    return EvidenceValue(
        value=value,
        status="verified",
        source_type="official_document",
        source_url=f"https://synthetic.invalid/metadata/{draw_no}",
        observed_at=observed.isoformat(),
        available_before_draw=True,
        confidence=confidence,
        notes="synthetic Gate 2-3P control",
    )


def _favored_numbers(
    spec: PhysicalScenarioSpec,
    *,
    ball_set_id: str,
    machine_id: str,
    draw_no: int,
    config: EngineConfig,
) -> set[int]:
    if spec.family == "ball_set":
        set_index = int(ball_set_id.removeprefix("B")) - 1
        start = set_index * 9 + 1
        return set(range(start, min(config.number_count, start + 8) + 1))
    if spec.family == "machine":
        return set(range(1, 11)) if machine_id == "M1" else set(range(36, 46))
    if spec.family == "regime_reversal":
        change = spec.change_point or (config.min_history + 1)
        return set(range(1, 11)) if draw_no < change else set(range(36, 46))
    return set()


def generate_physical_series(
    spec: PhysicalScenarioSpec,
    *,
    draw_count: int,
    seed: int,
    config: EngineConfig = DEFAULT_CONFIG,
) -> tuple[tuple[DrawRecord, ...], tuple[PhysicalDrawMetadata, ...]]:
    """Generate exact 6-of-45 draws with pre-draw physical metadata."""

    spec.validate()
    if draw_count < 1:
        raise ValueError("draw_count must be positive")
    rng = random.Random(seed)
    records: list[DrawRecord] = []
    metadata_records: list[PhysicalDrawMetadata] = []
    start_date = datetime(2002, 12, 7, 20, 35, tzinfo=timezone(timedelta(hours=9)))

    for draw_no in range(1, draw_count + 1):
        true_machine = "M1" if draw_no % 2 else "M2"
        true_ball_set = f"B{rng.randint(1, 5)}"
        machine_regime = "MR1" if true_machine == "M1" else "MR2"
        ball_regime = "BR1" if draw_no < (spec.change_point or draw_count + 1) else "BR2"

        favored = _favored_numbers(
            spec,
            ball_set_id=true_ball_set,
            machine_id=true_machine,
            draw_no=draw_no,
            config=config,
        )
        weights = [spec.lift if number in favored else 1.0 for number in range(1, config.number_count + 1)]
        numbers = sample_weighted_combination(weights, pick_count=config.pick_count, rng=rng)
        draw_datetime = start_date + timedelta(weeks=draw_no - 1)
        records.append(
            DrawRecord(
                draw_no=draw_no,
                draw_date=draw_datetime.date().isoformat(),
                numbers=numbers,
                verification_status="synthetic",
                locked=False,
                source=f"synthetic:{spec.name}",
            )
        )

        observed_machine = true_machine
        observed_ball_set = true_ball_set
        if rng.random() < spec.misclassification_rate:
            observed_machine = "M2" if true_machine == "M1" else "M1"
        if rng.random() < spec.misclassification_rate:
            alternatives = [f"B{index}" for index in range(1, 6) if f"B{index}" != true_ball_set]
            observed_ball_set = rng.choice(alternatives)

        fields = {
            "machine.machine_id": _evidence(
                observed_machine,
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
            "machine.machine_generation": _evidence(
                "MG1",
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
            "ball_set.ball_set_id": _evidence(
                observed_ball_set,
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
            "ball_set.ball_generation": _evidence(
                ball_regime,
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
            "regime.machine_regime_id": _evidence(
                machine_regime,
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
            "regime.ball_regime_id": _evidence(
                ball_regime,
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
            "regime.operating_procedure_regime_id": _evidence(
                "OR1",
                draw_no=draw_no,
                missing=rng.random() < spec.missing_rate,
            ),
        }
        metadata_records.append(
            PhysicalDrawMetadata(
                draw_no=draw_no,
                draw_datetime=draw_datetime.isoformat(),
                metadata_version=config.physical_data_schema_version,
                fields=fields,
            )
        )

    return tuple(records), tuple(metadata_records)


def holdout_target(
    records: Sequence[DrawRecord],
    metadata: Sequence[PhysicalDrawMetadata],
) -> tuple[tuple[DrawRecord, ...], tuple[PhysicalDrawMetadata, ...], DrawRecord, PhysicalDrawMetadata]:
    if len(records) != len(metadata) or len(records) < 2:
        raise ValueError("records and metadata must align and contain at least two draws")
    return tuple(records[:-1]), tuple(metadata[:-1]), records[-1], metadata[-1]
