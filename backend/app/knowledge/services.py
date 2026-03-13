"""Knowledge services for ingestion, retrieval, synthesis, and search."""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
import logging
import hashlib

from app.knowledge.knowledge_repository import KnowledgeRepository, KnowledgeEntity
from app.knowledge.vector_store import VectorStoreManager, VectorDocument, VectorSearchRequest
from app.knowledge.knowledge_graph import KnowledgeGraphManager, GraphNode, GraphRelationship
from app.knowledge.session_memory import SessionMemoryManager


class IngestionResult(BaseModel):
    """Ingestion result model."""

    entity_id: str
    vector_id: str
    graph_node_ids: List[str] = Field(default_factory=list)
    success: bool
    error: Optional[str] = None


class RetrievalResult(BaseModel):
    """Retrieval result model."""

    entity: Optional[KnowledgeEntity] = None
    vector_results: List[Dict[str, Any]] = Field(default_factory=list)
    graph_results: List[Dict[str, Any]] = Field(default_factory=list)
    relevance_score: float = 0.0


class SynthesisResult(BaseModel):
    """Knowledge synthesis result model."""

    synthesized_content: str
    sources: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    gaps: List[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Search result model."""

    query: str
    results: List[RetrievalResult] = Field(default_factory=list)
    total_count: int = 0
    search_time_ms: float = 0.0
    facets: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeIngestionService:
    """Service for ingesting documents into the knowledge base.

    This service handles:
    - Document parsing and chunking
    - Embedding generation
    - Entity extraction
    - Multi-store indexing
    """

    def __init__(
        self,
        repository: KnowledgeRepository,
        vector_store: VectorStoreManager,
        graph_manager: KnowledgeGraphManager,
        embedding_generator: Optional[Any] = None,
    ) -> None:
        """Initialize ingestion service.

        Args:
            repository: Knowledge repository.
            vector_store: Vector store manager.
            graph_manager: Knowledge graph manager.
            embedding_generator: Optional embedding generator tool.
        """
        self.repository = repository
        self.vector_store = vector_store
        self.graph_manager = graph_manager
        self.embedding_generator = embedding_generator

        self._logger = logging.getLogger("knowledge.ingestion")

    async def ingest(
        self,
        content: str,
        title: str,
        entity_type: str = "document",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> List[IngestionResult]:
        """Ingest a document into the knowledge base.

        Args:
            content: Document content.
            title: Document title.
            entity_type: Type of entity.
            metadata: Additional metadata.
            tags: Document tags.
            workspace_id: Workspace ID.
            user_id: User ID.
            chunk_size: Chunk size for splitting.
            chunk_overlap: Overlap between chunks.

        Returns:
            List[IngestionResult]: Ingestion results.
        """
        results = []

        # Chunk the content
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)

        self._logger.info(f"Ingesting document '{title}' with {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            # Create knowledge entity
            entity = KnowledgeEntity(
                title=f"{title} (Part {i + 1})",
                content=chunk,
                entity_type=entity_type,
                metadata=metadata or {},
                tags=tags or [],
                workspace_id=workspace_id,
                user_id=user_id,
            )

            # Store in repository
            stored_entity = await self.repository.create(entity)

            # Generate embedding
            embedding = await self._generate_embedding(chunk)

            # Store in vector store
            vector_doc = VectorDocument(
                id=f"vec_{entity.id}",
                vector=embedding,
                metadata={
                    "entity_id": entity.id,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **(metadata or {}),
                },
                content=chunk,
            )
            vector_id = await self.vector_store.upsert(vector_doc)

            # Extract entities and create graph nodes
            extraction = await self.graph_manager.extract_entities(chunk)
            nodes, relationships = await self.graph_manager.create_entities_from_extraction(
                extraction
            )

            # Link entity to graph
            if nodes:
                entity_node = GraphNode(
                    labels=["Document", entity_type],
                    properties={
                        "entity_id": entity.id,
                        "title": title,
                        "content": chunk,
                    },
                )
                entity_node_id = await self.graph_manager.create_node(entity_node)

                # Link to extracted entities
                for extracted_node in nodes:
                    relationship = GraphRelationship(
                        start_node_id=entity_node_id.id,
                        end_node_id=extracted_node.id,
                        type="CONTAINS_ENTITY",
                    )
                    await self.graph_manager.create_relationship(relationship)

            results.append(
                IngestionResult(
                    entity_id=entity.id,
                    vector_id=vector_id,
                    graph_node_ids=[n.id for n in nodes],
                    success=True,
                )
            )

        self._logger.info(f"Successfully ingested {len(results)} chunks")
        return results

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Input text.

        Returns:
            List[float]: Embedding vector.
        """
        if self.embedding_generator:
            # Use provided embedding generator
            result = await self.embedding_generator.execute({"text": text})
            if result.success and result.data:
                return result.data.embedding

        # Fallback: Generate deterministic mock embedding
        return self._mock_embedding(text)

    def _mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding for development.

        Args:
            text: Input text.

        Returns:
            List[float]: Mock embedding.
        """
        # Use hash for deterministic embedding
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = [
            (hash_bytes[i % len(hash_bytes)] / 255.0) * 2 - 1
            for i in range(1536)
        ]

        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        return [x / norm for x in embedding]

    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """Split text into chunks.

        Args:
            text: Input text.
            chunk_size: Chunk size in characters.
            chunk_overlap: Overlap between chunks.

        Returns:
            List[str]: Text chunks.
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence boundary
                for sep in [". ", "! ", "? ", "\n"]:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep != -1:
                        end = start + last_sep + len(sep)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - chunk_overlap
            if start >= len(text):
                break

        return chunks


class KnowledgeRetrievalService:
    """Service for retrieving knowledge from multiple sources.

    This service provides:
    - Multi-strategy retrieval (vector, graph, keyword)
    - Result fusion and ranking
    - Context assembly
    """

    def __init__(
        self,
        repository: KnowledgeRepository,
        vector_store: VectorStoreManager,
        graph_manager: KnowledgeGraphManager,
        session_memory: Optional[SessionMemoryManager] = None,
    ) -> None:
        """Initialize retrieval service.

        Args:
            repository: Knowledge repository.
            vector_store: Vector store manager.
            graph_manager: Knowledge graph manager.
            session_memory: Optional session memory manager.
        """
        self.repository = repository
        self.vector_store = vector_store
        self.graph_manager = graph_manager
        self.session_memory = session_memory

        self._logger = logging.getLogger("knowledge.retrieval")

    async def retrieve(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        strategies: Optional[List[str]] = None,
        workspace_id: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """Retrieve knowledge using multiple strategies.

        Args:
            query: Search query.
            query_embedding: Optional query embedding.
            top_k: Number of results.
            filters: Optional filters.
            strategies: Retrieval strategies to use.
            workspace_id: Optional workspace filter.

        Returns:
            List[RetrievalResult]: Retrieval results.
        """
        strategies = strategies or ["vector", "keyword", "graph"]
        results = []

        # Vector search
        if "vector" in strategies and query_embedding:
            vector_results = await self._vector_search(
                query_embedding,
                top_k,
                filters,
            )
            results.extend(vector_results)

        # Keyword search
        if "keyword" in strategies:
            keyword_results = await self._keyword_search(
                query,
                top_k,
                filters,
                workspace_id,
            )
            results.extend(keyword_results)

        # Graph search
        if "graph" in strategies:
            graph_results = await self._graph_search(query, top_k)
            results.extend(graph_results)

        # Fuse and rank results
        fused_results = self._fuse_results(results, top_k)

        self._logger.info(f"Retrieved {len(fused_results)} results for query: {query[:50]}")
        return fused_results

    async def _vector_search(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[RetrievalResult]:
        """Vector similarity search.

        Args:
            query_embedding: Query embedding.
            top_k: Number of results.
            filters: Optional filters.

        Returns:
            List[RetrievalResult]: Results.
        """
        search_request = VectorSearchRequest(
            query_vector=query_embedding,
            top_k=top_k,
            filter_conditions=filters,
        )

        vector_results = await self.vector_store.search(search_request)

        return [
            RetrievalResult(
                vector_results=[
                    {
                        "id": r.id,
                        "score": r.score,
                        "content": r.content,
                        "metadata": r.metadata,
                    }
                ],
                relevance_score=r.score,
            )
            for r in vector_results
        ]

    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        workspace_id: Optional[str],
    ) -> List[RetrievalResult]:
        """Keyword-based search.

        Args:
            query: Search query.
            top_k: Number of results.
            filters: Optional filters.
            workspace_id: Optional workspace filter.

        Returns:
            List[RetrievalResult]: Results.
        """
        from app.knowledge.knowledge_repository import KnowledgeQuery

        kw_query = KnowledgeQuery(
            query_text=query,
            workspace_id=workspace_id,
            limit=top_k,
        )

        if filters:
            # Apply filters to query
            pass

        entities = await self.repository.query(kw_query)

        return [
            RetrievalResult(
                entity=entity,
                relevance_score=0.5,  # Lower than vector results
            )
            for entity in entities
        ]

    async def _graph_search(
        self,
        query: str,
        top_k: int,
    ) -> List[RetrievalResult]:
        """Graph-based search.

        Args:
            query: Search query.
            top_k: Number of results.

        Returns:
            List[RetrievalResult]: Results.
        """
        # Extract entities from query
        extraction = await self.graph_manager.extract_entities(query)

        results = []
        for entity_data in extraction.entities:
            # Find related nodes in graph
            # (simplified - would use graph traversal in production)
            results.append(
                RetrievalResult(
                    graph_results=[
                        {
                            "entity": entity_data,
                            "type": "extracted",
                        }
                    ],
                    relevance_score=0.3,
                )
            )

        return results[:top_k]

    def _fuse_results(
        self,
        results: List[RetrievalResult],
        top_k: int,
    ) -> List[RetrievalResult]:
        """Fuse and rank results from multiple sources.

        Args:
            results: Results from all sources.
            top_k: Number of results to return.

        Returns:
            List[RetrievalResult]: Fused results.
        """
        # Simple score-based fusion
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Deduplicate
        seen_ids = set()
        unique_results = []

        for result in results:
            result_id = (
                result.entity.id if result.entity
                else (result.vector_results[0].get("id") if result.vector_results else None)
            )

            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)

        return unique_results[:top_k]


class KnowledgeSynthesisService:
    """Service for synthesizing knowledge from multiple sources.

    This service provides:
    - Multi-document summarization
    - Knowledge integration
    - Gap identification
    """

    def __init__(
        self,
        retrieval_service: KnowledgeRetrievalService,
        llm_client: Optional[Any] = None,
    ) -> None:
        """Initialize synthesis service.

        Args:
            retrieval_service: Knowledge retrieval service.
            llm_client: Optional LLM client tool.
        """
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client

        self._logger = logging.getLogger("knowledge.synthesis")

    async def synthesize(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        max_sources: int = 10,
        synthesis_type: str = "summary",
    ) -> SynthesisResult:
        """Synthesize knowledge from multiple sources.

        Args:
            query: Query to synthesize for.
            query_embedding: Optional query embedding.
            max_sources: Maximum number of sources.
            synthesis_type: Type of synthesis (summary, comparison, timeline).

        Returns:
            SynthesisResult: Synthesis result.
        """
        # Retrieve relevant knowledge
        results = await self.retrieval_service.retrieve(
            query=query,
            query_embedding=query_embedding,
            top_k=max_sources,
        )

        # Extract content from results
        contents = []
        sources = []

        for result in results:
            if result.entity:
                contents.append(result.entity.content)
                sources.append(result.entity.id)
            elif result.vector_results:
                for vr in result.vector_results:
                    if vr.get("content"):
                        contents.append(vr["content"])
                        sources.append(vr.get("id", ""))

        # Synthesize
        if self.llm_client:
            synthesized = await self._llm_synthesize(contents, query, synthesis_type)
        else:
            synthesized = self._simple_synthesize(contents, synthesis_type)

        # Identify gaps
        gaps = self._identify_gaps(query, contents)

        return SynthesisResult(
            synthesized_content=synthesized,
            sources=sources,
            confidence=self._calculate_confidence(results),
            gaps=gaps,
        )

    async def _llm_synthesize(
        self,
        contents: List[str],
        query: str,
        synthesis_type: str,
    ) -> str:
        """Synthesize using LLM.

        Args:
            contents: Source contents.
            query: Original query.
            synthesis_type: Synthesis type.

        Returns:
            str: Synthesized content.
        """
        context = "\n\n---\n\n".join(contents[:5])  # Limit context

        prompt = f"""Based on the following information, provide a {synthesis_type} for: {query}

{context}

Synthesis:"""

        result = await self.llm_client.execute({
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.3,
        })

        if result.success and result.data:
            return result.data.response

        return ""

    def _simple_synthesize(
        self,
        contents: List[str],
        synthesis_type: str,
    ) -> str:
        """Simple synthesis without LLM.

        Args:
            contents: Source contents.
            synthesis_type: Synthesis type.

        Returns:
            str: Synthesized content.
        """
        if not contents:
            return "No relevant information found."

        # Concatenate first few sources
        synthesized = "Synthesized from multiple sources:\n\n"
        synthesized += "\n\n".join(contents[:3])

        return synthesized

    def _identify_gaps(
        self,
        query: str,
        contents: List[str],
    ) -> List[str]:
        """Identify knowledge gaps.

        Args:
            query: Original query.
            contents: Source contents.

        Returns:
            List[str]: Identified gaps.
        """
        gaps = []

        # Simple gap detection based on content length
        total_content = " ".join(contents)

        if len(total_content) < 500:
            gaps.append("Limited information available on this topic")

        # Check for missing aspects (simplified)
        query_lower = query.lower()
        if "how" in query_lower and "steps" not in total_content.lower():
            gaps.append("Step-by-step guidance may be missing")

        if "compare" in query_lower and "difference" not in total_content.lower():
            gaps.append("Comparative analysis may be incomplete")

        return gaps

    def _calculate_confidence(self, results: List[RetrievalResult]) -> float:
        """Calculate synthesis confidence.

        Args:
            results: Retrieval results.

        Returns:
            float: Confidence score.
        """
        if not results:
            return 0.0

        # Average relevance score
        avg_score = sum(r.relevance_score for r in results) / len(results)

        # Boost for multiple sources
        source_bonus = min(len(results) / 10, 0.2)

        return min(avg_score + source_bonus, 1.0)


class SemanticSearchService:
    """Service for semantic search operations.

    This service provides:
    - Semantic search with embeddings
    - Faceted search
    - Query expansion
    - Result highlighting
    """

    def __init__(
        self,
        retrieval_service: KnowledgeRetrievalService,
        embedding_generator: Optional[Any] = None,
    ) -> None:
        """Initialize semantic search service.

        Args:
            retrieval_service: Knowledge retrieval service.
            embedding_generator: Optional embedding generator.
        """
        self.retrieval_service = retrieval_service
        self.embedding_generator = embedding_generator

        self._logger = logging.getLogger("knowledge.semantic_search")

    async def search(
        self,
        query: str,
        top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[str] = None,
        include_facets: bool = True,
    ) -> SearchResult:
        """Perform semantic search.

        Args:
            query: Search query.
            top_k: Number of results.
            filters: Optional filters.
            workspace_id: Optional workspace filter.
            include_facets: Whether to include facets.

        Returns:
            SearchResult: Search results.
        """
        start_time = datetime.now(timezone.utc)

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Expand query
        expanded_queries = self._expand_query(query)

        # Retrieve results
        results = await self.retrieval_service.retrieve(
            query=query,
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
            workspace_id=workspace_id,
        )

        # Search expanded queries for more results
        for expanded_query in expanded_queries:
            expanded_embedding = await self._generate_embedding(expanded_query)
            expanded_results = await self.retrieval_service.retrieve(
                query=expanded_query,
                query_embedding=expanded_embedding,
                top_k=top_k // 3,
                filters=filters,
                workspace_id=workspace_id,
            )
            results.extend(expanded_results)

        # Deduplicate and limit
        results = self.retrieval_service._fuse_results(results, top_k)

        search_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        # Generate facets
        facets = {}
        if include_facets:
            facets = self._generate_facets(results)

        return SearchResult(
            query=query,
            results=results,
            total_count=len(results),
            search_time_ms=search_time_ms,
            facets=facets,
        )

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Input text.

        Returns:
            List[float]: Embedding vector.
        """
        if self.embedding_generator:
            result = await self.embedding_generator.execute({"text": text})
            if result.success and result.data:
                return result.data.embedding

        # Fallback
        return self._mock_embedding(text)

    def _mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding."""
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = [
            (hash_bytes[i % len(hash_bytes)] / 255.0) * 2 - 1
            for i in range(1536)
        ]
        norm = sum(x * x for x in embedding) ** 0.5
        return [x / norm for x in embedding]

    def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms and related terms.

        Args:
            query: Original query.

        Returns:
            List[str]: Expanded queries.
        """
        # Simple expansion (can be enhanced with synonym database)
        expansions = []

        # Add variations
        expansions.append(query)

        # Remove common words for broader search
        words = query.split()
        if len(words) > 2:
            expansions.append(" ".join(words[:3]))

        return expansions[:3]

    def _generate_facets(self, results: List[RetrievalResult]) -> Dict[str, Any]:
        """Generate search facets.

        Args:
            results: Search results.

        Returns:
            Dict: Facets.
        """
        facets: Dict[str, Any] = {
            "entity_types": {},
            "tags": {},
            "workspaces": {},
        }

        for result in results:
            if result.entity:
                # Entity type facet
                et = result.entity.entity_type
                facets["entity_types"][et] = facets["entity_types"].get(et, 0) + 1

                # Tag facet
                for tag in result.entity.tags:
                    facets["tags"][tag] = facets["tags"].get(tag, 0) + 1

                # Workspace facet
                if result.entity.workspace_id:
                    ws = result.entity.workspace_id
                    facets["workspaces"][ws] = facets["workspaces"].get(ws, 0) + 1

        return facets
