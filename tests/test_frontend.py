"""Contract tests for the static playground UI.

These guard the frontend against regressions without a JS test runner:
required controls, a11y basics, and the risk-elevation visualization all
have to stay present in static/index.html.
"""

import re
import unittest
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "static" / "index.html"


class FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_core_controls_present(self) -> None:
        for element_id in (
            "goal", "constraints", "context", "blocker",
            "run", "runCompare", "runAction",
            "copyPlan", "sharePlan", "toggleRaw", "reloadRuns",
            "status", "runs", "rawJson", "health", "runtimeConfig",
        ):
            self.assertIn(f'id="{element_id}"', self.html, f"missing #{element_id}")

    def test_inputs_are_labelled(self) -> None:
        for field in ("goal", "constraints", "context", "blocker"):
            self.assertIn(f'<label for="{field}">', self.html, f"missing label for #{field}")

    def test_a11y_basics(self) -> None:
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('role="status"', self.html)
        self.assertIn('lang="en"', self.html)
        self.assertIn(":focus-visible", self.html)
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertIn('name="viewport"', self.html)

    def test_risk_badges_cover_all_severities(self) -> None:
        for severity in ("low", "medium", "high"):
            self.assertIn(f".risk-{severity}", self.html, f"missing .risk-{severity} style")

    def test_risk_elevation_strip(self) -> None:
        self.assertIn("function renderRouteStrip", self.html)
        self.assertIn("function activatePlanView", self.html)
        # severity-to-elevation mapping and step sync hooks
        self.assertIn('class="strip"', self.html)
        for cls in ("r-low", "r-medium", "r-high"):
            self.assertRegex(self.html, re.compile(rf"\.strip \.wp\.{cls}"), f"missing strip color for {cls}")
        self.assertIn('pathLength="1"', self.html)
        # strip is announced to assistive tech, dots are keyboard-operable
        self.assertIn("Risk elevation across", self.html)
        self.assertIn('tabindex="0" role="button"', self.html)

    def test_plan_states_exist(self) -> None:
        for marker in ("empty-state", "error-state", "skeleton-route", "history-empty"):
            self.assertIn(marker, self.html, f"missing state: {marker}")

    def test_api_contract_untouched(self) -> None:
        # the frontend must keep posting the same payload shape to the same endpoint
        self.assertIn('fetch("/api/plan"', self.html)
        self.assertIn("{ goal, constraints: constraints || null, context: context || null, tone }", self.html)
        self.assertIn('fetch("/api/config"', self.html)
        self.assertIn("runtimeConfigEl", self.html)


if __name__ == "__main__":
    unittest.main()
