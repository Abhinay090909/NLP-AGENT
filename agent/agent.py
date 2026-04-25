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
        answer = self_consistency(question, n=2)

    elif domain == "logic":
        answer = tree_of_thought(question)

    elif domain == "coding":
        answer = call_llm(
            f"Write only the code body, no explanation, no markdown, no backticks, no function signature. Start from the first line inside the function.\n\n{question}",
            temperature=0.0,
            max_tokens=1500
        )
        answer = answer.strip() if answer else ""

    elif domain == "common_sense":
        q_lower = question.strip().lower()
        first_word = q_lower.split()[0]
        
        bool_starters = {"was", "would", "are", "does", "will", "did", "can", "is", "do", "could", "were", "has", "have", "had"}
        
        if first_word in bool_starters:
            answer = call_llm(
                f"Answer with only True or False, nothing else.\n\nQuestion: {question}",
                temperature=0.0,
                max_tokens=10
            )
            answer = clean_answer(answer) if answer else ""
        else:
            answer = call_llm(
                f"Answer in as few words as possible, ideally one to four words. No full sentences. No explanation.\n\nQuestion: {question}",
                temperature=0.0,
                max_tokens=64
            )
            answer = clean_answer(answer) if answer else ""

    elif domain == "future_prediction":
        answer = call_llm(
            f"Make your best prediction based on available knowledge. You MUST end your response with exactly: \\boxed{{YOUR_PREDICTION}}\n\n{question}",
            temperature=0.3,
            max_tokens=256
        )
        answer = clean_answer(answer) if answer else ""

    elif domain == "planning":
        answer = call_llm(
            f"Return only the sequence of actions, one per line, nothing else.\n\n{question}",
            temperature=0.0,
            max_tokens=1500
        )
        answer = answer.strip() if answer else ""

    elif domain == "science":
        answer = least_to_most(question)

    else:
        answer = chain_of_thought(question)

    print(f"[agent] calls used: {get_call_count()} | answer: {answer}")
    return answer