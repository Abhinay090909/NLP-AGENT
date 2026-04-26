import re
from collections import Counter
from agent.utils import call_llm, call_llm_turns, extract_final_answer, clean_answer


def chain_of_thought(question):
    prompt = f"Think step by step in your head.\nDo not show your work.\nReturn only the final answer.\n\nQuestion: {question}"
    response = call_llm(prompt, temperature=0.3, max_tokens=256)
    return clean_answer(response)


def self_consistency(question, n=1):
    prompt = f"Solve this step by step. At the very end write 'Final Answer: X' where X is just the number or answer.\n\nQuestion: {question}"
    answers = []
    for _ in range(n):
        response = call_llm(prompt, temperature=0.3, max_tokens=1500)
        if response:
            ans = extract_final_answer(response)
            if ans:
                answers.append(ans)
    if not answers:
        return None
    return Counter(answers).most_common(1)[0][0]


def detect_domain(question):
    prompt = f"Classify this problem into exactly one of these domains:\nmath, common_sense, coding, future_prediction, planning\n\nProblem: {question}\n\nReply with just the domain name, nothing else."
    response = call_llm(prompt, temperature=0.0, max_tokens=10)
    if not response:
        return "common_sense"
    response = response.lower().strip()
    for domain in {"math", "common_sense", "coding", "future_prediction", "planning"}:
        if domain in response:
            return domain
    return "common_sense"


def self_refine(question):
    first = call_llm(
        f"Solve the problem carefully.\nReturn only the final answer.\n\nQuestion: {question}",
        temperature=0.3, max_tokens=512
    )
    first_ans = clean_answer(first)
    refined = call_llm(
        f"Check this answer carefully.\nIf it is wrong, fix it.\nReturn only the final answer.\n\nQuestion: {question}\nAnswer to check: {first_ans}",
        temperature=0.3, max_tokens=512
    )
    return clean_answer(refined) if refined else first_ans


def react(question):
    history = [
        {"role": "system", "content": "You are a problem solver. Available tools: calculator(expr). Write TOOL: calculator(expr) to use it. When done write Final Answer: <answer>"},
        {"role": "user", "content": f"Solve this: {question}"}
    ]
    for _ in range(4):
        response = call_llm_turns(history, temperature=0.3, max_tokens=512)
        if not response:
            break
        history.append({"role": "assistant", "content": response})
        if "final answer:" in response.lower():
            return extract_final_answer(response)
        if "TOOL: calculator(" in response:
            expr = re.search(r'calculator\((.+?)\)', response)
            if expr:
                try:
                    result = str(eval(expr.group(1)))
                except:
                    result = "error"
                history.append({"role": "user", "content": f"Tool result: {result}"})
    return extract_final_answer(history[-1]["content"]) if history else None


def tree_of_thought(question):
    branches = call_llm(
        f"Generate 3 different approaches to solve this. Number them 1, 2, 3.\n\nProblem: {question}",
        temperature=0.7, max_tokens=512
    )
    if not branches:
        return chain_of_thought(question)
    result = call_llm(
        f"Pick the best approach and solve fully.\nReturn only the final answer.\n\nProblem: {question}\n\nApproaches:\n{branches}",
        temperature=0.3, max_tokens=512
    )
    return clean_answer(result) if result else None


def decomposition(question):
    result = call_llm(
        f"Break this problem into smaller steps.\nSolve each part carefully in your head.\nReturn only the final answer.\n\nQuestion: {question}",
        temperature=0.3, max_tokens=512
    )
    return clean_answer(result)


def least_to_most(question):
    simpler = call_llm(
        f"What simpler problems must be solved first? List them briefly.\n\nProblem: {question}",
        temperature=0.3, max_tokens=256
    )
    if not simpler:
        return chain_of_thought(question)
    result = call_llm(
        f"Solve the simpler problems first then answer the main one.\nReturn only the final answer.\n\nMain problem: {question}\nSimpler problems: {simpler}",
        temperature=0.3, max_tokens=512
    )
    return clean_answer(result) if result else None


def answer_verification(question, answer):
    check = call_llm(
        f"Is this answer correct? Reply CORRECT or give the right answer only.\n\nQuestion: {question}\nAnswer: {answer}",
        temperature=0.0, max_tokens=256
    )
    if not check:
        return answer
    if "CORRECT" in check.upper():
        return answer
    return clean_answer(check)