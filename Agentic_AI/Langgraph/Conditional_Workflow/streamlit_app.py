import os
from typing import TypedDict, Annotated

import streamlit as st
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACADEMIC_PDF = os.path.join(BASE_DIR, "academics_handbook.pdf")
FEE_PDF = os.path.join(BASE_DIR, "fee_structure.pdf")

PROGRAMMES = ["BCA", "BBA", "B.Com (H)"]


class State(TypedDict):
    programme: str
    messages: Annotated[list, add_messages]
    query_type: str
    retrieved_context: str


@st.cache_resource(show_spinner="Building retrievers from college PDFs...")
def build_graph():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def build_retriever(pdf_path: str):
        loader = PyPDFLoader(pdf_path)
        document = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(document)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        return vectorstore.as_retriever(search_kwargs={"k": 4})

    academic_retriever = build_retriever(ACADEMIC_PDF)
    fee_retriever = build_retriever(FEE_PDF)

    llm = ChatGroq(model="groq/compound-mini", temperature=0.4)

    def classifier_node(state: State) -> dict:
        last_message = state["messages"][-1].content

        prompt = (
            "Classify the following student query into exactly one category: "
            "'academic', 'fee', or 'general'.\n\n"
            "Use 'academic' for questions about attendance, exams, grading, credits, "
            "promotion, course structure, summer training, or degree requirements.\n"
            "Use 'fee' for questions about tuition, payment, refund, late charges, "
            "scholarships, or any money-related topic.\n"
            "Use 'general' for greetings, casual talk, or anything not related to "
            "the college rules or fee.\n\n"
            f"Query: {last_message}\n\n"
            "Return only one word: academic, fee, or general."
        )

        response = llm.invoke(prompt)
        category = response.content.strip().lower()

        if "academic" in category:
            category = "academic"
        elif "fee" in category:
            category = "fee"
        else:
            category = "general"

        return {"query_type": category}

    def academic_rag_node(state: State) -> dict:
        query = state["messages"][-1].content
        docs = academic_retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        return {"retrieved_context": context}

    def fee_rag_node(state: State) -> dict:
        query = state["messages"][-1].content
        docs = fee_retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        return {"retrieved_context": context}

    def general_node(state: State) -> dict:
        return {"retrieved_context": "NO_RETRIEVAL_NEEDED"}

    def response_node(state: State) -> dict:
        query = state["messages"][-1].content
        programme = state.get("programme", "Unknown")
        context = state["retrieved_context"]

        if context == "NO_RETRIEVAL_NEEDED":
            prompt = (
                f"You are a friendly college assistant talking to a {programme} student. "
                f"Answer this question using your own general knowledge:\n\n{query}"
            )
        else:
            prompt = (
                f"You are a college assistant helping a {programme} student. "
                f"Use the following context from the official college documents to answer "
                f"the question accurately. If the context mentions specific figures for "
                f"different programmes, highlight the one relevant to {programme} if possible.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                f"Give a clear, friendly, and precise answer."
            )

        response = llm.invoke(prompt)
        return {"messages": [("ai", response.content.strip())]}

    def route_query(state: State):
        if state["query_type"] == "academic":
            return "academic_rag"
        elif state["query_type"] == "fee":
            return "fee_rag"
        else:
            return "general"

    graph = StateGraph(State)
    graph.add_node("classifier", classifier_node)
    graph.add_node("academic_rag", academic_rag_node)
    graph.add_node("fee_rag", fee_rag_node)
    graph.add_node("general", general_node)
    graph.add_node("response", response_node)

    graph.add_edge(START, "classifier")
    graph.add_conditional_edges("classifier", route_query)
    graph.add_edge("academic_rag", "response")
    graph.add_edge("fee_rag", "response")
    graph.add_edge("general", "response")
    graph.add_edge("response", END)

    return graph.compile()


st.set_page_config(page_title="College Assistant", page_icon="🎓")
st.title("🎓 College Assistant")
st.caption("LangGraph conditional RAG — routes your question to the academic handbook, fee structure, or general knowledge.")

with st.sidebar:
    st.header("Settings")
    programme = st.selectbox("Your programme", PROGRAMMES)
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if not os.path.exists(ACADEMIC_PDF) or not os.path.exists(FEE_PDF):
    st.error(
        "Missing PDFs. Expected 'academics_handbook.pdf' and 'fee_structure.pdf' "
        f"in {BASE_DIR}."
    )
    st.stop()

if "GROQ_API_KEY" not in os.environ:
    st.warning("GROQ_API_KEY not found in environment. Set it in a .env file before chatting.")

app = build_graph()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("query_type"):
            st.caption(f"Routed as: **{msg['query_type']}**")

user_query = st.chat_input("Ask about attendance, exams, fees, or anything else...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = app.invoke({
                "programme": programme,
                "messages": [("human", user_query)],
            })
            answer = result["messages"][-1].content
            query_type = result.get("query_type", "unknown")
            st.markdown(answer)
            st.caption(f"Routed as: **{query_type}**")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "query_type": query_type,
    })
