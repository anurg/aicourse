import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

load_dotenv()

model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that writes haikus."),
        ("human", "{question}"),
    ]
)

# Define the graph state
class State(TypedDict):
    question: str
    response: str

# Define the node function
def call_model(state: State) -> State:
    messages = prompt.format_messages(question=state["question"])
    result = model.invoke(messages)
    return {"question": state["question"], "response": result.content}

# Build the graph
graph = StateGraph(State)
graph.add_node("call_model", call_model)
graph.set_entry_point("call_model")
graph.add_edge("call_model", END)
app = graph.compile()

# Invoke the graph and print the response
result = app.invoke({"question": "Why is the sky blue?"})
print(result["response"])
