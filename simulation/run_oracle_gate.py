"""Command entry point for the approved Oracle DEV Gate."""

from __future__ import annotations

import json
import os
from pathlib import Path

from simulation.oracle_feasibility import run_oracle_gate


def main() -> None:
    commit = os.environ.get("IMPLEMENTATION_COMMIT", "unknown")
    result = run_oracle_gate(implementation_commit=commit)
    Path("r3m2-oracle-dev.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    if result["status"] != "ORACLE_PASS":
        raise RuntimeError("Oracle DEV Gate did not pass")


if __name__ == "__main__":
    main()
