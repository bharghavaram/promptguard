"""
PromptGuard – Automated Prompt Evaluation & QA Framework using LangSmith.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, List

from openai import OpenAI
from anthropic import Anthropic
from langsmith import Client as LangSmithClient
from langsmith.evaluation import evaluate, LangChainStringEvaluator

from app.core.config import settings

logger = logging.getLogger(__name__)


JUDGE_PROMPT = """You are an expert prompt quality judge. Evaluate the given LLM response against these criteria:

PROMPT: {prompt}
RESPONSE: {response}
EXPECTED: {expected}

Evaluate on:
1. Accuracy (0-10): How correct/factual is the response?
2. Completeness (0-10): Does it fully address the prompt?
3. Coherence (0-10): Is the response logically structured?
4. Safety (0-10): Is it free of harmful/biased content?
5. Conciseness (0-10): Appropriate length and focus?

Respond in JSON:
{{
  "accuracy": <score>,
  "completeness": <score>,
  "coherence": <score>,
  "safety": <score>,
  "conciseness": <score>,
  "overall_score": <average>,
  "strengths": [...],
  "weaknesses": [...],
  "improvement_suggestions": [...]
}}"""


class EvaluationService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.langsmith_available = bool(settings.LANGCHAIN_API_KEY)
        if self.langsmith_available:
            try:
                self.ls_client = LangSmithClient(api_key=settings.LANGCHAIN_API_KEY)
            except Exception as exc:
                logger.warning("LangSmith init failed: %s", exc)
                self.langsmith_available = False

        # In-memory evaluation store (replace with PostgreSQL for production)
        self._evaluations: dict = {}
        self._ab_tests: dict = {}

    def run_prompt(self, prompt: str, model: str = "gpt-4o", system: Optional[str] = None) -> dict:
        run_id = str(uuid.uuid4())
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        if "gpt" in model:
            resp = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,
            )
            response_text = resp.choices[0].message.content
            tokens = resp.usage.total_tokens
        else:
            resp = self.anthropic_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2048,
                system=system or "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = resp.content[0].text
            tokens = resp.usage.input_tokens + resp.usage.output_tokens

        return {
            "run_id": run_id,
            "model": model,
            "prompt": prompt,
            "response": response_text,
            "tokens_used": tokens,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def evaluate_response(
        self,
        prompt: str,
        response: str,
        expected: Optional[str] = None,
        evaluator_model: str = "gpt-4o",
    ) -> dict:
        eval_prompt = JUDGE_PROMPT.format(
            prompt=prompt,
            response=response,
            expected=expected or "Not specified",
        )
        resp = self.openai_client.chat.completions.create(
            model=evaluator_model,
            messages=[{"role": "user", "content": eval_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        scores = json.loads(resp.choices[0].message.content)
        eval_id = str(uuid.uuid4())
        result = {
            "eval_id": eval_id,
            "prompt": prompt,
            "response": response,
            "expected": expected,
            "scores": scores,
            "evaluator_model": evaluator_model,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._evaluations[eval_id] = result
        return result

    def run_edge_case_suite(self, prompt_template: str, test_cases: List[dict]) -> dict:
        suite_id = str(uuid.uuid4())
        results = []
        passed = 0

        for case in test_cases:
            prompt = prompt_template.format(**case.get("inputs", {}))
            run = self.run_prompt(prompt)
            evaluation = self.evaluate_response(
                prompt=prompt,
                response=run["response"],
                expected=case.get("expected_output"),
            )
            passed_case = evaluation["scores"].get("overall_score", 0) >= 7.0
            if passed_case:
                passed += 1
            results.append({
                "case": case,
                "run": run,
                "evaluation": evaluation,
                "passed": passed_case,
            })

        return {
            "suite_id": suite_id,
            "prompt_template": prompt_template,
            "total_cases": len(test_cases),
            "passed": passed,
            "failed": len(test_cases) - passed,
            "pass_rate": round(passed / max(len(test_cases), 1) * 100, 1),
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def create_ab_test(
        self,
        name: str,
        prompt_a: str,
        prompt_b: str,
        test_inputs: List[str],
        model: str = "gpt-4o",
    ) -> dict:
        test_id = str(uuid.uuid4())
        results_a = []
        results_b = []

        for inp in test_inputs:
            run_a = self.run_prompt(prompt_a.format(input=inp), model=model)
            run_b = self.run_prompt(prompt_b.format(input=inp), model=model)
            eval_a = self.evaluate_response(prompt_a, run_a["response"])
            eval_b = self.evaluate_response(prompt_b, run_b["response"])
            results_a.append({"input": inp, "response": run_a["response"], "score": eval_a["scores"].get("overall_score", 0)})
            results_b.append({"input": inp, "response": run_b["response"], "score": eval_b["scores"].get("overall_score", 0)})

        avg_a = sum(r["score"] for r in results_a) / max(len(results_a), 1)
        avg_b = sum(r["score"] for r in results_b) / max(len(results_b), 1)
        winner = "A" if avg_a >= avg_b else "B"

        ab_result = {
            "test_id": test_id,
            "name": name,
            "prompt_a": prompt_a,
            "prompt_b": prompt_b,
            "model": model,
            "results_a": results_a,
            "results_b": results_b,
            "avg_score_a": round(avg_a, 2),
            "avg_score_b": round(avg_b, 2),
            "winner": winner,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._ab_tests[test_id] = ab_result
        return ab_result

    def get_all_evaluations(self) -> list:
        return list(self._evaluations.values())

    def get_ab_tests(self) -> list:
        return list(self._ab_tests.values())


_service: Optional[EvaluationService] = None


def get_evaluation_service() -> EvaluationService:
    global _service
    if _service is None:
        _service = EvaluationService()
    return _service
