
# Scarpping agent
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re
import bs4
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langsmith import traceable

load_dotenv()

# globally declare embedding
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)


# Making each compent traceable by langsmith
# COMPONENT 1: Cache memory check
@traceable(name="Agent 1 - Cache Search")
def check_cache(claim):
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory="my_chroma_db",
        collection_name="query_informations"
    )

    results = vector_store.similarity_search_with_score(
        query=claim,
        k=5
    )

    print("Number of retrieved chunks:", len(results))
    for doc, score in results:
        print(score)

    return results


# COMPONENT 2: Gemini search query generation
@traceable(name="Agent 1 - Gemini Query Generation")
def generate_search_query(claim):
    # Creating the query
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    template = PromptTemplate(
        template="""
    You are an expert search query generator.

    Convert the following user input into ONE high-quality web search query for fact-checking.

    Rules:
    - Preserve all important entities (people, organizations, places, products, missions, events, dates).
    - Do NOT simplify or generalize the topic.
    - If the input is a question about a news event, keep the event name exactly.
    - Make the query broad enough to retrieve multiple reliable sources, but specific enough to avoid unrelated topics.
    - Do NOT answer the question.
    - Output ONLY the search query.

    User input:
    {claim}
    """,
        input_variables=["claim"]
    )

    parser = StrOutputParser()
    chain1 = template | model | parser
    result = chain1.invoke({"claim": claim})

    # Remove unwanted quotes/spaces
    return result.strip().strip('"').strip("'")


# COMPONENT 3: Trusted web search
@traceable(name="Agent 1 - Trusted Web Search")
def search_trusted_sources(query):
    trusted_sites = (
        "site:cdc.gov OR "
        "site:who.int OR "
        "site:nih.gov OR "
        "site:nature.com OR "
        "site:reuters.com OR "
        "site:apnews.com"
    )

    try:
        trusted_search = DuckDuckGoSearchResults(num_results=5)
        return trusted_search.run(f"{query} ({trusted_sites})")
    except Exception as e:
        print("Trusted search failed:", e)
        return ""


# COMPONENT 4: Normal web search
@traceable(name="Agent 1 - Normal Web Search")
def search_normal_sources(query):
    try:
        normal_search = DuckDuckGoSearchResults(num_results=5)
        return normal_search.run(query)
    except Exception as e:
        print("Normal search failed:", e)
        return ""


# COMPONENT 5: Extract and deduplicate URLs
@traceable(name="Agent 1 - URL Extraction")
def extract_urls(search_results):
    # Taking the URLs from search results for web scraping.
    # Using regex to extract URLs from search results.
    urls = re.findall(r'https?://[^\s,]+', search_results)
    urls = list(dict.fromkeys(urls))  # Remove duplicate URLs
    print(urls)
    return urls


# COMPONENT 6: Scrape an individual URL
@traceable(name="Agent 1 - Web Scraping")
def scrape_url(url):
    try:
        loader = WebBaseLoader(
            url,
            bs_kwargs={"parse_only": bs4.SoupStrainer("p")},
            requests_kwargs={
                "headers": {"User-Agent": "Mozilla/5.0"},
                "timeout": 10
            }
        )

        print(f"Success: {url}")
        return loader.load()

    except Exception as e:
        print(f"Failed: {url}")
        print(e)
        return []


# COMPONENT 7: Scrape multiple URLs concurrently
@traceable(name="Agent 1 - Concurrent Scraping")
def scrape_urls(urls):
    docs = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(scrape_url, url)
            for url in urls
        ]

        for future in as_completed(futures):
            docs.extend(future.result())

    return docs


# COMPONENT 8: Text chunking
@traceable(name="Agent 1 - Text Chunking")
def chunk_documents(docs):
    # Chunking process
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    actual_info = []
    metadatas = []

    for info in docs:
        chunks = text_splitter.split_text(info.page_content)

        for chunk in chunks:
            # Skip tiny chunks
            if len(chunk.strip()) < 100:
                continue

            actual_info.append(chunk)
            metadatas.append({
                "url": info.metadata.get("source", "unknown")
            })

    return actual_info, metadatas


# COMPONENT 9: Store chunks in ChromaDB
@traceable(name="Agent 1 - ChromaDB Storage")
def store_chunks(actual_info, metadatas):
    # Making embeddings and vector store ChromaDB
    print("Number of chunks:", len(actual_info))

    if not actual_info:
        return

    Chroma.from_texts(
        texts=actual_info,
        embedding=embeddings,
        persist_directory="my_chroma_db",
        collection_name="query_informations",
        metadatas=metadatas
    )


# Add traceable to trace the whole Agent 1
@traceable(name="Agent 1 - Search and Cache")
def run_agent1(claim):

    # CACHE MEMORY check
    results = check_cache(claim)

    # If relevant chunks already exist, skip searching
    if results and results[0][1] < 0.40:
        print("Relevant chunks found. Skipping search & scraping.")

        return {
            "claim": claim,
            "cached": True,
            "docs": [doc for doc, score in results]
        }

    # Creating the query using Gemini
    result = generate_search_query(claim)

    # Searching using DuckDuckGo
    # Searching 5 URLs from trusted sites and then 5 normal results
    trusted_results = search_trusted_sources(result)
    normal_results = search_normal_sources(result)

    # Combine both
    search_results = trusted_results + "\n" + normal_results

    # Extract URLs and remove duplicates
    urls = extract_urls(search_results)

    # Scrape pages concurrently
    docs = scrape_urls(urls)

    # Chunk the scraped information
    actual_info, metadatas = chunk_documents(docs)

    # Store chunks in ChromaDB
    store_chunks(actual_info, metadatas)

    # Step 6: export the claim, cached and docs
    return {
        "claim": claim,
        "cached": False,
        "docs": None
    }
