import time
from agent.utils import reset_call_count, get_call_count
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
        answer = self_consistency(question, n=3)
        if get_call_count() < max_llm_calls - 2:
            answer = answer_verification(question, answer)

    elif domain == "logic":
        answer = tree_of_thought(question)
        if get_call_count() < max_llm_calls - 2:
            answer = answer_verification(question, answer)

    elif domain == "coding":
        answer = react(question)
        if not answer:
            answer = decomposition(question)

    elif domain == "science":
        answer = least_to_most(question)
        if get_call_count() < max_llm_calls - 2:
            answer = answer_verification(question, answer)

    elif domain == "commonsense":
        answer = self_refine(question)

    else:
        answer = chain_of_thought(question)
        if get_call_count() < max_llm_calls - 2:
            answer = self_refine(question)

    print(f"[agent] calls used: {get_call_count()} | answer: {answer}")
    return answer