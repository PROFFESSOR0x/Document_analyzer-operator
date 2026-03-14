"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    agents,
    health,
    agent_management,
    tools,
    knowledge,
    llm_providers,
    settings,
)

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(
    agent_management.router,
    prefix="/agent-management",
    tags=["Agent Management"],
)
api_router.include_router(
    tools.router,
    prefix="/tools",
    tags=["Tools"],
)
api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["Knowledge Base"],
)
api_router.include_router(
    llm_providers.router,
    prefix="/llm-providers",
    tags=["LLM Providers"],
)
api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["Settings"],
)
