from huggingface_hub import InferenceClient
from langsmith import Client
client = Client()

dataset_name = "Chatbots Evaluation"

default_instructions = "Respond to the users question in a short, concise manner (one short sentence)."
def my_app(question: str, model: str = "Qwen/Qwen3-8B", instructions: str = default_instructions) -> str:
    hf_client = InferenceClient(
        api_key=os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    )
    return hf_client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": question},
        ],
    ).choices[0].message.content

#Calling my app for every datapoints
def ls_target(inputs: str) -> dict:
    return {"response":my_app(inputs["question"])}

## RUn our evaluation
experiment_results = client.evaluate(
    ls_target, ## Our AI system
    data = dataset_name,
    evaluators=[corectness, concision],
    experiment_prefix = "Qwen/Qwen3-8B-chatbot"
)

