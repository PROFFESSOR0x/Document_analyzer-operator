"""Tests for the knowledge infrastructure."""

import pytest
from typing import Dict, Any, List
from datetime import datetime, timezone
from uuid import uuid4

from app.knowledge.session_memory import SessionMemoryManager, SessionContext, MemoryMessage
from app.knowledge.knowledge_repository import (
    KnowledgeRepository,
    KnowledgeEntity,
    KnowledgeQuery,
    KnowledgeRelationship,
)
from app.knowledge.vector_store import (
    VectorStoreManager,
    VectorDocument,
    VectorSearchRequest,
)
from app.knowledge.knowledge_graph import (
    KnowledgeGraphManager,
    GraphNode,
    GraphRelationship,
)
from app.knowledge.services import (
    KnowledgeIngestionService,
    KnowledgeRetrievalService,
    KnowledgeSynthesisService,
    SemanticSearchService,
)


# ========== Session Memory Tests ==========

class TestSessionMemoryManager:
    """Tests for SessionMemoryManager class."""

    @pytest.fixture
    def memory_manager(self) -> SessionMemoryManager:
        """Create session memory manager for testing."""
        return SessionMemoryManager(max_messages=10, max_tokens=1000)

    def test_create_session(self, memory_manager: SessionMemoryManager) -> None:
        """Test session creation."""
        session = memory_manager.create_session(
            session_id="test-session",
            user_id="user-123",
            workspace_id="ws-456",
        )

        assert session.session_id == "test-session"
        assert session.user_id == "user-123"
        assert session.workspace_id == "ws-456"
        assert len(session.messages) == 0

    def test_get_session(self, memory_manager: SessionMemoryManager) -> None:
        """Test getting a session."""
        memory_manager.create_session("test-session", "user-123")

        session = memory_manager.get_session("test-session")
        assert session is not None
        assert session.session_id == "test-session"

    def test_get_session_not_found(self, memory_manager: SessionMemoryManager) -> None:
        """Test getting non-existent session."""
        session = memory_manager.get_session("nonexistent")
        assert session is None

    def test_add_message(self, memory_manager: SessionMemoryManager) -> None:
        """Test adding messages to session."""
        memory_manager.create_session("test-session", "user-123")
        memory_manager.add_message("test-session", "user", "Hello!")
        memory_manager.add_message("test-session", "assistant", "Hi there!")

        session = memory_manager.get_session("test-session")
        assert session is not None
        assert len(session.messages) == 2
        assert session.messages[0].role == "user"
        assert session.messages[1].role == "assistant"

    def test_get_messages(self, memory_manager: SessionMemoryManager) -> None:
        """Test getting messages from session."""
        memory_manager.create_session("test-session", "user-123")

        for i in range(5):
            memory_manager.add_message("test-session", "user", f"Message {i}")

        messages = memory_manager.get_messages("test-session", limit=3)
        assert len(messages) == 3

    def test_context_window_management(
        self,
        memory_manager: SessionMemoryManager,
    ) -> None:
        """Test context window management."""
        memory_manager.create_session("test-session", "user-123")

        # Add more messages than max
        for i in range(15):
            memory_manager.add_message("test-session", "user", f"Message {i}")

        session = memory_manager.get_session("test-session")
        assert session is not None
        assert len(session.messages) <= 10  # max_messages

    def test_compress_memory(self, memory_manager: SessionMemoryManager) -> None:
        """Test memory compression."""
        memory_manager.create_session("test-session", "user-123")

        for i in range(20):
            memory_manager.add_message(
                "test-session",
                "user",
                f"This is a longer message number {i} with more content.",
            )

        compressed = memory_manager.compress_memory("test-session")

        assert compressed is not None
        assert compressed.summary != ""

    def test_clear_session(self, memory_manager: SessionMemoryManager) -> None:
        """Test clearing a session."""
        memory_manager.create_session("test-session", "user-123")
        memory_manager.clear_session("test-session")

        session = memory_manager.get_session("test-session")
        assert session is None

    def test_get_context_for_llm(self, memory_manager: SessionMemoryManager) -> None:
        """Test getting context formatted for LLM."""
        memory_manager.create_session("test-session", "user-123")
        memory_manager.add_message("test-session", "user", "Hello!")
        memory_manager.add_message("test-session", "assistant", "Hi!")

        context = memory_manager.get_context_for_llm("test-session")

        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"


# ========== Knowledge Repository Tests ==========

class TestKnowledgeRepository:
    """Tests for KnowledgeRepository class."""

    @pytest.fixture
    def repository(self) -> KnowledgeRepository:
        """Create knowledge repository for testing."""
        # Create a mock async session
        class MockSession:
            pass

        return KnowledgeRepository(MockSession())  # type: ignore

    @pytest.mark.asyncio
    async def test_create_entity(self, repository: KnowledgeRepository) -> None:
        """Test creating a knowledge entity."""
        entity = KnowledgeEntity(
            title="Test Document",
            content="This is test content.",
            entity_type="document",
            tags=["test", "sample"],
        )

        created = await repository.create(entity)

        assert created.id == entity.id
        assert created.title == "Test Document"

    @pytest.mark.asyncio
    async def test_get_entity(self, repository: KnowledgeRepository) -> None:
        """Test getting a knowledge entity."""
        entity = KnowledgeEntity(
            title="Test Document",
            content="Content here.",
        )
        await repository.create(entity)

        retrieved = await repository.get(entity.id)

        assert retrieved is not None
        assert retrieved.id == entity.id

    @pytest.mark.asyncio
    async def test_update_entity(self, repository: KnowledgeRepository) -> None:
        """Test updating a knowledge entity."""
        entity = KnowledgeEntity(
            title="Original Title",
            content="Original content.",
        )
        await repository.create(entity)

        updated = await repository.update(
            entity.id,
            {"title": "Updated Title"},
        )

        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.version == 2

    @pytest.mark.asyncio
    async def test_delete_entity(self, repository: KnowledgeRepository) -> None:
        """Test deleting a knowledge entity."""
        entity = KnowledgeEntity(
            title="To Delete",
            content="Content.",
        )
        await repository.create(entity)

        deleted = await repository.delete(entity.id, soft_delete=True)

        assert deleted is True

        retrieved = await repository.get(entity.id)
        assert retrieved is not None
        assert retrieved.is_deleted is True

    @pytest.mark.asyncio
    async def test_query_entities(self, repository: KnowledgeRepository) -> None:
        """Test querying knowledge entities."""
        # Create multiple entities
        for i in range(5):
            entity = KnowledgeEntity(
                title=f"Document {i}",
                content=f"Content {i}",
                entity_type="document",
                tags=["test"],
            )
            await repository.create(entity)

        query = KnowledgeQuery(
            entity_type="document",
            limit=3,
        )

        results = await repository.query(query)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_create_relationship(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        """Test creating entity relationships."""
        relationship = KnowledgeRelationship(
            source_entity_id="entity-1",
            target_entity_id="entity-2",
            relationship_type="RELATED_TO",
        )

        created = await repository.create_relationship(relationship)

        assert created.id == relationship.id
        assert created.relationship_type == "RELATED_TO"

    @pytest.mark.asyncio
    async def test_get_statistics(self, repository: KnowledgeRepository) -> None:
        """Test getting repository statistics."""
        # Create entities with different types
        for i in range(3):
            entity = KnowledgeEntity(
                title=f"Doc {i}",
                content="Content",
                entity_type="document",
            )
            await repository.create(entity)

        stats = await repository.get_statistics()

        assert stats["total_entities"] == 3
        assert "document" in stats["by_type"]


# ========== Vector Store Tests ==========

class TestVectorStoreManager:
    """Tests for VectorStoreManager class."""

    @pytest.fixture
    def vector_store(self) -> VectorStoreManager:
        """Create vector store for testing."""
        return VectorStoreManager(provider="memory", vector_dimension=128)

    @pytest.mark.asyncio
    async def test_upsert_document(self, vector_store: VectorStoreManager) -> None:
        """Test upserting a vector document."""
        doc = VectorDocument(
            vector=[0.1] * 128,
            metadata={"title": "Test"},
            content="Test content",
        )

        doc_id = await vector_store.upsert(doc)

        assert doc_id == doc.id

    @pytest.mark.asyncio
    async def test_upsert_batch(self, vector_store: VectorStoreManager) -> None:
        """Test batch upsert."""
        docs = [
            VectorDocument(
                vector=[0.1 * i] * 128,
                metadata={"index": i},
                content=f"Content {i}",
            )
            for i in range(5)
        ]

        ids = await vector_store.upsert_batch(docs)

        assert len(ids) == 5

    @pytest.mark.asyncio
    async def test_vector_search(self, vector_store: VectorStoreManager) -> None:
        """Test vector similarity search."""
        # Insert documents
        docs = [
            VectorDocument(
                vector=[0.1 * (i + 1)] * 128,
                metadata={"label": f"doc-{i}"},
                content=f"Content {i}",
            )
            for i in range(10)
        ]
        await vector_store.upsert_batch(docs)

        # Search
        request = VectorSearchRequest(
            query_vector=[0.1] * 128,
            top_k=3,
        )

        results = await vector_store.search(request)

        assert len(results) == 3
        assert results[0].score > 0

    @pytest.mark.asyncio
    async def test_search_with_filter(
        self,
        vector_store: VectorStoreManager,
    ) -> None:
        """Test vector search with metadata filter."""
        docs = [
            VectorDocument(
                vector=[0.1] * 128,
                metadata={"category": "A" if i % 2 == 0 else "B"},
                content=f"Content {i}",
            )
            for i in range(10)
        ]
        await vector_store.upsert_batch(docs)

        request = VectorSearchRequest(
            query_vector=[0.1] * 128,
            top_k=10,
            filter_conditions={"category": "A"},
        )

        results = await vector_store.search(request)

        # All results should match filter
        for result in results:
            assert result.metadata.get("category") == "A"

    @pytest.mark.asyncio
    async def test_delete_document(self, vector_store: VectorStoreManager) -> None:
        """Test deleting a vector document."""
        doc = VectorDocument(vector=[0.1] * 128)
        await vector_store.upsert(doc)

        deleted = await vector_store.delete(doc.id)

        assert deleted is True

        retrieved = await vector_store.get(doc.id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_document(self, vector_store: VectorStoreManager) -> None:
        """Test getting a vector document."""
        doc = VectorDocument(
            vector=[0.1] * 128,
            metadata={"test": "value"},
            content="Test",
        )
        await vector_store.upsert(doc)

        retrieved = await vector_store.get(doc.id)

        assert retrieved is not None
        assert retrieved.id == doc.id

    @pytest.mark.asyncio
    async def test_count_documents(self, vector_store: VectorStoreManager) -> None:
        """Test counting documents."""
        docs = [VectorDocument(vector=[0.1] * 128) for _ in range(5)]
        await vector_store.upsert_batch(docs)

        count = await vector_store.count()

        assert count == 5

    @pytest.mark.asyncio
    async def test_cosine_similarity(self, vector_store: VectorStoreManager) -> None:
        """Test cosine similarity calculation."""
        # Identical vectors should have similarity 1.0
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = vector_store._cosine_similarity(vec1, vec2)

        assert abs(similarity - 1.0) < 0.001

        # Orthogonal vectors should have similarity 0.0
        vec3 = [0.0, 1.0, 0.0]
        similarity = vector_store._cosine_similarity(vec1, vec3)

        assert abs(similarity) < 0.001


# ========== Knowledge Graph Tests ==========

class TestKnowledgeGraphManager:
    """Tests for KnowledgeGraphManager class."""

    @pytest.fixture
    def graph_manager(self) -> KnowledgeGraphManager:
        """Create knowledge graph manager for testing."""
        return KnowledgeGraphManager(provider="memory")

    @pytest.mark.asyncio
    async def test_create_node(self, graph_manager: KnowledgeGraphManager) -> None:
        """Test creating a graph node."""
        node = GraphNode(
            labels=["Person"],
            properties={"name": "Alice"},
        )

        created = await graph_manager.create_node(node)

        assert created.id == node.id
        assert created.labels == ["Person"]

    @pytest.mark.asyncio
    async def test_create_relationship(
        self,
        graph_manager: KnowledgeGraphManager,
    ) -> None:
        """Test creating a relationship."""
        node1 = GraphNode(labels=["Person"], properties={"name": "Alice"})
        node2 = GraphNode(labels=["Person"], properties={"name": "Bob"})

        await graph_manager.create_node(node1)
        await graph_manager.create_node(node2)

        relationship = GraphRelationship(
            start_node_id=node1.id,
            end_node_id=node2.id,
            type="KNOWS",
        )

        created = await graph_manager.create_relationship(relationship)

        assert created.id == relationship.id
        assert created.type == "KNOWS"

    @pytest.mark.asyncio
    async def test_delete_node(self, graph_manager: KnowledgeGraphManager) -> None:
        """Test deleting a node."""
        node = GraphNode(labels=["Test"])
        await graph_manager.create_node(node)

        deleted = await graph_manager.delete_node(node.id)

        assert deleted is True

        retrieved = await graph_manager.get_node(node.id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_find_paths(self, graph_manager: KnowledgeGraphManager) -> None:
        """Test finding paths between nodes."""
        # Create a chain: A -> B -> C
        nodes = [
            GraphNode(labels=["Node"], properties={"name": chr(65 + i)})
            for i in range(3)
        ]

        for node in nodes:
            await graph_manager.create_node(node)

        for i in range(len(nodes) - 1):
            rel = GraphRelationship(
                start_node_id=nodes[i].id,
                end_node_id=nodes[i + 1].id,
                type="CONNECTS",
            )
            await graph_manager.create_relationship(rel)

        # Find path from A to C
        paths = await graph_manager.find_paths(
            nodes[0].id,
            nodes[2].id,
            max_depth=5,
        )

        assert len(paths) > 0
        assert paths[0].length == 2

    @pytest.mark.asyncio
    async def test_traverse(self, graph_manager: KnowledgeGraphManager) -> None:
        """Test graph traversal."""
        # Create star graph: center -> leaves
        center = GraphNode(labels=["Center"])
        await graph_manager.create_node(center)

        for i in range(3):
            leaf = GraphNode(labels=["Leaf"], properties={"index": i})
            await graph_manager.create_node(leaf)

            rel = GraphRelationship(
                start_node_id=center.id,
                end_node_id=leaf.id,
                type="CONNECTS",
            )
            await graph_manager.create_relationship(rel)

        # Traverse from center
        path = await graph_manager.traverse(center.id, max_depth=1)

        assert len(path.nodes) == 4  # center + 3 leaves

    @pytest.mark.asyncio
    async def test_extract_entities(
        self,
        graph_manager: KnowledgeGraphManager,
    ) -> None:
        """Test entity extraction from text."""
        text = "John Smith works at TechCorp Inc. The company was founded in 2020."

        extraction = await graph_manager.extract_entities(text)

        assert len(extraction.entities) > 0
        assert len(extraction.relationships) > 0

    @pytest.mark.asyncio
    async def test_get_statistics(
        self,
        graph_manager: KnowledgeGraphManager,
    ) -> None:
        """Test getting graph statistics."""
        # Create some nodes and relationships
        for i in range(5):
            node = GraphNode(labels=["Test"])
            await graph_manager.create_node(node)

        stats = await graph_manager.get_statistics()

        assert stats["node_count"] == 5
        assert stats["provider"] == "memory"


# ========== Knowledge Services Tests ==========

class TestKnowledgeServices:
    """Tests for knowledge services."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        from unittest.mock import AsyncMock, MagicMock

        # Create mock repositories
        mock_repo = MagicMock()
        mock_vector_store = MagicMock()
        mock_graph = MagicMock()
        mock_session = MagicMock()

        # Create real services with mocks
        ingestion = KnowledgeIngestionService(
            repository=mock_repo,
            vector_store=mock_vector_store,
            graph_manager=mock_graph,
        )

        retrieval = KnowledgeRetrievalService(
            repository=mock_repo,
            vector_store=mock_vector_store,
            graph_manager=mock_graph,
            session_memory=mock_session,
        )

        synthesis = KnowledgeSynthesisService(retrieval_service=retrieval)
        semantic_search = SemanticSearchService(retrieval_service=retrieval)

        return {
            "ingestion": ingestion,
            "retrieval": retrieval,
            "synthesis": synthesis,
            "semantic_search": semantic_search,
        }

    @pytest.mark.asyncio
    async def test_ingestion_chunking(self, mock_services) -> None:
        """Test text chunking in ingestion."""
        service = mock_services["ingestion"]

        # Test simple chunking
        text = "Sentence 1. Sentence 2. Sentence 3. " * 10
        chunks = service._chunk_text(text, chunk_size=50, chunk_overlap=10)

        assert len(chunks) > 1
        assert all(len(c) <= 60 for c in chunks)  # Allow some overlap

    @pytest.mark.asyncio
    async def test_mock_embedding_generation(
        self,
        mock_services,
    ) -> None:
        """Test mock embedding generation."""
        service = mock_services["ingestion"]

        embedding = service._mock_embedding("Test text")

        assert len(embedding) == 1536
        assert all(-1 <= x <= 1 for x in embedding)

    @pytest.mark.asyncio
    async def test_result_fusion(self, mock_services) -> None:
        """Test result fusion in retrieval."""
        service = mock_services["retrieval"]

        results = [
            RetrievalResult(relevance_score=0.9),
            RetrievalResult(relevance_score=0.5),
            RetrievalResult(relevance_score=0.7),
        ]

        fused = service._fuse_results(results, top_k=2)

        assert len(fused) == 2
        assert fused[0].relevance_score > fused[1].relevance_score

    @pytest.mark.asyncio
    async def test_synthesis_confidence(
        self,
        mock_services,
    ) -> None:
        """Test confidence calculation in synthesis."""
        service = mock_services["synthesis"]

        results = [
            RetrievalResult(relevance_score=0.8),
            RetrievalResult(relevance_score=0.6),
            RetrievalResult(relevance_score=0.9),
        ]

        confidence = service._calculate_confidence(results)

        assert 0 < confidence <= 1

    @pytest.mark.asyncio
    async def test_gap_identification(
        self,
        mock_services,
    ) -> None:
        """Test knowledge gap identification."""
        service = mock_services["synthesis"]

        query = "How do I implement this step by step?"
        contents = ["Short content."]

        gaps = service._identify_gaps(query, contents)

        assert len(gaps) > 0  # Should identify missing steps


# ========== Integration Tests ==========

class TestKnowledgeIntegration:
    """Integration tests for knowledge infrastructure."""

    @pytest.mark.asyncio
    async def test_full_ingestion_workflow(self) -> None:
        """Test complete ingestion workflow."""
        # Setup
        from unittest.mock import MagicMock

        mock_repo = MagicMock()
        mock_vector_store = MagicMock()
        mock_graph = MagicMock()

        service = KnowledgeIngestionService(
            repository=mock_repo,
            vector_store=mock_vector_store,
            graph_manager=mock_graph,
        )

        # Ingest
        results = await service.ingest(
            content="This is test content. " * 10,
            title="Test Document",
            entity_type="document",
            tags=["test"],
            chunk_size=100,
            chunk_overlap=20,
        )

        # Verify
        assert len(results) > 0
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_session_with_knowledge(self) -> None:
        """Test session memory with knowledge operations."""
        memory = SessionMemoryManager()

        # Create session
        memory.create_session("test-session", "user-123")

        # Add messages
        memory.add_message("test-session", "user", "What is Python?")
        memory.add_message(
            "test-session",
            "assistant",
            "Python is a programming language.",
        )

        # Get context
        context = memory.get_context_for_llm("test-session")

        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"
