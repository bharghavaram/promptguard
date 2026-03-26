"""PromptGuard – Prompt evaluation and A/B testing routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.services.evaluation_service import EvaluationService, get_evaluation_service

router = APIRouter(prefix="/eval", tags=["Prompt Evaluation"])


class RunPromptRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    system: Optional[str] = None


class EvaluateRequest(BaseModel):
    prompt: str
    response: str
    expected: Optional[str] = None
    evaluator_model: str = "gpt-4o"


class EdgeCaseSuiteRequest(BaseModel):
    prompt_template: str
    test_cases: List[dict]


class ABTestRequest(BaseModel):
    name: str
    prompt_a: str
    prompt_b: str
    test_inputs: List[str]
    model: str = "gpt-4o"


@router.post("/run")
async def run_prompt(
    request: RunPromptRequest,
    service: EvaluationService = Depends(get_evaluation_service),
):
    """Run a prompt against a specified LLM model."""
    return service.run_prompt(request.prompt, request.model, request.system)


@router.post("/evaluate")
async def evaluate_response(
    request: EvaluateRequest,
    service: EvaluationService = Depends(get_evaluation_service),
):
    """Evaluate a prompt-response pair using LLM-as-judge scoring."""
    return service.evaluate_response(
        request.prompt, request.response, request.expected, request.evaluator_model
    )


@router.post("/suite")
async def run_edge_case_suite(
    request: EdgeCaseSuiteRequest,
    service: EvaluationService = Depends(get_evaluation_service),
):
    """Run an edge case test suite against a prompt template."""
    if not request.test_cases:
        raise HTTPException(status_code=400, detail="At least one test case required.")
    return service.run_edge_case_suite(request.prompt_template, request.test_cases)


@router.post("/ab-test")
async def create_ab_test(
    request: ABTestRequest,
    service: EvaluationService = Depends(get_evaluation_service),
):
    """Create and run an A/B test between two prompt variants."""
    if not request.test_inputs:
        raise HTTPException(status_code=400, detail="At least one test input required.")
    return service.create_ab_test(
        request.name, request.prompt_a, request.prompt_b,
        request.test_inputs, request.model
    )


@router.get("/history")
async def get_evaluation_history(service: EvaluationService = Depends(get_evaluation_service)):
    """Get all evaluation history."""
    return {"evaluations": service.get_all_evaluations()}


@router.get("/ab-tests")
async def get_ab_tests(service: EvaluationService = Depends(get_evaluation_service)):
    """Get all A/B test results."""
    return {"ab_tests": service.get_ab_tests()}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "PromptGuard - Prompt Evaluation Framework"}
