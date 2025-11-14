"""
Configuration module for centralized settings and credentials.
"""
import base64
import os
from dotenv import load_dotenv
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Model and Embedding Configuration
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
EMBEDDING = os.getenv("EMBEDDING", "text-embedding-3-small")

TOKEN_ID = os.getenv("TOKEN_ID", "")

# Azure OpenAI Configuration
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "")

# Paths
PERSIST_DIR = os.getenv("PERSIST_DIR", "./persist/")
DB_PATH = os.getenv("DB_PATH", "pg.duckdb")
DATA_DIR = os.getenv("DATA_DIR", "./policies")


def initialize_settings():
    """
    Initialize LlamaIndex global settings with Azure OpenAI and Ollama embeddings.
    This should be called once at application startup.
    """
    Settings.llm = OpenAI(
        api_key=TOKEN_ID,
        api_base=OPENAI_API_BASE,
        model=MODEL,
    )

    Settings.embed_model = OpenAIEmbedding(
        api_base=OPENAI_API_BASE,
        model=EMBEDDING,
        api_key=TOKEN_ID,
        timeout=300.0,
    )
