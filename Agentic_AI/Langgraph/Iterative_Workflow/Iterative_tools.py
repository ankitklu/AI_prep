import os
from typing import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

search_tool = TavilySearch(max_results =3)

tools = [search_tool]

# Writer LLMs

writer_llm = ChatMistralAI(model = 'mistral-small-2506', temperature = 0.7)
writer_llm_with_tools = writer_llm.bind_tools(tools)

#reviewer LLM

reviewer_llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0.2)

#state building

class State(TypedDict):
    topic: str
    messages : Annotated[list, add_messages]
    draft : str
    review_feedback : str
    attempt : int





