# 🤖 GenAI RAG Chatbot - Airline Policies Assistant

A production-ready Retrieval-Augmented Generation (RAG) chatbot that enables natural language queries over airline policy documents. Built with modern Python technologies for blazing-fast performance and seamless deployment.

## 📋 Table of Contents

- [Overview](#overview)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Architecture & Design Choices](#architecture--design-choices)
- [Challenges & Solutions](#challenges--solutions)
- [API Documentation](#api-documentation)

---

## Overview

This application provides a dual-interface system for interacting with airline policy data:

- **FastAPI Backend**: RESTful API endpoints for document ingestion and semantic search
- **Gradio Frontend**: User-friendly web interface for interactive querying

The system leverages advanced RAG techniques including document chunking, semantic embeddings, vector storage, and intelligent query decomposition to provide accurate, context-aware answers about airline policies.

### Key Features

✨ **Intelligent Query Decomposition** - Complex questions are automatically broken down into sub-questions for better accuracy

🚀 **Lightning-Fast Search** - DuckDB vector store with OpenAI embeddings for high-performance semantic search

📄 **Rich Document Processing** - Automatic extraction of titles, summaries, keywords, and Q&A pairs from documents

🎨 **Dual Interfaces** - Both API and web UI for flexible integration and user interaction

🔄 **Async-First Design** - Built on async/await patterns for responsive, scalable performance

---

## Setup & Installation

### Prerequisites

- **Python 3.13+** (Project requires Python 3.13)
- **uv** - Ultra-fast Python package manager (required)
- **Azure OpenAI API credentials** - For LLM and embeddings
- **Git** - For version control

### 1. Install uv

`uv` is a Rust-based Python package manager that's 10-100x faster than pip. Install it globally:

```bash
# On macOS with Homebrew
brew install uv

# On other systems, visit: https://github.com/astral-sh/uv
# Or use: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the Repository

```bash
git clone https://github.com/dormstd/ai_technical_challenge.git
cd ai_technical_challenge
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root with your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration
OPENAI_API_BASE=https://your-resource.openai.azure.com/
TOKEN_ID=your-api-key-here
MODEL=gpt-4-1mini  # Azure deployment name
EMBEDDING=text-embedding-3-small  # Azure deployment name

# Optional: Configure paths
PERSIST_DIR=./persist/
DB_PATH=pg.duckdb
DATA_DIR=./policies
```

### 4. Install Dependencies

Using `uv`, install all project dependencies:

```bash
# Create virtual environment and install dependencies
uv sync

# This command:
# - Creates a .venv directory with isolated Python 3.13 environment
# - Installs all dependencies from pyproject.toml
# - Creates a uv.lock file for reproducible builds
```

### 5. Prepare Your Documents

Place airline policy documents in the `./policies` directory:

```bash
policies/
├── AmericanAirlines/
│   ├── Checked bag policy.md
│   ├── Pet Policy.md
│   └── ...
├── Delta/
│   ├── Baggage & Travel Fees.md
│   └── ...
└── United/
    └── ...
```

Supported formats: **PDF**, **Markdown**, **Text**

---

## Running the Application

The application consists of two components that can run independently or together:

### Option 1: Run Only the Backend API

```bash
uv run fastapi dev
```

The FastAPI server will start at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Option 2: Run Only the Frontend UI

```bash
# In a separate terminal, ensure backend is running first
uv run frontend.py
```

The Gradio interface will start at `http://localhost:7860`

### Option 3: Run Both (Recommended for Development)

**Terminal 1 - Start Backend:**
```bash
uv run fastapi dev
```

**Terminal 2 - Start Frontend:**
```bash
uv run frontend.py
```

Then open http://localhost:7860 in your browser.

### Initial Setup: Ingest Documents

Before querying, you need to ingest your policy documents. Use the API:

```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "input_dir": "./policies",
    "chunk_size": 512,
    "chunk_overlap": 128,
    "extract_title": true,
    "extract_qa": true,
    "extract_keywords": true,
    "extract_summary": true
  }'
```

Or use the Gradio interface which provides an ingestion workflow.

---

## Architecture & Design Choices

### 🏗️ Technology Stack

| Component | Technology | Why Chosen |
|-----------|-----------|-----------|
| **Package Manager** | `uv` | 10-100x faster than pip; optimized Rust implementation for dependency resolution |
| **Backend Framework** | FastAPI | Async-first design, automatic OpenAPI docs, excellent for AI applications |
| **Frontend** | Gradio | Minimal code to build ML demos; reactive componenáts; shareable links |
| **RAG Framework** | LlamaIndex | Purpose-built for LLM data indexing; excellent query engines; flexible integrations |
| **Vector Store** | DuckDB | Lightweight, fast, no server overhead; perfect for dev/testing at scale |
| **Embeddings** | OpenAI API | State-of-the-art semantic understanding; Azure integration |
| **LLM** | OpenAI API (Azure) | Best-in-class reasoning; supports complex query decomposition |

### Rationale
The main idea behind the architecture is to decouple the modules so that they can be replaced.
The backend has 2 endpoints that, for now, are together in the same micro.
In a production environment those 2 endpoints and the logics beneath them should be separate.
For testing purposes and because it is easier, I've decided to put them together so that I can ingest data into DuckDB easier.

Moreover, the frontend is also decoupled into another process that is connected to the api via the search endpoint. That way the frontend can be modified without impacting the rest. This has drawbacks, for example implementing streaming responses becomes more difficult but I think the pros outweight the cons for this challenge.

Using DuckDB was a personal choice because I wanted to try it for some time and I din't find the use case. I think it makes sense for dev/test environments and can even be used for production environments by "sharing" the DB file in a read only way for the search endpoints and it can be modified via the ingestion (especially thinking in a k8s deployment for a production environment)

UV was chosen because I think is the best tool for that, poetry was a step forward but UV is on another level entirely.
And llama-index because I think it is more mature in terms of RAG than the other frameworks.
For example, the subquestion query engine used in this example (because I think that kind of questions that this chatbot will get will benefit from this subquestion generation).

## Pending work
- Make use of the keywords extracted when running the queries.
- Industrialize the deployment of the solution (Docker, K8s, etc)
- Add metrics and monitoring