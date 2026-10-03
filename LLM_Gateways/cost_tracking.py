from litellm import completion, completion_cost
from dotenv import load_dotenv
load_dotenv()

MODEL = "groq/openai/gpt-oss-20b"

response = completion(
    model=MODEL,
    messages=[{"role": "user", "content": "Write a haiku about AI."}]
)

# Get the exact USD cost of this single call.
# Pass model and provider explicitly: Groq returns response.model="openai/gpt-oss-20b",
cost = completion_cost(completion_response=response, model=MODEL, custom_llm_provider="groq")

print("Response:    ", response.choices[0].message.content)
print("\nInput tokens: ", response.usage.prompt_tokens)
print("Output tokens:", response.usage.completion_tokens)
print(f"Cost:         ${cost:.8f}")

# (LLM_Gateways) (base) ankit.mishra@MP-MH26TH0205 LLM_Gateways % python3 cost_tracking.py
# Response:     Silicon mind awakes  
# Patterns pulse like stars in code  
# Thoughts bloom, unseen, night

# Input tokens:  78
# Output tokens: 326
# Cost:         $0.00010365

