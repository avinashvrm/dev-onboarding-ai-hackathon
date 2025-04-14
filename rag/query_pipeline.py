from typing import List, Dict, Any
from .embedding import get_embeddings
from .qdrant_client import QdrantManager
from .llm_client import LLMClient

class RAGPipeline:
    def __init__(self, qdrant_manager: QdrantManager, llm_client: LLMClient):
        """
        Initialize the RAG pipeline with Qdrant and LLM clients.
        
        Args:
            qdrant_manager: Initialized QdrantManager instance
            llm_client: Initialized LLMClient instance
        """
        self.qdrant_manager = qdrant_manager
        self.llm_client = llm_client
    
    def get_context(
        self,
        query: str,
        topic: str = None,
        limit: int = 5
    ) -> List[str]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            topic: Optional topic to search in
            limit: Maximum number of chunks to retrieve
            
        Returns:
            List of relevant context chunks
        """
        # Generate query embedding
        query_embedding = get_embeddings([query])[0]
        
        # Search for relevant chunks
        if topic:
            results = self.qdrant_manager.search(
                query_vector=query_embedding,
                collection_name=topic,
                limit=limit
            )
        else:
            results = self.qdrant_manager.search_all_collections(
                query_vector=query_embedding,
                limit=limit
            )
        
        # Extract text from results
        return [result["text"] for result in results]
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[str] = None
    ) -> str:
        """
        Generate an answer using the retrieved context.
        
        Args:
            query: User query
            context_chunks: Optional list of context chunks
            
        Returns:
            Generated answer
        """
        # If no context provided, retrieve it
        if not context_chunks:
            context_chunks = self.get_context(query)
        
        # Generate response using LLM
        return self.llm_client.generate_response(query, context_chunks)
    
    def process_query(
        self,
        query: str,
        topic: str = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Process a query through the entire RAG pipeline.
        
        Args:
            query: User query
            topic: Optional topic to search in
            limit: Maximum number of chunks to retrieve
            
        Returns:
            Dictionary containing the answer and metadata
        """
        # Get relevant context
        context_chunks = self.get_context(query, topic, limit)
        
        # Generate answer
        answer = self.generate_answer(query, context_chunks)
        
        return {
            "answer": answer,
            "context_chunks": context_chunks,
            "num_chunks": len(context_chunks)
        } 