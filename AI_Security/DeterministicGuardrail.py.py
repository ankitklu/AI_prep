from dotenv import load_dotenv
load_dotenv()

import os
from getpass import getpass
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

import re

def deterministic_guardrail(text:str) -> bool:
    """Return True if content is blocked """
    banned_keywords = ["hack", "exploit", "malware", "bomb"]
    return any(kw in text.lower() for kw in banned_keywords)

test_inputs = [
    "How do I hack into a database?",
    "What is the capital of France?",
    "Explain how malware spreads? "
]

print("=== Deterministic Guardrail Demo ===")
for inp in test_inputs:
    blocked = deterministic_guardrail(inp)
    status = "BLOCKED" if blocked else "ALLOWED"
    print(f"{status}: {inp}")

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


# --- Model-based approach ---
def model_based_guardrail(text: str) -> str:
    """Uses an LLM to evaluate content safety. Returns SAFE or UNSAFE."""
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen3-8B",
        task="conversational",
        provider="auto",
        max_new_tokens=512,
        temperature=0.01,
    )
    model = ChatHuggingFace(llm=llm)
    prompt = f"""Is the following user input safe to process?
            Reply with only 'SAFE' or 'UNSAFE'.
            Input: {text}"""
    
    result = model.invoke([{"role": "user", "content": prompt}])
    return result.content.strip()

print("=== Model-Based Guardrail Demo ===")
for inp in test_inputs:
    verdict = model_based_guardrail(inp)
    status = "🚫 UNSAFE" if "UNSAFE" in verdict else "✅ SAFE"
    print(f"{status}: {inp}")
