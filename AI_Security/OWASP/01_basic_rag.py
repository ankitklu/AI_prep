"""
Module 1: A basic RAG application with LangGraph.


User question -> retrieve (vector store) -> build one prompt -> LLM -> answer
                                             * system prompt
                                             * retrieved passages
                                             * user message

Required in .env:
    GROQ_API_KEY=gsk_...

Where the OWASP LLM Top 10 risks enter this app (see later modules):
    user message                     -> LLM01 Prompt injection
    system prompt                    -> LLM07 System prompt leakage
    documents / vector store         -> LLM01 Indirect prompt injection, LLM04 Data and model poisoning, LLM08 Vector and embedding weaknesses
    the LLM itself                   -> LLM03 Supply chain, LLM10 Unbounded consumption
    the reply                        -> LLM09 Misinformation, LLM02 Sensitive information disclosure
    reply sent to a user/other system -> LLM05 Improper output handling
    tools and actions                -> LLM06 Excessive agency
"""
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import END, START, StateGraph

from fake_docs import DOCUMENTS

load_dotenv()

assert os.getenv("GROQ_API_KEY"), "GROQ_API_KEY is missing. Add it to the .env file."

CHAT_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
print("Chat model:     ", CHAT_MODEL)
print("Embedding model:", EMBEDDING_MODEL)

# ---------------------------------------------------------------------------
# 2. The fake knowledge base (fake_docs.py) -> LangChain Document objects
# ---------------------------------------------------------------------------
documents = [
    Document(page_content=d["text"], metadata={"id": d["id"], "title": d["title"]})
    for d in DOCUMENTS
]

# ---------------------------------------------------------------------------
# 3. Embeddings and the vector store
#    InMemoryVectorStore needs no database - it lives in Python memory only.
# ---------------------------------------------------------------------------
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents)
print("Documents stored:", len(documents))

# ---------------------------------------------------------------------------
# 4. Build the RAG graph with LangGraph: START -> retrieve -> generate -> END
# ---------------------------------------------------------------------------
class RAGState(TypedDict):
    question: str              # what the user asked
    context: list[Document]    # passages found by the retriever
    answer: str                 # the LLM's reply


SYSTEM_PROMPT = (
    "You are the Acme Cloud help assistant. "
    "Answer the user's question using only the context below. "
    "If the answer is not in the context, say \"I don't know based on the company documents.\" "
    "Keep answers short."
)


def build_messages(question: str, context: list[Document]):
    passages = "\n\n".join(f"[{d.metadata['title']}]\n{d.page_content}" for d in context)
    return [
        ("system", f"{SYSTEM_PROMPT}\n\nContext:\n{passages}"),
        ("user", question),
    ]


llm = ChatGroq(model=CHAT_MODEL, temperature=0)
TOP_K = 2


def retrieve(state: RAGState) -> dict:
    docs = vector_store.similarity_search(state["question"], k=TOP_K)
    return {"context": docs}


def generate(state: RAGState) -> dict:
    messages = build_messages(state["question"], state["context"])
    response = llm.invoke(messages)
    return {"answer": response.content}


graph = StateGraph(RAGState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

rag_app = graph.compile()


# ---------------------------------------------------------------------------
# 5. Ask questions
# ---------------------------------------------------------------------------
def ask(question: str):
    result = rag_app.invoke({"question": question})
    print("Question:", question)
    print("Sources: ", [d.metadata["title"] for d in result["context"]])
    print("Answer:  ", result["answer"])
    print("-" * 80)
    return result


def show_prompt(question: str):
    """Look inside the exact prompt the LLM receives - useful once you start attacking it."""
    docs = vector_store.similarity_search(question, k=TOP_K)
    for role, content in build_messages(question, docs):
        print(f"===== {role.upper()} =====")
        print(content)
        print()


if __name__ == "__main__":
    ask("How many days of paid leave do employees get?")
    ask("Can I get a refund after 2 weeks?")
    ask("How long must my password be?")
    ask("Who is the CEO of Acme Cloud?")  # not in the docs -> "I don't know"

    print("\n=== Prompt inspection ===")
    show_prompt("What are the support hours?")
