"""
Ingestion router for document processing and vector store indexing.
"""
import time
import loguru
from fastapi import APIRouter, HTTPException
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    KeywordExtractor,
    SummaryExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import (TokenTextSplitter, SentenceSplitter)
from llama_index.vector_stores.duckdb import DuckDBVectorStore
from llama_index.readers.file import PyMuPDFReader

from app.schemas import IngestionRequest, IngestionResponse
from app.core import get_index, reset_models
from app.core.config import PERSIST_DIR, DB_PATH, DATA_DIR

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_documents(request: IngestionRequest):
    """
    Ingest documents from a directory and create vector store index.
    
    - **input_dir**: Directory containing documents to ingest
    - **chunk_size**: Token size for text splitting chunks
    - **chunk_overlap**: Token overlap between chunks
    - **extract_title**: Extract titles from documents
    - **extract_qa**: Extract questions answered from documents
    - **extract_keywords**: Extract keywords from documents
    - **extract_summary**: Extract summaries from documents
    """
    start_time = time.time()
    
    try:
        # Load documents from specified directory
        loguru.logger.info(f"Loading documents from {request.input_dir}")
        documents = SimpleDirectoryReader(
            input_dir=request.input_dir,
            file_extractor={"*.pdf": PyMuPDFReader()},
            recursive=True,
        ).load_data()
        
        documents_count = len(documents)
        loguru.logger.info(f"Loaded {documents_count} documents")
        
        # Create text splitter
        #text_splitter = TokenTextSplitter(
        #    separator=" ",
        #    chunk_size=request.chunk_size,
        #    chunk_overlap=request.chunk_overlap,
        #)
        text_splitter = SentenceSplitter(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        transformations = []
        # Build extractors based on request flags
        transformations.append(text_splitter)
        
        if request.extract_title:
            transformations.append(TitleExtractor(nodes=5))
        
        if request.extract_qa:
            transformations.append(QuestionsAnsweredExtractor(questions=3))
        
        if request.extract_keywords:
            transformations.append(KeywordExtractor(keywords=15))
        
        if request.extract_summary:
            transformations.append(SummaryExtractor(summaries=["prev", "self"], nodes=5, num_workers=5))
        
        # Create ingestion pipeline
        pipeline = IngestionPipeline(transformations=transformations)
        
        loguru.logger.info("Processing documents through pipeline")
        # Process documents to extract nodes with metadata
        nodes = pipeline.run(
            documents=documents,
            in_place=True,
            show_progress=True,
        )
        
        nodes_count = len(nodes)
        loguru.logger.info(f"Created {nodes_count} nodes from {documents_count} documents")
        
        # Create vector store and index
        loguru.logger.info("Creating vector store and index")
        vector_store = DuckDBVectorStore(DB_PATH, persist_dir=PERSIST_DIR)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex(nodes, storage_context=storage_context)
        
        # Reset global model instances to reload the new index
        reset_models()
        
        processing_time = time.time() - start_time
        
        loguru.logger.info("Ingestion completed successfully")
        
        return IngestionResponse(
            success=True,
            message="Documents ingested and indexed successfully",
            documents_processed=documents_count,
            nodes_created=nodes_count,
            processing_time_seconds=processing_time,
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        loguru.logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        )
