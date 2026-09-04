"""
Short-Term Memory Module

Handles short-term memory for conversation context.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .models import ShortTermMemoryItem

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Handles short-term memory for conversation context.
    """

    def __init__(self, max_items: int = 20, expiration_minutes: int = 30):
        self.max_items = max_items
        self.expiration_minutes = expiration_minutes
        self.memory_items: List[ShortTermMemoryItem] = []

    def add_item(
        self,
        content: Any,
        session_id: str,
        turn_number: int,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> None:
        """
        Add an item to short-term memory.

        Args:
            content: The content to store
            session_id: The session ID
            turn_number: The turn number in the conversation
            metadata: Additional metadata
            importance: Importance score (0.0 to 1.0)
        """
        if metadata is None:
            metadata = {}

        item = ShortTermMemoryItem(
            content=content,
            session_id=session_id,
            turn_number=turn_number,
            metadata=metadata,
            importance=importance
        )

        self.memory_items.append(item)
        logger.info(f"Added short-term memory item: {item.id}")

        # Enforce max items limit
        if len(self.memory_items) > self.max_items:
            # Remove oldest items first
            self.memory_items.sort(key=lambda x: x.timestamp)
            self.memory_items = self.memory_items[-self.max_items:]

    def get_recent_items(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ShortTermMemoryItem]:
        """
        Get recent items from short-term memory for a session.

        Args:
            session_id: The session ID to filter by
            limit: Maximum number of items to return

        Returns:
            List of recent memory items
        """
        # Filter by session ID and sort by timestamp (newest first)
        filtered = [
            item for item in self.memory_items
            if item.session_id == session_id
        ]
        filtered.sort(key=lambda x: x.timestamp, reverse=True)

        # Remove expired items
        now = datetime.now()
        expiration_time = now - timedelta(minutes=self.expiration_minutes)
        filtered = [
            item for item in filtered if item.timestamp > expiration_time
        ]

        return filtered[:limit]

    def clear_session_memory(self, session_id: str) -> None:
        """
        Clear all memory items for a session.

        Args:
            session_id: The session ID to clear
        """
        self.memory_items = [
            item for item in self.memory_items
            if item.session_id != session_id
        ]
        logger.info(f"Cleared short-term memory for session: {session_id}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the short-term memory."""
        now = datetime.now()
        expiration_time = now - timedelta(minutes=self.expiration_minutes)

        active_items = [
            item for item in self.memory_items
            if item.timestamp > expiration_time
        ]

        return {
            "total_items": len(self.memory_items),
            "active_items": len(active_items),
            "max_items": self.max_items,
            "expiration_minutes": self.expiration_minutes
        }