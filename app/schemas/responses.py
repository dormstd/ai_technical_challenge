"""
Response body models for API endpoints.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class NodeMetadata(BaseModel):
    """Metadata for an ingested node."""
    title: Optional[str] = Field(None, description="Extracted title")
    keywords: Optional[List[str]] = Field(None, description="Extracted keywords")
    summary: Optional[str] = Field(None, description="Summary of the node")


class IngestionResponse(BaseModel):
    """Response model for ingestion endpoint."""
    success: bool = Field(description="Whether ingestion was successful")
    message: str = Field(description="Status message")
    documents_processed: int = Field(description="Number of documents processed")
    nodes_created: int = Field(description="Number of nodes created")
    processing_time_seconds: float = Field(description="Total processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class SearchResult(BaseModel):
    """A single search result with file path and score."""
    file_name: Optional[str] = Field(None, description="File name of the document")
    summary: Optional[str] = Field(None, description="Summary of the document")
    score: Optional[float] = Field(None, description="Similarity score")


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    query: str = Field(description="The original search query")
    answer: str = Field(description="Generated answer from LLM")
    results: List[SearchResult] = Field(description="List of search results")
    processing_time_seconds: float = Field(description="Total processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
