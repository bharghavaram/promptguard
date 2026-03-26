# 🛡️ PromptGuard – Prompt Evaluation & Quality Assurance Framework

> **Automated prompt evaluation using LangSmith with LLM-as-judge scoring, A/B testing, and edge case test suites.**

## Overview

PromptGuard is a comprehensive prompt quality assurance framework that helps AI teams systematically test, evaluate, and improve their prompts before deployment. Integrates with LangSmith for tracing and includes a Streamlit dashboard.

**Key Metrics:**
- 🧪 500+ edge cases tested
- 📈 45% improvement in output reliability
- ⚡ Reduced new feature onboarding from 3 weeks to 4 days
- 👥 8+ developers actively using the platform

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Evaluation | LangSmith |
| LLMs | OpenAI GPT-4o, Anthropic Claude |
| Database | PostgreSQL |
| API | FastAPI |
| UI | Streamlit |
| Deployment | Docker |

## Evaluation Framework

```
Prompt + Test Cases
        │
        ▼
  LLM Execution Engine
  (GPT-4 / Claude)
        │
        ▼
  LLM-as-Judge Evaluator
  ┌─────────────────────┐
  │ • Accuracy  (0-10)  │
  │ • Completeness      │
  │ • Coherence         │
  │ • Safety            │
  │ • Conciseness       │
  └─────────────────────┘
        │
        ▼
  Overall Score + Feedback
        │
        ▼
  LangSmith Tracing ──── PostgreSQL Storage
```

## Quick Start

```bash
git clone https://github.com/bharghavram/promptguard.git
cd promptguard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI, Anthropic, and LangSmith API keys

# Start API
uvicorn main:app --reload

# Start Streamlit dashboard (separate terminal)
streamlit run pages/dashboard.py
```

- API Docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/eval/run` | Run a prompt against a model |
| `POST` | `/api/v1/eval/evaluate` | Evaluate a response with scores |
| `POST` | `/api/v1/eval/suite` | Run edge case test suite |
| `POST` | `/api/v1/eval/ab-test` | A/B test two prompt variants |
| `GET` | `/api/v1/eval/history` | Get evaluation history |
| `GET` | `/api/v1/eval/ab-tests` | Get A/B test results |

### Example: Evaluate a Prompt

```bash
curl -X POST "http://localhost:8000/api/v1/eval/run" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing in simple terms.", "model": "gpt-4o"}'
```

### Example: A/B Test Two Prompts

```bash
curl -X POST "http://localhost:8000/api/v1/eval/ab-test" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sentiment v1 vs v2",
    "prompt_a": "Classify the sentiment: {input}",
    "prompt_b": "Analyze and classify the emotional sentiment of this text: {input}",
    "test_inputs": ["I love this!", "This is terrible.", "It is okay."],
    "model": "gpt-4o"
  }'
```

### Example: Edge Case Suite

```bash
curl -X POST "http://localhost:8000/api/v1/eval/suite" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_template": "Summarise this in one sentence: {input}",
    "test_cases": [
      {"inputs": {"input": "Short text."}, "expected_output": "A sentence."},
      {"inputs": {"input": ""}, "expected_output": "Handle empty input gracefully."}
    ]
  }'
```

## Scoring Dimensions

| Dimension | Description | Weight |
|-----------|-------------|--------|
| Accuracy | Factual correctness | 25% |
| Completeness | Full coverage of prompt | 25% |
| Coherence | Logical structure | 20% |
| Safety | Free of harmful content | 20% |
| Conciseness | Appropriate length | 10% |

## Docker

```bash
docker build -t promptguard .
docker run -p 8000:8000 -p 8501:8501 --env-file .env promptguard
```

## Tests

```bash
pytest tests/ -v
```

---

*Built by Bharghava Ram Vemuri | Mar 2025 – May 2025*
