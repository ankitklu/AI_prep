from dotenv import load_dotenv
load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
parser = StrOutputParser()
search_tool = TavilySearchResults(max_results = 5)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who summarizes the following news article in simple terms"),
    ("human", "{article}")
])

chain = prompt | llm | parser

news_result = search_tool.run("Latest news on AI in healthcare")

result = chain.invoke({"article": news_result})

print(result)

