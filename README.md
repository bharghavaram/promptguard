> **📅 Period:** Mar 2025 – May 2025 &nbsp;|&nbsp; **Author:** [Bharghava Ram Vemuri](https://github.com/bharghavaram)

<div align="center">

# 🛡️ PromptGuard

### Prompt Evaluation & QA Framework · LangSmith + OpenAI + Anthropic + Streamlit

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![CI](https://github.com/bharghavaram/promptguard/actions/workflows/ci.yml/badge.svg)](https://github.com/bharghavaram/promptguard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![LangSmith](https://img.shields.io/badge/LangSmith-Evaluation-orange?style=flat)](https://smith.langchain.com)

</div>

---

<div align="center">
  <img src="https://raw.githubusercontent.com/bharghavaram/promptguard/main/docs/images/demo.svg" alt="promptguard demo" width="820"/>
</div>

--- 🎯 Problem Statement

Teams deploy prompts to production without systematic testing — a prompt change that improves performance for one use case silently breaks three others. Evaluating LLM outputs requires expensive human review and lacks reproducibility. PromptGuard provides automated prompt evaluation: A/B testing infrastructure, LangSmith-integrated evaluation pipelines, multi-model comparison (GPT-4o vs Claude vs Mistral), 500+ edge case test suites, and regression detection — reducing new feature onboarding from 3 weeks to 4 days.

---

## 🏗️ Architecture

```
Prompt Candidate (A vs B)
        │
   ┌────▼────────────────────────────────────┐
   │  Test Suite Runner                      │
   │  500+ edge cases: factual · creative    │
   │  · edge · adversarial · multilingual    │
   └────┬────────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────────┐
   │  Multi-Model Evaluator                    │
   │  GPT-4o · Claude 3.5 · Mistral           │
   └────┬──────────────────────────────────────┘
        │
   LangSmith Evaluation Pipeline
   (correctness · coherence · toxicity · latency)
        │
   A/B Result + Regression Detection
   + Streamlit Dashboard
```

---

## 📁 Project Structure

```
promptguard/
├── main.py
├── app/
│   ├── services/
│   │   ├── eval_service.py        # Core evaluation orchestration
│   │   ├── langsmith_service.py   # LangSmith integration
│   │   ├── ab_service.py          # A/B testing framework
│   │   ├── regression_service.py  # Regression detection
│   │   └── metrics_service.py     # BLEU/ROUGE/coherence metrics
│   └── api/routes/
│       ├── evaluate.py
│       ├── ab_test.py
│       └── reports.py
├── pages/                         # Streamlit evaluation dashboard
├── tests/
├── Dockerfile
├── .env.example
└── requirements.txt
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/bharghavaram/promptguard.git
cd promptguard
pip install -r requirements.txt
cp .env.example .env   # Add OPENAI_API_KEY + LANGCHAIN_API_KEY
uvicorn main:app --reload
```

---

## 🤖 Model & Algorithm Details

| Metric | Measurement Method |
|--------|-------------------|
| Correctness | LLM-as-judge (GPT-4o rates 1–5) |
| Coherence | BERTScore + readability metrics |
| Toxicity | Perspective API + keyword filter |
| Latency | P50/P95 per model |
| Regression | >10% drop in correctness triggers alert |
| A/B Winner | Statistical significance (p<0.05, t-test) |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/evaluate/prompt` | Evaluate single prompt on test suite |
| POST | `/ab-test/start` | Start A/B test (prompt A vs B) |
| GET | `/ab-test/{id}/results` | A/B test winner + confidence |
| POST | `/regression/check` | Check prompt for regression vs baseline |
| GET | `/metrics/history` | Historical evaluation metrics |

---

## 💡 Sample Input → Output

```json
{
  "prompt_a_score": {"correctness":3.8,"coherence":0.81,"toxicity":0.02,"latency_p95_ms":834},
  "prompt_b_score": {"correctness":4.3,"coherence":0.89,"toxicity":0.01,"latency_p95_ms":912},
  "winner": "prompt_b",
  "improvement": "+13.2% correctness, +9.9% coherence",
  "statistical_significance": 0.031,
  "recommendation": "Deploy prompt_b — statistically significant improvement at p=0.031",
  "regressions_detected": 0,
  "test_cases_run": 500
}
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Test cases in library | 500+ |
| Evaluation speed | 100 test cases/minute |
| Regression detection accuracy | 94% |
| Feature onboarding time | 3 weeks → 4 days |
| Models supported | GPT-4o · Claude 3.5 · Mistral · Llama-3 |

---

## 🧪 Testing · 🗺️ Roadmap · 📄 License

```bash
pytest tests/ -v
```
**Roadmap:** Custom evaluation rubrics · Prompt versioning + rollback · Continuous evaluation in CI/CD · Team collaboration with shared test libraries

MIT License — see [LICENSE](LICENSE). Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
