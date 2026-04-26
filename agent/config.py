import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
api_base = os.getenv("API_BASE", "https://openai.rc.asu.edu/v1")
model_name = os.getenv("MODEL_NAME", "qwen3-30b-a3b-instruct-2507")

max_llm_calls = 20
request_timeout = 60
sleep_between_calls = 0.05