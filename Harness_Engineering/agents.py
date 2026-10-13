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




def general_agent(question: str) -> str:
    llm = get_llm()
    prompt = f"""
You are a General Customer Support Agent.

Answer general questions politely and simply.
If the question requires technical support or billing support, say that it should
be handled by the appropriate specialist.

Customer question:
{question}

Return only the answer.
"""
    return llm.invoke(prompt).content




def reviewer_agent(question: str, draft: str) -> str:
    llm = get_llm()
    prompt = f"""
You are the Quality Review Agent in a production customer-support system.

Check the draft answer for:
1. clarity,
2. relevance,
3. unsafe requests for passwords/card numbers,
4. unsupported guarantees,
5. unnecessary complexity.

Rewrite the answer if needed.
Keep the final answer concise and beginner-friendly.

Original customer question:
{question}

Draft answer:
{draft}

Return only the improved final answer.
"""
    return llm.invoke(prompt).content
    

