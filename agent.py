import os
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# 1. Define a tool (a function the agent can call)
@tool
def get_current_weather(city: str) -> str:
    """Get the current weather in a given city."""
    if city == "San Francisco":
        return "It's always sunny in San Francisco!"
    else:
        return f"The weather in {city} is mild and pleasant."

# 2. Initialize the model with tool use capabilities
llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# 3. Create the agent using langgraph (modern LangChain 1.x API)
agent = create_agent(llm, [get_current_weather])

# 4. Run the agent
result = agent.invoke({"messages": [{"role": "user", "content": "What is the weather like in San Francisco?"}]})
print(result['messages'][-1].content)
