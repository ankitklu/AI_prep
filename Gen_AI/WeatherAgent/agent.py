from dotenv import load_dotenv
load_dotenv()

import os
import requests 

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from tavily import TavilyClient
from rich import print  
from langchain_google_genai import ChatGoogleGenerativeAI

# Now let;s create some tools that we can use to get weather information. We will create two tools: one for getting the current weather and another for getting the weather forecast.

#Weather Tool

API_KEY = os.getenv("OPENWEATHER_API_KEY")

@tool
def get_weather(city: str) -> str:
    """ Get Current weather of a city"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message')}"

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    return f"Weather in {city}: {temp}°C, {desc}"

# print(get_weather.invoke("Bangalore"))

# Tavily News tool

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def get_news(city: str) -> str:
    """ Get News of a city"""

    query = f"Latest news in {city}"

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = response.get("results", [])

    if not results:
        return f"No news found for {city}"
    
    news_list = []
    
    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")
        
        news_list.append(
            f"- {title}\n  🔗 {url}\n  📝 {snippet[:100]}..."
        )
    
    return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)

# print(get_news.invoke("Bangalore"))

#llm

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

tools = {
    "get_weather": get_weather,
    "get_news": get_news
}

llm_with_tool = llm.bind_tools([get_weather, get_news])

#Agent LOOP

def run_cli():
    messages = []

    print("City intelligence System")
    print("type Exit to quit")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Exiting...")
            break

        messages.append(HumanMessage(content=user_input))

        while True:
            # NOTE: gemini-3.6-flash attaches a `thought_signature` to function-call
            # responses, and the installed langchain-google-genai version doesn't yet
            # round-trip it. Replaying an AIMessage with tool_calls (or a ToolMessage)
            # back to the model raises a 400 "missing thought_signature" error, so we
            # never put those back into `messages` — tool results are fed back as
            # plain text instead.
            result = llm_with_tool.invoke(messages)

            #if tool is required

            if result.tool_calls:
                for tool_call in result.tool_calls:
                    tool_name = tool_call['name']

                    #HUMAN IN THE LOOP
                    confirm = input(f"Agent wants to call {tool_name} Approve(Yes/No): ")

                    if confirm.lower() == "no":
                        print("tool call denied and i cannot get the info...")
                        messages.append(HumanMessage(
                            content=f"Tool call to {tool_name} was denied by the user."
                        ))
                        continue

                    #execute tool
                    tool_result = tools[tool_name].invoke(tool_call['args'])

                    messages.append(HumanMessage(
                        content=f"Tool {tool_name} was called with args {tool_call['args']} and returned: {tool_result}"
                    ))

                continue

            else:
                messages.append(result)
                print(result.content)
                break


if __name__ == "__main__":
    run_cli()