# Agent Framework Core

Comprehensive agent framework for the Document-Analyzer-Operator Platform supporting dynamic agent creation, registration, and execution.

## Overview

The Agent Framework Core provides:

- **Base Agent System**: Abstract base classes with lifecycle management, state management, and task execution
- **Agent Registry**: Type registration, instance management, and capability-based discovery
- **Agent Communication Protocol**: Message format, routing, and event publishing/subscribing
- **Agent Types**: Pre-built agent categories (Cognitive, Content, Engineering, Programming, Operational, Validation)
- **Dynamic Agent Creation**: Factory pattern with templates and configuration validation
- **Agent Orchestration**: Task assignment, load balancing, and scaling

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Framework Core                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Base Agent    │  │    Registry     │  │  Orchestration  │  │
│  │                 │  │                 │  │                 │  │
│  │ - Lifecycle     │  │ - Type Mgmt     │  │ - Load Balance  │  │
│  │ - State Mgmt    │  │ - Discovery     │  │ - Task Assign   │  │
│  │ - Messaging     │  │ - Health        │  │ - Scaling       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        Agent Types                               │
├────────────┬────────────┬────────────┬────────────┬─────────────┤
│ Cognitive  │  Content   │ Engineering│ Programming│ Operational │
│            │            │            │            │             │
│ - Research │ - Architect│ - Analyst  │ - Generator│ - Workflow  │
│ - Doc Intel│ - Writer   │ - Selector │ - Reviewer │ - Files     │
│ - Synthesis│ - Editor   │ - Debater  │ - Debugger │ - Automation│
└────────────┴────────────┴────────────┴────────────┴─────────────┘
```

## Quick Start

### Creating a Custom Agent

```python
from app.agents.core.base import BaseAgent
from typing import Dict, Any

class MyCustomAgent(BaseAgent):
    """Custom agent implementation."""

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task."""
        # Your task execution logic here
        return {"result": "success"}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "category": "custom",
            "skills": ["skill1", "skill2"],
        }

# Usage
agent = MyCustomAgent("agent-1", "MyAgent", "custom")
await agent.initialize()
await agent.start()
result = await agent.execute({"type": "my_task", "data": "..."})
```

### Using the Registry

```python
from app.agents.registry.agent_registry import AgentRegistry

registry = AgentRegistry()

# Register agent type
registry.register_type(
    type_name="my_agent",
    agent_class=MyCustomAgent,
    description="My custom agent",
    capabilities={"skill1": "Description"},
)

# Create instance
agent = registry.create_instance(
    type_name="my_agent",
    agent_id="my-agent-1",
    name="My Agent",
    config={"key": "value"},
)

# Register instance
registry.register_instance(agent)
```

### Using the Orchestrator

```python
from app.agents.orchestration.orchestrator import AgentOrchestrator
from app.agents.orchestration.task_assigner import Task

orchestrator = AgentOrchestrator()
await orchestrator.initialize()

# Register agent type
orchestrator.register_agent_type("my_agent", MyCustomAgent)

# Create and start agent
agent = orchestrator.create_agent("my_agent", name="MyAgent")
await orchestrator.start_agent(agent.agent_id)

# Submit task
task = Task(
    type="my_task",
    payload={"data": "..."},
    timeout_seconds=60.0,
)
await orchestrator.submit_task(task)

# Shutdown
await orchestrator.shutdown()
```

## Agent Lifecycle

```
CREATED → INITIALIZED → STARTED → RUNNING → STOPPED → TERMINATED
                              ↓
                           PAUSED
                              ↓
                          RESUMED
```

### State Transitions

| From State | To State | Method |
|------------|----------|--------|
| CREATED | INITIALIZING | `initialize()` |
| INITIALIZING | IDLE | (auto on success) |
| IDLE | RUNNING | `start()` or `execute()` |
| RUNNING | PAUSED | `pause()` |
| PAUSED | RUNNING | `resume()` |
| RUNNING | STOPPED | `stop()` |
| STOPPED | TERMINATED | `terminate()` |

## Agent Communication Protocol

### Message Types

- **RequestMessage**: Request expecting a response
- **ResponseMessage**: Response to a request
- **EventMessage**: One-way event notification
- **CommandMessage**: Command to execute
- **ResultMessage**: Result of command execution
- **ErrorMessage**: Error notification

### Message Priority

- **CRITICAL (3)**: Processed immediately
- **HIGH (2)**: High priority
- **NORMAL (1)**: Default priority
- **LOW (0)**: Low priority

### Example: Sending Messages

```python
# Send request
response = await agent.send_request(
    receiver_id="target-agent",
    payload={"query": "data"},
    timeout_seconds=30.0,
)

# Send event
await agent.send_event(
    event_name="task_completed",
    payload={"task_id": "123"},
    broadcast=True,
)

# Send command
result = await agent.send_command(
    receiver_id="worker-agent",
    command="process",
    args=["arg1"],
    kwargs={"key": "value"},
)
```

## Agent Types

### Cognitive Agents

For analysis and reasoning tasks:

- **BaseCognitiveAgent**: Base for cognitive agents
- **ResearchAgent**: Web research and information gathering
- **DocumentIntelligenceAgent**: Document parsing and analysis
- **KnowledgeSynthesisAgent**: Knowledge integration

### Content Agents

For content creation tasks:

- **BaseContentAgent**: Base for content agents
- **ContentArchitectAgent**: Content structure planning
- **WritingAgent**: Content generation
- **EditingAgent**: Content refinement

### Engineering Agents

For technical decision making:

- **BaseEngineeringAgent**: Base for engineering agents
- **ArchitectureAnalystAgent**: System analysis
- **TechnologySelectorAgent**: Tech stack selection
- **DebateModeratorAgent**: Technical debate coordination

### Programming Agents

For code-related tasks:

- **BaseProgrammingAgent**: Base for programming agents
- **CodeGeneratorAgent**: Code creation
- **CodeReviewerAgent**: Code analysis
- **DebuggerAgent**: Bug fixing

### Operational Agents

For task execution:

- **BaseOperationalAgent**: Base for operational agents
- **WorkflowExecutorAgent**: Workflow execution
- **FileOperationsAgent**: File management
- **AutomationAgent**: Task automation

### Validation Agents

For quality assurance:

- **BaseValidationAgent**: Base for validation agents
- **OutputValidatorAgent**: Output validation
- **ConsistencyCheckerAgent**: Consistency verification
- **FactVerifierAgent**: Fact checking

## Load Balancing Strategies

- **ROUND_ROBIN**: Distribute evenly across agents
- **LEAST_BUSY**: Send to agent with fewest tasks
- **FASTEST**: Send to agent with best performance
- **CAPABILITY_BASED**: Match task requirements to agent skills
- **WEIGHTED**: Distribute based on agent weights

## API Endpoints

### Agent Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/agent-management/` | List agents |
| GET | `/api/v1/agent-management/{id}` | Get agent |
| GET | `/api/v1/agent-management/{id}/info` | Get agent info |
| POST | `/api/v1/agent-management/` | Create agent |
| PATCH | `/api/v1/agent-management/{id}` | Update agent |
| DELETE | `/api/v1/agent-management/{id}` | Delete agent |
| POST | `/api/v1/agent-management/{id}/start` | Start agent |
| POST | `/api/v1/agent-management/{id}/stop` | Stop agent |
| GET | `/api/v1/agent-management/{id}/metrics` | Get metrics |
| WS | `/api/v1/agent-management/ws/{id}` | WebSocket updates |

## Database Models

### Agent

Core agent instance data with relationships to sessions and metrics.

### AgentType

Agent type definitions with capabilities and default configurations.

### AgentSession

Tracks agent execution sessions with context and metadata.

### AgentMetric

Stores performance metrics for monitoring and analysis.

## Testing

Run tests with pytest:

```bash
cd backend
pytest tests/test_agents/ -v
```

### Test Coverage

- `test_base_agent.py`: Base agent functionality
- `test_registry.py`: Agent registry operations
- `test_orchestrator.py`: Orchestrator and load balancing

## Integration with Backend

The agent framework integrates with the existing backend through:

1. **Database Models**: Extended agent models with sessions and metrics
2. **API Routes**: New `/agent-management` endpoints
3. **Services**: `AgentService` for CRUD operations
4. **WebSocket**: Real-time agent status updates
5. **Events**: Integration with existing event system

## Best Practices

1. **Always initialize agents** before starting them
2. **Handle errors gracefully** using the built-in error hierarchy
3. **Use telemetry** to monitor agent performance
4. **Implement proper cleanup** in `_on_terminate()`
5. **Use async/await** consistently throughout
6. **Register capabilities** for capability-based routing
7. **Configure timeouts** for long-running tasks
8. **Monitor health** using the orchestrator's health checks

## Known Limitations

1. **Message persistence**: Messages are not persisted by default
2. **Distributed agents**: Framework assumes single-process deployment
3. **LLM integration**: Agent implementations are placeholders for LLM integration
4. **Resource limits**: No built-in resource quota management

## TODOs

- [ ] Add message persistence layer
- [ ] Implement distributed agent support
- [ ] Add LLM provider integration
- [ ] Implement resource quota management
- [ ] Add agent versioning and migration
- [ ] Implement agent templates library
- [ ] Add comprehensive monitoring dashboard
- [ ] Implement agent collaboration patterns
- [ ] Add retry policies configuration
- [ ] Implement circuit breaker pattern

## File Structure

```
backend/app/agents/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base.py           # Base agent class
│   ├── states.py         # State management
│   ├── messages.py       # Communication protocol
│   ├── errors.py         # Error hierarchy
│   └── telemetry.py      # Metrics and telemetry
├── registry/
│   ├── __init__.py
│   ├── agent_registry.py # Type and instance registry
│   └── agent_factory.py  # Factory pattern
├── orchestration/
│   ├── __init__.py
│   ├── orchestrator.py   # Main orchestrator
│   ├── load_balancer.py  # Load balancing
│   └── task_assigner.py  # Task assignment
└── types/
    ├── __init__.py
    ├── cognitive/        # Cognitive agents
    ├── content/          # Content agents
    ├── engineering/      # Engineering agents
    ├── programming/      # Programming agents
    ├── operational/      # Operational agents
    └── validation/       # Validation agents
```

## License

Part of the Document-Analyzer-Operator Platform.
