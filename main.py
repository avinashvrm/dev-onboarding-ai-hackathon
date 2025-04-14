from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import uvicorn

from rag.embedding import get_embeddings
from rag.chunking import chunk_document, chunk_code
from rag.qdrant_client import QdrantManager
from rag.llm_client import LLMClient
from rag.query_pipeline import RAGPipeline

app = FastAPI(title="MCP RAG Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
qdrant_manager = QdrantManager()
llm_client = LLMClient()
rag_pipeline = RAGPipeline(qdrant_manager, llm_client)

class QueryRequest(BaseModel):
    query: str
    context_chunks: Optional[List[str]] = None

class TopicQueryRequest(BaseModel):
    topic_id: str
    query: str

@app.post("/ingest_document")
async def ingest_document(
    files: List[UploadFile] = File(...),
    topic: str = Form(...)
):
    results = []
    for file in files:
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        # Choose chunking strategy based on file type
        if file_extension in ['pdf', 'txt', 'md']:
            chunks = chunk_document(content, file_extension)
        elif file_extension in ['py', 'js', 'php', 'ts']:
            chunks = chunk_code(content, file_extension)
        else:
            return {"error": f"Unsupported file type: {file_extension}"}
        
        # Generate embeddings and store in Qdrant
        embeddings = get_embeddings(chunks)
        qdrant_manager.store_vectors(
            embeddings=embeddings,
            texts=chunks,
            metadata=[{
                "filename": file.filename,
                "topic": topic,
                "chunk_id": i
            } for i in range(len(chunks))]
        )
        results.append({"filename": file.filename, "chunks": len(chunks)})
    
    return {"status": "success", "results": results}

@app.get("/list_available_rag_topics")
async def list_topics():
    topics = qdrant_manager.get_collections()
    return {"topics": topics}

@app.post("/get_rag_context_by_topic")
async def get_context_by_topic(request: TopicQueryRequest):
    query_embedding = get_embeddings([request.query])[0]
    results = qdrant_manager.search(
        query_vector=query_embedding,
        collection_name=request.topic_id,
        limit=5
    )
    return {"results": results}

@app.post("/search_doc_for_rag_context")
async def search_all_topics(request: QueryRequest):
    query_embedding = get_embeddings([request.query])[0]
    results = qdrant_manager.search_all_collections(
        query_vector=query_embedding,
        limit=5
    )
    return {"results": results}

@app.post("/query_llm")
async def query_llm(request: QueryRequest):
    if not request.context_chunks:
        # If no context provided, use RAG pipeline to get context
        context = rag_pipeline.get_context(request.query)
    else:
        context = request.context_chunks
    
    response = llm_client.generate_response(request.query, context)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 