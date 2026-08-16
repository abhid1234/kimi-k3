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

    def test_hero_structure(self) -> None:
        # hero is a bar (wordmark left / status right) plus a centred stack —
        # not the old single centred cluster
        self.assertIn('class="hero-bar"', self.html)
        self.assertIn('class="hero-status"', self.html)
        self.assertIn('class="hero-kicker"', self.html)
        self.assertIn('class="hero-actions"', self.html)
        for element_id in ("heroCta", "heroSample"):
            self.assertIn(f'id="{element_id}"', self.html, f"missing #{element_id}")
        # secondary CTA renders the bundled sample with no API call
        self.assertIn("function showSamplePlan", self.html)

    def test_action_plan_pack(self) -> None:
        self.assertIn("function renderPack", self.html)
        self.assertIn("function packGrade", self.html)
        self.assertIn("function riskMix", self.html)
        self.assertIn("function firstMoves", self.html)
        self.assertIn("function copyPackSummary", self.html)
        self.assertIn('id="copyPack"', self.html)
        for cls in (".pack-meter", ".pack-grade", ".mix", ".moves", ".facet"):
            self.assertIn(cls, self.html, f"missing pack style {cls}")
        for grade in ("g-strong", "g-solid", "g-thin"):
            self.assertIn(grade, self.html, f"missing grade class {grade}")
        for sev in ("m-low", "m-medium", "m-high"):
            self.assertIn(sev, self.html, f"missing risk-mix class {sev}")

    def test_plan_strength_score_is_not_saturated(self) -> None:
        """The score must discriminate — a flat 100 makes the meter meaningless."""
        self.assertIn("function computeScore", self.html)
        # the saturating formula (40 + steps * 12) must be gone
        self.assertNotIn("40 + steps * 12", self.html)
        for part in ("depth", "coverage", "specificity", "literacy", "confBonus"):
            self.assertIn(part, self.html, f"missing score component: {part}")

    def test_error_state_preserves_request(self) -> None:
        # a failed run keeps the user's input visible and retries it verbatim
        self.assertIn("error-kept", self.html)
        self.assertIn("kept-goal", self.html)
        self.assertIn('id="retryRun"', self.html)
        self.assertIn("function retryLast", self.html)
        self.assertIn("lastFailure", self.html)
        # retry must not simply re-click the primary button
        self.assertNotIn("document.getElementById('run').click()", self.html)

    def test_hidden_attribute_is_enforced(self) -> None:
        """`display` rules must not defeat [hidden] — it leaked the copy/share
        tools onto the empty, loading and error states."""
        self.assertRegex(self.html, re.compile(r"\[hidden\]\s*\{\s*display:\s*none\s*!important"))

    def test_budget_guard_surface_intact(self) -> None:
        # budget copy stays user-facing and the cap is shown with a currency unit
        self.assertIn("is-budget", self.html)
        self.assertIn("Daily budget reached", self.html)
        self.assertIn("/day cap", self.html)

    def test_share_mode_is_stateful(self) -> None:
        self.assertIn("function copySharePlanLink()", self.html)
        self.assertIn("mode: shareMode", self.html)
        self.assertIn("function sanitizeShareMode", self.html)
        self.assertIn("shareMode", self.html)


if __name__ == "__main__":
    unittest.main()
