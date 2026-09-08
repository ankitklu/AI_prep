from dotenv import load_dotenv
load_dotenv()

import os
import requests

from langchain.tools import tool
from tavily import TavilyClient
from rich import print
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

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

# create_agent builds a LangGraph agent internally; HumanInTheLoopMiddleware pauses
# (via an interrupt) before running any tool listed in interrupt_on, and a checkpointer
# is required so the paused run can be resumed with the human's decision.
agent = create_agent(
    llm,
    tools=[get_weather, get_news],
    system_prompt="You are a helpful city assistant.",
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on={"get_weather": True, "get_news": True})
    ],
    checkpointer=InMemorySaver(),
)


def extract_text(content) -> str:
    """gemini-3.6-flash returns AIMessage.content as a list of content blocks
    (with 'extras'/thought-signature metadata) rather than a plain string."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") for block in content if isinstance(block, dict)
    )


#Agent LOOP

def run_cli():
    config = {"configurable": {"thread_id": "cli-session"}}

    print("City Agent | type exit to quit")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Exit.....")
            break

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        #HUMAN IN THE LOOP: keep resuming while a tool call is pending approval
        while "__interrupt__" in result:
            action_requests = result["__interrupt__"][0].value["action_requests"]

            decisions = []
            for action in action_requests:
                confirm = input(
                    f"Agent wants to call {action['name']} with {action['args']} Approve(Yes/No): "
                )
                if confirm.lower() == "no":
                    print("tool call denied and i cannot get the info...")
                    decisions.append({"type": "reject", "message": "User denied this tool call."})
                else:
                    decisions.append({"type": "approve"})

            result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

        print(extract_text(result["messages"][-1].content))


if __name__ == "__main__":
    run_cli()
