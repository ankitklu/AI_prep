from langchain.tools import tool

@tool # decorator to register the function as a tool
def get_greeting(name:str) -> str:
    """A simple greeting tool that takes a name as input and returns a greeting message."""
    return f"Hello, {name}! Welcome to the AI tool."

result = get_greeting.invoke({"name":"Ankit"})  # Example usage of the tool

print(result)

print(get_greeting.name)  # Print the name of the tool
print(get_greeting.description)  # Print the description of the tool
print(get_greeting.args)  # Print the arguments of the tool

