# Egypt Tourism RAG Assistant

A multilingual **Retrieval-Augmented Generation (RAG)** assistant for answering tourism-related questions about Egypt in **Arabic and English**.

The system retrieves relevant information from a tourism knowledge base, reranks the retrieved passages, and generates grounded answers with source references.

### Live Demo

[Try the deployed application](https://egypt-tourism-rag-mfupvxjkvv5jfp87vhkdbn.streamlit.app/)

---

## Features

* Arabic & English question answering
* Multilingual semantic search
* MMR-based retrieval
* Cross-encoder reranking
* Grounded Gemini responses
* Source references
* FastAPI backend
* Streamlit interface
* Docker support

---

## Architecture

```text
User
 │
 ▼
Streamlit
 │
 ▼
FastAPI
 │
 ▼
RAG Pipeline
 │
 ├── BGE-M3 Embeddings
 │
 ├── ChromaDB
 │      └── MMR Retrieval
 │
 ├── BGE Reranker
 │
 └── Gemini
        │
        ▼
   Answer + Sources
```

---

## RAG Pipeline

```text
User Question
      ↓
Multilingual Embedding
      ↓
MMR Retrieval
      ↓
Cross-Encoder Reranking
      ↓
Relevant Context
      ↓
Gemini Generation
      ↓
Grounded Answer + Sources
```

### Models

| Component    | Model                     |
| ------------ | ------------------------- |
| Embeddings   | `BAAI/bge-m3`             |
| Reranker     | `BAAI/bge-reranker-v2-m3` |
| Generation   | Google Gemini             |
| Vector Store | ChromaDB                  |

### Retrieval Configuration

```text
MMR
k = 10
fetch_k = 25
lambda_mult = 0.6
```

---

## Evaluation

The retrieval pipeline was evaluated on Arabic and English tourism queries.

| Metric      |     Score |
| ----------- | --------: |
| Recall@3    | **0.851** |
| Precision@3 | **0.507** |
| MRR         | **0.971** |
| Hit Rate    | **1.000** |

---

## Project Structure

```text
Egypt-Tourism-Rag/
│
├── chroma_db_main/
├── notebooks/
│   └── Tourism_RAG_Assistant.ipynb
│
├── main.py
├── rag_pipeline.py
├── streamlit_app.py
├── requirements.txt
├── Dockerfile
├── config.toml
└── README.md
```

---

## Run Locally

### Install

```bash
git clone https://github.com/FatmaEissa/Egypt-Tourism-Rag.git
cd Egypt-Tourism-Rag

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Environment

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

### Start FastAPI

```bash
uvicorn main:app --reload
```

### Start Streamlit

In another terminal:

```bash
streamlit run streamlit_app.py
```

---

## API

### `GET /health`

Health check endpoint.

### `POST /ask`

Example:

```json
{
  "question": "What can I visit in Luxor?",
  "context_k": 5
}
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Tech Stack

**Python · FastAPI · Streamlit · LangChain · ChromaDB · Hugging Face · Gemini · Docker**

---

## Author

**Fatma Eissa**

AI / Machine Learning Engineer

[GitHub](https://github.com/FatmaEissa) · [LinkedIn](https://www.linkedin.com/in/fatmaeiissa/)





