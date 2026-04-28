import re
import time
import requests
from agent.config import api_key, api_base, model_name, request_timeout, sleep_between_calls

call_count = 0


def reset_call_count():
    global call_count
    call_count = 0


def get_call_count():
    return call_count


def call_llm(prompt, system="You are a helpful assistant. Reply with only the final answer—no explanation.", temperature=0.7, max_tokens=1024):
    global call_count
    call_count += 1
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=request_timeout)
        time.sleep(sleep_between_calls)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def call_llm_turns(messages, temperature=0.7, max_tokens=512):
    global call_count
    call_count += 1
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=request_timeout)
        time.sleep(sleep_between_calls)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def clean_answer(text):
    if not text:
        return ""
    text = str(text).strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else text

def extract_final_answer(text):
    if not text:
        return ""
    text = str(text).strip()

    match = re.search(r'####\s*(.+)', text)
    if match:
        return match.group(1).strip()

    match = re.search(r'(?:final answer|answer)\s*[:\-]\s*\**\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip().rstrip('*').strip()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else ""

def clean_code(text):
    if not text:
        return ""
    text = re.sub(r'```[\w]*\n?', '', text)
    text = re.sub(r'```', '', text).strip()
    lines = text.splitlines()
    lines = [l for l in lines if not l.strip().startswith('def ')]
    if not lines:
        return ""
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return ""
    min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
    normalized = []
    for l in lines:
        if l.strip():
            current_indent = len(l) - len(l.lstrip())
            relative_indent = current_indent - min_indent
            normalized.append('    ' + ' ' * relative_indent + l.lstrip())
        else:
            normalized.append('')
<<<<<<< HEAD
    return '\n'.join(normalized)
=======
    return '\n'.join(normalized)

def clean_plan(text):
    if not text:
        return ""
    lines = text.splitlines()
    plan_lines = []
    for l in lines:
        l = l.strip().lower()
        if not l:
            continue
        if l in ['([plan])', '([plan end])']:
            continue
        if l.startswith('(action '):
            l = '(' + l[8:]
        if l.startswith('(use '):
            l = '(' + l[5:]
        l = l.replace(' from ', ' ').replace(' to ', ' ')
        if l.startswith('(') and l.endswith(')'):
            plan_lines.append(l)
        elif l and not l.startswith('-') and not l.startswith('#') and not l[0].isdigit():
            plan_lines.append(f"({l})")
    return '\n'.join(plan_lines)
>>>>>>> dfaa3a1 (fix: improve planning with subtype detection and multi-turn reasoning)
