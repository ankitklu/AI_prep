from dotenv import load_dotenv
load_dotenv()

import os
from getpass import getpass
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search resilts for : {query}"

@tool
def send_email(to:str, subject:str, body:str) -> str:
    """Send an email to a recipient. """
    return f"Email sen tto {to} with subject {subject}"

@tool
def delete_records(table:str , condition: str) -> str:
    """Delete records from the database."""
    return f"Deleted records from {table} where {condition}"


llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen3-8B",
        task="conversational",
        provider="auto",
        max_new_tokens=2048,
        temperature=0.01,
)
model = ChatHuggingFace(llm=llm)

hitl_agent = create_agent(
    model = model,
    tools = [search_web, send_email, delete_records],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": True,
                "delete_records": True,
                "search_web": False,
            }
        ),
    ],
    checkpointer = InMemorySaver(),
)

print("Human in the loop middleware created")

# Step 1: Invoke - agent will pause before send_email

config = {"configurable": {"thread_id": "session_001"}}

result = hitl_agent.invoke(
   {"messages" : [{"role":"user", "content":" Send and email to team@companu.com about the Q4 results"}]},
   config = config
)

print("=== Agent paused - awaiting human approval ===")

# Step 2: Human reviews and APPROVES
approved_result = hitl_agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]},
    config=config    # Same thread_id resumes the paused session
))



print("=== Approved! Final response ===")
print(approved_result["messages"][-1].content)




# from langchain.agents import create_agent
# from langchain.agents.middleware import PIIMiddleware
# from langchain_core.tools import tool
# from langca

# @tool
# def customer_lookup(query: str) -> str:
#     """Look up customer information."""
#     return f"Customer record found query: {query}"

# llm = HuggingFaceEndpoint(
#         repo_id="Qwen/Qwen3-8B",
#         task="conversational",
#         provider="auto",
#         max_new_tokens=2048,
#         temperature=0.01,
# )
# model = ChatHuggingFace(llm=llm)

# agent = create_agent(
#     model=model,
#     tools = [customer_lookup],
#     middleware=[
#         PIIMiddleware(
#             "email",
#             strategy="redact",
#             apply_to_input = True,
#         ),
#         PIIMiddleware(
#             "credit_card",
#             strategy="mask",
#             apply_to_input = True
#         ),
#         PIIMiddleware(
#             "api_key",
#             detector=r"sk-[a-zA-z0-9]{32}",
#             strategy="block",
#             apply_to_input = True
#         ),
#     ],
# )

# print("Agent with PII middleware created successully")

# result = agent.invoke({
#     "messages": [{
#         "role": "user",
#         "content": "My email is john.doe@example.com and my card is 5105-10151-0510-5100. Can you help me ?"
#     }]
# })

# print("=== Agent Response ====")
# print(result["messages"][-1].content)


