"""
Memory Data Models

Defines the data structures used by the memory system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class MemoryItem:
    """Base class for memory items."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "importance": self.importance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5)
        )


@dataclass
class ShortTermMemoryItem(MemoryItem):
    """Item for short-term memory (conversation context)."""
    session_id: str = ""
    turn_number: int = 0


@dataclass
class LongTermMemoryItem(MemoryItem):
    """Item for long-term memory (persistent knowledge)."""
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    source: str = ""  # Where this knowledge came from
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class VectorMemoryItem(MemoryItem):
    """Item for vector memory (embeddings for similarity search)."""
    embedding: Optional[List[float]] = None
    text_content: str = ""  # Original text for embedding

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update({
            "embedding": self.embedding,
            "text_content": self.text_content
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorMemoryItem":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            embedding=data.get("embedding"),
            text_content=data.get("text_content", "")
        )