# dev-onboarding-ai-hackathon

# MCP RAG Server

A FastAPI-based Retrieval-Augmented Generation (RAG) server that uses ChromaDB as a vector store.

## Features

- FastAPI server with async endpoints
- Local ChromaDB vector store for document embeddings
- Sentence-transformers for generating embeddings
- Document ingestion with chunking and metadata extraction
- Support for PDF and TXT files
- Topic-based document organization

## API Endpoints

1. **GET /list_available_rag_topics**
   - Lists all available topics (slack, docs, codebase)

2. **POST /get_rag_context_by_topic**
   - Get relevant context from a specific topic based on a query

3. **POST /search_doc_for_rag_context**
   - Search across all topics and return the best match

4. **POST /ingest_document**
   - Ingest documents into a topic collection

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

```bash
cd mcp_rag_server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Interactive API Documentation

FastAPI generates interactive API documentation. After starting the server, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Examples

### List Available Topics

```bash
curl -X GET http://localhost:8000/list_available_rag_topics
```

### Get Context by Topic

```bash
curl -X POST http://localhost:8000/get_rag_context_by_topic \
  -H "Content-Type: application/json" \
  -d '{"topic_id": "docs", "query": "How to configure payroll system?"}'
```

### Search Across All Topics

```bash
curl -X POST http://localhost:8000/search_doc_for_rag_context \
  -H "Content-Type: application/json" \
  -d '{"query": "How does the payroll LOP calculation work?"}'
```

### Ingest Documents

```bash
curl -X POST http://localhost:8000/ingest_document \
  -F "topic=docs" \
  -F "files=@/path/to/document.pdf" \
  -F "files=@/path/to/another.txt"
``` 
