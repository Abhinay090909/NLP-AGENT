import time
from agent.utils import reset_call_count, get_call_count, call_llm, clean_answer, clean_plan
from agent.techniques import (
    detect_domain,
    chain_of_thought,
    self_consistency,
    self_refine,
    react,
    tree_of_thought,
    decomposition,
    least_to_most,
    answer_verification,
    coding_completion,
    planning_completion,
    mcq_answer,
    tf_answer,
    context_answer
)
from agent.config import max_llm_calls

def is_garbage(answer):
    if not answer:
        return True
    if any(c in str(answer) for c in ["\\", "$$", "{", "$"]):
        return True
    if not any(c.isdigit() for c in str(answer)):
        return True
    return False

def solve(question, domain=None):
    reset_call_count()

    if not domain:
        domain = detect_domain(question)

    print(f"[agent] domain: {domain} | question: {question[:60]}...")

    if domain == "math":
        answer = self_consistency(question, n=3)
        answer = answer_verification(question, answer)
        if is_garbage(answer):
            answer = call_llm(
                f"Give me only the final answer to this math problem, no explanation, just the number or expression.\n\nProblem: {question}",
                temperature=0.0, max_tokens=256
            )
            answer = clean_answer(answer) if answer else ""

    elif domain == "coding":
        answer = coding_completion(question)

    elif domain == "common_sense":
        if "best answer for the question among these" in question:
            answer = mcq_answer(question)
        elif question.strip().lower().split()[0] in {"was","would","are","does","will","did","can","is","do","could","were","has","have","had"}:
            answer = tf_answer(question)
        elif "answer the question using the context" in question.lower():
            answer = context_answer(question)
        else:
            answer = self_refine(question)
        answer = clean_answer(answer) if answer else ""

    elif domain == "future_prediction":
        answer = chain_of_thought(question)
        answer = clean_answer(answer) if answer else ""

    elif domain == "planning":
        answer = planning_completion(question)

    else:
        answer = self_refine(question)
        # ask model to shorten if answer is too long
        if answer and len(answer.split()) > 8:
            short = call_llm(
                f"Shorten this answer to the key fact only, 1-5 words max.\n\nAnswer: {answer}\nQuestion: {question}",
                temperature=0.0, max_tokens=32
            )
            answer = clean_answer(short) if short else answer
        answer = clean_answer(answer) if answer else ""

    print(f"[agent] calls used: {get_call_count()} | answer: {answer}")
    return answer