"""Tool API endpoints for tool execution and management."""

from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.api.deps import ActiveUser
from app.tools.base import ToolRegistry, ToolExecutionEngine, ToolCategory
from app.tools import (
    WebSearchTool,
    WebScraperTool,
    APIClientTool,
    RSSFeedTool,
    PDFParserTool,
    DOCXParserTool,
    MarkdownParserTool,
    TableExtractionTool,
    ImageOCRTool,
    LLMClientTool,
    EmbeddingGeneratorTool,
    TextClassifierTool,
    SummarizationTool,
    QuestionAnsweringTool,
    ShellExecutorTool,
    GitOperationsTool,
    FileConverterTool,
    ScheduledTaskTool,
    DatabaseQueryTool,
    DataValidationTool,
    DataTransformationTool,
    CSVExcelTool,
)

router = APIRouter()

# Initialize tool registry and engine
_tool_registry: Optional[ToolRegistry] = None
_tool_engine: Optional[ToolExecutionEngine] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create tool registry."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry.get_instance()
        _register_default_tools(_tool_registry)
    return _tool_registry


def get_tool_engine() -> ToolExecutionEngine:
    """Get or create tool execution engine."""
    global _tool_engine
    if _tool_engine is None:
        _tool_engine = ToolExecutionEngine(get_tool_registry())
    return _tool_engine


def _register_default_tools(registry: ToolRegistry) -> None:
    """Register default tools."""
    # Web Tools
    registry.register_class(WebSearchTool)
    registry.register_class(WebScraperTool)
    registry.register_class(APIClientTool)
    registry.register_class(RSSFeedTool)

    # Document Tools
    registry.register_class(PDFParserTool)
    registry.register_class(DOCXParserTool)
    registry.register_class(MarkdownParserTool)
    registry.register_class(TableExtractionTool)
    registry.register_class(ImageOCRTool)

    # AI Tools
    registry.register_class(LLMClientTool)
    registry.register_class(EmbeddingGeneratorTool)
    registry.register_class(TextClassifierTool)
    registry.register_class(SummarizationTool)
    registry.register_class(QuestionAnsweringTool)

    # Automation Tools
    registry.register_class(ShellExecutorTool)
    registry.register_class(GitOperationsTool)
    registry.register_class(FileConverterTool)
    registry.register_class(ScheduledTaskTool)

    # Data Tools
    registry.register_class(DatabaseQueryTool)
    registry.register_class(DataValidationTool)
    registry.register_class(DataTransformationTool)
    registry.register_class(CSVExcelTool)


# ========== Request/Response Models ==========

class ToolExecuteRequest(BaseModel):
    """Tool execution request."""

    tool_name: str
    input_data: Dict[str, Any]
    timeout: Optional[float] = None


class ToolExecuteResponse(BaseModel):
    """Tool execution response."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    execution_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolListResponse(BaseModel):
    """Tool list response."""

    tools: List[Dict[str, Any]]
    total_count: int


class ToolInfoResponse(BaseModel):
    """Tool information response."""

    name: str
    description: str
    category: str
    version: str
    tags: List[str]
    requires_auth: bool
    rate_limit: Optional[int]
    timeout_seconds: float
    execution_count: int


# ========== Endpoints ==========

@router.get("", response_model=ToolListResponse)
async def list_tools(
    current_user: ActiveUser,
    category: Optional[str] = None,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolListResponse:
    """List all available tools.

    Args:
        current_user: Current authenticated user.
        category: Optional category filter.
        registry: Tool registry.

    Returns:
        ToolListResponse: List of tools.
    """
    tools = registry.list_all()

    if category:
        tools = [t for t in tools if t.get("category") == category]

    return ToolListResponse(
        tools=tools,
        total_count=len(tools),
    )


@router.get("/categories", response_model=List[str])
async def list_tool_categories(
    current_user: ActiveUser,
) -> List[str]:
    """List all tool categories.

    Args:
        current_user: Current authenticated user.

    Returns:
        List[str]: List of categories.
    """
    return [category.value for category in ToolCategory]


@router.get("/{tool_name}", response_model=ToolInfoResponse)
async def get_tool_info(
    tool_name: str,
    current_user: ActiveUser,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolInfoResponse:
    """Get information about a specific tool.

    Args:
        tool_name: Tool name.
        current_user: Current authenticated user.
        registry: Tool registry.

    Returns:
        ToolInfoResponse: Tool information.

    Raises:
        HTTPException: If tool not found.
    """
    try:
        tool = registry.get(tool_name)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool not found: {tool_name}",
        )

    info = tool.get_info()
    return ToolInfoResponse(**info)


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    current_user: ActiveUser,
    background_tasks: BackgroundTasks,
    engine: ToolExecutionEngine = Depends(get_tool_engine),
) -> ToolExecuteResponse:
    """Execute a tool.

    Args:
        request: Execution request.
        current_user: Current authenticated user.
        background_tasks: Background tasks.
        engine: Tool execution engine.

    Returns:
        ToolExecuteResponse: Execution result.

    Raises:
        HTTPException: If tool not found or execution fails.
    """
    try:
        result = await engine.execute(
            tool_name=request.tool_name,
            input_data=request.input_data,
            timeout=request.timeout,
        )

        return ToolExecuteResponse(
            success=result.success,
            data=result.data.model_dump() if result.data else None,
            error=result.error,
            error_type=result.error_type,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/execute/batch", response_model=List[ToolExecuteResponse])
async def execute_tools_batch(
    requests: List[ToolExecuteRequest],
    current_user: ActiveUser,
    concurrent: bool = True,
    engine: ToolExecutionEngine = Depends(get_tool_engine),
) -> List[ToolExecuteResponse]:
    """Execute multiple tools in batch.

    Args:
        requests: List of execution requests.
        current_user: Current authenticated user.
        concurrent: Whether to execute concurrently.
        engine: Tool execution engine.

    Returns:
        List[ToolExecuteResponse]: List of results.
    """
    executions = [
        {
            "tool_name": req.tool_name,
            "input_data": req.input_data,
            "timeout": req.timeout,
        }
        for req in requests
    ]

    results = await engine.execute_batch(executions, concurrent=concurrent)

    return [
        ToolExecuteResponse(
            success=result.success,
            data=result.data.model_dump() if result.data else None,
            error=result.error,
            error_type=result.error_type,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata,
        )
        for result in results
    ]


@router.get("/{tool_name}/history")
async def get_tool_execution_history(
    tool_name: str,
    current_user: ActiveUser,
    limit: int = 100,
    engine: ToolExecutionEngine = Depends(get_tool_engine),
) -> Dict[str, Any]:
    """Get execution history for a tool.

    Args:
        tool_name: Tool name.
        current_user: Current authenticated user.
        limit: Maximum number of records.
        engine: Tool execution engine.

    Returns:
        Dict: Execution history.
    """
    history = engine.get_execution_history(tool_name=tool_name, limit=limit)
    return {"tool_name": tool_name, "history": history, "count": len(history)}


@router.get("/stats")
async def get_tool_statistics(
    current_user: ActiveUser,
    registry: ToolRegistry = Depends(get_tool_registry),
    engine: ToolExecutionEngine = Depends(get_tool_engine),
) -> Dict[str, Any]:
    """Get tool usage statistics.

    Args:
        current_user: Current authenticated user.
        registry: Tool registry.
        engine: Tool execution engine.

    Returns:
        Dict: Statistics.
    """
    tools = registry.list_all()

    # Calculate statistics
    by_category = {}
    total_executions = 0

    for tool in tools:
        category = tool.get("category", "unknown")
        if category not in by_category:
            by_category[category] = {"count": 0, "executions": 0}
        by_category[category]["count"] += 1
        by_category[category]["executions"] += tool.get("execution_count", 0)
        total_executions += tool.get("execution_count", 0)

    return {
        "total_tools": len(tools),
        "total_executions": total_executions,
        "by_category": by_category,
        "recent_history": engine.get_execution_history(limit=10),
    }
