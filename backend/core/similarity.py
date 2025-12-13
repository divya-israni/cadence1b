"""
Similarity calculation module using cosine similarity.
"""
import numpy as np
from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity


def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score (0-1)
    """
    # Reshape for sklearn
    emb1 = embedding1.reshape(1, -1)
    emb2 = embedding2.reshape(1, -1)
    
    similarity = cosine_similarity(emb1, emb2)[0][0]
    return float(similarity)


def find_top_matches(
    query_embedding: np.ndarray,
    candidate_embeddings: List[np.ndarray],
    top_n: int = 10,
    min_similarity: float = 0.0
) -> List[Tuple[int, float]]:
    """
    Find top N matches based on cosine similarity.
    
    Args:
        query_embedding: Query embedding vector
        candidate_embeddings: List of candidate embedding vectors
        top_n: Number of top matches to return
        min_similarity: Minimum similarity threshold (default 0.0, filter poor matches)
    
    Returns:
        List of tuples (index, similarity_score) sorted by score descending
    """
    if not candidate_embeddings:
        return []
    
    # Convert to numpy array for batch processing
    query_emb = query_embedding.reshape(1, -1)
    candidate_matrix = np.array(candidate_embeddings)
    
    # Calculate similarities
    similarities = cosine_similarity(query_emb, candidate_matrix).flatten()
    
    # Filter by minimum similarity
    valid_indices = np.where(similarities >= min_similarity)[0]
    
    if len(valid_indices) == 0:
        # If no matches meet threshold, return top N anyway (but log warning)
        print(f"Warning: No matches above threshold {min_similarity}. Returning top matches anyway.")
        valid_indices = np.arange(len(similarities))
    
    # Get top N indices from valid matches
    valid_similarities = similarities[valid_indices]
    top_valid_indices = valid_similarities.argsort()[-top_n:][::-1]
    top_indices = valid_indices[top_valid_indices]
    
    # Return list of (index, score) tuples
    results = [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    return results

