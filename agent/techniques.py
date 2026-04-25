# agent/techniques.py
import re
from collections import Counter
from agent.utils import call_llm, extract_final_answer


# ── Technique 1: Chain of Thought ──────────────────────────────────────────
def chain_of_thought(question):
    """Ask the model to reason step by step before giving a final answer."""
    prompt = f"""Solve the following problem step by step.
At the end, write your final answer on a new line starting with 'Answer:'.

Problem: {question}"""

    response = call_llm(prompt, temperature=0.3, max_tokens=1024)
    return extract_final_answer(response)


# ── Technique 2: Self Consistency ──────────────────────────────────────────
def self_consistency(question, n=5):
    """
    Generate n independent answers with CoT and majority vote.
    More reliable than a single pass for math and logic.
    """
    prompt = f"""Solve the following problem step by step.
At the end, write your final answer on a new line starting with 'Answer:'.

Problem: {question}"""

    answers = []
    for _ in range(n):
        response = call_llm(prompt, temperature=0.7, max_tokens=1024)
        answer = extract_final_answer(response)
        if answer:
            answers.append(answer.lower().strip())

    if not answers:
        return None

    # return the most common answer
    most_common = Counter(answers).most_common(1)[0][0]
    return most_common


# ── Technique 3: Domain Routing ────────────────────────────────────────────
def detect_domain(question):
    """
    Use one LLM call to classify the domain so we can pick the best strategy.
    Returns one of: math, logic, commonsense, coding, science, other
    """
    prompt = f"""Classify this problem into exactly one of these domains:
math, logic, commonsense, coding, science, other

Problem: {question}

Reply with just the domain name, nothing else."""

    response = call_llm(prompt, temperature=0.0, max_tokens=10)
    if not response:
        return "other"

    response = response.lower().strip()
    valid = {"math", "logic", "commonsense", "coding", "science", "other"}
    for domain in valid:
        if domain in response:
            return domain
    return "other"