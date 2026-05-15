"""
RAG with Chroma — supports both in-memory (ephemeral) and on-disk (persistent) modes.

Install once:
    pip install langchain-chroma

Toggle PERSIST below:
    True  → on-disk store at PERSIST_DIR, survives across runs
    False → ephemeral, lives only inside this process
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
PDF_PATH        = r"ness_labs_mindful_productivity_guide.pdf"
COLLECTION_NAME = "mindful_productivity"
PERSIST         = True                     # False → in-memory ephemeral
PERSIST_DIR     = "./chroma_db"            # used only when PERSIST is True
CHUNK_SIZE      = 1000
CHUNK_OVERLAP   = 200
TOP_K           = 4

# ─────────────────────────────────────────────────────────────────
# Build (or open) the vector store
# ─────────────────────────────────────────────────────────────────
embeddings = OpenAIEmbeddings()

chroma_kwargs = {
    "collection_name":    COLLECTION_NAME,
    "embedding_function": embeddings,
}
if PERSIST:
    chroma_kwargs["persist_directory"] = PERSIST_DIR

vector_store = Chroma(**chroma_kwargs)

# Skip re-ingest if the collection is already populated.
# (Only meaningful when PERSIST=True; ephemeral stores always start empty.)
existing_count = vector_store._collection.count()

if existing_count > 0:
    print(f"✅ Opened collection '{COLLECTION_NAME}' with {existing_count} chunks — skipping ingest")
else:
    print(f"\n📄 Loading: {PDF_PATH}")
    documents = PyPDFLoader(PDF_PATH).load()
    print(f"✅ Loaded {len(documents)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size     = CHUNK_SIZE,
        chunk_overlap  = CHUNK_OVERLAP,
        length_function = len,
        separators     = ["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    lengths = [len(c.page_content) for c in chunks]
    print(f"\n📊 Chunk Statistics:")
    print(f"   chunks: {len(chunks)}")
    print(f"   min:    {min(lengths)} chars")
    print(f"   max:    {max(lengths)} chars")
    print(f"   avg:    {sum(lengths)//len(lengths)} chars")

    vector_store.add_documents(documents=chunks)
    print(f"✅ Embedded and stored {len(chunks)} chunks")

# ─────────────────────────────────────────────────────────────────
# Retrieval + LCEL chain
# ─────────────────────────────────────────────────────────────────
retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K})

stuff_template = """Answer based on the context below.
Context: {context}
Question: {question}
Answer:"""

stuff_prompt = ChatPromptTemplate.from_template(stuff_template)
llm          = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

stuff_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | stuff_prompt
    | llm
    | StrOutputParser()
)

# ─────────────────────────────────────────────────────────────────
# Ask
# ─────────────────────────────────────────────────────────────────
question = "What is the best practice for Mindful Productivity which helps in Procrastination? How can I practice it?"

print("\n🧠 Answer:\n")
print(stuff_chain.invoke(question))