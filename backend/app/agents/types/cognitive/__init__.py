"""Cognitive agents for analysis and reasoning tasks."""

from app.agents.types.cognitive.base import BaseCognitiveAgent
from app.agents.types.cognitive.research import ResearchAgent
from app.agents.types.cognitive.document_intelligence import DocumentIntelligenceAgent
from app.agents.types.cognitive.knowledge_synthesis import KnowledgeSynthesisAgent

__all__ = [
    "BaseCognitiveAgent",
    "ResearchAgent",
    "DocumentIntelligenceAgent",
    "KnowledgeSynthesisAgent",
]
