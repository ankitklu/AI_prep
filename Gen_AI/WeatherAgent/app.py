import streamlit as st
from langchain_core.messages import HumanMessage

from agent import llm_with_tool, tools

st.set_page_config(page_title="City Intelligence Agent")
st.title("City Intelligence Agent")
st.caption("Ask about the weather or latest news for any city.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "display_history" not in st.session_state:
    st.session_state.display_history = []

for role, text in st.session_state.display_history:
    with st.chat_message(role):
        st.write(text)

user_input = st.chat_input("e.g. What's the weather in Bangalore?")

if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.session_state.display_history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Same approach as agent.py's CLI loop: gemini-3.6-flash requires a
            # thought_signature on replayed function-call messages that this
            # langchain-google-genai version doesn't support, so tool results
            # are fed back to the model as plain text instead of ToolMessages.
            while True:
                result = llm_with_tool.invoke(st.session_state.messages)

                if result.tool_calls:
                    for tool_call in result.tool_calls:
                        tool_name = tool_call["name"]
                        st.write(f"🔧 Calling `{tool_name}` with {tool_call['args']}...")
                        tool_result = tools[tool_name].invoke(tool_call["args"])
                        st.session_state.messages.append(HumanMessage(
                            content=f"Tool {tool_name} was called with args {tool_call['args']} and returned: {tool_result}"
                        ))
                    continue
                else:
                    st.session_state.messages.append(result)
                    st.write(result.content)
                    st.session_state.display_history.append(("assistant", result.content))
                    break
