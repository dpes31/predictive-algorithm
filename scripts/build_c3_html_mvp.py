"""Build the Product Closeout C3 static MVP from the locked M0 product runner."""

from __future__ import annotations

import argparse
import pathlib

from engine.hashing import canonical_json, sha256_value
from product.run_prediction import run_product_prediction

TARGET_DRAW_NO = 1231
GENERATED_AT = "2026-07-03T00:00:00Z"


def build(output_dir: str | pathlib.Path) -> dict[str, str]:
    root = pathlib.Path(__file__).resolve().parents[1]
    output = pathlib.Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    prediction = run_product_prediction(
        target_draw_no=TARGET_DRAW_NO,
        dataset_path=root / "data/draws.json",
        generated_at=GENERATED_AT,
    )
    prediction_path = output / "product-prediction.json"
    prediction_path.write_text(canonical_json(prediction) + "\n", encoding="utf-8")

    index_source = root / "public/index.html"
    index_path = output / "index.html"
    if index_source.resolve() != index_path.resolve():
        index_path.write_bytes(index_source.read_bytes())

    manifest = {
        "contract": "product-closeout-html-1.0.0",
        "target_draw_no": TARGET_DRAW_NO,
        "generated_at": GENERATED_AT,
        "prediction_hash": prediction["hashes"]["prediction_hash"],
        "prediction_file_sha256": sha256_value(prediction),
        "index_file_sha256": sha256_value(index_path.read_text(encoding="utf-8")),
        "research_only": True,
        "public_release_allowed": False,
    }
    (output / "build-manifest.json").write_text(canonical_json(manifest) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="dist")
    args = parser.parse_args()
    manifest = build(args.output_dir)
    print(canonical_json(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
