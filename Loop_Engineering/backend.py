import os
from typing import Literal, TypedDict, TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph

from pydantic import BaseModel, Field

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", 2))

model = ChatGroq(
    model=MODEL,
    api_key=os.getenv("GROQ_API_KEY"),
)

class Review(BaseModel):
    """Review of the answer."""
    feedback: str = Field(..., description="Short, specific feedback. Empty string when decision is PASS.")
    decision: Literal["PASS", "REVISE"] = Field(..., description="PASS only if the answer satisfies every review rule; otherwise REVISE.")

reviewer_model = model.with_structured_output(Review, method="json_schema")

class State(TypedDict):
    """State of the graph."""
    topic: str
    draft:str
    feedback: str
    decision: str
    revision_count: int

def writer(state: State):
    """Agent 1: create the first answer."""

    response = model.invoke(
        [
            {
                "role":"system",
                "content":(
                    "You are a beginner-friendly teacher. Explain the topic in 120-160 words. "
                    "Use simple language, one everyday analogy, and one tiny example."
                ),
            },
            {"role":"user","content":f"Explain: {state['topic']}"},
        ]
    )
    return {
        "draft": response.content,
        "feedback": "",
        "decision":"",
        "revision_count": 0,
    }

#VERIFIER in the loop
def reviewer(state: State):
    """Agent 2: evaluate the current answer."""

    review = reviewer_model.invoke(
        [
            {
                "role":"system",
                "content":(
                    "You are a strict reviewer. Evaluate the answer based on the following rules:\n"
                    "1. The answer must be beginner-friendly.\n"
                    "2. The answer must be 120-160 words long.\n"
                    "3. The answer must use simple language.\n"
                    "4. The answer must include one everyday analogy.\n"
                    "5. The answer must include one tiny example.\n"
                    "6. If the answer satisfies all the rules, return PASS; otherwise return REVISE and give one or two precise improvements."
                ),
            },
            {"role":"user","content":f"Topic: {state['topic']}\n\n Answer: \n{state['draft']}"},
        ]
    )
    return {"decision": review.decision, "feedback": review.feedback}

def reviser(state: State):
    """Agent 3: revise the answer based on the feedback."""

    response = model.invoke(
        [
            {
                "role":"system",
                "content":(
                    "You are a reiser. Improve the answer based on the feedback. "
                    "Keep it beginner-friendly, 120-160 words long, use simple language, include one everyday analogy and one tiny example. Return only the improved answer."
                ),
            },
            {"role":"user","content":f"Topic: {state['topic']}\n\n Current Answer: {state['draft']}\n\n Reviewer Feedback: \n{state['feedback']}"},
        ]
    )
    return {
        "draft": response.content,
        "revision_count": state["revision_count"] + 1,
    }

def route_after_review(state: State):
    """The loop controller."""

    if state["decision"]=="PASS":
        return "done"

    if state["revision_count"]>= MAX_REVISIONS:
        return "done"

    return "revise"


builder = StateGraph(State)

builder.add_node("writer", writer)
builder.add_node("reviewer", reviewer)
builder.add_node("reviser", reviser)

builder.add_edge(START, "writer")
builder.add_edge("writer", "reviewer")

builder.add_conditional_edges(
    "reviewer",
    route_after_review,
    {"revise": "reviser", "done": END}
)

builder.add_edge("reviser", "reviewer")

graph = builder.compile()

def run_workflow(topic: str):
    """Run the graph and return data that both the CLI and FastAPI UI can use."""
    initial_state: State = {
        "topic": topic,
        "draft" : "",
        "feedback": "",
        "decision": "",
        "revision_count": 0
    }

    final_state = initial_state.copy()
    events=[]

    for update in graph.stream(initial_state, stream_mode="updates"):
        for node_name, values in update.items():

            final_state.update(values)
            events.append(
                {
                    "agent": node_name,
                    "draft": values.get("draft", ""),
                    "decision": values.get("decision", ""),
                    "feedback": values.get("feedback", ""),
                    "revision_count": final_state["revision_count"],
                }
            )

    return {
        "topic": topic,
        "events" : events,
        "final_answer": final_state["draft"],
        "final_decision": final_state["decision"],
        "revision_count": final_state["revision_count"],
        "provider": "Groq",
        "model": MODEL
    }


def run_demo(topic: str):
    """Small CLI version, useful if you want to demo without the browser."""
    result = run_workflow(topic)

    print("\n=== SELF-CORRECTING MULTI-AGENT DEMO ===")
    print(f"Provider: {result['provider']}")
    print(f"Model: {result['model']}")
    print(f"Topic: {topic}\n")

    for event in result["events"]:
        print(f"\n--- {event['agent'].upper()} ---")
        if event["agent"] in {"writer", "reviser"}:
            print(event["draft"])
        elif event["agent"] == "reviewer":
            print("Decision:", event["decision"])
            print("Feedback:", event["feedback"] or "No changes needed")

    print("\n=== FINAL ANSWER ===")
    print(result["final_answer"])
    print(f"\nFinal decision: {result['final_decision']}")
    print(f"Revisions used: {result['revision_count']}")


if __name__ == "__main__":
    topic = input("Enter a topic (example: What is an AI Agent?) : ").strip()

    if not topic:
        topic = "What is an AI Agent?"

    run_demo(topic)


