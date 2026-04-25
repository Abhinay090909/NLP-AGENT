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


def call_llm(prompt, system="You are a helpful assistant.", temperature=0.7, max_tokens=1024):
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


def extract_final_answer(text):
    if not text:
        return ""
    match = re.search(r'(?:answer|result)\s*[:\-]\s*(.+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    return lines[-1] if lines else text.strip()