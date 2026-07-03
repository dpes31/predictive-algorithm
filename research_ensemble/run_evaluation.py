"""CLI for the frozen A4 retrospective evaluation."""

from __future__ import annotations

import argparse
import pathlib
import traceback
from typing import Any

from engine.hashing import sha256_value

from .evaluation import EVALUATION_CONTRACT_VERSION, evaluate_dataset, write_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the frozen Algorithm Integration A4 evaluation.")
    parser.add_argument("--dataset", default="data/draws.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--rows-output")
    return parser


def _failure_result(exc: BaseException) -> dict[str, Any]:
    blocked = isinstance(exc, (FileNotFoundError, ModuleNotFoundError))
    status = "A4_EVALUATION_BLOCKED" if blocked else "A4_EVALUATION_FAIL"
    canonical = {
        "status": status,
        "decision_reasons": [f"unhandled_{type(exc).__name__}"],
        "contract_version": EVALUATION_CONTRACT_VERSION,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "traceback": traceback.format_exc(),
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
    }
    canonical["canonical_result_hash"] = sha256_value(canonical)
    return {"runtime": {}, "canonical_result": canonical, "canonical_result_hash": canonical["canonical_result_hash"]}


def main() -> int:
    args = _parser().parse_args()
    try:
        result = evaluate_dataset(dataset_path=args.dataset, rows_output=args.rows_output)
    except BaseException as exc:  # preserve terminal evidence instead of losing the run
        result = _failure_result(exc)
    write_result(result, pathlib.Path(args.output))
    canonical = result["canonical_result"]
    print(f"A4_RUNTIME_STATUS={canonical['status']}")
    print(f"A4_CANONICAL_RESULT_HASH={result['canonical_result_hash']}")
    print(f"A4_DECISION_REASONS={canonical.get('decision_reasons', [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
