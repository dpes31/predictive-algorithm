"""Command entry point for Gate 2-3P-R3M-3-2 DEV-PG validation."""

from __future__ import annotations

import json
import os
from pathlib import Path

from simulation.predictable_group_feasibility import run_predictable_group_gate


def main() -> None:
    result = run_predictable_group_gate(
        implementation_commit=os.environ.get("IMPLEMENTATION_COMMIT", "unknown")
    )
    Path("r3m3-predictable-group-dev.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
