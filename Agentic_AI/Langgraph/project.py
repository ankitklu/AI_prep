import os
from typing import TypedDict

#Lets create the state first

class pipelinestate(TypedDict):
    raw_input : str
    edited_text : str
    script_text : str
    final_output: str

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model = "groq/compound-mini", temperature=0.7)

def editor_node(state: pipelinestate) -> dict: # Cleans up grammar and node
    """Stage 1: Cleasn up grammar, removes typos, and refines the tone."""

    prompt = (
        "You are an expert copyediror. Clean up the followig raw text. "
        "Fix any grammatical errors, spelling mistakes, and smooth out the transition flow"
        "while keeping the core message intact. Return only the edited text. \n\n"
        f"Text:\n {state['raw_input']}"
    )

    respone = llm.invoke(prompt)

    return {
        "edited_text" : respone.content.strip()
    }

def scriptwriter_node(state: pipelinestate) -> dict:

    """Stage 2: Formats the clean text into an engaging video script style."""
    print("\n--- [Stage 2] Executing Scriptwriter Node ---")

    prompt = (
        "You are charimatic YouTube content creator, Take this edited text and transform"
        "it linto a highly engaging , punchy, conversational video script hook. Make it sound"
        "like a real person speaking passionately. Return only the script conetn. \n\n"
        f"Edited Text:\n{state['edited_text']}"
    )

    response = llm.invoke(prompt)
    return {"script_text": response.content.strip()}

def translator_node(state: pipelinestate) -> dict:
    """Stage 3: Translates the script into natural flowing Hinglish."""
    print("\n--- [Stage 3] Executing Hinglish Translator Node ---")

    prompt = (
        "You are an expert content localizer for the Indian market. Take the following script "
        "and convert it into natural, flowing 'Hinglish'. Do not simply translate it sentence by sentence "
        "or repeat information. Alternating comfortably between Hindi and English phrases as "
        "an intellectual tech educator would speak naturally on a live stream. Keep the energy high. "
        "Return only the final Hinglish text.\n\n"
        f"Script:\n{state['script_text']}"
    )

    response = llm.invoke(prompt)
    return {"final_output": response.content.strip()}

#create the graph to create the nodes so that we have to create teh edges.
# Edges are very important to create teh workflows.


from langgraph.graph import StateGraph, START, END

#create the graph
graph = StateGraph(pipelinestate)

#add the nodes is our graph

graph.add_node("editor", editor_node)
graph.add_node("scriptwriter", scriptwriter_node)
graph.add_node("translator", translator_node)

#Add edges(sequential - one after another)

graph.add_edge(START, "editor")
graph.add_edge("editor", "scriptwriter")
graph.add_edge("scriptwriter", "translator")
graph.add_edge("translator", END)

#compile the graph
app = graph.compile()

result = app.invoke({
    "raw_input" : "today we gonna talk about how ai agents work, its actually pretty simple once you"
                  "break it down, so basically an agent is just a llm that can use tools and make"
                  "decisions on its own instead of just answering one question"
})

print("Your Result are:- \n\n")
print(result['final_output'])

