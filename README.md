# MCP RAG Server

A FastAPI-based Retrieval-Augmented Generation (RAG) system that uses Qdrant as a local vector store and OpenAI (or other LLM providers) for generating responses.

## Features

- Document ingestion with automatic chunking
- Support for multiple file types (PDF, TXT, MD, PY, JS, PHP, TS)
- Topic-based document organization
- Semantic search using sentence transformers
- Configurable LLM integration
- FastAPI endpoints for easy integration

## Prerequisites

- Python 3.8+
- Docker (for running Qdrant)
- OpenAI API key (or other LLM provider)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp_rag_server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

5. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the API keys and configuration

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`

### API Endpoints

1. `POST /ingest_document`
   - Upload documents with topic
   - Supports multiple file types
   - Example:
   ```bash
   curl -X POST "http://localhost:8000/ingest_document" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "files=@document.pdf" \
        -F "topic=docs"
   ```

2. `GET /list_available_rag_topics`
   - List all available topics
   - Example:
   ```bash
   curl "http://localhost:8000/list_available_rag_topics"
   ```

3. `POST /get_rag_context_by_topic`
   - Search within a specific topic
   - Example:
   ```bash
   curl -X POST "http://localhost:8000/get_rag_context_by_topic" \
        -H "Content-Type: application/json" \
        -d '{"topic_id": "docs", "query": "How to configure the system?"}'
   ```

4. `POST /search_doc_for_rag_context`
   - Search across all topics
   - Example:
   ```bash
   curl -X POST "http://localhost:8000/search_doc_for_rag_context" \
        -H "Content-Type: application/json" \
        -d '{"query": "How to configure the system?"}'
   ```

5. `POST /query_llm`
   - Generate response using LLM
   - Example:
   ```bash
   curl -X POST "http://localhost:8000/query_llm" \
        -H "Content-Type: application/json" \
        -d '{"query": "How to configure the system?", "context_chunks": ["..."]}'
   ```

## Configuration

- Update `.env` file with your API keys and configuration
- Modify `rag/llm_client.py` to use a different LLM provider
- Adjust chunking parameters in `rag/chunking.py`

## License

MIT License 