# 🛡️ AI Misinformation Detection

An AI-powered fact-checking system that verifies user claims using a multi-agent Retrieval-Augmented Generation (RAG) pipeline.

The system retrieves evidence from trusted sources, reranks the retrieved information using a CrossEncoder, and generates a final verdict with supporting explanations and citations.

## 📸 Demo
Interface
<img width="1098" height="652" alt="image" src="https://github.com/user-attachments/assets/1f88136f-954e-4577-b914-2a76ef6dacb4" />
---
### Fact Check Result
Example 1
<img width="987" height="875" alt="Screenshot 2026-07-02 003228" src="https://github.com/user-attachments/assets/65c460bd-4ce3-4a8a-9a6d-f0fe34111c6e" />
---
Example 2
<img width="970" height="870" alt="Screenshot 2026-07-02 003952" src="https://github.com/user-attachments/assets/d4ec6a8f-4d72-418a-b0f4-83d413905d98" />
---
Example 3
<img width="976" height="877" alt="Screenshot 2026-07-02 004118" src="https://github.com/user-attachments/assets/cb784d3f-f485-4ae3-b790-a4b5180196eb" />
---

## ✨ Features

- Multi-Agent RAG Architecture
- Intelligent Web Search
- Parallel Web Scraping
- Semantic Search using ChromaDB
- CrossEncoder Reranking
- Cache-based Retrieval
- LLM-powered Verdict Generation
- Confidence Score
- Evidence-based Explanations
- Source Attribution


## 🏗️ Architecture

```text
                User Query
                     │
                     ▼
     Agent 1 (Query Generation)
       ├── Search (DuckDuckGo)
       ├── Parallel Web Scraping
       ├── Chunking
       └── Embedding
                     │
                     ▼
                ChromaDB
                     │
                     ▼
       Agent 2 (Retrieval + MMR)
                     │
                     ▼
      CrossEncoder Reranking
                     │
                     ▼
      Agent 3 (LLM Fact Checker)
                     │
                     ▼
        Verdict + Confidence + Sources
                     │
                     ▼
                Streamlit UI
```

## ⚙️ How It Works

1. The user enters a claim or news-related question.

2. **Agent 1**
   - Converts the input into an optimized search query.
   - Searches trusted and general web sources.
   - Scrapes relevant webpages.
   - Splits the content into chunks and stores embeddings in ChromaDB.
   - Reuses cached information if available.

3. **Agent 2**
   - Retrieves relevant chunks using semantic search (MMR).
   - Reranks the retrieved evidence using a CrossEncoder.
   - Prioritizes trusted domains such as Reuters, AP News, Nature, CDC, and WHO.

4. **Agent 3**
   - Uses the highest-quality evidence to generate:
     - Verdict (True / False / Misleading)
     - Confidence Score
     - Explanation
     - Supporting Sources

5. The final fact-check result is displayed through the Streamlit frontend.


## 🚀 Installation

```bash
git clone https://github.com/<username>/AI-Misinformation-Detection.git
cd AI-Misinformation-Detection

pip install -r requirements.txt
```

### Start Backend

```bash
uvicorn backend.api:app --reload
```

### Start Frontend

```bash
streamlit run frontend/app.py
```

## 👨‍💻 Future Improvements
- Better cache invalidation
- Support PDF evidence
- Hybrid Retrieval
- Claim history
- User authentication
