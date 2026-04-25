from openai import OpenAI

API_KEY = "YOUR_API_KEY_HERE"

client = OpenAI(
    base_url="https://openai.rc.asu.edu/v1",
    api_key=API_KEY
)

def call_llm(prompt, system=None, temperature=0.0, max_tokens=200):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="qwen3-30b-a3b-instruct-2507",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "ok": True,
            "text": response.choices[0].message.content.strip(),
            "status": 200
        }

    except Exception as e:
        return {
            "ok": False,
            "text": str(e),
            "status": 500
        }

def llm_text(prompt, system=None, temperature=0.0, max_tokens=200):
    result = call_llm(prompt, system, temperature, max_tokens)
    return result["text"]
