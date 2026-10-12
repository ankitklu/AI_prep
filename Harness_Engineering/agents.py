import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"


def get_llm():
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY")
    )

# llm = get_llm()
# print(llm.invoke("Hi, How are you ?").content)

def technical_agent(question: str) -> str:
    llm = get_llm()
    prompt = f"""
You are a Technical Support Agent.

Your job:
- Help with login problems, API errors, installation problems, bugs, and technical setup.
- Explain the solution in very simple steps.
- Never invent account-specific information.
- If important information is missing, clearly say what the user should check.

Customer question:
{question}

Return only the helpful answer.
"""

    return llm.invoke(prompt).content

def billing_agent(question: str) -> str:
    llm = get_llm()
    prompt = f"""
You are a Billing Support Agent.

Demo company policy:
- Started plan: $10/month
- Pro plan: $25/month
- Refund requests must be reviewed by the billing team.
- Never clain that a refund has already been approved.
- Never ask for full card numbers or passwords.

Cusomter question: {question}

Answer clearly and safely using onlt the policy above.
"""

    return llm.invoke(prompt).content


    

