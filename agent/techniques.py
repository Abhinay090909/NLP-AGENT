import re
from collections import Counter
from agent.utils import call_llm, call_llm_turns, extract_final_answer, clean_answer, clean_code


def chain_of_thought(question):
    prompt = f"Think step by step to solve this problem. You MUST end your response with 'Final Answer: ' followed by only the answer, nothing else.\n\nQuestion: {question}"
    response = call_llm(prompt, temperature=0.3, max_tokens=1500)
    return extract_final_answer(response)


def self_consistency(question, n=3):
    prompt = f"Think step by step to solve this problem. You MUST end your response with 'Final Answer: ' followed by only the answer, nothing else.\n\nQuestion: {question}"
    answers = []
    for _ in range(n):
        response = call_llm(prompt, temperature=0.7, max_tokens=2000)
        if response:
            ans = extract_final_answer(response)
            if ans:
                answers.append(ans)
    if not answers:
        return None
    return Counter(answers).most_common(1)[0][0]


def detect_domain(question):
    q = question.strip()
    
    if "You are an agent that can predict future events" in q:
        return "future_prediction"
    
    if "[PLAN]" in q:
        return "planning"
    
    if "```" in q or "You should write self-contained code starting with" in q:
        return "coding"
    
    if "$" in q or "\\" in q or "<<" in q:
        return "math"
    
    return "common_sense"

def self_refine(question):
    first = call_llm(
        f"Solve this problem step by step. At the end write 'Final Answer: ' followed by just the answer.\n\nQuestion: {question}",
        temperature=0.3, max_tokens=512
    )
    first_ans = extract_final_answer(first)
    refined = call_llm(
        f"Review this solution. Check for calculation errors, wrong assumptions, or missing steps. If correct keep the answer, if wrong fix it. At the end write 'Final Answer: ' followed by just the answer.\n\nQuestion: {question}\nSolution: {first}\nAnswer: {first_ans}",
        temperature=0.3, max_tokens=512
    )
    return extract_final_answer(refined) if refined else first_ans


def react(question):
    history = [
        {"role": "system", "content": "You are a problem solver. Available tools: calculator(expr). Write TOOL: calculator(expr) to use it. When done write 'Final Answer: ' followed by just the answer."},
        {"role": "user", "content": f"Solve this: {question}"}
    ]
    for _ in range(4):
        response = call_llm_turns(history, temperature=0.3, max_tokens=1024)
        if not response:
            break
        history.append({"role": "assistant", "content": response})
        if "final answer:" in response.lower():
            return extract_final_answer(response)
        match = re.search(r'TOOL:\s*calculator\((.+?)\)', response, re.IGNORECASE)
        if match:
            try:
                result = str(eval(match.group(1)))
            except:
                result = "error"
            history.append({"role": "user", "content": f"Tool result: {result}"})
    return extract_final_answer(history[-1]["content"]) if history else None


def tree_of_thought(question):
    branches = call_llm(
        f"Generate 3 different approaches to solve this problem. Number them 1, 2, 3. For each approach show the reasoning and the answer you get.\n\nProblem: {question}",
        temperature=0.7, max_tokens=768
    )
    if not branches:
        return chain_of_thought(question)
    result = call_llm(
        f"Here are 3 approaches to a problem. Pick the most convincing one and state the final answer. At the end write 'Final Answer: ' followed by just the answer.\n\nProblem: {question}\n\nApproaches:\n{branches}",
        temperature=0.3, max_tokens=1024
    )
    return extract_final_answer(result) if result else None


def decomposition(question):
    prompt = f"Break this problem into numbered sub-problems. Solve each one. At the end write 'Final Answer: ' followed by just the answer.\n\nQuestion: {question}"
    response = call_llm(prompt, temperature=0.3, max_tokens=512)
    return extract_final_answer(response)


def least_to_most(question):
    simpler = call_llm(
        f"What simpler sub-problems need to be solved first to answer this? List them briefly.\n\nProblem: {question}",
        temperature=0.3, max_tokens=512
    )
    if not simpler:
        return chain_of_thought(question)
    result = call_llm(
        f"Solve each sub-problem in order then answer the main problem. At the end write 'Final Answer: ' followed by just the answer.\n\nMain problem: {question}\nSub-problems: {simpler}",
        temperature=0.3, max_tokens=512
    )
    return extract_final_answer(result) if result else None

def answer_verification(question, answer):
    check = call_llm(
        f"Is this answer correct? Reply CORRECT if it is. If wrong, reply with just the correct answer and nothing else.\n\nQuestion: {question}\nAnswer: {answer}",
        temperature=0.0, max_tokens=256
    )
    if not check:
        return answer
    if "CORRECT" in check.upper():
        return answer
    corrected = extract_final_answer(check)
    return corrected if corrected else answer

def coding_completion(question):
    prompt = f"Complete this Python function. Return only the function body with proper indentation. No def line, no imports, no code fences, no explanation.\n\n{question}\n\nFunction body:"
    response = call_llm(prompt, temperature=0.2, max_tokens=1024)
    return clean_code(response)