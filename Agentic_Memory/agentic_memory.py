import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("Ser GOOGLE_API_KEY in your environment/.env before running this method.")

from mem0 import Memory

# m = Memory()

mem0_config = {
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-3.5-flash",
            "api_key": os.environ["GOOGLE_API_KEY"],
            "temperature": 0,
        },
    },
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "models/gemini-embedding-001",
            "embedding_dims": 1536,
            "api_key": os.environ["GOOGLE_API_KEY"],
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": ":memory:",
            "embedding_model_dims": 1536,
        },
    }
}

m = Memory.from_config(mem0_config)

messages = [
    {"role": "user", "content": "Hi, I'm Alex. I love basketball and gaming."},
    {"role": "assistant", "content": "Hey Alex! I'll remember your interests."}
]
m.add(messages, user_id="alex")
results = m.search("WHat do you know about me?", filters={"user_id": "alex"})
print(results)