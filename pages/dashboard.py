"""PromptGuard – Streamlit Dashboard."""
import streamlit as st
import httpx
import json

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="PromptGuard", page_icon="🛡️", layout="wide")
st.title("🛡️ PromptGuard – Prompt Evaluation & QA Framework")
st.markdown("Test, evaluate, and compare your LLM prompts with automated scoring and A/B testing.")

tab1, tab2, tab3, tab4 = st.tabs(["▶️ Run & Evaluate", "🧪 Edge Case Suite", "⚔️ A/B Testing", "📊 History"])

with tab1:
    st.header("Run Prompt & Evaluate")
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "claude"])
        system_msg = st.text_area("System Message (optional)", height=80)
    with col2:
        expected = st.text_area("Expected Output (optional, for scoring)", height=80)

    prompt = st.text_area("Prompt", height=150, placeholder="Enter your prompt here...")

    if st.button("▶️ Run & Evaluate") and prompt:
        with st.spinner("Running prompt and evaluating..."):
            try:
                run_r = httpx.post(f"{API_URL}/eval/run", json={"prompt": prompt, "model": model, "system": system_msg or None}, timeout=60)
                run_result = run_r.json()
                st.markdown("### Response")
                st.write(run_result.get("response", ""))
                st.caption(f"Tokens used: {run_result.get('tokens_used', 0)}")

                eval_r = httpx.post(f"{API_URL}/eval/evaluate", json={"prompt": prompt, "response": run_result["response"], "expected": expected or None}, timeout=60)
                eval_result = eval_r.json()
                scores = eval_result.get("scores", {})

                st.markdown("### Quality Scores")
                cols = st.columns(5)
                for i, (metric, val) in enumerate(scores.items()):
                    if isinstance(val, (int, float)):
                        cols[i % 5].metric(metric.replace("_", " ").title(), f"{val}/10")

                if scores.get("improvement_suggestions"):
                    st.markdown("#### Improvement Suggestions")
                    for s in scores["improvement_suggestions"]:
                        st.write(f"• {s}")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.header("Edge Case Test Suite")
    template = st.text_area("Prompt Template (use {input} placeholder)", placeholder="Classify the sentiment of: {input}")
    test_cases_json = st.text_area(
        "Test Cases (JSON array)",
        height=200,
        value='[\n  {"inputs": {"input": "I love this product!"}, "expected_output": "positive"},\n  {"inputs": {"input": "This is terrible."}, "expected_output": "negative"}\n]',
    )
    if st.button("🧪 Run Suite") and template:
        try:
            test_cases = json.loads(test_cases_json)
            with st.spinner("Running edge case suite..."):
                r = httpx.post(f"{API_URL}/eval/suite", json={"prompt_template": template, "test_cases": test_cases}, timeout=180)
                result = r.json()
                st.metric("Pass Rate", f"{result.get('pass_rate', 0)}%")
                col1, col2 = st.columns(2)
                col1.metric("Passed", result.get("passed", 0))
                col2.metric("Failed", result.get("failed", 0))
        except json.JSONDecodeError:
            st.error("Invalid JSON in test cases.")
        except Exception as e:
            st.error(f"Error: {e}")

with tab3:
    st.header("A/B Prompt Testing")
    test_name = st.text_input("Test Name", placeholder="Sentiment v1 vs v2")
    col1, col2 = st.columns(2)
    with col1:
        prompt_a = st.text_area("Prompt A", placeholder="Classify the text: {input}", height=100)
    with col2:
        prompt_b = st.text_area("Prompt B", placeholder="What is the sentiment of this text: {input}", height=100)
    inputs_text = st.text_area("Test Inputs (one per line)", placeholder="I love this!\nThis is awful.\nMeh, it's okay.")

    if st.button("⚔️ Run A/B Test") and test_name and prompt_a and prompt_b and inputs_text:
        inputs = [line.strip() for line in inputs_text.strip().split("\n") if line.strip()]
        with st.spinner("Running A/B test..."):
            try:
                r = httpx.post(f"{API_URL}/eval/ab-test", json={"name": test_name, "prompt_a": prompt_a, "prompt_b": prompt_b, "test_inputs": inputs}, timeout=180)
                result = r.json()
                col1, col2, col3 = st.columns(3)
                col1.metric("Prompt A Score", result.get("avg_score_a", 0))
                col2.metric("Prompt B Score", result.get("avg_score_b", 0))
                col3.metric("Winner", f"Prompt {result.get('winner', '?')}")
            except Exception as e:
                st.error(f"Error: {e}")

with tab4:
    st.header("Evaluation History")
    if st.button("🔄 Refresh"):
        try:
            r = httpx.get(f"{API_URL}/eval/history", timeout=30)
            evals = r.json().get("evaluations", [])
            st.write(f"Total evaluations: {len(evals)}")
            for ev in evals[-10:]:
                with st.expander(f"Eval {ev.get('eval_id', '')[:8]}... – Score: {ev.get('scores', {}).get('overall_score', 'N/A')}"):
                    st.json(ev)
        except Exception as e:
            st.error(f"Error: {e}")
