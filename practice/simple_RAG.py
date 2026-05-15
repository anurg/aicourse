from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

pdf_path = r"ness_labs_mindful_productivity_guide.pdf"
print(f"\n📄 Loading: {pdf_path}")
loader = PyPDFLoader(pdf_path)
documents = loader.load()

print(f"✅ Loaded {len(documents)} pages")
print(f"\n📖 Page 1 Preview:")
print("-" * 50)
print(documents[0].page_content[:400] + "...")
print(f"\n📋 Metadata: {documents[0].metadata}")

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

print(f"\n⚙️  Settings:")
print(f"   chunk_size: 1000")
print(f"   chunk_overlap: 200")
    
chunks = text_splitter.split_documents(documents)

print(f"\n✅ Created {len(chunks)} chunks from {len(documents)} pages")
    
# Statistics
lengths = [len(c.page_content) for c in chunks]
print(f"\n📊 Chunk Statistics:")
print(f"   Min: {min(lengths)} chars")
print(f"   Max: {max(lengths)} chars")
print(f"   Avg: {sum(lengths)//len(lengths)} chars")

from langchain_openai import OpenAIEmbeddings
# import numpy as np
embeddings = OpenAIEmbeddings()

from langchain_core.vectorstores import InMemoryVectorStore
vector_store = InMemoryVectorStore(embeddings)
ids = vector_store.add_documents(documents=chunks)

retriever = vector_store.as_retriever(search_kwargs={"k": 4})
question="Summarize the document in 500 words!"

###prompt
stuff_template = """Answer based on the context below.
Context: {context}
Question: {question}
Answer:"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

stuff_prompt = ChatPromptTemplate.from_template(stuff_template)
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

stuff_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | stuff_prompt
        | llm
    )
# result = stuff_chain.invoke(question)
# print (result.content)
for result in stuff_chain.stream(question):
    print(result.content, end="")


    # TODOS - Use Chroma in-memory and Persistence beyond session for preventing embeddings multiple times.
    # TODOS - 