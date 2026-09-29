import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langsmith import Client

# ==========================================
# 1. Load environment variables
# ==========================================

load_dotenv()

print(
    "LangSmith API key:",
    "Loaded" if os.getenv("LANGSMITH_API_KEY") else "MISSING"
)

print(
    "HuggingFace token:",
    "Loaded" if os.getenv("HUGGINGFACEHUB_API_TOKEN") else "MISSING"
)


# ==========================================
# 2. Create clients
# ==========================================

client = Client()

hf_client = InferenceClient(
    api_key=os.environ["HUGGINGFACEHUB_API_TOKEN"]
)


# ==========================================
# 3. Define the Judge
# ==========================================

def correctness(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict
):

    question = inputs["question"]

    expected_answer = reference_outputs["answer"]

    actual_answer = outputs["response"]

    prompt = f"""
You are an expert professor evaluating a student's answer.

Question:
{question}

Expected Answer:
{expected_answer}

Student Answer:
{actual_answer}

Determine whether the student's answer is correct.

The answer does not need to use exactly the same wording
as the expected answer. Judge based on factual meaning.

Respond with exactly one word:

CORRECT

or

INCORRECT
"""

    response = hf_client.chat.completions.create(
        model="Qwen/Qwen3-8B",
        messages=[
            {
                "role": "system",
                "content": "You are a strict and fair evaluator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content.strip().upper()

    return {
        "key": "correctness",
        "score": 1 if result == "CORRECT" else 0
    }


# ==========================================
# 4. Define another evaluator
# ==========================================

def concision(
    outputs: dict,
    reference_outputs: dict
):

    actual_length = len(outputs["response"])

    expected_length = len(reference_outputs["answer"])

    return {
        "key": "concision",
        "score": int(actual_length < 2 * expected_length)
    }


# ==========================================
# 5. Define your application
# ==========================================

default_instructions = """
Respond to the user's question in a short,
concise manner (one short sentence).
"""


def my_app(
    question: str,
    model: str = "Qwen/Qwen3-8B",
    instructions: str = default_instructions
):

    response = hf_client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content


# ==========================================
# 6. Adapt application to LangSmith
# ==========================================

def ls_target(inputs: dict):

    return {
        "response": my_app(inputs["question"])
    }

## Other models
# def ls_target(inputs: dict):

#     return {
#         "response": my_app(inputs["question"], model = "somehting you want to evaluate")
#     }


# ==========================================
# 7. Run evaluation
# ==========================================

dataset_name = "Chatbots Evaluation"

experiment_results = client.evaluate(
    ls_target,
    data=dataset_name,
    evaluators=[
        correctness,
        concision
    ],
    experiment_prefix="Qwen-Qwen3-8B-chatbot"
)

print("Evaluation completed!")