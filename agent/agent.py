import time
from agent.utils import reset_call_count, get_call_count, call_llm, clean_answer
from agent.techniques import (
    detect_domain,
    chain_of_thought,
    self_consistency,
    self_refine,
    react,
    tree_of_thought,
    decomposition,
    least_to_most,
    answer_verification
)
from agent.config import max_llm_calls

def solve(question, domain=None):
    reset_call_count()

    if not domain:
        domain = detect_domain(question)

    print(f"[agent] domain: {domain} | question: {question[:60]}...")

    if domain == "math":
        answer = self_consistency(question, n=1)
        answer = answer_verification(question, answer)

    elif domain == "coding":
        answer = decomposition(question)

    elif domain == "common_sense":
        first_word = question.strip().lower().split()[0]
        bool_starters = {"was","would","are","does","will","did","can","is","do","could","were","has","have","had"}
        if first_word in bool_starters:
            answer = call_llm(f"Answer with only True or False, nothing else.\n\nQuestion: {question}", temperature=0.0, max_tokens=10)
            answer = clean_answer(answer) if answer else ""
        else:
            answer = self_refine(question)
            answer = clean_answer(answer) if answer else ""

    elif domain == "future_prediction":
        answer = chain_of_thought(question)
        answer = clean_answer(answer) if answer else ""

    elif domain == "planning":
        answer = least_to_most(question)
        answer = answer.strip() if answer else ""

    else:
        answer = tree_of_thought(question)
        answer = clean_answer(answer) if answer else ""

    print(f"[agent] calls used: {get_call_count()} | answer: {answer}")
    return answer