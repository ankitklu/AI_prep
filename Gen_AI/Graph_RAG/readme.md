# The 5 things we need to know.

1. Node - A real thing. Example: a Movie or Person
2. Label - The node type. Example: :Movie, :Person
3. Property - Details about a node. Example: title, year, name
4. Relationship - How nodes are connected, ACTED_IN
5. Direction - Who connects to whom. Person -> Movie


# Cypher: How we tal to the graph
- Cypher is Neo4j's query language. Think in patterns instead of joins.

## CREATE
- Create a node or relationship.
- ```CREATE (:Movie{title: "Inception"})```

## MATCH
- Find a graph pattern
- ```MATCH(m:Movie) RETURN m```

## MATCH + Relationship
- Traverse Connections
- ```MATCH (p)-[:ACTED_IN]->(m) RETURN p,m````


## Read this pattern lika a sentence:

(Person) -[:ACTED_IN] -> (Movie)
- "Find a Person who ACTED_IN a Movie."

### Cypher Queries
CREATE (Leo: Person{name:"Leonardo DiCaprio", born:1974})
CREATE (Matthew: Person{name:"Matthew McConaughey", born:1969})

CREATE(Inception: Movie{title:"Inception", released:2010})
CREATE(Inception: Movie{title:"Interstellar", released:2014})

CREATE (Nolan: Person{name: "Christopher Nolan"}),
       (Incpetion: Movie {title: "Inception"})
CREATE (Nolan)-[:DIRECTED] -> (Incpetion);

CREATE (Nolan: Person{name: "Christopher Nolan"}),
       (Incpetion: Movie {title: "Inception"})
CREATE (Nolan)-[:DIRECTED] -> (Incpetion);


# How to Implement a GRAPH RAG ?
- Step 1:- Break documents into chunks
- Step 2:- Extract Entities and relationships ---------- Chunk -> LLM -> Extracted Graph facts (Nodes : Movie, person, Genre ; Relationships: Christopher Nolan DIRECTED -> Inception, Lenonardo DiCaprio - ACTED_IN -> Inception)
- Step 3:- Build the graph Schema --------- Node Labels | Relationship Types | Simple Pattern
- Step 4:- Store the graph (Neo4j) - Entities(Nodes) and Relationships in a Graph Database


## What info is hidden inside these sentences ?
- Entities: Movies | People | Genres
- Relationships: DIRECTED | ACTED_IN | HAS_GENRE
- Properties: name |title | released


# GRAPH RAG

- Question -> Graph Retrieval -> LLM provides the answer

1. User Question (A user asks a question in natural language) -> "Who acted in movies directed by Christopher Nolan ?"
2. LLM Understands the question (The LLM extracts key entities and understands the intent). -> Identified from the question: Christopher Nolan, acted in , Movies
3. LLM reads Neo4j Schema (The LLM looks at the graph schema to understand how the data is structured) -> Graph Schema (Neo4j) -> Nodes:- Person, Movie, Genre -> Relationships: DIRECTED, ACTED_IN, HAS_GENRE
4. Generate Cypher Query (The LLM generates a Cypher query based on the question and schema) ->
```MATCH (d:Person)-[:DIRECTED]->(m:Movie)
   MATCH (a:Person)-[:ACTED_IN]->(m)
   WHERE d.name="Christopher Nolan"
   RETURN m.title, a.name
````

5. Neo4j Graph Retrieval
6. Retrieved Graph Context
7. LLM Generated the Final Answer

# RAG Pipeline

* Two phases : build the knowledge graph once, then query it many times.

## INJESTION/BUILD
Documents | Chunk | Extract Graph | Neo4j

## Query / ANSWER
Question | Text/Cypher | Graph Retrieval | Answer