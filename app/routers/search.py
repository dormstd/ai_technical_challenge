"""
Search router for querying the vector store index.
"""
import time
import json
import loguru
from fastapi import APIRouter, HTTPException
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.core.question_gen.prompts import (
    DEFAULT_SUB_QUESTION_PROMPT_TMPL,
)

from app.schemas import SearchRequest, SearchResponse, SearchResult
from app.core import get_index

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search the vector store index for documents matching the query.
    
    - **query**: Search query string
    - **similarity_top_k**: Number of top similar results to return (1-50)
    - **use_sub_questions**: Use SubQuestionQueryEngine for complex query decomposition
    """
    start_time = time.time()
    
    try:
        loguru.logger.info(f"Processing search query: {request.query}")
        
        # Get the index
        index = get_index()
        
        if request.use_sub_questions:
            # Use SubQuestionQueryEngine for complex queries
            loguru.logger.info("Using SubQuestionQueryEngine for query decomposition")
            
            question_gen = LLMQuestionGenerator.from_defaults(
                prompt_template_str="""
                    Follow the example, but instead of giving a question, always prefix the question
                    with: 'Answer in markdown. By first identifying and quoting the most relevant sources, '.
                    """
                + DEFAULT_SUB_QUESTION_PROMPT_TMPL,
            )
            
            engine = index.as_query_engine(similarity_top_k=request.similarity_top_k)
            
            query_engine = SubQuestionQueryEngine.from_defaults(
                query_engine_tools=[
                    QueryEngineTool(
                        query_engine=engine,
                        metadata=ToolMetadata(
                            name="airline_policy_documents",
                            description="Airline policy documents for answering questions about airline policies and related topics.",
                        ),
                    )
                ],
                question_gen=question_gen,
                use_async=False,
            )
        else:
            # Use simple query engine
            loguru.logger.info("Using standard query engine")
            query_engine = index.as_query_engine(similarity_top_k=request.similarity_top_k)
        
        # Execute query
        response = query_engine.query(request.query)
        
        # Extract answer
        answer = str(response)
        
        # Check if response is empty or contains the "Empty Response" placeholder
        # Small guardrails
        if not answer or answer.strip() == "" or answer.strip().lower() == "empty response":
            loguru.logger.warning(f"Empty response for query: {request.query}")
            answer = "I couldn't find relevant information to answer your question. Please contact customer support for further assistance."
        
        # Extract source nodes if available
        results = []
        if hasattr(response, "source_nodes"):
            for node in response.source_nodes:
                if not node.text.lower().strip().startswith("sub question:"):
                    # Extract metadata from node metadata if available
                    if hasattr(node, "metadata"):
                        file_name = node.metadata.get("file_name")
                        summary = node.metadata.get("document_title")
                    
                    result = SearchResult(
                        file_name=file_name if file_name else "Unknown",
                        summary=summary if summary else "No summary available",
                        score=node.score if hasattr(node, "score") else None,
                    )
                    results.append(result)
        
        processing_time = time.time() - start_time
        
        loguru.logger.info(f"Search completed in {processing_time:.2f}s")
        
        return SearchResponse(
            query=request.query,
            answer=answer,
            results=results,
            processing_time_seconds=processing_time,
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        loguru.logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}",
        )
