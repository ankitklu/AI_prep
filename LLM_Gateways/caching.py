import litellm
from dotenv import load_dotenv
load_dotenv()

litellm.callbacks = []
litellm.success_callback = []
litellm.failure_callback = []
litellm._async_success_callback = []
litellm._async_failure_callback = []

litellm.cache = None

print("...............LiteLLM cache state reset...............")

import time
from litellm import completion
from litellm.caching import Cache

#Enabling in memory caching
litellm.cache = Cache(type="local")

prompt = "What does LLM stand for ? Answer in one line."
MODEL = "groq/openai/gpt-oss-20b"

start = time.time()
r1 = completion(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    caching = True
)

t1 = time.time() - start
print(f"First call (API):  {t1:.2f}s", r1.choices[0].message.content)

start = time.time()
r2 = completion(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    caching = True
)

t2 = time.time() - start
print(f"Second call (cache): {t2:.2f}s", r2.choices[0].message.content)

print("----------------------")

print(f"\n Speedup: {t1/t2:.2f}x faster on second call due to caching.")


# ...............LiteLLM cache state reset...............
# First call (API):  0.72s LLM stands for **Large Language Model**.
# Second call (cache): 0.30s LLM stands for **Large Language Model**.
# ----------------------

#  Speedup: 2.36x faster on second call due to caching.