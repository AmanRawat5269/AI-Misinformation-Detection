from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from sentence_transformers import CrossEncoder

#Declare reranker and embedding globally
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

embeddings=OllamaEmbeddings(model='nomic-embed-text', num_ctx=8192)

#giving a little more edge to trusted chunks
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


def run_agent2(agent1_output): 
    
    #If cached is present
    claim = agent1_output["claim"]

    if agent1_output["cached"]:
        print("Using cached chunks...")
        results = agent1_output["docs"]

    else:
        print("Searching Chroma...")
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory='my_chroma_db',
            collection_name='query_informations'
        )
        
        results = vector_store.max_marginal_relevance_search(
            query=claim,
            k=8,
            fetch_k=20 
        )  
    
    
    #Rerank using CrossEncoder 
      
    passages = [doc.page_content for doc in results]
    rerank_scores = reranker.predict([(claim, passage) for passage in passages])

    #Sort by rerank score and keep top 3
    ranked = []

    for doc, score in zip(results, rerank_scores):

        url = doc.metadata.get("url", "")

        # Give a small bonus to trusted sources
        if any(domain in url for domain in TRUSTED_DOMAINS):
            score += 0.08

        ranked.append((doc, score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    top_results = [doc for doc, score in ranked[:3]]

    return top_results
