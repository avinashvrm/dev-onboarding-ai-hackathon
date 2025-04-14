from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using the sentence transformer model.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embeddings (vectors)
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def get_embedding_dimension() -> int:
    """
    Get the dimension of the embeddings generated by the model.
    
    Returns:
        Integer representing the embedding dimension
    """
    return model.get_sentence_embedding_dimension() 