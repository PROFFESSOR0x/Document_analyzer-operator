"""Agent type implementations module."""

# Cognitive Agents
from app.agents.types.cognitive.base import BaseCognitiveAgent
from app.agents.types.cognitive.research import ResearchAgent
from app.agents.types.cognitive.document_intelligence import DocumentIntelligenceAgent
from app.agents.types.cognitive.knowledge_synthesis import KnowledgeSynthesisAgent

# Content Agents
from app.agents.types.content.base import BaseContentAgent
from app.agents.types.content.architect import ContentArchitectAgent
from app.agents.types.content.writing import WritingAgent
from app.agents.types.content.editing import EditingAgent

# Engineering Agents
from app.agents.types.engineering.base import BaseEngineeringAgent
from app.agents.types.engineering.architecture_analyst import ArchitectureAnalystAgent
from app.agents.types.engineering.technology_selector import TechnologySelectorAgent
from app.agents.types.engineering.debate_moderator import DebateModeratorAgent

# Programming Agents
from app.agents.types.programming.base import BaseProgrammingAgent
from app.agents.types.programming.code_generator import CodeGeneratorAgent
from app.agents.types.programming.code_reviewer import CodeReviewerAgent
from app.agents.types.programming.debugger import DebuggerAgent

# Operational Agents
from app.agents.types.operational.base import BaseOperationalAgent
from app.agents.types.operational.workflow_executor import WorkflowExecutorAgent
from app.agents.types.operational.file_operations import FileOperationsAgent
from app.agents.types.operational.automation import AutomationAgent

# Validation Agents
from app.agents.types.validation.base import BaseValidationAgent
from app.agents.types.validation.output_validator import OutputValidatorAgent
from app.agents.types.validation.consistency_checker import ConsistencyCheckerAgent
from app.agents.types.validation.fact_verifier import FactVerifierAgent

__all__ = [
    # Cognitive
    "BaseCognitiveAgent",
    "ResearchAgent",
    "DocumentIntelligenceAgent",
    "KnowledgeSynthesisAgent",
    # Content
    "BaseContentAgent",
    "ContentArchitectAgent",
    "WritingAgent",
    "EditingAgent",
    # Engineering
    "BaseEngineeringAgent",
    "ArchitectureAnalystAgent",
    "TechnologySelectorAgent",
    "DebateModeratorAgent",
    # Programming
    "BaseProgrammingAgent",
    "CodeGeneratorAgent",
    "CodeReviewerAgent",
    "DebuggerAgent",
    # Operational
    "BaseOperationalAgent",
    "WorkflowExecutorAgent",
    "FileOperationsAgent",
    "AutomationAgent",
    # Validation
    "BaseValidationAgent",
    "OutputValidatorAgent",
    "ConsistencyCheckerAgent",
    "FactVerifierAgent",
]
