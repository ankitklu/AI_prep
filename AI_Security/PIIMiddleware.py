from dotenv import load_dotenv
load_dotenv()

import os
from getpass import getpass
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


@tool
def customer_lookup(query: str) -> str:
    """Look up customer information."""
    return f"Customer record found query: {query}"

llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen3-8B",
        task="conversational",
        provider="auto",
        max_new_tokens=2048,
        temperature=0.01,
)
model = ChatHuggingFace(llm=llm)

agent = create_agent(
    model=model,
    tools = [customer_lookup],
    middleware=[
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input = True,
        ),
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input = True
        ),
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-z0-9]{32}",
            strategy="block",
            apply_to_input = True
        ),
    ],
)

print("Agent with PII middleware created successully")

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "My email is john.doe@example.com and my card is 5105-10151-0510-5100. Can you help me ?"
    }]
})

print("=== Agent Response ====")
print(result["messages"][-1].content)
