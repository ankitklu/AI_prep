import uuid

import streamlit as st
from langgraph.types import Command

from agent import agent, extract_text

st.set_page_config(page_title="City Intelligence Agent")
st.title("City Intelligence Agent")
st.caption("Ask about the weather or latest news for any city.")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "display_history" not in st.session_state:
    st.session_state.display_history = []
if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None

config = {"configurable": {"thread_id": st.session_state.thread_id}}

for role, text in st.session_state.display_history:
    with st.chat_message(role):
        st.write(text)


def handle_result(result):
    if "__interrupt__" in result:
        st.session_state.pending_interrupt = result["__interrupt__"][0]
    else:
        text = extract_text(result["messages"][-1].content)
        st.session_state.display_history.append(("assistant", text))
        st.session_state.pending_interrupt = None


if st.session_state.pending_interrupt is not None:
    action_requests = st.session_state.pending_interrupt.value["action_requests"]

    with st.chat_message("assistant"):
        for action in action_requests:
            st.write(f"🔧 Agent wants to call `{action['name']}` with {action['args']}")

        col1, col2 = st.columns(2)
        approve = col1.button("Approve", use_container_width=True)
        reject = col2.button("Reject", use_container_width=True)

    if approve or reject:
        if approve:
            decisions = [{"type": "approve"} for _ in action_requests]
        else:
            decisions = [
                {"type": "reject", "message": "User denied this tool call."}
                for _ in action_requests
            ]
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)
        handle_result(result)
        st.rerun()

else:
    user_input = st.chat_input("e.g. What's the weather in Bangalore?")

    if user_input:
        st.session_state.display_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Thinking..."):
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
        handle_result(result)
        st.rerun()
