"""
rag_pipeline.py

Egypt Tourism RAG — inference pipeline.

This module is a direct extraction of the INFERENCE path from the original
Kaggle notebook (`Tourism_RAG_Assistant.ipynb`). No retrieval/generation
logic has been changed, simplified, or replaced.

What was intentionally left out (because it is not part of answering a
question at request time, it was part of the notebook's offline
build/evaluation workflow):
  - Wikipedia scraping / corpus building (Sections 2-4 of the notebook)
  - Chunking (Section 4) — the persisted ChromaDB already contains the
    chunked, embedded corpus, so chunking does not run again here.
  - Vectorstore *building* (`build_or_load_vectorstore`'s rebuild branch,
    Section 6) — this file only LOADS the existing persisted collection.
  - Retrieval/generation evaluation (Sections 11-16 and the Appendix).

Everything that IS part of the notebook's live `ask_rag()` call path is
preserved as-is below:
  - Embedding model config (Section 5)
  - MMR retriever config (Section 7)
  - Reranker + `retrieve_and_rerank` (Sections 8-9)
  - Prompt template + `ask_rag` generation logic (Section 10)

TODO (could not be determined from the notebook / needs your confirmation):
  - GEMINI_MODEL was set to "gemini-3.5-flash-lite" in the notebook
    (Section 10, Cell 27). This value is preserved exactly as written.
    Please double check this is the model name you intend to use — it is
    reproduced verbatim from your notebook, not verified against a live
    Gemini model list.
  - The notebook read the API key via Kaggle's `UserSecretsClient`
    (`kaggle_secrets`), which only works inside Kaggle. That has been
    swapped for reading `GEMINI_API_KEY` from the environment / `.env`
    file, since this is now a local/deployed project. This is the one
    deliberate adaptation in this file — it changes *where the key comes
    from*, not any RAG logic.
"""

# import os

# import torch
# from dotenv import load_dotenv
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from sentence_transformers import CrossEncoder
# from google import genai

# load_dotenv()

# # ---------------------------------------------------------------------------
# # Configuration (values preserved exactly from the notebook)
# # ---------------------------------------------------------------------------

# # Section 6: Vector Database
# # Notebook: PERSIST_DIR_BASE = "./chroma_db"; persist_dir = f"{PERSIST_DIR_BASE}_main"
# # Overridable via env var in case you deploy with a different mount path.
# CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db_main")
# COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "egypt_tourism_v2")
# # Section 5: Embedding Model
# EMBEDDING_MODEL_NAME = "BAAI/bge-m3"


# # Section 7: Baseline Retriever (MMR)
# MMR_K = 10
# MMR_FETCH_K = 25
# MMR_LAMBDA_MULT = 0.6


# # Section 8: Reranker
# RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"


# # Section 10: RAG Generation
# GEMINI_MODEL = "gemini-3.5-flash-lite"

# # Load API key from .env
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError(
#         "GEMINI_API_KEY is not set. Please add it to your .env file."
#     )

# # ---------------------------------------------------------------------------
# # Section 5: Embedding Model
# # ---------------------------------------------------------------------------

# _device = "cuda" if torch.cuda.is_available() else "cpu"

# embedding_model = HuggingFaceEmbeddings(
#     model_name=EMBEDDING_MODEL_NAME,
#     model_kwargs={"device": _device},
#     encode_kwargs={"normalize_embeddings": True},
# )


# # ---------------------------------------------------------------------------
# # Section 6: Vector Database — LOAD existing persisted collection only.
# # The notebook's `build_or_load_vectorstore` would rebuild if the chunk
# # count didn't match; here we only ever load, since this project ships
# # with the already-built `chroma_db_main/` directory.
# # ---------------------------------------------------------------------------

# if not os.path.isdir(CHROMA_PERSIST_DIR) or not os.listdir(CHROMA_PERSIST_DIR):
#     raise FileNotFoundError(
#         f"Expected a persisted Chroma collection at '{CHROMA_PERSIST_DIR}' "
#         f"(collection_name='{COLLECTION_NAME}'), but the directory is missing "
#         f"or empty. Copy your existing chroma_db_main/ into this project."
#     )

# vectorstore = Chroma(
#     collection_name=COLLECTION_NAME,
#     embedding_function=embedding_model,
#     persist_directory=CHROMA_PERSIST_DIR,
# )


# # ---------------------------------------------------------------------------
# # Section 7: Baseline Retriever (MMR) — unchanged
# # ---------------------------------------------------------------------------

# def get_mmr_retriever(vectorstore, k=MMR_K, fetch_k=MMR_FETCH_K, lambda_mult=MMR_LAMBDA_MULT):
#     return vectorstore.as_retriever(
#         search_type="mmr",
#         search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult},
#     )


# retrival_mmr = get_mmr_retriever(vectorstore)


# # ---------------------------------------------------------------------------
# # Section 8: Reranker — unchanged
# # ---------------------------------------------------------------------------

# reranker = CrossEncoder(RERANKER_MODEL_NAME)


# # ---------------------------------------------------------------------------
# # Section 9: Improved Retriever (MMR + Reranker) — unchanged
# # ---------------------------------------------------------------------------

# def retrieve_and_rerank(query, retriever, reranker, top_n=10):
#     candidates = retriever.invoke(query)
#     if not candidates:
#         return []
#     pairs = [[query, doc.page_content] for doc in candidates]
#     scores = reranker.predict(pairs)
#     reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
#     return reranked[:top_n]


# # ---------------------------------------------------------------------------
# # Section 10: RAG Generation — unchanged
# # ---------------------------------------------------------------------------

# client = genai.Client(api_key=GEMINI_API_KEY)


# def build_prompt(query, context):
#     return f"""You are an Egypt tourism assistant.

# Answer the user's question using ONLY the provided context.

# Rules:
# - Do not use outside knowledge.
# - Do not invent information.
# - If a retrieved passage doesn't actually address the question, ignore it - don't let it leak into the answer.
# - If the answer is not contained in the context, say exactly:
#   "I don't have enough information in the provided sources."
# - Keep the answer concise and specific.

# Context:
# {context}

# Question:
# {query}
# """


# def ask_rag(query, context_k=5, verbose=True):
#     """Original notebook function (Section 10, Cell 28), unchanged."""
#     reranked = retrieve_and_rerank(query, retrival_mmr, reranker, top_n=max(context_k, 10))
#     results = [doc for doc, score in reranked[:context_k]]
#     context = "\n\n".join(doc.page_content for doc in results)
#     prompt = build_prompt(query, context)

#     try:
#         response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
#         answer = response.text
#     except Exception as e:
#         print("LLM Error:", e)
#         return None

#     if verbose:
#         print("ANSWER:")
#         print(answer)
#         print("\nSOURCES:")
#         seen = set()
#         for doc in results:
#             url = doc.metadata.get("source_url")
#             if url not in seen:
#                 print(f"- {doc.metadata.get('title')} ({doc.metadata.get('category')}) - {url}")
#                 seen.add(url)

#     return {"question": query, "context": context, "answer": answer, "sources": results}


# # ---------------------------------------------------------------------------
# # Clean callable wrapper for the app layer (FastAPI / Streamlit).
# # Thin adapter over `ask_rag` — no RAG logic lives here, it only reshapes
# # the notebook's Document-object sources into JSON-serializable dicts.
# # ---------------------------------------------------------------------------

# def answer_question(question: str, context_k: int = 5) -> dict:
#     """
#     Run the existing RAG pipeline (MMR retrieval -> reranking -> Gemini
#     generation) for a single question and return a JSON-serializable result.

#     Returns:
#         {
#             "answer": str,
#             "sources": [
#                 {
#                     "title": str,
#                     "source_url": str,
#                     "category": str,
#                     "chunk_id": str,
#                     "chunk_index": int,
#                 },
#                 ...
#             ]
#         }
#     """
#     result = ask_rag(question, context_k=context_k, verbose=False)

#     if result is None:
#         return {
#             "answer": "Sorry, I couldn't generate an answer due to an internal error.",
#             "sources": [],
#         }

#     sources = []
#     seen_urls = set()
#     for doc in result["sources"]:
#         url = doc.metadata.get("source_url")
#         if url in seen_urls:
#             continue
#         seen_urls.add(url)
#         sources.append(
#             {
#                 "title": doc.metadata.get("title"),
#                 "source_url": url,
#                 "category": doc.metadata.get("category"),
#                 "chunk_id": doc.metadata.get("chunk_id"),
#                 "chunk_index": doc.metadata.get("chunk_index"),
#             }
#         )

#     return {"answer": result["answer"], "sources": sources}


# if __name__ == "__main__":
#     # Quick manual smoke test: python rag_pipeline.py
#     demo = answer_question("Tell me about the Pyramids of Giza.")
#     print(demo["answer"])
#     print(demo["sources"])

















import os

import torch
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from google import genai

load_dotenv()


# ============================================================================
# Configuration
# ============================================================================

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db_main")
COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "egypt_tourism_v2"
)

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"


# MMR Retriever
MMR_K = 10
MMR_FETCH_K = 25
MMR_LAMBDA_MULT = 0.6


# Reranker
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"


# Gemini
GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )


# ============================================================================
# Embedding Model
# ============================================================================

_device = "cuda" if torch.cuda.is_available() else "cpu"

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": _device},
    encode_kwargs={"normalize_embeddings": True},
)


# ============================================================================
# Vector Database
# ============================================================================

if (
    not os.path.isdir(CHROMA_PERSIST_DIR)
    or not os.listdir(CHROMA_PERSIST_DIR)
):
    raise FileNotFoundError(
        f"Expected a persisted Chroma collection at "
        f"'{CHROMA_PERSIST_DIR}' "
        f"(collection_name='{COLLECTION_NAME}'), "
        f"but the directory is missing or empty. "
        f"Copy your existing chroma_db_main/ into this project."
    )


vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_model,
    persist_directory=CHROMA_PERSIST_DIR,
)


# ============================================================================
# MMR Retriever
# ============================================================================

def get_mmr_retriever(
    vectorstore,
    k=MMR_K,
    fetch_k=MMR_FETCH_K,
    lambda_mult=MMR_LAMBDA_MULT
):
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult
        },
    )


retrival_mmr = get_mmr_retriever(vectorstore)


# ============================================================================
# Reranker
# ============================================================================

reranker = CrossEncoder(RERANKER_MODEL_NAME)


# ============================================================================
# Gemini Client
# ============================================================================

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================================
# Query Rewriting
# ============================================================================
#
# The purpose of this step is NOT to answer the question.
#
# It converts a vague / conversational user question into a clearer
# search query that is more suitable for retrieval.
#
# Example:
#
#   "What can I see there?"
#
# becomes something like:
#
#   "tourist attractions and places to visit in Luxor Egypt"
#
# If rewriting fails, the original question is returned.
# ============================================================================

def rewrite_query(query: str) -> str:

    rewrite_prompt = f"""
You are a query rewriting component for an Egypt tourism RAG system.

Your task is to rewrite the user's question into ONE clear,
specific search query that will work well for retrieving
relevant tourism documents.

Rules:
- Do NOT answer the question.
- Do NOT add information that is not implied by the question.
- Keep the original meaning.
- Make vague references more explicit when possible.
- Include the location or tourism topic when it is clearly present.
- Keep the rewritten query concise.
- Return ONLY the rewritten query.
- If the original question is already clear, simply improve its wording slightly.

User question:
{query}
"""

    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=rewrite_prompt
        )

        rewritten = response.text.strip()

        if rewritten:
            return rewritten

    except Exception as e:
        print("Query rewriting error:", e)

    # Safe fallback
    return query


# ============================================================================
# Retrieval + Reranking
# ============================================================================

def retrieve_and_rerank(
    query,
    retriever,
    reranker,
    top_n=10
):

    candidates = retriever.invoke(query)

    if not candidates:
        return []

    pairs = [
        [query, doc.page_content]
        for doc in candidates
    ]

    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return reranked[:top_n]


# ============================================================================
# RAG Prompt
# ============================================================================

def build_prompt(query, context):

    return f"""
You are an Egypt tourism assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If a retrieved passage doesn't actually address the question,
  ignore it.
- If the answer is not contained in the context, say exactly:

"I don't have enough information in the provided sources."

- Keep the answer concise and specific.

Context:
{context}

Question:
{query}
"""


# ============================================================================
# Main RAG Function
# ============================================================================

def ask_rag(
    query,
    context_k=5,
    verbose=True
):
    """
    Full RAG pipeline:

    User Question
          ↓
    Query Rewriting
          ↓
    MMR Retrieval
          ↓
    Reranking
          ↓
    Top Context
          ↓
    Gemini Generation
    """

    # ------------------------------------------------------------------------
    # 1. Rewrite the user's query for better retrieval
    # ------------------------------------------------------------------------

    rewritten_query = rewrite_query(query)

    if verbose:
        print("ORIGINAL QUERY:")
        print(query)

        print("\nREWRITTEN QUERY:")
        print(rewritten_query)


    # ------------------------------------------------------------------------
    # 2. Retrieve + rerank using the rewritten query
    # ------------------------------------------------------------------------

    reranked = retrieve_and_rerank(
        rewritten_query,
        retrival_mmr,
        reranker,
        top_n=max(context_k, 10)
    )


    # ------------------------------------------------------------------------
    # 3. Select final context
    # ------------------------------------------------------------------------

    results = [
        doc
        for doc, score in reranked[:context_k]
    ]


    if not results:

        return {
            "question": query,
            "rewritten_query": rewritten_query,
            "context": "",
            "answer": "I don't have enough information in the provided sources.",
            "sources": []
        }


    context = "\n\n".join(
        doc.page_content
        for doc in results
    )


    # ------------------------------------------------------------------------
    # 4. Generate answer
    # ------------------------------------------------------------------------

    prompt = build_prompt(
        query,
        context
    )


    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        answer = response.text

    except Exception as e:

        print("LLM Error:", e)

        return None


    # ------------------------------------------------------------------------
    # 5. Display result
    # ------------------------------------------------------------------------

    if verbose:

        print("\nANSWER:")
        print(answer)

        print("\nSOURCES:")

        seen = set()

        for doc in results:

            url = doc.metadata.get("source_url")

            if url not in seen:

                print(
                    f"- {doc.metadata.get('title')} "
                    f"({doc.metadata.get('category')}) - "
                    f"{url}"
                )

                seen.add(url)


    return {
        "question": query,
        "rewritten_query": rewritten_query,
        "context": context,
        "answer": answer,
        "sources": results
    }


# ============================================================================
# FastAPI / Streamlit Wrapper
# ============================================================================

def answer_question(
    question: str,
    context_k: int = 5
) -> dict:

    result = ask_rag(
        question,
        context_k=context_k,
        verbose=False
    )


    if result is None:

        return {
            "answer": (
                "Sorry, I couldn't generate an answer "
                "due to an internal error."
            ),
            "sources": []
        }


    sources = []

    seen_urls = set()


    for doc in result["sources"]:

        url = doc.metadata.get("source_url")

        if url in seen_urls:
            continue

        seen_urls.add(url)


        sources.append(
            {
                "title": doc.metadata.get("title"),
                "source_url": url,
                "category": doc.metadata.get("category"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "chunk_index": doc.metadata.get("chunk_index"),
            }
        )


    return {
        "answer": result["answer"],
        "sources": sources
    }


# ============================================================================
# Manual Test
# ============================================================================

if __name__ == "__main__":

    demo = answer_question(
        "What can I visit in Luxor?"
    )

    print("\nANSWER:")
    print(demo["answer"])

    print("\nSOURCES:")
    print(demo["sources"])

