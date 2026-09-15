FROM python:3.11-slim

WORKDIR /app

# System deps needed by torch/sentence-transformers/chromadb at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag_pipeline.py main.py ./
# The persisted ChromaDB and (optionally) the raw source docs.
# For large collections, prefer mounting these as volumes at `docker run`
# time instead of baking them into the image — see README.
COPY chroma_db_main/ ./chroma_db_main/
COPY data/ ./data/

EXPOSE 8000

# No API keys are baked into the image — provide GEMINI_API_KEY at
# `docker run` time (e.g. `--env-file .env`).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
