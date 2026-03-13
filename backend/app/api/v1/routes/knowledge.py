"""Knowledge base API endpoints."""

from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4

from app.api.deps import ActiveUser
from app.db.session import get_db, AsyncSession
from app.knowledge.knowledge_repository import (
    KnowledgeRepository,
    KnowledgeEntity,
    KnowledgeQuery,
)
from app.knowledge.vector_store import VectorStoreManager, VectorSearchRequest
from app.knowledge.knowledge_graph import KnowledgeGraphManager
from app.knowledge.session_memory import SessionMemoryManager
from app.knowledge.services import (
    KnowledgeIngestionService,
    KnowledgeRetrievalService,
    KnowledgeSynthesisService,
    SemanticSearchService,
)

router = APIRouter()

# ========== Service Dependencies ==========

_knowledge_services: Optional[Dict[str, Any]] = None


def get_knowledge_services(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get or create knowledge services."""
    global _knowledge_services

    if _knowledge_services is None:
        # Initialize repositories
        repository = KnowledgeRepository(db)
        vector_store = VectorStoreManager(provider="memory")
        graph_manager = KnowledgeGraphManager(provider="memory")
        session_memory = SessionMemoryManager()

        # Initialize services
        ingestion_service = KnowledgeIngestionService(
            repository=repository,
            vector_store=vector_store,
            graph_manager=graph_manager,
        )

        retrieval_service = KnowledgeRetrievalService(
            repository=repository,
            vector_store=vector_store,
            graph_manager=graph_manager,
            session_memory=session_memory,
        )

        synthesis_service = KnowledgeSynthesisService(
            retrieval_service=retrieval_service,
        )

        semantic_search_service = SemanticSearchService(
            retrieval_service=retrieval_service,
        )

        _knowledge_services = {
            "repository": repository,
            "vector_store": vector_store,
            "graph_manager": graph_manager,
            "session_memory": session_memory,
            "ingestion": ingestion_service,
            "retrieval": retrieval_service,
            "synthesis": synthesis_service,
            "semantic_search": semantic_search_service,
        }

    return _knowledge_services


# ========== Request/Response Models ==========

class KnowledgeEntityCreate(BaseModel):
    """Knowledge entity creation request."""

    title: str
    content: str
    entity_type: str = "document"
    source: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    workspace_id: Optional[str] = None


class KnowledgeEntityUpdate(BaseModel):
    """Knowledge entity update request."""

    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class KnowledgeEntityResponse(BaseModel):
    """Knowledge entity response."""

    id: str
    title: str
    content: str
    entity_type: str
    source: Optional[str] = None
    metadata: Dict[str, Any]
    tags: List[str]
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime


class KnowledgeIngestRequest(BaseModel):
    """Knowledge ingestion request."""

    content: str
    title: str
    entity_type: str = "document"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    chunk_size: int = 1000
    chunk_overlap: int = 200


class KnowledgeSearchRequest(BaseModel):
    """Knowledge search request."""

    query: str
    top_k: int = 20
    filters: Optional[Dict[str, Any]] = None
    strategies: Optional[List[str]] = None


class KnowledgeSearchResponse(BaseModel):
    """Knowledge search response."""

    query: str
    results: List[Dict[str, Any]]
    total_count: int
    search_time_ms: float
    facets: Dict[str, Any]


class KnowledgeSynthesizeRequest(BaseModel):
    """Knowledge synthesis request."""

    query: str
    max_sources: int = 10
    synthesis_type: str = "summary"


class KnowledgeSynthesizeResponse(BaseModel):
    """Knowledge synthesis response."""

    synthesized_content: str
    sources: List[str]
    confidence: float
    gaps: List[str]


class SessionMemoryCreate(BaseModel):
    """Session memory creation request."""

    session_id: Optional[str] = None
    workspace_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionMemoryMessage(BaseModel):
    """Session memory message."""

    role: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorSearchRequest(BaseModel):
    """Vector search request."""

    query: str
    top_k: int = 10
    min_score: float = 0.0
    filters: Optional[Dict[str, Any]] = None


# ========== Knowledge Entity Endpoints ==========

@router.post("/entities", response_model=KnowledgeEntityResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_entity(
    entity_data: KnowledgeEntityCreate,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> KnowledgeEntityResponse:
    """Create a knowledge entity.

    Args:
        entity_data: Entity creation data.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        KnowledgeEntityResponse: Created entity.
    """
    entity = KnowledgeEntity(
        title=entity_data.title,
        content=entity_data.content,
        entity_type=entity_data.entity_type,
        source=entity_data.source,
        source_url=entity_data.source_url,
        metadata=entity_data.metadata,
        tags=entity_data.tags,
        workspace_id=entity_data.workspace_id,
        user_id=current_user.id,
    )

    created = await services["repository"].create(entity)

    return KnowledgeEntityResponse(
        id=created.id,
        title=created.title,
        content=created.content,
        entity_type=created.entity_type,
        source=created.source,
        metadata=created.metadata,
        tags=created.tags,
        workspace_id=created.workspace_id,
        user_id=created.user_id,
        version=created.version,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("/entities/{entity_id}", response_model=KnowledgeEntityResponse)
async def get_knowledge_entity(
    entity_id: str,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> KnowledgeEntityResponse:
    """Get a knowledge entity by ID.

    Args:
        entity_id: Entity ID.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        KnowledgeEntityResponse: Entity data.

    Raises:
        HTTPException: If entity not found.
    """
    entity = await services["repository"].get(entity_id)

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entity not found",
        )

    return KnowledgeEntityResponse(
        id=entity.id,
        title=entity.title,
        content=entity.content,
        entity_type=entity.entity_type,
        source=entity.source,
        metadata=entity.metadata,
        tags=entity.tags,
        workspace_id=entity.workspace_id,
        user_id=entity.user_id,
        version=entity.version,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


@router.patch("/entities/{entity_id}", response_model=KnowledgeEntityResponse)
async def update_knowledge_entity(
    entity_id: str,
    entity_data: KnowledgeEntityUpdate,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> KnowledgeEntityResponse:
    """Update a knowledge entity.

    Args:
        entity_id: Entity ID.
        entity_data: Entity update data.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        KnowledgeEntityResponse: Updated entity.

    Raises:
        HTTPException: If entity not found.
    """
    updates = entity_data.model_dump(exclude_unset=True)

    updated = await services["repository"].update(entity_id, updates)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entity not found",
        )

    return KnowledgeEntityResponse(
        id=updated.id,
        title=updated.title,
        content=updated.content,
        entity_type=updated.entity_type,
        source=updated.source,
        metadata=updated.metadata,
        tags=updated.tags,
        workspace_id=updated.workspace_id,
        user_id=updated.user_id,
        version=updated.version,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_entity(
    entity_id: str,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> None:
    """Delete a knowledge entity.

    Args:
        entity_id: Entity ID.
        current_user: Current authenticated user.
        services: Knowledge services.

    Raises:
        HTTPException: If entity not found.
    """
    deleted = await services["repository"].delete(entity_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entity not found",
        )


@router.get("/entities", response_model=List[KnowledgeEntityResponse])
async def list_knowledge_entities(
    current_user: ActiveUser,
    entity_type: Optional[str] = None,
    workspace_id: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> List[KnowledgeEntityResponse]:
    """List knowledge entities.

    Args:
        current_user: Current authenticated user.
        entity_type: Optional entity type filter.
        workspace_id: Optional workspace filter.
        tags: Optional tags filter.
        limit: Maximum number of results.
        offset: Offset for pagination.
        services: Knowledge services.

    Returns:
        List[KnowledgeEntityResponse]: List of entities.
    """
    tag_list = tags.split(",") if tags else None

    query = KnowledgeQuery(
        entity_type=entity_type,
        workspace_id=workspace_id,
        tags=tag_list,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    entities = await services["repository"].query(query)

    return [
        KnowledgeEntityResponse(
            id=e.id,
            title=e.title,
            content=e.content,
            entity_type=e.entity_type,
            source=e.source,
            metadata=e.metadata,
            tags=e.tags,
            workspace_id=e.workspace_id,
            user_id=e.user_id,
            version=e.version,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in entities
    ]


# ========== Ingestion Endpoints ==========

@router.post("/ingest", response_model=List[Dict[str, Any]])
async def ingest_knowledge(
    request: KnowledgeIngestRequest,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> List[Dict[str, Any]]:
    """Ingest knowledge into the knowledge base.

    Args:
        request: Ingestion request.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        List[Dict]: Ingestion results.
    """
    results = await services["ingestion"].ingest(
        content=request.content,
        title=request.title,
        entity_type=request.entity_type,
        metadata=request.metadata,
        tags=request.tags,
        workspace_id=None,
        user_id=current_user.id,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return [
        {
            "entity_id": r.entity_id,
            "vector_id": r.vector_id,
            "graph_node_ids": r.graph_node_ids,
            "success": r.success,
            "error": r.error,
        }
        for r in results
    ]


# ========== Search Endpoints ==========

@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> KnowledgeSearchResponse:
    """Search knowledge base.

    Args:
        request: Search request.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        KnowledgeSearchResponse: Search results.
    """
    results = await services["retrieval"].retrieve(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
        strategies=request.strategies,
        workspace_id=None,
    )

    # Format results
    formatted_results = []
    for result in results:
        item = {
            "relevance_score": result.relevance_score,
        }

        if result.entity:
            item["entity"] = {
                "id": result.entity.id,
                "title": result.entity.title,
                "content": result.entity.content[:500],  # Truncate
                "entity_type": result.entity.entity_type,
            }

        if result.vector_results:
            item["vector_results"] = result.vector_results

        if result.graph_results:
            item["graph_results"] = result.graph_results

        formatted_results.append(item)

    return KnowledgeSearchResponse(
        query=request.query,
        results=formatted_results,
        total_count=len(formatted_results),
        search_time_ms=0.0,
        facets={},
    )


@router.post("/semantic-search", response_model=KnowledgeSearchResponse)
async def semantic_search(
    request: KnowledgeSearchRequest,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> KnowledgeSearchResponse:
    """Perform semantic search.

    Args:
        request: Search request.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        KnowledgeSearchResponse: Search results.
    """
    result = await services["semantic_search"].search(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
        include_facets=True,
    )

    # Format results
    formatted_results = []
    for r in result.results:
        item = {"relevance_score": r.relevance_score}

        if r.entity:
            item["entity"] = {
                "id": r.entity.id,
                "title": r.entity.title,
                "content": r.entity.content[:500],
            }

        formatted_results.append(item)

    return KnowledgeSearchResponse(
        query=result.query,
        results=formatted_results,
        total_count=result.total_count,
        search_time_ms=result.search_time_ms,
        facets=result.facets,
    )


# ========== Synthesis Endpoints ==========

@router.post("/synthesize", response_model=KnowledgeSynthesizeResponse)
async def synthesize_knowledge(
    request: KnowledgeSynthesizeRequest,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> KnowledgeSynthesizeResponse:
    """Synthesize knowledge from multiple sources.

    Args:
        request: Synthesis request.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        KnowledgeSynthesizeResponse: Synthesis result.
    """
    result = await services["synthesis"].synthesize(
        query=request.query,
        max_sources=request.max_sources,
        synthesis_type=request.synthesis_type,
    )

    return KnowledgeSynthesizeResponse(
        synthesized_content=result.synthesized_content,
        sources=result.sources,
        confidence=result.confidence,
        gaps=result.gaps,
    )


# ========== Session Memory Endpoints ==========

@router.post("/sessions", response_model=Dict[str, Any])
async def create_session(
    request: SessionMemoryCreate,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> Dict[str, Any]:
    """Create a session memory.

    Args:
        request: Session creation request.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        Dict: Session information.
    """
    session_id = request.session_id or str(uuid4())

    session = services["session_memory"].create_session(
        session_id=session_id,
        user_id=current_user.id,
        workspace_id=request.workspace_id,
        metadata=request.metadata,
    )

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "workspace_id": session.workspace_id,
        "created_at": session.created_at.isoformat(),
    }


@router.post("/sessions/{session_id}/messages")
async def add_session_message(
    session_id: str,
    message: SessionMemoryMessage,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> Dict[str, Any]:
    """Add a message to session memory.

    Args:
        session_id: Session ID.
        message: Message data.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        Dict: Updated session information.
    """
    session = services["session_memory"].add_message(
        session_id=session_id,
        role=message.role,
        content=message.content,
        metadata=message.metadata,
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return {
        "session_id": session.session_id,
        "message_count": len(session.messages),
        "token_count": session.token_count,
        "updated_at": session.updated_at.isoformat(),
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: ActiveUser,
    limit: Optional[int] = None,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> Dict[str, Any]:
    """Get messages from session.

    Args:
        session_id: Session ID.
        current_user: Current authenticated user.
        limit: Optional message limit.
        services: Knowledge services.

    Returns:
        Dict: Messages.

    Raises:
        HTTPException: If session not found.
    """
    session = services["session_memory"].get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    messages = services["session_memory"].get_messages(
        session_id=session_id,
        limit=limit,
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "metadata": m.metadata,
            }
            for m in messages
        ],
        "count": len(messages),
    }


@router.post("/sessions/{session_id}/compress")
async def compress_session_memory(
    session_id: str,
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> Dict[str, Any]:
    """Compress session memory.

    Args:
        session_id: Session ID.
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        Dict: Compressed memory.

    Raises:
        HTTPException: If session not found.
    """
    compressed = services["session_memory"].compress_memory(session_id)

    if not compressed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or empty",
        )

    return {
        "session_id": session_id,
        "summary": compressed.summary,
        "key_points": compressed.key_points,
        "entities": compressed.entities,
        "compressed_at": compressed.compressed_at.isoformat(),
    }


# ========== Statistics Endpoints ==========

@router.get("/stats")
async def get_knowledge_statistics(
    current_user: ActiveUser,
    services: Dict[str, Any] = Depends(get_knowledge_services),
) -> Dict[str, Any]:
    """Get knowledge base statistics.

    Args:
        current_user: Current authenticated user.
        services: Knowledge services.

    Returns:
        Dict: Statistics.
    """
    repo_stats = await services["repository"].get_statistics()
    vector_stats = await services["vector_store"].get_statistics()
    graph_stats = await services["graph_manager"].get_statistics()

    return {
        "repository": repo_stats,
        "vector_store": vector_stats,
        "knowledge_graph": graph_stats,
    }
