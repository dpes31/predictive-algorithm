"""CLI for Product Closeout Gate C2 offline QA."""

from __future__ import annotations

import argparse
import json
import pathlib

from engine.hashing import canonical_json

from .harness import run_internal_qa


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Product Closeout Gate C2 internal QA.")
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = run_internal_qa()
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(result) + "\n", encoding="utf-8")
    canonical = result["canonical_result"]
    print(f"PRODUCT_CLOSEOUT_QA_RUNTIME_STATUS={canonical['status']}")
    print(f"PRODUCT_CLOSEOUT_QA_CANONICAL_HASH={result['canonical_result_hash']}")
    print("PRODUCT_CLOSEOUT_QA_RESULT_JSON=" + json.dumps(canonical, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
