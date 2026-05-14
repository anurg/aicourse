import os
import argparse
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

OUTPUT_FILE = "output.txt"

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--refresh", action="store_true", help="Re-invoke LLM and overwrite cached output")
args = parser.parse_args()

if not args.refresh and os.path.exists(OUTPUT_FILE):
    print(f"Reading from cached file: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "r") as f:
        print(f.read())
else:
    # print("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
    model = init_chat_model(model="gpt-5.2")

    question = "Can you explain Langchain?"
    messages = [SystemMessage(content="You are a help tech trainer explaining hard things in simple language."),
                HumanMessage(content=question)]
    result = model.invoke(messages)

    with open(OUTPUT_FILE, "w") as f:
        f.write(result.content)

    print(result.content)
    print(f"\nOutput saved to {OUTPUT_FILE}")