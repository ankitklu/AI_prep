from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import GraphCypherQAChain
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME=os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE=os.getenv("NEO4J_DATABASE")
groq_api_key = os.getenv("GROQ_API_KEY")


graph = Neo4jGraph(
    url = NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE
)

print("Connected to Neo4j")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=groq_api_key,
    reasoning_effort="low",
    model_kwargs={
        "parallel_tool_calls": False
    }
)


# print(llm.invoke("Hi, How are you? "))

movie_texts = [
    "Christopher Nolan directed Inception. Leonardo DiCaprio acted in Inception. Inception is a Science Fiction movie released in 2010.",
    "Christopher Nolan directed Interstellar. Matthew McConaughey acted in Interstellar. Interstellar is a Science Fiction movie released in 2014.",
    "Christopher Nolan directed The Dark Knight. Christian Bale acted in The Dark Knight. The Dark Knight is an Action movie released in 2008."
]

documents = [Document(page_content=text) for text in movie_texts]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)

chunks = text_splitter.split_documents(documents)

# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}:", chunk.page_content)


llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Movie", "Genre"],
    allowed_relationships=["DIRECTED", "ACTED_IN", "IN_GENRE"]
)

graph_documents = llm_transformer.convert_to_graph_documents(chunks)

# Store the Graph to Graph Documents
graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,
    include_source=True
)

print("Graph data added to Neo4j")

result = graph.query("""
MATCH (director:Person)-[:DIRECTED]->(movie:Movie)
OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(movie)
RETURN director.id AS director, movie.id AS movie, collect(actor.id) AS actors
""")

# 9. Generation: let the LLM answer using the graph
# GraphCypherQAChain does three simple things:

# Reads the Neo4j schema
# Converts the user question into Cypher
# Executes Cypher and sends the retrieved facts to the LLM for the final answer


chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True
)

response = chain.invoke({
    "query": "Which movies did Christopher Nolan direct?"
})

print(response["result"])