API_KEY  = CREATE FROM Voyager Portal
API_BASE = "https://openai.rc.asu.edu/v1"
MODEL    = "qwen3-30b-a3b-instruct-2507"


def call_llm(prompt, system="You are a helpful assistant.", temperature=0.0, max_tokens=512):
    url = f"{API_BASE}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    for _ in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=90)
            if r.status_code == 200:
                time.sleep(0.1)
                return r.json()["choices"][0]["message"]["content"]
            time.sleep(3)
        except Exception as e:
            print(f"[WARN] {e}", file=sys.stderr)
            time.sleep(3)
    return ""

def tree_of_thought(question, domain, branches=3):
    approaches = [
        call_llm(
            f"Suggest ONE distinct approach #{i+1} (no solution yet):\n{question}",
            system=SYSTEM[domain], temperature=0.7, max_tokens=150
        )
        for i in range(branches)
    ]
    scores = []
    for a in approaches:
        r = call_llm(
            f"Problem: {question}\nApproach: {a}\nRate 1-10. Reply with only a number.",
            system="Reply with only a single integer.", max_tokens=5
        )
        nums = re.findall(r"\d+", r)
        scores.append(int(nums[0]) if nums else 5)
    best = approaches[scores.index(max(scores))]
    return call_llm(
        f"Problem: {question}\nUse this approach:\n{best}\n\nSolve fully and state the final answer.",
        system=SYSTEM[domain], max_tokens=512
    )

def verify(question, answer):
    r = call_llm(
        f"Q: {question}\nA: {answer}\nIs this correct? Reply True or False only.",
        system="Reply with exactly True or False.", max_tokens=5
    )
    return r.strip().lower().startswith("true")
