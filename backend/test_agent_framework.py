"""Test script to verify agent framework imports."""

import sys
import os
os.environ["POSTGRES_DB"] = "test_db"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"

sys.path.insert(0, ".")

def test_imports():
    """Test all agent framework imports."""
    errors = []
    
    # Core imports
    try:
        from app.agents.core.base import BaseAgent
        print("✓ BaseAgent import OK")
    except Exception as e:
        errors.append(f"BaseAgent: {e}")
    
    try:
        from app.agents.core.states import AgentState, AgentLifecycleState
        print("✓ AgentState imports OK")
    except Exception as e:
        errors.append(f"States: {e}")
    
    try:
        from app.agents.core.messages import AgentMessage, MessageType, RequestMessage
        print("✓ Message imports OK")
    except Exception as e:
        errors.append(f"Messages: {e}")
    
    try:
        from app.agents.core.errors import AgentError, AgentExecutionError
        print("✓ Error imports OK")
    except Exception as e:
        errors.append(f"Errors: {e}")
    
    try:
        from app.agents.core.telemetry import AgentTelemetry, AgentMetrics
        print("✓ Telemetry imports OK")
    except Exception as e:
        errors.append(f"Telemetry: {e}")
    
    # Registry imports
    try:
        from app.agents.registry.agent_registry import AgentRegistry
        print("✓ AgentRegistry import OK")
    except Exception as e:
        errors.append(f"Registry: {e}")
    
    try:
        from app.agents.registry.agent_factory import AgentFactory
        print("✓ AgentFactory import OK")
    except Exception as e:
        errors.append(f"Factory: {e}")
    
    # Orchestration imports
    try:
        from app.agents.orchestration.orchestrator import AgentOrchestrator
        print("✓ AgentOrchestrator import OK")
    except Exception as e:
        errors.append(f"Orchestrator: {e}")
    
    try:
        from app.agents.orchestration.load_balancer import LoadBalancer
        print("✓ LoadBalancer import OK")
    except Exception as e:
        errors.append(f"LoadBalancer: {e}")
    
    try:
        from app.agents.orchestration.task_assigner import TaskAssigner, Task
        print("✓ TaskAssigner import OK")
    except Exception as e:
        errors.append(f"TaskAssigner: {e}")
    
    # Agent type imports
    try:
        from app.agents.types.cognitive.base import BaseCognitiveAgent
        print("✓ BaseCognitiveAgent import OK")
    except Exception as e:
        errors.append(f"BaseCognitiveAgent: {e}")
    
    try:
        from app.agents.types.cognitive.research import ResearchAgent
        print("✓ ResearchAgent import OK")
    except Exception as e:
        errors.append(f"ResearchAgent: {e}")
    
    try:
        from app.agents.types.cognitive.document_intelligence import DocumentIntelligenceAgent
        print("✓ DocumentIntelligenceAgent import OK")
    except Exception as e:
        errors.append(f"DocumentIntelligenceAgent: {e}")
    
    try:
        from app.agents.types.cognitive.knowledge_synthesis import KnowledgeSynthesisAgent
        print("✓ KnowledgeSynthesisAgent import OK")
    except Exception as e:
        errors.append(f"KnowledgeSynthesisAgent: {e}")
    
    try:
        from app.agents.types.content.base import BaseContentAgent
        print("✓ BaseContentAgent import OK")
    except Exception as e:
        errors.append(f"BaseContentAgent: {e}")
    
    try:
        from app.agents.types.engineering.base import BaseEngineeringAgent
        print("✓ BaseEngineeringAgent import OK")
    except Exception as e:
        errors.append(f"BaseEngineeringAgent: {e}")
    
    try:
        from app.agents.types.programming.base import BaseProgrammingAgent
        print("✓ BaseProgrammingAgent import OK")
    except Exception as e:
        errors.append(f"BaseProgrammingAgent: {e}")
    
    try:
        from app.agents.types.operational.base import BaseOperationalAgent
        print("✓ BaseOperationalAgent import OK")
    except Exception as e:
        errors.append(f"BaseOperationalAgent: {e}")
    
    try:
        from app.agents.types.validation.base import BaseValidationAgent
        print("✓ BaseValidationAgent import OK")
    except Exception as e:
        errors.append(f"BaseValidationAgent: {e}")
    
    # Schema imports (models require DB connection)
    try:
        from app.schemas.agent import AgentCreate, AgentResponse
        print("✓ Agent schemas import OK")
    except Exception as e:
        errors.append(f"Agent schemas: {e}")
    
    try:
        from app.schemas.agent_session import AgentSessionCreate
        print("✓ AgentSession schema import OK")
    except Exception as e:
        errors.append(f"AgentSession schema: {e}")
    
    try:
        from app.schemas.agent_metric import AgentMetricCreate
        print("✓ AgentMetric schema import OK")
    except Exception as e:
        errors.append(f"AgentMetric schema: {e}")
    
    # Report
    print("\n" + "=" * 50)
    if errors:
        print(f"FAILED: {len(errors)} import errors")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("SUCCESS: All imports OK!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
