from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE_HTML = ROOT / "app" / "archive.html"
ARCHIVE_JS = ROOT / "app" / "assets" / "js" / "archive.js"
APP_CSS = ROOT / "app" / "assets" / "css" / "app.css"


class StaticArchiveContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = ARCHIVE_HTML.read_text(encoding="utf-8")
        cls.javascript = ARCHIVE_JS.read_text(encoding="utf-8")
        cls.css = APP_CSS.read_text(encoding="utf-8")

    def test_archive_has_required_controls_and_render_targets(self):
        required_ids = {
            "data-status",
            "summary-count",
            "summary-latest",
            "summary-verified",
            "summary-version",
            "draw-search",
            "year-filter",
            "sort-order",
            "reset-filter",
            "visible-count",
            "draw-list",
            "load-more",
            "stat-window",
            "frequency-grid",
            "draw-card-template",
        }
        for element_id in required_ids:
            self.assertIn(f'id="{element_id}"', self.html, element_id)

    def test_browser_reads_only_generated_archive_index(self):
        self.assertIn('fetch("./data/archive_index.json"', self.javascript)
        self.assertNotIn("smok95.github.io", self.javascript)
        self.assertNotIn("dhlottery.co.kr", self.javascript)

    def test_number_color_ranges_are_present(self):
        for css_class in ("ball-yellow", "ball-blue", "ball-red", "ball-gray", "ball-green"):
            self.assertIn(css_class, self.css)
            self.assertIn(css_class, self.javascript)

    def test_archive_explains_statistics_are_not_predictions(self):
        self.assertIn("다음 회차의 당첨확률 우위를 의미하지 않습니다", self.html)

    def test_gate_one_does_not_expose_active_prediction_button(self):
        index_html = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
        self.assertIn("예측 엔진 준비 중", index_html)
        self.assertIn("disabled", index_html)


if __name__ == "__main__":
    unittest.main()
