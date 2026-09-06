from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.tools import tool

from rich import print

#1 Creating a tool
@tool
def get_text_length(text:str) -> int:
    """A simple tool that takes a text as input and returns the length of the text."""
    return len(text)

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

#tool binding

llm_with_tool = llm.bind_tools([get_text_length])

question = "Return the number of characters in the following text: 'Hello, how are you?'"

result = llm_with_tool.invoke(question)

print(result.tool_calls[0])

for tool_call in result.tool_calls:
    tool_result = get_text_length.invoke(tool_call["args"])
    final_response = llm.invoke(
        f"{question}\n\nThe tool {tool_call['name']} returned: {tool_result}. "
        "Using this result, answer the original question."
    )

print(final_response.content)

