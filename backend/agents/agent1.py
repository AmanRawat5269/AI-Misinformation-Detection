#Scarpping agent
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


load_dotenv()

#globally declare embedding 
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

def run_agent1(claim):
    
    # CACHE MEMORY check
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
    
    # If relevant chunks already exist, skip searching
    if results and results[0][1] < 0.40:
        print("Relevant chunks found. Skipping search & scraping.")
        
        
        return {
        "claim": claim,
        "cached": True,
        "docs": [doc for doc, score in results]
    }
        
    #Creating the query 
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
    result = chain1.invoke({'claim':claim})
    # Remove unwanted quotes/spaces
    result = result.strip().strip('"').strip("'")


    #Searching using duckduck go search
    
    #Searching 5 urls from trustes_sites and than 5 randomly
    trusted_sites = (
    "site:cdc.gov OR "
    "site:who.int OR "
    "site:nih.gov OR "
    "site:nature.com OR "
    "site:reuters.com OR "
    "site:apnews.com"
    )

    # Trusted search (5 results)
    try:
        trusted_search = DuckDuckGoSearchResults(num_results=5)
        trusted_results = trusted_search.run(f"{result} ({trusted_sites})")
    except Exception as e:
        print("Trusted search failed:", e)
        trusted_results = ""

    # Normal web search (5 results)
    try:
        normal_search = DuckDuckGoSearchResults(num_results=5)
        normal_results = normal_search.run(result)
    except Exception as e:
        print("Normal search failed:", e)
        normal_results = ""

    # Combine both
    search_results = trusted_results + "\n" + normal_results


    #Taking the url from the search_result and than send them to the webbasescrpper for scraping.
    #using regex to extract the urls from the search_results
    urls = re.findall(r'https?://[^\s,]+', search_results)
    urls = list(dict.fromkeys(urls))   # Remove duplicate URLs
    print(urls)
    
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
        
    
    docs = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_url, url) for url in urls]

        for future in as_completed(futures):
            docs.extend(future.result())


    #Chunking process
    
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


    
    #Making embedding and vectorstore chromaDB
    
    print("Number of chunks:", len(actual_info))

    vector_store = Chroma.from_texts(
        texts=actual_info,
        embedding = embeddings,
        persist_directory = 'my_chroma_db',
        collection_name = 'query_informations',
        metadatas = metadatas
    )

    #step6 export the claim , cached and docs
    return {
        "claim": claim,
        "cached": False,
        "docs": None
    }
