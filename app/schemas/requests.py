"""
Request body models for API endpoints.
"""
from typing import Optional
from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    """Request model for document ingestion endpoint."""
    input_dir: str = Field(
        default="./policies",
        description="Directory path containing documents to ingest"
    )
    chunk_size: int = Field(
        default=512,
        description="Token size for text splitting chunks",
        ge=100,
        le=2000
    )
    chunk_overlap: int = Field(
        default=128,
        description="Token overlap between chunks",
        ge=0,
        le=500
    )
    extract_title: bool = Field(
        default=True,
        description="Extract titles from documents"
    )
    extract_qa: bool = Field(
        default=True,
        description="Extract questions answered from documents"
    )
    extract_keywords: bool = Field(
        default=True,
        description="Extract keywords from documents"
    )
    extract_summary: bool = Field(
        default=True,
        description="Extract summaries from documents"
    )


class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    query: str = Field(
        description="Search query for the knowledge base"
    )
    similarity_top_k: int = Field(
        default=10,
        description="Number of top similar results to return",
        ge=1,
        le=50
    )
    use_sub_questions: bool = Field(
        default=False,
        description="Use SubQuestionQueryEngine for complex queries"
    )
