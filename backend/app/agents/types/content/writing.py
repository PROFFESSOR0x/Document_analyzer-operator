"""Writing agent."""

from typing import Dict, Any, Optional
import logging

from app.agents.types.content.base import BaseContentAgent


class WritingAgent(BaseContentAgent):
    """Agent for content generation."""

    def __init__(
        self,
        agent_id: str,
        name: str = "Writer",
        agent_type: str = "writing",
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(agent_id, name, agent_type, config or {})
        self.style = self.config.get("style", "professional")

    def get_capabilities(self) -> Dict[str, Any]:
        base_caps = super().get_capabilities()
        return {
            **base_caps,
            "skills": ["content_generation", "creative_writing", "technical_writing"],
            "styles": [self.style],
        }

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {"content": "", "word_count": 0}


__all__ = ["WritingAgent"]
