import os
import re
import sys
import textwrap
from operator import itemgetter

# Windows consoles often default to cp1252; UTF-8 avoids UnicodeEncodeError on print.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import TokenTextSplitter
from pydantic import BaseModel, Field
from typing import List

load_dotenv(".env.example")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if not OPENAI_API_KEY:
    raise SystemExit("Set OPENAI_API_KEY in envnew (or export it) - no API key in source code.")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "batch5demo")
def ensure_database_exists() -> None:
    """Create the named database if missing (Neo4j 5+, system permission)."""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", NEO4J_DATABASE):
        raise ValueError(f"Unsafe NEO4J_DATABASE name: {NEO4J_DATABASE!r}")
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        with driver.session(database="system") as session:
            session.run(f"CREATE DATABASE `{NEO4J_DATABASE}` IF NOT EXISTS")
        driver.close()
        print(f"Ensured database exists: {NEO4J_DATABASE}")
    except Exception as exc:
        print(
            f"Note: could not auto-create database ({exc!r}). "
            f"Create `{NEO4J_DATABASE}` manually in Neo4j if connect fails."
        )


ensure_database_exists()
embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small",
)
chat = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0, model="gpt-4o-mini")
kg = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
)
kg.refresh_schema()
print("Connection established and schema refreshed.")

raw_documents = [
    Document(
        page_content=(
            "POLICY PACK: MedFridge Ltd - Cold-chain oncology injectables (EU GDP). "
            "SKUs: MF-Insulin-Pro (2-8 deg C), MF-MAB-Cool (-25 to -15 deg C frozen). "
            "Batch B-4421 (MF-Insulin-Pro) was released from Plant Dresden on 2025-11-02 "
            "with a stability budget of 48 aggregate excursion-minutes above 8 deg C before "
            "lot disposition must be escalated to QP (Qualified Person). Courier Apex "
            "Cold carried the pallet to distributor NordicCare. NordicCare's receiving "
            "SOP states: if logger shows any single contiguous excursion >20 minutes "
            "above 8 deg C, the pallet is QUARANTINED and cannot be merged with sellable "
            "inventory until QA completes investigation. However, NordicCare may "
            "PRE-RELEASE to hospital back-order if (a) the excursion is at most 25 minutes, "
            "(b) MedFridge Medical Affairs emails written exception referencing batch "
            "stability report SR-B4421-REV-C, and (c) the hospital accepts residual "
            "risk form RF-77. Batch B-4408 is unrelated (different stability report). "
            "Regulatory: EMA variation VAR-1189 caps combined truck + warehouse hand-off "
            "delay at 36 hours for MF-Insulin-Pro; Apex logged 31 hours end-to-end for "
            "B-4421. If quarantine is triggered, NordicCare must notify EudraVigilance "
            "only when product has already left quarantine to a patient - not while "
            "held on-site. Finance rule: revenue for B-4421 cannot be recognized at "
            "MedFridge until NordicCare posts 'Available for sale' in ERP ledger code "
            "NCF-AS-01."
        ),
        metadata={
            "title": "MedFridge cold-chain and NordicCare release rules",
            "source": "business:medfridge-policy-pack",
            "domain": "pharma_logistics",
        },
    ),
    Document(
        page_content=(
            "COMMERCIAL MEMO: HelioStack SaaS - Enterprise Agreement EA-2024-771 with "
            "ACME Corp (manufacturing vertical). Contract term 2024-07-01 to 2027-06-30. "
            "Committed ARR: $1.2M for 2,400 named seats of module 'HelioMES'; unit list "
            "price $600/seat/year before tiered discount. Clause 14(b): at each renewal "
            "anniversary, customer may downgrade up to 20% of committed seats without "
            "termination fee; downgraded seats convert to month-to-month list price for "
            "remainder of term unless re-committed. Clause 14(c): if downgrade exceeds "
            "20%, HelioStack may terminate for convenience with 90-day notice and forfeit "
            "only unbilled future periods (no clawback of cash already collected). "
            "Revenue policy (ASC 606 memo FIN-HS-09): for multi-year prepay deals, "
            "HelioStack recognizes revenue straight-line over the service period; "
            "if seats are removed mid-period, deferred revenue is reduced prospectively "
            "from the downgrade effective date - never retroactively restating prior "
            "quarters. Customer success owns 'adoption score' gates: if adoption score "
            "<40 at day-180, auto-renew uplift of 7% is waived. ACME's plant in "
            "Gdansk shares one tenant with subsidiary ACME Baltics; Baltics seats are "
            "counted inside the same 2,400 pool (not additive). Competitor OrionMES is "
            "excluded from data residency routing per Annex D."
        ),
        metadata={
            "title": "HelioStack ACME enterprise agreement and revenue rules",
            "source": "business:heliostack-ea-771",
            "domain": "b2b_saas_contracts",
        },
    ),
    Document(
        page_content=(
            "TRADE OPS BRIEF: FobCo (Mumbai exporter) sold specialty dyes to RhineChem "
            "AG under contract CTR-RH-303. Payment: irrevocable letter of credit LCI-9001 "
            "issued by Deutsche Handelsbank (confirming bank added). Required documents "
            "under UCP 600 field 46A: commercial invoice, packing list, certificate of "
            "origin, full set onboard bill of lading showing shipment from Nhava Sheva "
            "to Hamburg, and phytosanitary certificate. Contract Incoterms 2020: CIF "
            "Hamburg - seller arranges carriage and insurance to named port; risk "
            "transfers when goods pass ship's rail at origin port per Incoterms rules. "
            "The B/L received by the negotiating bank shows 'FOB Nhava Sheva' and "
            "freight 'collect'. Discrepancy playbook: if Incoterms on B/L contradict "
            "contract, RhineChem's treasury may ACCEPT waiver if RhineChem signs "
            "discrepancy indemnity DI-IND-01 before presentation; otherwise documents "
            "must be re-issued. Force majeure addendum FM-22: port worker strikes at "
            "Hamburg do NOT excuse FobCo from presenting conforming documents - they only "
            "extend delivery tolerance by 10 calendar days for physical arrival, not for "
            "documentary compliance. Sanctions screen: RhineChem is Tier-1 cleared; "
            "transhipment via sanctioned corridor SC-List-B is forbidden even if cheaper."
        ),
        metadata={
            "title": "FobCo RhineChem LC and Incoterms discrepancy handling",
            "source": "business:fobco-trade-ctr-rh-303",
            "domain": "trade_finance",
        },
    ),
]

text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
documents = text_splitter.split_documents(raw_documents)
print(f"Loaded {len(documents)} chunk(s) from {len(raw_documents)} business policy document(s).")
print("Sample chunk metadata:", [d.metadata.get("title") for d in documents[:3]])

llm_transformer = LLMGraphTransformer(llm=chat)
graph_documents = llm_transformer.convert_to_graph_documents(documents)
print(graph_documents)
kg.add_graph_documents(
    graph_documents,
    include_source=True,
    baseEntityLabel=True,
)
vector_index = Neo4jVector.from_documents(
    documents=documents,
    embedding=embeddings,
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    index_name="graphrag_classnote_vector",
    node_label="Document",
    embedding_node_property="embedding",
    text_node_property="text",
    pre_delete_collection=True,
)
class Entities(BaseModel):
    """Identifying information about entities."""

    names: List[str] = Field(
        ...,                    # Ellipsis = REQUIRED field (no default; LLM must always return a list)
        description="Person, organization, product, or key technical concept "
        "names that appear in the text (for graph-aware retrieval).",
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You extract person, organization, product, and notable concept entities "
            "from the user's question for knowledge-graph lookup.",
        ),
        (
            "human",
            "Extract entities from: {question}",
        ),
    ]
)
entity_chain = prompt | chat.with_structured_output(Entities)

kg.query(
    "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]"
)
def generate_full_text_query(input: str) -> str:
    """Convert free-text into a Lucene fuzzy query.

    Example: "MedFridge NordicCare" -> "MedFridge~2 AND NordicCare~2"

    - remove_lucene_chars() strips special chars (+, -, !, etc.) that would break Lucene syntax
    - ~2 = fuzzy matching with edit distance 2 (tolerates typos/spelling variations)
    - AND = all words must match (not just any one)
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    if not words:
        return ""
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()


def structured_retriever(question: str) -> str:
    """Graph-based retrieval: extract entities from the question, find them in
    the knowledge graph via fulltext search, then traverse their relationships
    to gather structured context (e.g., 'MedFridge - RELEASED -> Batch B-4421').

    Returns a newline-separated string of relationship triples."""
    result = ""
    # Step A: Use LLM to extract entity names from the user's question
    entities = entity_chain.invoke({"question": question})
    for entity in entities.names:
        print(f" Getting Entity: {entity}")
        # Step B: For each entity, search the fulltext index and traverse relationships
        response = kg.query(
            # queryNodes: search the "entity" fulltext index with fuzzy query, return top 2 matches
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
            YIELD node,score
            CALL {
              WITH node
              MATCH (node)-[r:!MENTIONS]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
              UNION ALL
              WITH node
              MATCH (node)<-[r:!MENTIONS]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
            }
            RETURN output LIMIT 50
            """,
            # !MENTIONS excludes the MENTIONS relationship (source doc link) -- we only want
            # domain-specific relationships like RELEASED, CARRIED, QUARANTINED, etc.
            # UNION ALL collects BOTH outgoing and incoming relationships for full context.
            {"query": generate_full_text_query(entity)},
        )
        result += "\n".join([el["output"] for el in response])
    return result

def retriever(question: str):
    """The heart of GraphRAG: combines two retrieval strategies for richer context.

    1. structured_data   = relationship triples from the Knowledge Graph
                           (e.g., "NordicCare - QUARANTINED -> Batch B-4421")
    2. unstructured_data = semantically similar text chunks from the vector index
                           (the raw policy text that is most relevant)

    Both are merged into a single context string and sent to the LLM."""
    print(f"Search query: {question}")
    structured_data = structured_retriever(question)               # graph traversal results
    unstructured_data = [
        el.page_content for el in vector_index.similarity_search(question)  # top-k similar chunks
    ]
    final_data = f"""Structured data:
{structured_data}
Unstructured data:
{chr(10).join(f"--- doc chunk ---{chr(10)}{t}" for t in unstructured_data)}
"""
    print(f"\n--- Retrieved context preview (first ~1800 chars) ---\n{final_data[:1800]}...")
    return final_data

template = """Answer using ONLY the context below. Apply stated policies, numbers, and conditional rules explicitly.
If the context is insufficient, say what is missing - do not invent facts.

Context:
{context}

Question: {question}

Answer (clear and concise):"""
qa_prompt = ChatPromptTemplate.from_template(template)
chain = (
    RunnableParallel(
        {
            # itemgetter("question") pulls the "question" value from the input dict
            # RunnableLambda wraps a plain function so it can be used in a | pipe chain
            "context": RunnableLambda(itemgetter("question")) | RunnableLambda(retriever),
            "question": RunnableLambda(itemgetter("question")),
        }
    )
    | qa_prompt       # fill the prompt template
    | chat            # send to LLM
    | StrOutputParser()  # extract plain string from AIMessage
)
DEMO_QUESTIONS = [
    (
        "MedFridge / NordicCare",
        "Batch B-4421 (MF-Insulin-Pro) had a single contiguous temperature excursion "
        "of 22 minutes above 8 deg C before NordicCare received it. Per the policy pack, "
        "must the pallet be quarantined, or can it be pre-released to a hospital "
        "back-order - and what three conditions must be met for pre-release?",
    ),
    (
        "HelioStack / ACME",
        "Under EA-2024-771 and revenue memo FIN-HS-09, if ACME downgrades exactly 20% "
        "of committed HelioMES seats effective mid-quarter (not exceeding 20%), how is "
        "recognized revenue adjusted - retrospectively or prospectively - and what "
        "happens to cash already collected?",
    ),
    (
        "FobCo / RhineChem LC",
        "Bill of lading shows FOB Nhava Sheva and freight collect, but contract CTR-RH-303 "
        "is CIF Hamburg. Can RhineChem's treasury still accept documents to pay under "
        "LCI-9001 without re-issued B/L - if yes, what must happen first?",
    ),
    (
        "Cross-check (same corpus)",
        "Does MedFridge recognize revenue for batch B-4421 when NordicCare only "
        "quarantines the pallet (no 'Available for sale' in NCF-AS-01)? Answer yes/no "
        "and cite the rule.",
    ),
]

def print_qa_block(title: str, question: str, answer: str) -> None:
    """Pretty-print a single Q&A pair with visual separators."""
    width = 78
    print("\n" + "=" * width)
    print(f" TOPIC: {title}")
    print("=" * width)
    print("QUESTION:")
    print(textwrap.fill(question, width=width))
    print("-" * width)
    print("ANSWER:")
    print(textwrap.fill(answer.strip(), width=width))
    print("=" * width)


# Quick smoke test: run only the structured retriever on the first question
# to verify entity extraction + graph traversal works before the full chain
print("\n" + "#" * 78)
print("# Structured retriever smoke test (first demo question entities)")
print("#" * 78)
_title0, q0 = DEMO_QUESTIONS[0]
print(structured_retriever(q0)[:1200] or "(no graph lines for extracted entities)")

# Run the full GraphRAG chain for every demo question
answers = []
for idx, (topic_title, question) in enumerate(DEMO_QUESTIONS, start=1):
    print(f"\n>>> Running chain for question {idx}/{len(DEMO_QUESTIONS)}...")
    ans = chain.invoke({"question": question})  # triggers: entity extraction -> graph + vector retrieval -> LLM answer
    answers.append(ans)
    print_qa_block(topic_title, question, ans)

# Basic sanity check: ensure no question got an empty answer
for i, ans in enumerate(answers, start=1):
    assert ans.strip(), f"Empty answer for question {i}"
print("\nSelf-check passed: all answers non-empty.")
