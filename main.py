from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os

from routes.rag_routes import router as rag_router

# Configure logging
logger.add("app.log", rotation="500 MB")

app = FastAPI(
    title="MCP RAG Server",
    description="A RAG system using ChromaDB and FastAPI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag_router, prefix="/api/v1", tags=["RAG"])

# Create necessary directories
os.makedirs("db", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to MCP RAG Server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 