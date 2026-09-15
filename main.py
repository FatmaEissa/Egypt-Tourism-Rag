"""
main.py

FastAPI application exposing the Egypt Tourism RAG assistant.

This file contains NO retrieval/generation logic itself — it only
validates requests/responses and delegates to `rag_pipeline.answer_question`.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from rag_pipeline import answer_question

app = FastAPI(
    title="Egypt Tourism RAG Assistant",
    description="Ask questions about Egypt tourism (Arabic & English supported).",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question in English or Arabic.")
    context_k: int | None = Field(
        default=5, ge=1, le=10, description="Number of reranked chunks to use as context."
    )

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question must not be empty or whitespace only.")
        return v.strip()


class Source(BaseModel):
    title: str | None = None
    source_url: str | None = None
    category: str | None = None
    chunk_id: str | None = None
    chunk_index: int | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        result = answer_question(request.question, context_k=request.context_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AskResponse(answer=result["answer"], sources=result["sources"])



