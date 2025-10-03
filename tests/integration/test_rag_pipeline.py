"""Integration tests for RAG pipeline components."""

import pytest
from unittest.mock import Mock, patch
from src.core.nodes.retriever_faiss import Retriever
from src.core.nodes.reason_ollama import ReasonNode
from src.core.nodes.reranker_bge import RerankerNode


class TestRAGPipeline:
    """Integration tests for RAG pipeline."""
    
    @pytest.fixture
    def mock_retriever(self):
        """Mock retriever for testing."""
        with patch('src.core.nodes.retriever_faiss.Retriever.__init__', return_value=None):
            retriever = Retriever()
            retriever.search = Mock(return_value=[
                {"id": "doc1", "content": "Test content 1", "score": 0.9},
                {"id": "doc2", "content": "Test content 2", "score": 0.8}
            ])
            return retriever
    
    @pytest.fixture
    def mock_reranker(self):
        """Mock reranker for testing."""
        with patch('src.core.nodes.reranker_bge.RerankerNode.__init__', return_value=None):
            reranker = RerankerNode()
            reranker.rerank = Mock(return_value=[
                {"id": "doc1", "content": "Test content 1", "score": 0.95},
                {"id": "doc2", "content": "Test content 2", "score": 0.85}
            ])
            return reranker
    
    @pytest.fixture
    def mock_reasoner(self):
        """Mock reasoner for testing."""
        with patch('src.core.nodes.reason_ollama.ReasonNode.__init__', return_value=None):
            reasoner = ReasonNode()
            reasoner.reason = Mock(return_value={
                "answer": "Test answer",
                "confidence": 0.9,
                "sources": ["doc1", "doc2"]
            })
            return reasoner
    
    def test_retrieval_to_reranking_flow(self, mock_retriever, mock_reranker):
        """Test the flow from retrieval to reranking."""
        query = "test query"
        
        # Test retrieval
        retrieved_docs = mock_retriever.search(query, top_k=10)
        assert len(retrieved_docs) == 2
        assert retrieved_docs[0]["score"] == 0.9
        
        # Test reranking
        reranked_docs = mock_reranker.rerank(query, retrieved_docs)
        assert len(reranked_docs) == 2
        assert reranked_docs[0]["score"] == 0.95
    
    def test_full_rag_pipeline(self, mock_retriever, mock_reranker, mock_reasoner):
        """Test the complete RAG pipeline flow."""
        query = "What is credit reporting?"
        
        # Step 1: Retrieval
        retrieved_docs = mock_retriever.search(query, top_k=10)
        
        # Step 2: Reranking
        reranked_docs = mock_reranker.rerank(query, retrieved_docs)
        
        # Step 3: Reasoning
        result = mock_reasoner.reason(query, reranked_docs)
        
        assert result["answer"] == "Test answer"
        assert result["confidence"] == 0.9
        assert len(result["sources"]) == 2
