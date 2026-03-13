"""Agent factory for dynamic agent creation."""

from typing import Dict, Any, Optional, Type, List
from uuid import uuid4
import logging

from app.agents.core.base import BaseAgent
from app.agents.core.errors import AgentRegistrationError, AgentConfigurationError
from app.agents.registry.agent_registry import AgentRegistry


class AgentTemplate:
    """Template for creating agents with predefined configurations.

    Attributes:
        name: Template name.
        agent_type: Type of agent.
        description: Template description.
        default_config: Default configuration.
        version: Template version.
    """

    def __init__(
        self,
        name: str,
        agent_type: str,
        description: str = "",
        default_config: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
    ) -> None:
        """Initialize agent template.

        Args:
            name: Template name.
            agent_type: Type of agent.
            description: Template description.
            default_config: Default configuration.
            version: Template version.
        """
        self.name = name
        self.agent_type = agent_type
        self.description = description
        self.default_config = default_config or {}
        self.version = version

    def create_agent(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create agent creation parameters.

        Args:
            agent_id: Optional agent ID (generated if not provided).
            name: Optional agent name (template name if not provided).
            config_override: Optional configuration overrides.

        Returns:
            Dict: Agent creation parameters.
        """
        config = {**self.default_config, **(config_override or {})}
        return {
            "agent_id": agent_id or str(uuid4()),
            "name": name or self.name,
            "agent_type": self.agent_type,
            "config": config,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary.

        Returns:
            Dict: Template data.
        """
        return {
            "name": self.name,
            "agent_type": self.agent_type,
            "description": self.description,
            "default_config": self.default_config,
            "version": self.version,
        }


class AgentFactory:
    """Factory for creating and managing agent instances.

    This class provides:
    - Agent factory pattern implementation
    - Agent template system
    - Agent configuration validation
    - Agent versioning

    Usage:
        factory = AgentFactory(registry)
        factory.register_template("researcher", "research_agent", {...})
        agent = factory.create("researcher", name="my-researcher")
    """

    def __init__(self, registry: AgentRegistry) -> None:
        """Initialize agent factory.

        Args:
            registry: Agent registry instance.
        """
        self._registry = registry
        self._templates: Dict[str, AgentTemplate] = {}
        self._logger = logging.getLogger("agent.factory")

    def register_template(
        self,
        name: str,
        agent_type: str,
        description: str = "",
        default_config: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
    ) -> None:
        """Register an agent template.

        Args:
            name: Template name.
            agent_type: Type of agent.
            description: Template description.
            default_config: Default configuration.
            version: Template version.

        Raises:
            AgentRegistrationError: If template already exists.
        """
        if name in self._templates:
            raise AgentRegistrationError(
                f"Template '{name}' is already registered",
                agent_type=name,
            )

        template = AgentTemplate(
            name=name,
            agent_type=agent_type,
            description=description,
            default_config=default_config or {},
            version=version,
        )
        self._templates[name] = template
        self._logger.info(f"Registered agent template: {name}")

    def unregister_template(self, name: str) -> None:
        """Unregister an agent template.

        Args:
            name: Template name.

        Raises:
            AgentRegistrationError: If template not found.
        """
        if name not in self._templates:
            raise AgentRegistrationError(
                f"Template '{name}' not found",
                agent_type=name,
            )

        del self._templates[name]
        self._logger.info(f"Unregistered agent template: {name}")

    def get_template(self, name: str) -> AgentTemplate:
        """Get an agent template.

        Args:
            name: Template name.

        Returns:
            AgentTemplate: Template instance.

        Raises:
            AgentRegistrationError: If template not found.
        """
        if name not in self._templates:
            raise AgentRegistrationError(
                f"Template '{name}' not found",
                agent_type=name,
            )
        return self._templates[name]

    def list_templates(self) -> List[AgentTemplate]:
        """List all registered templates.

        Returns:
            List[AgentTemplate]: List of templates.
        """
        return list(self._templates.values())

    def create(
        self,
        template_name: str,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        config_override: Optional[Dict[str, Any]] = None,
        initialize: bool = True,
    ) -> BaseAgent:
        """Create an agent from a template.

        Args:
            template_name: Name of the template.
            agent_id: Optional agent ID.
            name: Optional agent name.
            config_override: Optional configuration overrides.
            initialize: Whether to initialize the agent.

        Returns:
            BaseAgent: Created agent instance.

        Raises:
            AgentRegistrationError: If template not found.
            AgentConfigurationError: If configuration is invalid.
        """
        template = self.get_template(template_name)
        params = template.create_agent(
            agent_id=agent_id,
            name=name,
            config_override=config_override,
        )

        # Validate configuration
        self._validate_config(params["agent_type"], params["config"])

        # Create agent instance
        agent = self._registry.create_instance(
            type_name=params["agent_type"],
            agent_id=params["agent_id"],
            name=params["name"],
            config=params["config"],
        )

        self._logger.info(f"Created agent from template {template_name}: {agent.name}")

        if initialize:
            import asyncio
            try:
                asyncio.get_event_loop().run_until_complete(agent.initialize())
            except RuntimeError:
                # No event loop, will be initialized later
                pass

        return agent

    def create_custom(
        self,
        agent_type: str,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        initialize: bool = True,
    ) -> BaseAgent:
        """Create a custom agent without a template.

        Args:
            agent_type: Type of agent.
            agent_id: Optional agent ID.
            name: Optional agent name.
            config: Optional configuration.
            initialize: Whether to initialize the agent.

        Returns:
            BaseAgent: Created agent instance.

        Raises:
            AgentRegistrationError: If agent type not found.
            AgentConfigurationError: If configuration is invalid.
        """
        agent_id = agent_id or str(uuid4())
        name = name or f"{agent_type}-{agent_id[:8]}"
        config = config or {}

        # Validate configuration
        self._validate_config(agent_type, config)

        # Create agent instance
        agent = self._registry.create_instance(
            type_name=agent_type,
            agent_id=agent_id,
            name=name,
            config=config,
        )

        self._logger.info(f"Created custom agent: {agent.name} ({agent_id})")

        if initialize:
            import asyncio
            try:
                asyncio.get_event_loop().run_until_complete(agent.initialize())
            except RuntimeError:
                # No event loop, will be initialized later
                pass

        return agent

    def _validate_config(self, agent_type: str, config: Dict[str, Any]) -> None:
        """Validate agent configuration.

        Args:
            agent_type: Type of agent.
            config: Configuration to validate.

        Raises:
            AgentConfigurationError: If configuration is invalid.
        """
        try:
            registration = self._registry.get_type(agent_type)
        except AgentRegistrationError:
            # Type not found in registry, skip validation
            return

        schema = registration.config_schema
        if not schema:
            return

        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in config:
                raise AgentConfigurationError(
                    f"Missing required config field: {field}",
                    config_key=field,
                )

        # Check field types
        properties = schema.get("properties", {})
        for key, value in config.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    raise AgentConfigurationError(
                        f"Config field '{key}' must be a string",
                        config_key=key,
                    )
                elif expected_type == "integer" and not isinstance(value, int):
                    raise AgentConfigurationError(
                        f"Config field '{key}' must be an integer",
                        config_key=key,
                    )
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise AgentConfigurationError(
                        f"Config field '{key}' must be a boolean",
                        config_key=key,
                    )

    def get_version(self, template_name: str) -> str:
        """Get template version.

        Args:
            template_name: Template name.

        Returns:
            str: Version string.

        Raises:
            AgentRegistrationError: If template not found.
        """
        template = self.get_template(template_name)
        return template.version

    def to_dict(self) -> Dict[str, Any]:
        """Convert factory to dictionary.

        Returns:
            Dict: Factory data.
        """
        return {
            "templates": {
                name: template.to_dict()
                for name, template in self._templates.items()
            },
            "total_templates": len(self._templates),
        }
