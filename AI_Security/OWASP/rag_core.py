"""
A basic RAG application built with LangGraph.

This file contains the same code that is explained step by step in
01_basic_rag.py. Later security scripts (02_prompt_injection.py, ...) import
from here, so the "baseline app" lives in one place.

No OpenAI: Groq is the default LLM, a local HuggingFace model does the embeddings.

Flow:   question -> retrieve -> generate -> answer
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import END, START, StateGraph

from fake_docs import DOCUMENTS

load_dotenv()

CHAT_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K = 2

SYSTEM_PROMPT = (
    "You are the Acme Cloud help assistant. "
    "Answer the user's question using only the context below. "
    "If the answer is not in the context, say \"I don't know based on the company documents.\" "
    "Keep answers short."
)


# ---------------------------------------------------------------------------
# 1. The graph state: the data that flows between the steps
# ---------------------------------------------------------------------------
class RAGState(TypedDict):
    question: str
    context: list[Document]
    answer: str


# ---------------------------------------------------------------------------
# 2. Knowledge base: fake documents -> embeddings -> vector store
# ---------------------------------------------------------------------------
def load_documents() -> list[Document]:
    return [
        Document(page_content=d["text"], metadata={"id": d["id"], "title": d["title"]})
        for d in DOCUMENTS
    ]


def build_vector_store(embeddings=None) -> InMemoryVectorStore:
    if embeddings is None:
        from langchain_huggingface import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    store = InMemoryVectorStore(embeddings)
    store.add_documents(load_documents())
    return store


# ---------------------------------------------------------------------------
# 3. Prompt building: system prompt + retrieved passages + user message
# ---------------------------------------------------------------------------
def build_messages(question: str, context: list[Document]) -> list[tuple[str, str]]:
    passages = "\n\n".join(f"[{d.metadata['title']}]\n{d.page_content}" for d in context)
    return [
        ("system", f"{SYSTEM_PROMPT}\n\nContext:\n{passages}"),
        ("user", question),
    ]


# ---------------------------------------------------------------------------
# 4. The graph: retrieve node -> generate node
# ---------------------------------------------------------------------------
def build_rag_graph(llm=None, embeddings=None, vector_store=None):
    if llm is None:
        from langchain_groq import ChatGroq

        llm = ChatGroq(model=CHAT_MODEL, temperature=0)
    if vector_store is None:
        vector_store = build_vector_store(embeddings)

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
    return graph.compile()


def ask(app, question: str) -> RAGState:
    return app.invoke({"question": question})
