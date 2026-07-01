from __future__ import annotations

import argparse
import json
from pathlib import Path

from simulation.correction_development import run_m3_preflight


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=200)
    parser.add_argument("--draw-count", type=int, default=1230)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = run_m3_preflight(replicates=args.replicates, draw_count=args.draw_count)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "activation_rate": payload["activation_rate"], "max_e_value": payload["max_e_value"], "eligible_k_m3": payload["eligible_k_m3"], "report_hash": payload["report_hash"]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
