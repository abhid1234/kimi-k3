import unittest

from app.schemas import PlanRequest, PlanResponse, PlanStep


class SchemaTests(unittest.TestCase):
    def test_plan_request_min_length(self) -> None:
        with self.assertRaises(ValueError):
            PlanRequest(goal="too short")

    def test_plan_request_valid(self) -> None:
        req = PlanRequest(
            goal="Build an MVP scheduling flow for a small team.",
            constraints="no external DB",
            context="solo developer",
            tone="concise",
        )
        self.assertEqual(req.tone, "concise")

    def test_plan_response_shape(self) -> None:
        payload = {
            "summary": "Ship an MVP quickly.",
            "assumptions": ["Assume cloud infra available."],
            "plan": [{"step": 1, "action": "Draft scope", "why": "focus", "risk": "low"}],
            "risks": ["Scope drift"],
            "next_actions": ["Write first ticket"],
            "confidence": "medium",
        }
        parsed = PlanResponse.model_validate(payload)
        self.assertIsInstance(parsed.plan[0], PlanStep)
        self.assertEqual(parsed.plan[0].step, 1)


if __name__ == "__main__":
    unittest.main()
