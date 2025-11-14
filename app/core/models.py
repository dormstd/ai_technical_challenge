"""
Shared model initialization module.
Provides singleton-like access to vector store and index.
"""
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.duckdb import DuckDBVectorStore
from .config import PERSIST_DIR, DB_PATH

# Global instances (lazy loaded)
_vector_store = None
_index = None


def get_vector_store() -> DuckDBVectorStore:
    """
    Get or create the vector store instance.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = DuckDBVectorStore.from_local(f"{PERSIST_DIR}{DB_PATH}")
    return _vector_store


def get_index() -> VectorStoreIndex:
    """
    Get or create the vector store index instance.
    """
    global _index
    if _index is None:
        vector_store = get_vector_store()
        _index = VectorStoreIndex.from_vector_store(vector_store)
    return _index


def reset_models():
    """
    Reset global model instances. Useful for testing.
    """
    global _vector_store, _index
    _vector_store = None
    _index = None
