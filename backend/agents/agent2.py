
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sentence_transformers import CrossEncoder
from langsmith import traceable

# Declare reranker and embedding globally
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

# Giving a little more edge to trusted chunks
TRUSTED_DOMAINS = [
    "cdc.gov",
    "who.int",
    "nih.gov",
    "nature.com",
    "pubmed.ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov",
    "reuters.com",
    "apnews.com"
]


@traceable(name="Agent 2 - Chroma Retrieval")
def retrieve_chunks(agent1_output):
    # If cached is present
    if agent1_output["cached"]:
        print("Using cached chunks...")
        # Docs store the actual chunks
        results = agent1_output["docs"]

    else:
        print("Searching Chroma...")
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory='my_chroma_db',
            collection_name='query_informations'
        )

        # Retrieve relevant chunks using MMR
        results = vector_store.max_marginal_relevance_search(
            query=agent1_output["claim"],
            k=8,
            fetch_k=20
        )

    return results


@traceable(name="Agent 2 - CrossEncoder Reranking")
def rerank_chunks(claim, results):
    passages = [doc.page_content for doc in results]

    rerank_scores = reranker.predict(
        [(claim, passage) for passage in passages]
    )

    ranked = []

    for doc, score in zip(results, rerank_scores):
        url = doc.metadata.get("url", "")

        # Give a small bonus to trusted sources
        if any(domain in url for domain in TRUSTED_DOMAINS):
            score += 0.08

        ranked.append((doc, score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked


@traceable(name="Agent 2 - Select Top 3")
def select_top_results(ranked):
    # Keep the top 3 chunks
    return [doc for doc, score in ranked[:3]]


@traceable(name="Agent 2 - Retrieval and Reranking")
def run_agent2(agent1_output):
    claim = agent1_output["claim"]

    # Step 1: Retrieve chunks
    results = retrieve_chunks(agent1_output)

    # Step 2: Rerank retrieved chunks
    ranked = rerank_chunks(claim, results)

    # Step 3: Select the top 3
    top_results = select_top_results(ranked)

    return top_results
