"""
Long-Term Memory Module

Handles long-term memory for persistent knowledge storage.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging
import json
from sqlalchemy import create_engine, Column, String, Text, Float, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .models import LongTermMemoryItem

logger = logging.getLogger(__name__)

Base = declarative_base()


class LongTermMemoryDB(Base):
    """SQLAlchemy model for long-term memory."""
    __tablename__ = "long_term_memory"

    id = Column(String, primary_key=True)
    content = Column(Text)
    timestamp = Column(DateTime)
    item_metadata = Column("metadata", Text)  # JSON string
    importance = Column(Float)
    category = Column(String)
    tags = Column(Text)  # Comma-separated string
    source = Column(String)
    access_count = Column(Integer)
    last_accessed = Column(DateTime)

    def to_memory_item(self) -> LongTermMemoryItem:
        """Convert to MemoryItem."""
        return LongTermMemoryItem(
            id=self.id,
            content=json.loads(self.content),
            timestamp=self.timestamp,
            metadata=json.loads(self.item_metadata) if self.item_metadata else {},
            importance=self.importance,
            category=self.category,
            tags=self.tags.split(",") if self.tags else [],
            source=self.source,
            access_count=self.access_count,
            last_accessed=self.last_accessed
        )

    @classmethod
    def from_memory_item(cls, item: LongTermMemoryItem) -> "LongTermMemoryDB":
        """Create from MemoryItem."""
        return cls(
            id=item.id,
            content=json.dumps(item.content),
            timestamp=item.timestamp,
            item_metadata=json.dumps(item.metadata),
            importance=item.importance,
            category=item.category,
            tags=",".join(item.tags),
            source=item.source,
            access_count=item.access_count,
            last_accessed=item.last_accessed
        )


class LongTermMemory:
    """
    Handles long-term memory for persistent knowledge storage.
    """

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_item(
        self,
        content: Any,
        category: str = "general",
        tags: Optional[List[str]] = None,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> LongTermMemoryItem:
        """
        Add an item to long-term memory.

        Args:
            content: The content to store
            category: Category of the memory item
            tags: List of tags
            source: Source of the information
            metadata: Additional metadata
            importance: Importance score (0.0 to 1.0)

        Returns:
            The created memory item
        """
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}

        item = LongTermMemoryItem(
            content=content,
            category=category,
            tags=tags,
            source=source,
            metadata=metadata,
            importance=importance
        )

        db_item = LongTermMemoryDB.from_memory_item(item)

        with self.Session() as session:
            session.add(db_item)
            session.commit()
            logger.info(f"Added long-term memory item: {item.id}")

        return item

    def get_items(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.3
    ) -> List[LongTermMemoryItem]:
        """
        Get items from long-term memory.

        Args:
            category: Filter by category
            tags: Filter by tags (must match all tags)
            limit: Maximum number of items to return
            min_importance: Minimum importance score to include

        Returns:
            List of memory items
        """
        with self.Session() as session:
            query = session.query(LongTermMemoryDB)

            if category:
                query = query.filter(LongTermMemoryDB.category == category)

            if tags:
                for tag in tags:
                    query = query.filter(LongTermMemoryDB.tags.contains(tag))

            query = query.filter(LongTermMemoryDB.importance >= min_importance)
            query = query.order_by(LongTermMemoryDB.last_accessed.desc())
            query = query.limit(limit)

            db_items = query.all()

            # Convert to MemoryItem and update access count
            items = [item.to_memory_item() for item in db_items]

            # Update access count and last accessed time
            for db_item in db_items:
                db_item.access_count += 1
                db_item.last_accessed = datetime.now()

            session.commit()

            return items

    def search_items(
        self,
        query: str,
        limit: int = 10,
        min_importance: float = 0.3
    ) -> List[LongTermMemoryItem]:
        """
        Search for items in long-term memory.

        Args:
            query: Search query
            limit: Maximum number of items to return
            min_importance: Minimum importance score to include

        Returns:
            List of matching memory items
        """
        with self.Session() as session:
            # Simple search - in practice, you'd use full-text search
            query = session.query(LongTermMemoryDB)
            query = query.filter(
                (LongTermMemoryDB.content.ilike(f"%{query}%"))
                | (LongTermMemoryDB.tags.ilike(f"%{query}%"))
                | (LongTermMemoryDB.category.ilike(f"%{query}%"))
            )
            query = query.filter(LongTermMemoryDB.importance >= min_importance)
            query = query.order_by(LongTermMemoryDB.last_accessed.desc())
            query = query.limit(limit)

            db_items = query.all()

            # Convert to MemoryItem and update access count
            items = [item.to_memory_item() for item in db_items]

            # Update access count and last accessed time
            for db_item in db_items:
                db_item.access_count += 1
                db_item.last_accessed = datetime.now()

            session.commit()

            return items

    def update_item(
        self,
        item_id: str,
        content: Optional[Any] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        importance: Optional[float] = None
    ) -> Optional[LongTermMemoryItem]:
        """
        Update an existing memory item.

        Args:
            item_id: ID of the item to update
            content: New content (optional)
            category: New category (optional)
            tags: New tags (optional)
            source: New source (optional)
            metadata: New metadata (optional)
            importance: New importance (optional)

        Returns:
            The updated memory item or None if not found
        """
        with self.Session() as session:
            db_item = session.query(LongTermMemoryDB).filter_by(id=item_id).first()

            if not db_item:
                logger.warning(f"Memory item not found: {item_id}")
                return None

            # Update fields if provided
            if content is not None:
                db_item.content = json.dumps(content)
            if category is not None:
                db_item.category = category
            if tags is not None:
                db_item.tags = ",".join(tags)
            if source is not None:
                db_item.source = source
            if metadata is not None:
                db_item.metadata = json.dumps(metadata)
            if importance is not None:
                db_item.importance = importance

            db_item.last_accessed = datetime.now()
            session.commit()

            logger.info(f"Updated long-term memory item: {item_id}")
            return db_item.to_memory_item()

    def delete_item(self, item_id: str) -> bool:
        """
        Delete a memory item.

        Args:
            item_id: ID of the item to delete

        Returns:
            True if item was deleted, False if not found
        """
        with self.Session() as session:
            db_item = session.query(LongTermMemoryDB).filter_by(id=item_id).first()

            if not db_item:
                logger.warning(f"Memory item not found: {item_id}")
                return False

            session.delete(db_item)
            session.commit()
            logger.info(f"Deleted long-term memory item: {item_id}")
            return True

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the long-term memory."""
        with self.Session() as session:
            total_items = session.query(LongTermMemoryDB).count()

            # Count items by category
            category_counts = {}
            for category, count in session.query(
                LongTermMemoryDB.category,
                func.count(LongTermMemoryDB.id)
            ).group_by(LongTermMemoryDB.category):
                category_counts[category] = count

            # Get most accessed items
            most_accessed = (
                session.query(LongTermMemoryDB)
                .order_by(LongTermMemoryDB.access_count.desc())
                .limit(5)
                .all()
            )

            return {
                "total_items": total_items,
                "categories": category_counts,
                "most_accessed": [
                    {
                        "id": item.id,
                        "category": item.category,
                        "access_count": item.access_count
                    }
                    for item in most_accessed
                ]
            }