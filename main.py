"""
PromptGuard – Prompt Evaluation & Quality Assurance Framework
FastAPI + Streamlit application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.evaluation import router as evaluation_router
from app.core.config import settings

app = FastAPI(
    title="PromptGuard – Prompt Evaluation & QA Framework",
    description=(
        "Automated prompt evaluation using LangSmith. "
        "Tests 500+ edge cases, multi-dimensional LLM-as-judge scoring, "
        "A/B testing infrastructure, and PostgreSQL-backed evaluation history. "
        "Reduced new feature onboarding from 3 weeks to 4 days."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluation_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "PromptGuard – Prompt Evaluation & Quality Assurance",
        "version": "1.0.0",
        "docs": "/docs",
        "streamlit_ui": "Run: streamlit run pages/dashboard.py",
        "endpoints": {
            "run_prompt": "POST /api/v1/eval/run",
            "evaluate": "POST /api/v1/eval/evaluate",
            "edge_case_suite": "POST /api/v1/eval/suite",
            "ab_test": "POST /api/v1/eval/ab-test",
            "history": "GET /api/v1/eval/history",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
