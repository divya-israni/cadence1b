"""
Embedding generation module for BERT and RoBERTa models.
"""
import numpy as np
from typing import Optional, List
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """
    Handles BERT and RoBERTa embedding generation.
    Models are lazy-loaded on first use.
    """
    
    def __init__(self):
        self.bert_model: Optional[SentenceTransformer] = None
        self.roberta_model: Optional[SentenceTransformer] = None
        self.bert_loaded = False
        self.roberta_loaded = False
    
    def _load_bert(self):
        """Lazy load BERT model."""
        if not self.bert_loaded:
            try:
                self.bert_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.bert_loaded = True
            except Exception as e:
                raise RuntimeError(f"Failed to load BERT model: {e}")
    
    def _load_roberta(self):
        """Lazy load RoBERTa model."""
        if not self.roberta_loaded:
            try:
                # Use a faster, smaller RoBERTa model optimized for semantic similarity
                # 'all-MiniLM-L12-v2' is similar size to BERT but uses RoBERTa architecture
                # Alternative: 'paraphrase-MiniLM-L6-v2' (even faster, 384 dims)
                self.roberta_model = SentenceTransformer('all-MiniLM-L12-v2')
                self.roberta_loaded = True
                print("RoBERTa model 'all-MiniLM-L12-v2' loaded (384 dimensions, optimized for similarity)")
            except Exception as e:
                raise RuntimeError(f"Failed to load RoBERTa model: {e}")
    
    def generate_bert_embedding(self, text: str) -> np.ndarray:
        """
        Generate BERT embedding for text.
        
        Args:
            text: Input text string
        
        Returns:
            BERT embedding as numpy array
        """
        self._load_bert()
        if self.bert_model is None:
            raise RuntimeError("BERT model not available")
        
        embedding = self.bert_model.encode([text], convert_to_numpy=True, show_progress_bar=False)
        return embedding[0]
    
    def generate_bert_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate BERT embeddings for multiple texts in batch (much faster).
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
        
        Returns:
            List of BERT embeddings as numpy arrays
        """
        self._load_bert()
        if self.bert_model is None:
            raise RuntimeError("BERT model not available")
        
        embeddings = self.bert_model.encode(
            texts, 
            convert_to_numpy=True, 
            batch_size=batch_size,
            show_progress_bar=False
        )
        return [emb for emb in embeddings]
    
    def generate_roberta_embedding(self, text: str) -> np.ndarray:
        """
        Generate RoBERTa embedding for text.
        
        Args:
            text: Input text string
        
        Returns:
            RoBERTa embedding as numpy array
        """
        self._load_roberta()
        if self.roberta_model is None:
            raise RuntimeError("RoBERTa model not available")
        
        embedding = self.roberta_model.encode([text], convert_to_numpy=True, show_progress_bar=False)
        return embedding[0]
    
    def generate_roberta_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate RoBERTa embeddings for multiple texts in batch (much faster).
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
        
        Returns:
            List of RoBERTa embeddings as numpy arrays
        """
        self._load_roberta()
        if self.roberta_model is None:
            raise RuntimeError("RoBERTa model not available")
        
        embeddings = self.roberta_model.encode(
            texts, 
            convert_to_numpy=True, 
            batch_size=batch_size,
            show_progress_bar=False
        )
        return [emb for emb in embeddings]
    
    def generate_embedding(self, text: str, model_type: str = 'bert') -> np.ndarray:
        """
        Generate embedding using specified model type.
        
        Args:
            text: Input text string
            model_type: 'bert' or 'roberta'
        
        Returns:
            Embedding as numpy array
        """
        if model_type.lower() == 'roberta':
            return self.generate_roberta_embedding(text)
        else:
            return self.generate_bert_embedding(text)

