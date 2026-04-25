import re
from collections import Counter
from agent.utils import call_llm, call_llm_turns, extract_final_answer


def chain_of_thought(question):
    prompt = f"Solve this problem step by step.\nWrite your final answer on a new line starting with 'Answer:'\n\nProblem: {question}"
    response = call_llm(prompt, temperature=0.3, max_tokens=1024)
    return extract_final_answer(response)


def self_consistency(question, n=5):
    prompt = f"Solve this problem step by step.\nWrite your final answer on a new line starting with 'Answer:'\n\nProblem: {question}"
    answers = []
    for _ in range(n):
        response = call_llm(prompt, temperature=0.7, max_tokens=1024)
        answer = extract_final_answer(response)
        if answer:
            answers.append(answer.lower().strip())
    if not answers:
        return None
    return Counter(answers).most_common(1)[0][0]


def detect_domain(question):
    prompt = f"Classify this problem into exactly one of these domains:\nmath, logic, commonsense, coding, science, other\n\nProblem: {question}\n\nReply with just the domain name, nothing else."
    response = call_llm(prompt, temperature=0.0, max_tokens=10)
    if not response:
        return "other"
    response = response.lower().strip()
    for domain in {"math", "logic", "commonsense", "coding", "science", "other"}:
        if domain in response:
            return domain
    return "other"


def self_refine(question):
    first = call_llm(
        f"Solve this problem step by step.\nWrite your final answer on a new line starting with 'Answer:'\n\nProblem: {question}",
        temperature=0.3,
        max_tokens=1024
    )
    if not first:
        return None
    refined = call_llm(
        f"Here is a problem and an attempted solution. Find any mistakes and give a better solution.\nAt the end write your final answer starting with 'Answer:'\n\nProblem: {question}\n\nAttempt: {first}",
        temperature=0.3,
        max_tokens=1024
    )
    return extract_final_answer(refined) if refined else extract_final_answer(first)


def react(question):
    history = [
        {"role": "system", "content": "You are a problem solver. You can reason and use tools. Available tools: calculator(expr), search(query). When you want to use a tool write TOOL: calculator(2+2) or TOOL: search(query). When you have the final answer write Answer: <answer>"},
        {"role": "user", "content": f"Solve this: {question}"}
    ]
    for _ in range(4):
        response = call_llm_turns(history, temperature=0.3, max_tokens=512)
        if not response:
            break
        history.append({"role": "assistant", "content": response})
        if "answer:" in response.lower():
            return extract_final_answer(response)
        if "TOOL: calculator(" in response:
            expr = re.search(r'calculator\((.+?)\)', response)
            if expr:
                try:
                    result = str(eval(expr.group(1)))
                except:
                    result = "error"
                history.append({"role": "user", "content": f"Tool result: {result}"})
        elif "TOOL: search(" in response:
            history.append({"role": "user", "content": "Tool result: no search available, reason from your knowledge"})
    return extract_final_answer(history[-1]["content"]) if history else None


def tree_of_thought(question):
    branches = call_llm(
        f"Generate 3 different approaches to solve this problem. Number them 1, 2, 3. Just the approaches, no full solution yet.\n\nProblem: {question}",
        temperature=0.7,
        max_tokens=512
    )
    if not branches:
        return chain_of_thought(question)
    result = call_llm(
        f"Here are 3 approaches to solve a problem. Pick the most promising one and solve it fully.\nEnd with 'Answer: <your answer>'\n\nProblem: {question}\n\nApproaches:\n{branches}",
        temperature=0.3,
        max_tokens=1024
    )
    return extract_final_answer(result) if result else None