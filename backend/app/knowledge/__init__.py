"""Knowledge Infrastructure for persistent storage and retrieval.

This module provides:
- Session Memory Management
- Long-term Knowledge Storage
- Vector Store for Embeddings
- Knowledge Graph Management
- Knowledge Services
"""

from app.knowledge.session_memory import SessionMemoryManager
from app.knowledge.knowledge_repository import KnowledgeRepository
from app.knowledge.vector_store import VectorStoreManager
from app.knowledge.knowledge_graph import KnowledgeGraphManager
from app.knowledge.services import (
    KnowledgeIngestionService,
    KnowledgeRetrievalService,
    KnowledgeSynthesisService,
    SemanticSearchService,
)

__all__ = [
    "SessionMemoryManager",
    "KnowledgeRepository",
    "VectorStoreManager",
    "KnowledgeGraphManager",
    "KnowledgeIngestionService",
    "KnowledgeRetrievalService",
    "KnowledgeSynthesisService",
    "SemanticSearchService",
]
