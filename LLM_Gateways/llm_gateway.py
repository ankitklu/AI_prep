import warnings
import logging

warnings.filterwarnings("ignore", category=UserWarning, module="litellm")
logging.getLogger("litellm").setLevel(logging.ERROR)

#Now import LiteLLM normally
from litellm import completion

# completion is the main function to generate text completions using LiteLLM. You can use it as follows:
# response = completion("Hello, how are you?")
# Like it can perfrom all the core capabilities of LiteLLM, including text generation, chat, and more. You can also specify parameters like model, temperature, max tokens, etc. For example:

import litellm
litellm.suppress_debug_info = True

import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("LiteLLM").setLevel(logging.ERROR)

import os
from dotenv import load_dotenv
load_dotenv()

# LiteLLM reads GEMINI_API_KEY and HF_TOKEN; map the names used in .env
os.environ.setdefault("GEMINI_API_KEY", os.getenv("GOOGLE_GEMINI_API_KEY", ""))
os.environ.setdefault("HF_TOKEN", os.getenv("HUGGINGFACEHUB_API_TOKEN", ""))


print("GROQ key ", "LOADED" if os.getenv("GROQ_API_KEY") else "NOT LOADED")
# print("Langsmith key ", "LOADED" if os.getenv("LANGSMITH_API_KEY") else "NOT LOADED")
print("Hugging Face key ", "LOADED" if os.getenv("HUGGINGFACEHUB_API_TOKEN") else "NOT LOADED")
print("Google Gemini key ", "LOADED" if os.getenv("GOOGLE_GEMINI_API_KEY") else "NOT LOADED")
print("Anthropic key ", "LOADED" if os.getenv("ANTHROPIC_API_KEY") else "NOT LOADED")

    


response_groq = completion(
    model="groq/openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    temperature=0.1,
)
print("GROQ response:", response_groq.choices[0].message.content)

# response_hf = completion(
#     model="huggingface/meta-llama/Llama-3.1-8B-Instruct",
#     messages=[{"role": "user", "content": "Hello, how are you?"}],
#     temperature=0.1,
# )
# print("Hugging Face response:", response_hf.choices[0].message.content)

response_gemini = completion(
    model="gemini/gemini-3.8-flash",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    temperature=0.1,
)
print("Google Gemini response:", response_gemini.choices[0].message.content)

prompt = "Explain RAG in one sentence."

providers = [
    ("Groq", "groq/openai/gpt-oss-20b"),
    ("Hugging Face", "huggingface/meta-llama/Llama-3.1-8B-Instruct"),
    ("Google Gemini", "gemini/gemini-3.8-flash"),
    ("Anthropic", "anthropic/claude-haiku-4-5-20251001"),
]

# ONE loop. ONE function call. Multiple providers.
for label, model in providers:
    try:
        r = completion(model=model, messages=[{"role": "user", "content": prompt}])
        print(f"{label:<15}: {r.choices[0].message.content[:80]}")
    except Exception as e:
        print(f"{label:<15}: ❌ {type(e).__name__}")

##-------------------- AUTOMATIC FALLBACK --------------------##

# With a gateway, if one provider fails, we automatically fallback to another. Production-ready code would have a more robust fallback strategy, but this is a simple example.

response = completion(
    model="gemini/gemini-3.8-flash",  # Primary
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    fallbacks=["groq/openai/gpt-oss-20b"],  # Used only if Gemini fails
)

print("Response with fallback:", response.choices[0].message.content)
print("Used model:", response.model)
