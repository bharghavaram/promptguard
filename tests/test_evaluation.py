"""Tests for PromptGuard Evaluation Service."""
import pytest
from unittest.mock import MagicMock, patch
import json


def test_ab_test_winner_logic():
    """Winner is determined by higher average score."""
    with patch("app.services.evaluation_service.OpenAI"), \
         patch("app.services.evaluation_service.Anthropic"), \
         patch("app.services.evaluation_service.LangSmithClient"):
        from app.services.evaluation_service import EvaluationService
        svc = EvaluationService.__new__(EvaluationService)
        svc._ab_tests = {}
        svc._evaluations = {}

        # Mock run_prompt
        svc.run_prompt = MagicMock(return_value={"response": "test", "tokens_used": 10, "run_id": "x", "model": "gpt-4o", "prompt": "p", "timestamp": ""})
        # Mock evaluate_response to return scores
        call_count = [0]
        def mock_eval(prompt, response, expected=None, evaluator_model="gpt-4o"):
            call_count[0] += 1
            score = 8.0 if call_count[0] % 2 == 1 else 6.0  # A scores higher
            return {"eval_id": "e", "prompt": prompt, "response": response, "expected": expected, "scores": {"overall_score": score}, "evaluator_model": evaluator_model, "timestamp": ""}
        svc.evaluate_response = mock_eval

        result = svc.create_ab_test("test", "Prompt A {input}", "Prompt B {input}", ["input1"], "gpt-4o")
        assert result["winner"] == "A"


def test_health_endpoint():
    with patch("app.services.evaluation_service.OpenAI"), \
         patch("app.services.evaluation_service.Anthropic"), \
         patch("app.services.evaluation_service.LangSmithClient"):
        from fastapi.testclient import TestClient
        from main import app
        client = TestClient(app)
        r = client.get("/api/v1/eval/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
