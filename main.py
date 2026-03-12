import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Initialize the ChatAnthropic model.
# The API key will be automatically picked up from the ANTHROPIC_API_KEY environment variable.
# You can specify a different model, such as "claude-3-sonnet-20240229" or "claude-3-haiku-20240307".
model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.0)

# Define a simple prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that writes haikus."),
        ("human", "{question}"),
    ]
)

# Define the output parser
output_parser = StrOutputParser()

# Create the LangChain chain
chain = prompt | model | output_parser

# Invoke the chain and print the response
response = chain.invoke({"question": "Why is the sky blue?"})
print(response)
