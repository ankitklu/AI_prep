from litellm import Router
import os
from dotenv import load_dotenv
load_dotenv()

# Two deployments under the same alias
# A pool of "smart" models — all equally capable, just different providers
model_list = [
    {
        "model_name": "gpt-pool",
        "litellm_params": {
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "model_info": {"id": "openai-gpt4o"}
    },
    
    {
        "model_name": "gpt-pool",
        "litellm_params": {
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
        "model_info": {"id": "groq-llama-70b"}
    },
]

router = Router(
    model_list=model_list,
    routing_strategy="simple-shuffle"
)

print(f"{'Request':<10}{'Deployment Picked':<22}{'Latency':<12}{'Response':<40}")
print("-" * 84)

for i in range(6):
    r = router.completion(
        model="gpt-pool",
        messages=[{"role": "user", "content": f"Say hello, request {i+1}"}]
    )
    # Pull out which deployment served this request
    deployment_id = r._hidden_params.get("model_id", "unknown")
    latency = r._response_ms
    answer = r.choices[0].message.content[:35]
    print(f"#{i+1:<9}{deployment_id:<22}{latency:>6.0f} ms   {answer}")