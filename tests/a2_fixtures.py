from __future__ import annotations
from engine.contracts import DrawRecord
from research_ensemble.registry import seal_physical_adapter, seal_registry


def synthetic_records(count: int = 303) -> list[DrawRecord]:
    output = []
    for draw_no in range(1, count + 1):
        start = (draw_no * 11) % 45
        numbers = tuple(sorted(((start + offset * 7) % 45) + 1 for offset in range(6)))
        output.append(DrawRecord(draw_no=draw_no, draw_date=f"2020-01-{(draw_no % 28) + 1:02d}", numbers=numbers, verification_status="auto_checked", source="synthetic_fixture"))
    return output


def user_registry(values: dict[str, float] | None = None, source: str = "USER_SUPPLIED") -> dict:
    return seal_registry({
        "registry_type": "user_input", "contract_version": "user-input-registry-1.0.0",
        "registry_version": "synthetic-1.0.0", "status": "APPROVED",
        "approved_by": "user", "approved_at": "2026-07-03T00:00:00+09:00",
        "entries": [{
            "entry_id": "UPI-SYNTHETIC", "name": "synthetic number vector",
            "classification": "NUMBER_LEVEL", "value_type": "NUMBER_VECTOR",
            "unit": "fixture", "value": None,
            "number_mapping": values or {str(number): float(number) for number in range(1, 46)},
            "applicable_draws": {"from": None, "to": None}, "source_type": source,
            "user_statement_reference": "synthetic unit-test fixture only",
            "supplied_at": "2026-07-03T00:00:00+09:00", "approved_for_scoring": True,
            "allowed_hypothesis_ids": ["HYP-SYNTHETIC"], "missing_policy": "ABSTAIN_COMPONENT",
        }],
    })


def hypothesis_registry(status: str = "ACTIVE", cap: float = 0.10, required: bool = False) -> dict:
    return seal_registry({
        "registry_type": "hypothesis", "contract_version": "hypothesis-registry-1.0.0",
        "registry_version": "synthetic-1.0.0", "status": "APPROVED",
        "approved_by": "user", "approved_at": "2026-07-03T00:00:00+09:00",
        "entries": [{
            "hypothesis_id": "HYP-SYNTHETIC", "version": "1.0.0", "status": status,
            "statement": "synthetic fixture", "rationale": "not real-world evidence",
            "source_type": "USER_APPROVED", "input_entry_ids": ["UPI-SYNTHETIC"],
            "transform_type": "LINEAR_NUMBER_SCORE", "formula": "fixture-linear",
            "parameters": {}, "expected_direction": "POSITIVE", "applicable_scope": {},
            "required": required, "minimum_support": 0.0, "single_hypothesis_cap": cap,
            "missing_policy": "ABSTAIN_RUN" if required else "ABSTAIN_COMPONENT",
            "contradiction_policy": "SHRINK", "approved_by": "user" if status == "ACTIVE" else None,
            "approved_at": "2026-07-03T00:00:00+09:00" if status == "ACTIVE" else None,
        }],
    })


def physical_adapter(cap: float = 0.05) -> dict:
    return seal_physical_adapter({
        "registry_type": "physical_adapter", "contract_version": "user-physical-adapter-1.0.0",
        "adapter_version": "synthetic-1.0.0", "status": "APPROVED",
        "approved_by": "user", "approved_at": "2026-07-03T00:00:00+09:00",
        "fields": [{"field_id": "PHY-SYNTHETIC", "input_entry_id": "UPI-SYNTHETIC", "hypothesis_id": "HYP-SYNTHETIC", "normalization": "CROSS_SECTIONAL_Z_CLIP_3", "direction_source": "HYPOTHESIS_ONLY", "field_cap": cap}],
    })
