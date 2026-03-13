"""Vector store manager for embedding storage and similarity search."""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
import logging
import json

from app.core.settings import get_settings

settings = get_settings()


class VectorDocument(BaseModel):
    """Vector document model."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    vector: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    content: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VectorSearchRequest(BaseModel):
    """Vector search request model."""

    query_vector: List[float]
    top_k: int = Field(default=10, ge=1, le=100)
    filter_conditions: Optional[Dict[str, Any]] = None
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)


class VectorSearchResult(BaseModel):
    """Vector search result model."""

    id: str
    score: float
    metadata: Dict[str, Any]
    content: Optional[str] = None
    distance: float = 0.0


class VectorStoreManager:
    """Manager for vector database operations.

    This class provides:
    - Vector storage and retrieval
    - Similarity search
    - Metadata filtering
    - Batch operations

    Supports multiple backends:
    - In-memory (default, for development)
    - Qdrant
    - Pinecone
    - Weaviate
    """

    def __init__(
        self,
        provider: str = "memory",
        collection_name: str = "knowledge",
        vector_dimension: int = 1536,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize vector store manager.

        Args:
            provider: Vector store provider (memory, qdrant, pinecone).
            collection_name: Collection name.
            vector_dimension: Vector dimension.
            config: Provider-specific configuration.
        """
        self.provider = provider
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension
        self.config = config or {}

        self._documents: Dict[str, VectorDocument] = {}
        self._logger = logging.getLogger("knowledge.vector_store")

        # Initialize provider
        if provider == "qdrant":
            self._init_qdrant()
        elif provider == "pinecone":
            self._init_pinecone()

        self._logger.info(f"Initialized vector store with provider: {provider}")

    def _init_qdrant(self) -> None:
        """Initialize Qdrant client."""
        try:
            from qdrant_client import QdrantClient

            self._qdrant_client = QdrantClient(
                url=self.config.get("url", "http://localhost:6333"),
                api_key=self.config.get("api_key"),
            )

            # Create collection if not exists
            from qdrant_client.http.models import (
                Distance,
                VectorParams,
            )

            collections = self._qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self._qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dimension,
                        distance=Distance.COSINE,
                    ),
                )

            self._logger.info(f"Qdrant collection '{self.collection_name}' ready")

        except ImportError:
            raise ImportError("qdrant-client not installed. Install with: pip install qdrant-client")
        except Exception as e:
            self._logger.warning(f"Failed to initialize Qdrant: {e}. Falling back to memory store.")
            self.provider = "memory"

    def _init_pinecone(self) -> None:
        """Initialize Pinecone client."""
        try:
            import pinecone

            api_key = self.config.get("api_key")
            environment = self.config.get("environment", "us-west1-gcp")

            pinecone.init(api_key=api_key, environment=environment)

            # Create index if not exists
            indexes = pinecone.list_indexes()
            if self.collection_name not in indexes:
                pinecone.create_index(
                    name=self.collection_name,
                    dimension=self.vector_dimension,
                    metric="cosine",
                )

            self._pinecone_index = pinecone.Index(self.collection_name)
            self._logger.info(f"Pinecone index '{self.collection_name}' ready")

        except ImportError:
            raise ImportError("pinecone-client not installed. Install with: pip install pinecone-client")
        except Exception as e:
            self._logger.warning(f"Failed to initialize Pinecone: {e}. Falling back to memory store.")
            self.provider = "memory"

    async def upsert(
        self,
        document: VectorDocument,
    ) -> str:
        """Upsert a vector document.

        Args:
            document: Document to upsert.

        Returns:
            str: Document ID.
        """
        if self.provider == "memory":
            self._documents[document.id] = document
        elif self.provider == "qdrant":
            from qdrant_client.http.models import PointStruct

            self._qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=document.id,
                        vector=document.vector,
                        payload={
                            **document.metadata,
                            "content": document.content,
                            "created_at": document.created_at.isoformat(),
                        },
                    )
                ],
            )
        elif self.provider == "pinecone":
            self._pinecone_index.upsert(
                vectors=[(
                    document.id,
                    document.vector,
                    {
                        **document.metadata,
                        "content": document.content,
                        "created_at": document.created_at.isoformat(),
                    },
                )]
            )

        self._logger.debug(f"Upserted vector document: {document.id}")
        return document.id

    async def upsert_batch(
        self,
        documents: List[VectorDocument],
        batch_size: int = 100,
    ) -> List[str]:
        """Upsert multiple vector documents.

        Args:
            documents: Documents to upsert.
            batch_size: Batch size for upserts.

        Returns:
            List[str]: Document IDs.
        """
        ids = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            if self.provider == "memory":
                for doc in batch:
                    self._documents[doc.id] = doc
                    ids.append(doc.id)

            elif self.provider == "qdrant":
                from qdrant_client.http.models import PointStruct

                points = [
                    PointStruct(
                        id=doc.id,
                        vector=doc.vector,
                        payload={
                            **doc.metadata,
                            "content": doc.content,
                            "created_at": doc.created_at.isoformat(),
                        },
                    )
                    for doc in batch
                ]

                self._qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                ids.extend([doc.id for doc in batch])

            elif self.provider == "pinecone":
                vectors = [
                    (
                        doc.id,
                        doc.vector,
                        {
                            **doc.metadata,
                            "content": doc.content,
                            "created_at": doc.created_at.isoformat(),
                        },
                    )
                    for doc in batch
                ]
                self._pinecone_index.upsert(vectors=vectors)
                ids.extend([doc.id for doc in batch])

        self._logger.info(f"Upserted batch of {len(documents)} documents")
        return ids

    async def search(
        self,
        request: VectorSearchRequest,
    ) -> List[VectorSearchResult]:
        """Search for similar vectors.

        Args:
            request: Search request.

        Returns:
            List[VectorSearchResult]: Search results.
        """
        if self.provider == "memory":
            return self._memory_search(request)
        elif self.provider == "qdrant":
            return await self._qdrant_search(request)
        elif self.provider == "pinecone":
            return await self._pinecone_search(request)

        return []

    def _memory_search(self, request: VectorSearchRequest) -> List[VectorSearchResult]:
        """In-memory similarity search.

        Args:
            request: Search request.

        Returns:
            List[VectorSearchResult]: Search results.
        """
        results = []

        for doc in self._documents.values():
            # Apply filters
            if request.filter_conditions:
                if not self._matches_filter(doc.metadata, request.filter_conditions):
                    continue

            # Calculate cosine similarity
            score = self._cosine_similarity(request.query_vector, doc.vector)

            if score >= request.min_score:
                results.append(
                    VectorSearchResult(
                        id=doc.id,
                        score=score,
                        metadata=doc.metadata,
                        content=doc.content,
                        distance=1.0 - score,
                    )
                )

        # Sort by score and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[: request.top_k]

    async def _qdrant_search(self, request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Qdrant similarity search.

        Args:
            request: Search request.

        Returns:
            List[VectorSearchResult]: Search results.
        """
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue

        search_filter = None
        if request.filter_conditions:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in request.filter_conditions.items()
            ]
            search_filter = Filter(must=conditions)

        search_results = self._qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=request.query_vector,
            limit=request.top_k,
            query_filter=search_filter,
            score_threshold=request.min_score,
        )

        return [
            VectorSearchResult(
                id=str(result.id),
                score=result.score,
                metadata=result.payload or {},
                content=(result.payload or {}).get("content"),
                distance=1.0 - result.score,
            )
            for result in search_results
        ]

    async def _pinecone_search(self, request: VectorSearchRequest) -> List[VectorSearchResult]:
        """Pinecone similarity search.

        Args:
            request: Search request.

        Returns:
            List[VectorSearchResult]: Search results.
        """
        search_kwargs = {
            "vector": request.query_vector,
            "top_k": request.top_k,
            "include_metadata": True,
        }

        if request.filter_conditions:
            search_kwargs["filter"] = request.filter_conditions

        results = self._pinecone_index.query(**search_kwargs)

        return [
            VectorSearchResult(
                id=match["id"],
                score=match["score"],
                metadata=match.get("metadata", {}),
                content=match.get("metadata", {}).get("content"),
                distance=1.0 - match["score"],
            )
            for match in results.get("matches", [])
            if match["score"] >= request.min_score
        ]

    async def delete(self, document_id: str) -> bool:
        """Delete a vector document.

        Args:
            document_id: Document ID.

        Returns:
            bool: True if deleted.
        """
        if self.provider == "memory":
            if document_id in self._documents:
                del self._documents[document_id]
                return True
        elif self.provider == "qdrant":
            self._qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[document_id],
            )
        elif self.provider == "pinecone":
            self._pinecone_index.delete(ids=[document_id])

        self._logger.debug(f"Deleted vector document: {document_id}")
        return True

    async def delete_by_filter(self, filter_conditions: Dict[str, Any]) -> int:
        """Delete documents matching filter.

        Args:
            filter_conditions: Filter conditions.

        Returns:
            int: Number of deleted documents.
        """
        if self.provider == "memory":
            ids_to_delete = [
                doc_id
                for doc_id, doc in self._documents.items()
                if self._matches_filter(doc.metadata, filter_conditions)
            ]
            for doc_id in ids_to_delete:
                del self._documents[doc_id]
            return len(ids_to_delete)

        elif self.provider == "qdrant":
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filter_conditions.items()
            ]
            search_filter = Filter(must=conditions)

            # Get matching IDs first
            results = self._qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=10000,
            )
            ids = [str(point.id) for point in results[0]]

            self._qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=ids,
            )
            return len(ids)

        elif self.provider == "pinecone":
            self._pinecone_index.delete(filter=filter_conditions)
            return 0  # Pinecone doesn't return count

        return 0

    async def get(self, document_id: str) -> Optional[VectorDocument]:
        """Get a vector document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Optional[VectorDocument]: Document or None.
        """
        if self.provider == "memory":
            return self._documents.get(document_id)
        elif self.provider == "qdrant":
            result = self._qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[document_id],
            )
            if result:
                point = result[0]
                return VectorDocument(
                    id=str(point.id),
                    vector=point.vector,
                    metadata=point.payload or {},
                    content=(point.payload or {}).get("content"),
                )
        elif self.provider == "pinecone":
            result = self._pinecone_index.fetch(ids=[document_id])
            if document_id in result.get("vectors", {}):
                vector_data = result["vectors"][document_id]
                return VectorDocument(
                    id=document_id,
                    vector=vector_data.get("vector", []),
                    metadata=vector_data.get("metadata", {}),
                    content=vector_data.get("metadata", {}).get("content"),
                )

        return None

    async def count(self, filter_conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count documents.

        Args:
            filter_conditions: Optional filter.

        Returns:
            int: Document count.
        """
        if self.provider == "memory":
            if filter_conditions:
                return sum(
                    1
                    for doc in self._documents.values()
                    if self._matches_filter(doc.metadata, filter_conditions)
                )
            return len(self._documents)

        elif self.provider == "qdrant":
            result = self._qdrant_client.count(
                collection_name=self.collection_name,
            )
            return result.count

        elif self.provider == "pinecone":
            stats = self._pinecone_index.describe_index_stats()
            return stats.get("total_vector_count", 0)

        return 0

    def _cosine_similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        """Calculate cosine similarity between vectors.

        Args:
            vector_a: First vector.
            vector_b: Second vector.

        Returns:
            float: Cosine similarity.
        """
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a * a for a in vector_a) ** 0.5
        norm_b = sum(b * b for b in vector_b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _matches_filter(
        self,
        metadata: Dict[str, Any],
        filter_conditions: Dict[str, Any],
    ) -> bool:
        """Check if metadata matches filter.

        Args:
            metadata: Document metadata.
            filter_conditions: Filter conditions.

        Returns:
            bool: True if matches.
        """
        for key, value in filter_conditions.items():
            if key not in metadata:
                return False
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
        return True

    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics.

        Returns:
            Dict: Statistics.
        """
        count = await self.count()

        return {
            "provider": self.provider,
            "collection": self.collection_name,
            "document_count": count,
            "vector_dimension": self.vector_dimension,
        }
