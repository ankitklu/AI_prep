from dotenv import load_dotenv
load_dotenv()

import os
import requests 

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily import TavilyClient
from rich import print  
from lanchain_google_genai import ChatGoogleGenerativeAI

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
        search_depths="advanced",
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
        result = llm_with_tool.invoke(messages=messages)

        messages.append(ToolMessage(content=result.content))
    
    response = llm_with_tool.invoke(messages=messages)
    
    messages.append(ToolMessage(content=response.content))
    
    print(f"Agent: {response.content}")