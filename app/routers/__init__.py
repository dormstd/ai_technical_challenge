"""API routers for the application."""
from .ingestion import router as ingestion_router
from .search import router as search_router

__all__ = ["ingestion_router", "search_router"]
