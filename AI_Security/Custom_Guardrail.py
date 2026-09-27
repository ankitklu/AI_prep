from dotenv import load_dotenv
load_dotenv()

import os
from getpass import getpass
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.tools import tool

from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config, ContentFilterMiddleware
from langgraph.runtime import Runtime

class ContentFilterMiddleware(AgentMiddleware):
    """
    Deterministic guardrail: Block requests containing banned keywords.
    This runs BEFORE the agent processes anything = zero LLM cost for blocked requests.
    """

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self,
        state: AgentState,
        runtime: Runtime
    ) -> dict[str, Any] | None:

        # Get the latest user message
        messages = state.get("messages", [])

        if not messages:
            return None

        last_message = messages[-1]

        # Extract text from the message
        content = last_message.content.lower()

        # Check banned keywords
        for keyword in self.banned_keywords:
            if keyword in content:
                return {
                    "messages": [
                        {
                            "role": "assistant",
                            "content": "Sorry, I can't help with that request."
                        }
                    ],
                    "jump_to": "end"
                }

        # No banned keyword → continue normally
        return None

    @tool
    def search_tool(query: str) -> str:
        """Search for information."""
        return f"Results for: {query}"

    # Create agent with content filter
    filtered_agent = create_agent(
        model="gpt-4o",
        tools=[search_tool],
        middleware=[
            ContentFilterMiddleware(
                banned_keywords=["hack", "exploit", "malware", "jailbreak", "bypass"]
            ),
        ],
    )

    print("Content filter agent created!")