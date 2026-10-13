from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

from agents import (
    technical_agent,
    billing_agent,
    general_agent,
    reviewer_agent
)


class SupportState(TypedDict):
    question: str
    route: str
    draft: str
    final_answer: str
    blocked: bool
    trace: list[str]


def guardrail_node(state: SupportState):
    """
    A simple deterministic safety layer.
    In a real system this could include moderation,
    PII detection, permissions and policy checks.
    """
    question = state["question"].lower()
    dangerous_phrases = [
        "give me your password",
        "steal password",
        "full credit card number",
        "How to change or reset password?"
    ]

    blocked = any(phrase in question for phrase in dangerous_phrases)

    trace = state.get("trace", []) + ["Guardrail checked the request"]

    if blocked:
        return {
            "blocked": True,
            "final_answer": (
                "I can't help with requests involving passwords, stolen credentials, "
                "or full payment-card information."
            ),
            "trace": trace,
        }

    return {
        "blocked": False,
        "trace": trace,
    }


def after_guardrail(state: SupportState) -> Literal["router", "end"]:
    if state["blocked"]:
        return "end"
    return "router"




def router_node(state: SupportState):
    """
    We deliberately use deterministic routing for this beginner demo.

    Why?
    Production systems should not use an LLM for every decision.
    If a rule is simple and predictable, normal Python code is often
    cheaper, faster and easier to test.
    """
    question = state["question"].lower()

    technical_words = [
        "error", "bug", "login", "api", "install",
        "installation", "code", "server", "technical"
    ]
    billing_words = [
        "price", "pricing", "payment", "refund", "bill",
        "billing", "subscription", "plan", "charged"
    ]

    if any(word in question for word in technical_words):
        route = "technical"
    elif any(word in question for word in billing_words):
        route = "billing"
    else:
        route = "general"

    return {
        "route": route,
        "trace": state.get("trace", []) + [f"Router selected: {route}"],
    }


def choose_agent(state: SupportState) -> Literal[
    "technical_agent", "billing_agent", "general_agent"
]:
    if state["route"] == "technical":
        return "technical_agent"
    if state["route"] == "billing":
        return "billing_agent"
    return "general_agent"



def technical_node(state: SupportState):
    answer = technical_agent(state["question"])
    return {
        "draft": answer,
        "trace": state.get("trace", []) + ["Technical Agent created a draft"],
    }


def billing_node(state: SupportState):
    answer = billing_agent(state["question"])
    return {
        "draft": answer,
        "trace": state.get("trace", []) + ["Billing Agent created a draft"],
    }


def general_node(state: SupportState):
    answer = general_agent(state["question"])
    return {
        "draft": answer,
        "trace": state.get("trace", []) + ["General Agent created a draft"],
    }


def reviewer_node(state: SupportState):
    final_answer = reviewer_agent(
        question=state["question"],
        draft=state["draft"],
    )
    return {
        "final_answer": final_answer,
        "trace": state.get("trace", []) + ["Reviewer Agent checked the answer"],
    }




builder = StateGraph(SupportState)

builder.add_node("guardrail", guardrail_node)
builder.add_node("router", router_node)
builder.add_node("technical_agent", technical_node)
builder.add_node("billing_agent", billing_node)
builder.add_node("general_agent", general_node)
builder.add_node("reviewer", reviewer_node)

builder.add_edge(START, "guardrail")

builder.add_conditional_edges(
    "guardrail",
    after_guardrail,
    {
        "router": "router",
        "end": END,
    },
)

builder.add_conditional_edges(
    "router",
    choose_agent,
    {
        "technical_agent": "technical_agent",
        "billing_agent": "billing_agent",
        "general_agent": "general_agent",
    },
)

builder.add_edge("technical_agent", "reviewer")
builder.add_edge("billing_agent", "reviewer")
builder.add_edge("general_agent", "reviewer")
builder.add_edge("reviewer", END)

support_graph = builder.compile()



def run_support_system(question: str):
    initial_state: SupportState = {
        "question": question,
        "route": "",
        "draft": "",
        "final_answer": "",
        "blocked": False,
        "trace": [],
    }

    result = support_graph.invoke(initial_state)

    return {
        "route": result.get("route", "blocked"),
        "answer": result["final_answer"],
        "trace": result.get("trace", []),
    }