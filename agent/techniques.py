import re
from collections import Counter
from agent.utils import call_llm, call_llm_turns, extract_final_answer, clean_answer, clean_code, clean_plan


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

def planning_completion(question):
    is_logistics = "hoist" in question.lower() or "crate" in question.lower()
    
    if is_logistics:
        system = "You are a PDDL planning agent. Output the plan as a sequence of actions. Each line must be exactly: (action hoist crate location) or (drive truck from to) or (load/unload hoist crate truck depot). Use only the exact names from the problem. No extra words."
        user = f"{question}\nComplete the [PLAN]. Output only action lines like: (lift hoist1 crate0 pallet1 depot1)"
    else:
        system = "You are a PDDL planning agent. Study the example plan format carefully and follow it exactly."
        user = f"{question}\nComplete the [PLAN]. Follow the exact format of the example plan shown above."
    
    history = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]
    r1 = call_llm_turns(history, temperature=0.0, max_tokens=2000)
    if not r1:
        return ""
    history.append({"role": "assistant", "content": r1})
    history.append({"role": "user", "content": "Rewrite the final plan only. Each line must be (action arg1 arg2 ...) with exact short names. No 'use', no 'to', no 'from', no 'the', no 'object'. Match the example format exactly."})
    r2 = call_llm_turns(history, temperature=0.0, max_tokens=1024)
    if not r2:
        return clean_plan(r1)
    history.append({"role": "assistant", "content": r2})
    history.append({"role": "user", "content": "Is every action valid given the preconditions? If not fix it. Output only the corrected plan lines."})
    r3 = call_llm_turns(history, temperature=0.0, max_tokens=1024)
    return clean_plan(r3) if r3 else clean_plan(r2)

def mcq_answer(question):
    options = re.findall(r'\d+\)\s+(.+?)(?=\n\d+\)|\Z)', question, re.DOTALL)
    options_clean = [o.strip() for o in options]
    options_formatted = "\n".join(f"{i}) {o}" for i, o in enumerate(options_clean))
    prompt = f"Choose the best answer. Reply with only the option number.\n\nQuestion:\n{question}\n\nOptions:\n{options_formatted}\n\nReply with only the number."
    votes = []
    for _ in range(3):
        response = call_llm(prompt, temperature=0.3, max_tokens=10)
        if response:
            match = re.search(r'\d+', response.strip())
            if match:
                idx = int(match.group())
                if idx < len(options_clean):
                    votes.append(idx)
    if not votes:
        return ""
    best_idx = Counter(votes).most_common(1)[0][0]
    return options_clean[best_idx]


def tf_answer(question):
    prompt = f"Think carefully about this question. Consider all facts before answering.\nAnswer with only True or False, nothing else.\n\nQuestion: {question}"
    response = call_llm(prompt, temperature=0.0, max_tokens=10)
    if not response:
        return ""
    response = response.strip().lower()
    if "true" in response:
        return "True"
    if "false" in response:
        return "False"
    return response


def context_answer(question):
    prompt = f"Answer the question using only the information provided in the context. Return only the answer, nothing else.\n\nQuestion and context:\n{question}"
    response = call_llm(prompt, temperature=0.0, max_tokens=128)
    return clean_answer(response) if response else ""

def future_prediction(question):
    prompt = f"Make your best prediction. At the end write 'Final Answer: ' followed by only the predicted value, no explanation.\n\n{question}"
    response = call_llm(prompt, temperature=0.3, max_tokens=512)
    if not response:
        return "[]"
    boxed = re.search(r'\\boxed\{(.+?)\}', response)
    if boxed:
        answer = boxed.group(1).strip()
    else:
        answer = extract_final_answer(response)
    if not answer:
        return "[]"
    if not answer.startswith('['):
        items = [i.strip() for i in answer.split(',')]
        if len(items) > 1:
            answer = "[" + ", ".join(f"'{i}'" for i in items) + "]"
        else:
            answer = f"['{answer}']"
    if answer.replace('.','').replace('-','').isdigit():
        answer = f"[{answer}]" 
    else:
        if ',' in answer:
            items = [f"'{i.strip()}'" for i in answer.split(',')]
            answer = f"[{', '.join(items)}]"
        else:
            answer = f"['{answer}']"
    return answer