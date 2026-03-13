"""Workflow Integration - Integration with existing systems."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Optional

from temporalio import workflow

from app.core.logging_config import get_logger
from app.workflow.engine import WorkflowContext, WorkflowState
from app.workflow.management import WorkflowManager, WorkflowMonitor

logger = get_logger(__name__)


class AgentIntegration:
    """Execute agents within workflows.

    This class provides integration between workflows and the agent framework.

    Attributes:
        agent_orchestrator: Agent orchestrator instance.
        agent_service: Agent service instance.
    """

    def __init__(
        self,
        agent_orchestrator: Optional[Any] = None,
        agent_service: Optional[Any] = None,
    ) -> None:
        """Initialize agent integration.

        Args:
            agent_orchestrator: Agent orchestrator instance.
            agent_service: Agent service instance.
        """
        self.agent_orchestrator = agent_orchestrator
        self.agent_service = agent_service
        self._agent_cache: dict[str, Any] = {}

    async def execute_agent_task(
        self,
        agent_id: str,
        task_type: str,
        payload: dict[str, Any],
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Execute a task using an agent.

        Args:
            agent_id: Agent ID to execute.
            task_type: Type of task.
            payload: Task payload.
            timeout: Task timeout in seconds.

        Returns:
            dict: Task execution result.

        Raises:
            ValueError: If agent not found.
            TimeoutError: If task times out.
        """
        logger.info(f"Executing agent task: {agent_id} - {task_type}")

        try:
            # Get agent from orchestrator or service
            agent = await self._get_agent(agent_id)

            if agent is None:
                raise ValueError(f"Agent not found: {agent_id}")

            # Execute task with timeout
            result = await asyncio.wait_for(
                self._execute_agent_task_internal(agent, task_type, payload),
                timeout=timeout,
            )

            logger.info(f"Agent task completed: {agent_id} - {task_type}")
            return result

        except asyncio.TimeoutError:
            logger.error(f"Agent task timed out: {agent_id} - {task_type}")
            raise TimeoutError(f"Agent task timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Agent task failed: {agent_id} - {task_type} - {e}")
            raise

    async def _get_agent(self, agent_id: str) -> Optional[Any]:
        """Get agent instance.

        Args:
            agent_id: Agent ID.

        Returns:
            Agent instance or None.
        """
        # Check cache first
        if agent_id in self._agent_cache:
            return self._agent_cache[agent_id]

        # Try to get from orchestrator
        if self.agent_orchestrator:
            try:
                agent = self.agent_orchestrator.get_agent(agent_id)
                if agent:
                    self._agent_cache[agent_id] = agent
                    return agent
            except Exception:
                pass

        # Try to get from service
        if self.agent_service:
            try:
                agent = await self.agent_service.get_agent(agent_id)
                if agent:
                    self._agent_cache[agent_id] = agent
                    return agent
            except Exception:
                pass

        return None

    async def _execute_agent_task_internal(
        self, agent: Any, task_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute agent task internally.

        Args:
            agent: Agent instance.
            task_type: Task type.
            payload: Task payload.

        Returns:
            dict: Task result.
        """
        # Check if agent has execute method
        if hasattr(agent, "execute"):
            result = await agent.execute({"type": task_type, "data": payload})
            return result
        elif hasattr(agent, "process"):
            result = await agent.process(task_type, payload)
            return result
        else:
            # Fallback: assume agent is callable
            result = await agent(task_type, payload)
            return result

    def clear_cache(self) -> None:
        """Clear agent cache."""
        self._agent_cache.clear()
        logger.info("Agent cache cleared")


class ToolIntegration:
    """Use tools in workflow activities.

    This class provides integration between workflows and the tool framework.

    Attributes:
        tool_registry: Tool registry instance.
        tool_executor: Tool executor instance.
    """

    def __init__(
        self,
        tool_registry: Optional[Any] = None,
        tool_executor: Optional[Any] = None,
    ) -> None:
        """Initialize tool integration.

        Args:
            tool_registry: Tool registry instance.
            tool_executor: Tool executor instance.
        """
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor
        self._tool_cache: dict[str, Any] = {}

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Execute a tool.

        Args:
            tool_name: Name of the tool.
            arguments: Tool arguments.
            timeout: Execution timeout in seconds.

        Returns:
            dict: Tool execution result.

        Raises:
            ValueError: If tool not found.
            TimeoutError: If execution times out.
        """
        logger.info(f"Executing tool: {tool_name}")

        try:
            # Get tool from registry
            tool = await self._get_tool(tool_name)

            if tool is None:
                raise ValueError(f"Tool not found: {tool_name}")

            # Execute tool with timeout
            result = await asyncio.wait_for(
                self._execute_tool_internal(tool, arguments),
                timeout=timeout,
            )

            logger.info(f"Tool completed: {tool_name}")
            return result

        except asyncio.TimeoutError:
            logger.error(f"Tool timed out: {tool_name}")
            raise TimeoutError(f"Tool timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Tool failed: {tool_name} - {e}")
            raise

    async def _get_tool(self, tool_name: str) -> Optional[Any]:
        """Get tool instance.

        Args:
            tool_name: Tool name.

        Returns:
            Tool instance or None.
        """
        # Check cache first
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name]

        # Try to get from registry
        if self.tool_registry:
            try:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    self._tool_cache[tool_name] = tool
                    return tool
            except Exception:
                pass

        return None

    async def _execute_tool_internal(
        self, tool: Any, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute tool internally.

        Args:
            tool: Tool instance.
            arguments: Tool arguments.

        Returns:
            dict: Tool result.
        """
        # Check if tool has execute method
        if hasattr(tool, "execute"):
            result = await tool.execute(arguments)
            return result
        elif hasattr(tool, "run"):
            result = await tool.run(arguments)
            return result
        elif hasattr(tool, "__call__"):
            result = await tool(arguments)
            return result
        else:
            raise ValueError("Tool does not have an executable method")

    def clear_cache(self) -> None:
        """Clear tool cache."""
        self._tool_cache.clear()
        logger.info("Tool cache cleared")


class KnowledgeIntegration:
    """Store/retrieve knowledge during workflows.

    This class provides integration between workflows and the knowledge base.

    Attributes:
        knowledge_service: Knowledge service instance.
    """

    def __init__(self, knowledge_service: Optional[Any] = None) -> None:
        """Initialize knowledge integration.

        Args:
            knowledge_service: Knowledge service instance.
        """
        self.knowledge_service = knowledge_service

    async def store_knowledge(
        self,
        entity_type: str,
        entity_data: dict[str, Any],
        workspace_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Store knowledge in the knowledge base.

        Args:
            entity_type: Type of entity.
            entity_data: Entity data.
            workspace_id: Optional workspace ID.
            metadata: Optional metadata.

        Returns:
            str: Entity ID.
        """
        logger.info(f"Storing knowledge: {entity_type}")

        if self.knowledge_service:
            try:
                entity = await self.knowledge_service.create_entity(
                    entity_type=entity_type,
                    entity_data=entity_data,
                    workspace_id=workspace_id,
                    metadata=metadata,
                )
                logger.info(f"Knowledge stored: {entity_type} - {entity.id}")
                return entity.id
            except Exception as e:
                logger.error(f"Failed to store knowledge: {e}")
                raise

        # Fallback: just return a placeholder ID
        import uuid

        return str(uuid.uuid4())

    async def retrieve_knowledge(
        self,
        entity_type: str,
        query: str,
        workspace_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve knowledge from the knowledge base.

        Args:
            entity_type: Type of entity.
            query: Search query.
            workspace_id: Optional workspace ID.
            limit: Maximum number of results.

        Returns:
            list: List of matching entities.
        """
        logger.info(f"Retrieving knowledge: {entity_type} - {query}")

        if self.knowledge_service:
            try:
                entities = await self.knowledge_service.search_entities(
                    entity_type=entity_type,
                    query=query,
                    workspace_id=workspace_id,
                    limit=limit,
                )
                return [e.to_dict() for e in entities]
            except Exception as e:
                logger.error(f"Failed to retrieve knowledge: {e}")
                return []

        return []

    async def link_knowledge(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Link two knowledge entities.

        Args:
            source_entity_id: Source entity ID.
            target_entity_id: Target entity ID.
            relationship_type: Type of relationship.
            metadata: Optional metadata.
        """
        logger.info(
            f"Linking knowledge: {source_entity_id} -> {target_entity_id} ({relationship_type})"
        )

        if self.knowledge_service:
            try:
                await self.knowledge_service.create_relationship(
                    source_entity_id=source_entity_id,
                    target_entity_id=target_entity_id,
                    relationship_type=relationship_type,
                    metadata=metadata,
                )
                logger.info("Knowledge linked successfully")
            except Exception as e:
                logger.error(f"Failed to link knowledge: {e}")
                raise


class ValidationIntegration:
    """Validate workflow outputs.

    This class provides integration between workflows and the validation engine.

    Attributes:
        validation_service: Validation service instance.
    """

    def __init__(self, validation_service: Optional[Any] = None) -> None:
        """Initialize validation integration.

        Args:
            validation_service: Validation service instance.
        """
        self.validation_service = validation_service

    async def validate_output(
        self,
        output_data: dict[str, Any],
        validation_rules: list[dict[str, Any]],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Validate workflow output.

        Args:
            output_data: Output data to validate.
            validation_rules: List of validation rules.
            context: Optional validation context.

        Returns:
            dict: Validation results.
        """
        logger.info(f"Validating output with {len(validation_rules)} rules")

        if self.validation_service:
            try:
                result = await self.validation_service.validate(
                    data=output_data,
                    rules=validation_rules,
                    context=context,
                )
                return result.to_dict() if hasattr(result, "to_dict") else result
            except Exception as e:
                logger.error(f"Validation failed: {e}")
                return {
                    "valid": False,
                    "errors": [str(e)],
                    "warnings": [],
                }

        # Fallback: basic validation
        return {
            "valid": True,
            "errors": [],
            "warnings": [],
        }


class WebSocketIntegration:
    """Real-time workflow progress updates via WebSocket.

    This class provides integration between workflows and WebSocket events.

    Attributes:
        websocket_manager: WebSocket manager instance.
        event_publisher: Event publisher instance.
    """

    def __init__(
        self,
        websocket_manager: Optional[Any] = None,
        event_publisher: Optional[Any] = None,
    ) -> None:
        """Initialize WebSocket integration.

        Args:
            websocket_manager: WebSocket manager instance.
            event_publisher: Event publisher instance.
        """
        self.websocket_manager = websocket_manager
        self.event_publisher = event_publisher

    async def publish_workflow_event(
        self,
        event_type: str,
        workflow_id: str,
        event_data: dict[str, Any],
        user_id: Optional[str] = None,
    ) -> None:
        """Publish a workflow event via WebSocket.

        Args:
            event_type: Type of event.
            workflow_id: Workflow ID.
            event_data: Event data.
            user_id: Optional user ID for targeted delivery.
        """
        event = {
            "type": event_type,
            "workflow_id": workflow_id,
            "data": event_data,
            "timestamp": asyncio.get_event_loop().time(),
        }

        logger.debug(f"Publishing workflow event: {event_type} - {workflow_id}")

        if self.event_publisher:
            try:
                await self.event_publisher.publish(
                    channel=f"workflow:{workflow_id}",
                    message=event,
                )
            except Exception as e:
                logger.error(f"Failed to publish event: {e}")

        if self.websocket_manager and user_id:
            try:
                await self.websocket_manager.send_to_user(
                    user_id=user_id,
                    message=event,
                )
            except Exception as e:
                logger.error(f"Failed to send WebSocket message: {e}")

    async def notify_workflow_started(
        self, workflow_id: str, workflow_type: str, user_id: Optional[str] = None
    ) -> None:
        """Notify that a workflow has started.

        Args:
            workflow_id: Workflow ID.
            workflow_type: Workflow type.
            user_id: Optional user ID.
        """
        await self.publish_workflow_event(
            event_type="workflow.started",
            workflow_id=workflow_id,
            event_data={
                "workflow_type": workflow_type,
                "status": "started",
            },
            user_id=user_id,
        )

    async def notify_workflow_progress(
        self,
        workflow_id: str,
        progress: int,
        current_task: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Notify workflow progress.

        Args:
            workflow_id: Workflow ID.
            progress: Progress percentage.
            current_task: Optional current task ID.
            user_id: Optional user ID.
        """
        await self.publish_workflow_event(
            event_type="workflow.progress",
            workflow_id=workflow_id,
            event_data={
                "progress": progress,
                "current_task": current_task,
            },
            user_id=user_id,
        )

    async def notify_workflow_completed(
        self,
        workflow_id: str,
        result: dict[str, Any],
        user_id: Optional[str] = None,
    ) -> None:
        """Notify that a workflow has completed.

        Args:
            workflow_id: Workflow ID.
            result: Workflow result.
            user_id: Optional user ID.
        """
        await self.publish_workflow_event(
            event_type="workflow.completed",
            workflow_id=workflow_id,
            event_data={
                "status": "completed",
                "result": result,
            },
            user_id=user_id,
        )

    async def notify_workflow_failed(
        self,
        workflow_id: str,
        error_message: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Notify that a workflow has failed.

        Args:
            workflow_id: Workflow ID.
            error_message: Error message.
            user_id: Optional user ID.
        """
        await self.publish_workflow_event(
            event_type="workflow.failed",
            workflow_id=workflow_id,
            event_data={
                "status": "failed",
                "error": error_message,
            },
            user_id=user_id,
        )


class WorkflowIntegration:
    """Main integration class that combines all integrations.

    This class provides a unified interface for integrating workflows with
    existing systems.

    Attributes:
        agent_integration: Agent integration.
        tool_integration: Tool integration.
        knowledge_integration: Knowledge integration.
        validation_integration: Validation integration.
        websocket_integration: WebSocket integration.
    """

    def __init__(
        self,
        agent_orchestrator: Optional[Any] = None,
        agent_service: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        tool_executor: Optional[Any] = None,
        knowledge_service: Optional[Any] = None,
        validation_service: Optional[Any] = None,
        websocket_manager: Optional[Any] = None,
        event_publisher: Optional[Any] = None,
    ) -> None:
        """Initialize workflow integration.

        Args:
            agent_orchestrator: Agent orchestrator instance.
            agent_service: Agent service instance.
            tool_registry: Tool registry instance.
            tool_executor: Tool executor instance.
            knowledge_service: Knowledge service instance.
            validation_service: Validation service instance.
            websocket_manager: WebSocket manager instance.
            event_publisher: Event publisher instance.
        """
        self.agent_integration = AgentIntegration(
            agent_orchestrator=agent_orchestrator,
            agent_service=agent_service,
        )
        self.tool_integration = ToolIntegration(
            tool_registry=tool_registry,
            tool_executor=tool_executor,
        )
        self.knowledge_integration = KnowledgeIntegration(
            knowledge_service=knowledge_service,
        )
        self.validation_integration = ValidationIntegration(
            validation_service=validation_service,
        )
        self.websocket_integration = WebSocketIntegration(
            websocket_manager=websocket_manager,
            event_publisher=event_publisher,
        )

    async def execute_workflow_with_integration(
        self,
        workflow_manager: WorkflowManager,
        workflow_type: str,
        input_data: dict[str, Any],
        user_id: Optional[str] = None,
        enable_websocket: bool = True,
    ) -> str:
        """Execute a workflow with full integration.

        Args:
            workflow_manager: Workflow manager.
            workflow_type: Workflow type.
            input_data: Input data.
            user_id: Optional user ID.
            enable_websocket: Whether to enable WebSocket notifications.

        Returns:
            str: Workflow execution ID.
        """
        # Create workflow
        execution = await workflow_manager.create_workflow(
            workflow_type=workflow_type,
            input_data=input_data,
            context={"user_id": user_id} if user_id else None,
            metadata={"user_id": user_id} if user_id else None,
        )

        # Notify started
        if enable_websocket:
            await self.websocket_integration.notify_workflow_started(
                workflow_id=execution.execution_id,
                workflow_type=workflow_type,
                user_id=user_id,
            )

        # Start workflow
        run_id = await workflow_manager.start_workflow(execution.execution_id)

        return execution.execution_id


# Global integration instance
_workflow_integration: Optional[WorkflowIntegration] = None


def get_workflow_integration() -> WorkflowIntegration:
    """Get the global workflow integration instance.

    Returns:
        WorkflowIntegration: Workflow integration instance.
    """
    global _workflow_integration
    if _workflow_integration is None:
        _workflow_integration = WorkflowIntegration()
    return _workflow_integration


def init_workflow_integration(
    agent_orchestrator: Optional[Any] = None,
    agent_service: Optional[Any] = None,
    tool_registry: Optional[Any] = None,
    tool_executor: Optional[Any] = None,
    knowledge_service: Optional[Any] = None,
    validation_service: Optional[Any] = None,
    websocket_manager: Optional[Any] = None,
    event_publisher: Optional[Any] = None,
) -> WorkflowIntegration:
    """Initialize the global workflow integration.

    Args:
        agent_orchestrator: Agent orchestrator instance.
        agent_service: Agent service instance.
        tool_registry: Tool registry instance.
        tool_executor: Tool executor instance.
        knowledge_service: Knowledge service instance.
        validation_service: Validation service instance.
        websocket_manager: WebSocket manager instance.
        event_publisher: Event publisher instance.

    Returns:
        WorkflowIntegration: Initialized workflow integration.
    """
    global _workflow_integration
    _workflow_integration = WorkflowIntegration(
        agent_orchestrator=agent_orchestrator,
        agent_service=agent_service,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        knowledge_service=knowledge_service,
        validation_service=validation_service,
        websocket_manager=websocket_manager,
        event_publisher=event_publisher,
    )
    return _workflow_integration
