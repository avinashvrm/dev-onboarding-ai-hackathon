import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
from typing import List, Optional
from loguru import logger

class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.Client(Settings(
            persist_directory="db",
            is_persistent=True
        ))
        self.topics = ["slack", "docs", "codebase"]
        self._initialize_collections()

    def _initialize_collections(self):
        """Initialize collections for each topic if they don't exist."""
        for topic in self.topics:
            try:
                self.client.get_collection(topic)
            except ValueError:
                self.client.create_collection(
                    name=topic,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Created new collection for topic: {topic}")

    def get_available_topics(self) -> List[str]:
        """Get list of available topics."""
        return self.topics

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.embedding_model.encode(texts).tolist()

    def add_documents(self, topic: str, documents: List[str], ids: Optional[List[str]] = None) -> None:
        """Add documents to a specific topic collection."""
        if topic not in self.topics:
            raise ValueError(f"Invalid topic: {topic}")

        collection = self.client.get_collection(topic)
        embeddings = self._get_embeddings(documents)
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids
        )
        logger.info(f"Added {len(documents)} documents to topic: {topic}")

    def search_topic(self, topic: str, query: str, n_results: int = 1) -> str:
        """Search within a specific topic."""
        if topic not in self.topics:
            raise ValueError(f"Invalid topic: {topic}")

        collection = self.client.get_collection(topic)
        query_embedding = self._get_embeddings([query])[0]
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        if not results['documents']:
            return "No relevant context found."
        
        return results['documents'][0][0]

    def search_all_topics(self, query: str, n_results: int = 1) -> str:
        """Search across all topics."""
        best_result = ""
        best_score = -1

        for topic in self.topics:
            try:
                collection = self.client.get_collection(topic)
                query_embedding = self._get_embeddings([query])[0]
                
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                
                if results['documents'] and results['distances']:
                    score = 1 - results['distances'][0][0]  # Convert distance to similarity
                    if score > best_score:
                        best_score = score
                        best_result = results['documents'][0][0]
            except Exception as e:
                logger.error(f"Error searching topic {topic}: {str(e)}")
                continue

        return best_result if best_result else "No relevant context found." 