"""Session memory management for short-term conversation context."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from collections import deque
import logging
import hashlib
import json

from app.core.settings import get_settings

settings = get_settings()


class MemoryMessage(BaseModel):
    """Memory message model."""

    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionContext(BaseModel):
    """Session context model."""

    session_id: str
    user_id: str
    workspace_id: Optional[str] = None
    messages: List[MemoryMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    token_count: int = 0


class CompressedMemory(BaseModel):
    """Compressed memory summary."""

    summary: str
    key_points: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    compressed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionMemoryManager:
    """Manager for short-term session memory.

    This class provides:
    - Context window management
    - Memory compression
    - Memory retrieval
    - Token counting
    """

    def __init__(
        self,
        max_messages: int = 100,
        max_tokens: int = 8000,
        compression_threshold: float = 0.8,
    ) -> None:
        """Initialize session memory manager.

        Args:
            max_messages: Maximum number of messages to keep.
            max_tokens: Maximum token count before compression.
            compression_threshold: Threshold for triggering compression.
        """
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold

        self._sessions: Dict[str, SessionContext] = {}
        self._compressed_memories: Dict[str, CompressedMemory] = {}
        self._logger = logging.getLogger("knowledge.session_memory")

    def create_session(
        self,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionContext:
        """Create a new session.

        Args:
            session_id: Session identifier.
            user_id: User identifier.
            workspace_id: Optional workspace identifier.
            metadata: Optional session metadata.

        Returns:
            SessionContext: Created session.
        """
        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
            metadata=metadata or {},
        )

        self._sessions[session_id] = session
        self._logger.info(f"Created session {session_id} for user {user_id}")

        return session

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get a session by ID.

        Args:
            session_id: Session identifier.

        Returns:
            Optional[SessionContext]: Session or None if not found.
        """
        return self._sessions.get(session_id)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[SessionContext]:
        """Add a message to session.

        Args:
            session_id: Session identifier.
            role: Message role (user, assistant, system).
            content: Message content.
            metadata: Optional message metadata.

        Returns:
            Optional[SessionContext]: Updated session or None if not found.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        message = MemoryMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        session.messages.append(message)
        session.updated_at = datetime.now(timezone.utc)

        # Update token count
        session.token_count = self._estimate_tokens(content)

        # Manage context window
        self._manage_context_window(session)

        # Check if compression needed
        if session.token_count > self.max_tokens * self.compression_threshold:
            self._logger.info(f"Session {session_id} approaching token limit, compression recommended")

        return session

    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        include_compressed: bool = True,
    ) -> List[MemoryMessage]:
        """Get messages from session.

        Args:
            session_id: Session identifier.
            limit: Optional message limit.
            include_compressed: Whether to include compressed memory.

        Returns:
            List[MemoryMessage]: Messages.
        """
        session = self._sessions.get(session_id)
        if not session:
            return []

        messages = session.messages[-limit:] if limit else session.messages

        # Prepend compressed memory summary if available
        if include_compressed and session_id in self._compressed_memories:
            compressed = self._compressed_memories[session_id]
            summary_message = MemoryMessage(
                role="system",
                content=f"Previous conversation summary: {compressed.summary}",
                metadata={"compressed": True, "key_points": compressed.key_points},
            )
            messages = [summary_message] + messages

        return messages

    def compress_memory(
        self,
        session_id: str,
        compression_model: Optional[Any] = None,
    ) -> Optional[CompressedMemory]:
        """Compress session memory.

        Args:
            session_id: Session identifier.
            compression_model: Optional model for compression.

        Returns:
            Optional[CompressedMemory]: Compressed memory or None.
        """
        session = self._sessions.get(session_id)
        if not session or not session.messages:
            return None

        # Extract key information
        messages_text = "\n".join([m.content for m in session.messages[-50:]])

        # Simple extractive compression (can be enhanced with LLM)
        compressed = self._simple_compress(messages_text)

        self._compressed_memories[session_id] = compressed

        # Clear old messages after compression
        session.messages = session.messages[-10:]  # Keep last 10 messages
        session.token_count = self._estimate_tokens(messages_text[:500])

        self._logger.info(f"Compressed memory for session {session_id}")

        return compressed

    def _simple_compress(self, text: str) -> CompressedMemory:
        """Simple text compression.

        Args:
            text: Text to compress.

        Returns:
            CompressedMemory: Compressed memory.
        """
        # Extract first and last sentences as summary
        sentences = text.split(".")
        summary_parts = []

        if len(sentences) > 0:
            summary_parts.append(sentences[0].strip() + ".")
        if len(sentences) > 1:
            summary_parts.append(sentences[-1].strip() + ".")

        summary = " ".join(summary_parts)[:500]

        # Extract potential key points (lines with numbers or bullets)
        lines = text.split("\n")
        key_points = [
            line.strip()
            for line in lines
            if line.strip().startswith(("-", "*", "•", "1.", "2.", "3."))
        ][:10]

        # Extract potential entities (capitalized words)
        import re
        entities = list(set(re.findall(r"\b[A-Z][a-z]+\b", text)))[:20]

        return CompressedMemory(
            summary=summary,
            key_points=key_points,
            entities=entities,
            topics=[],
        )

    def _manage_context_window(self, session: SessionContext) -> None:
        """Manage context window size.

        Args:
            session: Session to manage.
        """
        # Remove oldest messages if exceeding max
        while len(session.messages) > self.max_messages:
            session.messages.pop(0)

        # Recalculate token count
        total_tokens = sum(
            self._estimate_tokens(m.content)
            for m in session.messages
        )
        session.token_count = total_tokens

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Args:
            text: Input text.

        Returns:
            int: Estimated token count.
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def clear_session(self, session_id: str) -> bool:
        """Clear a session.

        Args:
            session_id: Session identifier.

        Returns:
            bool: True if cleared.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._compressed_memories:
            del self._compressed_memories[session_id]

        self._logger.info(f"Cleared session {session_id}")
        return True

    def get_session_ids(self, user_id: Optional[str] = None) -> List[str]:
        """Get session IDs.

        Args:
            user_id: Optional user ID filter.

        Returns:
            List[str]: Session IDs.
        """
        if user_id:
            return [
                s.session_id
                for s in self._sessions.values()
                if s.user_id == user_id
            ]
        return list(self._sessions.keys())

    def get_context_for_llm(
        self,
        session_id: str,
        max_tokens: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """Get context formatted for LLM.

        Args:
            session_id: Session identifier.
            max_tokens: Optional token limit.

        Returns:
            List[Dict]: Messages formatted for LLM.
        """
        messages = self.get_messages(session_id, include_compressed=True)

        if max_tokens:
            # Truncate to fit token limit
            truncated = []
            current_tokens = 0

            for msg in reversed(messages):
                msg_tokens = self._estimate_tokens(msg.content)
                if current_tokens + msg_tokens > max_tokens:
                    break
                truncated.insert(0, msg)
                current_tokens += msg_tokens

            messages = truncated

        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
