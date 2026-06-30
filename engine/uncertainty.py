"""Uncertainty interface reserved for Gate 2-3 calibration.

Gate 2-2 must not fabricate 95% intervals before null and bootstrap calibration
exist. The explicit status prevents UI or downstream agents from treating a
point estimate as a validated interval.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UncertaintyEstimate:
    lower: float | None
    upper: float | None
    status: str = "pending_gate2_3"


def pending_uncertainty() -> UncertaintyEstimate:
    return UncertaintyEstimate(lower=None, upper=None)
