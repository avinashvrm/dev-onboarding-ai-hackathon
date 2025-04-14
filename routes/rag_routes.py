from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import os
from loguru import logger

from models.schemas import (
    TopicListResponse,
    RAGQueryRequest,
    RAGSearchRequest,
    RAGResponse,
    IngestResponse
)
from services.vector_store import VectorStore
from utils.document_processor import process_document

router = APIRouter()
vector_store = VectorStore()

@router.get("/list_available_rag_topics", response_model=TopicListResponse)
async def list_topics():
    """List all available RAG topics."""
    try:
        topics = vector_store.get_available_topics()
        return TopicListResponse(topics=topics)
    except Exception as e:
        logger.error(f"Error listing topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_rag_context_by_topic", response_model=RAGResponse)
async def get_context_by_topic(request: RAGQueryRequest):
    """Get context from a specific topic."""
    try:
        context = vector_store.search_topic(request.topic_id, request.query)
        return RAGResponse(context=context)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_doc_for_rag_context", response_model=RAGResponse)
async def search_all_topics(request: RAGSearchRequest):
    """Search across all topics for context."""
    try:
        context = vector_store.search_all_topics(request.query)
        return RAGResponse(context=context)
    except Exception as e:
        logger.error(f"Error searching all topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest_document", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    topic: str = Form(...)
):
    """Ingest a document into the specified topic."""
    try:
        if topic not in vector_store.get_available_topics():
            raise HTTPException(status_code=400, detail=f"Invalid topic: {topic}")

        # Save the uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Process the document
            chunks = process_document(temp_path)
            
            # Add to vector store
            vector_store.add_documents(topic, chunks)
            
            return IngestResponse(
                status="success",
                message=f"Document ingested into '{topic}' topic"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 