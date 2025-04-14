from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from .embedding import get_embedding_dimension

class QdrantManager:
    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize Qdrant client and create collections if they don't exist.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
        """
        self.client = QdrantClient(host=host, port=port)
        self.embedding_dim = get_embedding_dimension()
    
    def ensure_collection(self, collection_name: str):
        """
        Create a collection if it doesn't exist.
        """
        collections = self.client.get_collections().collections
        exists = any(col.name == collection_name for col in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_dim,
                    distance=models.Distance.COSINE
                )
            )
    
    def store_vectors(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: List[Dict[str, Any]],
        collection_name: str = "default"
    ):
        """
        Store vectors in Qdrant with their metadata.
        """
        self.ensure_collection(collection_name)
        
        points = []
        for i, (embedding, text, meta) in enumerate(zip(embeddings, texts, metadata)):
            points.append(models.PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": text,
                    **meta
                }
            ))
        
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    def search(
        self,
        query_vector: List[float],
        collection_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in a specific collection.
        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [
            {
                "text": hit.payload["text"],
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
            }
            for hit in results
        ]
    
    def search_all_collections(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search across all collections and return the best matches.
        """
        collections = self.client.get_collections().collections
        all_results = []
        
        for collection in collections:
            results = self.search(
                query_vector=query_vector,
                collection_name=collection.name,
                limit=limit
            )
            all_results.extend(results)
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:limit]
    
    def get_collections(self) -> List[str]:
        """
        Get list of all collection names.
        """
        collections = self.client.get_collections().collections
        return [col.name for col in collections] 