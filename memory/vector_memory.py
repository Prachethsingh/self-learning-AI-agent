"""
Vector Memory Module

Handles vector memory for similarity search and retrieval.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import qdrant_client
from qdrant_client.models import PointStruct, Distance, VectorParams
from .models import VectorMemoryItem

logger = logging.getLogger(__name__)


class VectorMemory:
    """
    Handles vector memory for similarity search and retrieval.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6379",
        collection_name: str = "self_learning_agent",
        embedding_model: str = "all-MiniLM-L6-v2",
        vector_size: int = 384
    ):
        """
        Initialize vector memory.

        Args:
            qdrant_url: URL of the Qdrant server
            collection_name: Name of the collection to use
            embedding_model: Name of the sentence transformer model
            vector_size: Size of the embedding vectors
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_size = vector_size

        # Initialize Qdrant client
        try:
            self.client = qdrant_client.QdrantClient(url=qdrant_url, timeout=3)
            self._create_collection(collection_name)
        except Exception as e:
            logger.warning(f"Failed to connect to Qdrant at {qdrant_url}: {e}. Falling back to in-memory Qdrant.")
            self.client = qdrant_client.QdrantClient(location=":memory:")
            self._create_collection(collection_name)
        self.collection_name = collection_name

    def _create_collection(self, collection_name: str) -> None:
        """Create a collection in Qdrant if it doesn't exist."""
        try:
            self.client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' already exists")
        except Exception:
            logger.info(f"Creating collection '{collection_name}'")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    def add_item(
        self,
        text_content: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> VectorMemoryItem:
        """
        Add an item to vector memory.

        Args:
            text_content: Text content to embed
            content: The actual content to store
            metadata: Additional metadata
            importance: Importance score (0.0 to 1.0)

        Returns:
            The created memory item
        """
        if metadata is None:
            metadata = {}

        # Generate embedding
        embedding = self.embedding_model.encode(text_content)

        # Create memory item
        item = VectorMemoryItem(
            content=content,
            text_content=text_content,
            embedding=embedding.tolist(),
            metadata=metadata,
            importance=importance
        )

        # Store in Qdrant
        point = PointStruct(
            id=item.id,
            vector=embedding.tolist(),
            payload={
                "content": str(content),
                "text_content": text_content,
                "metadata": metadata,
                "importance": importance,
                "timestamp": item.timestamp.isoformat()
            }
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        logger.info(f"Added vector memory item: {item.id}")
        return item

    def search_similar(
        self,
        query: str,
        limit: int = 5,
        min_importance: float = 0.3,
        score_threshold: float = 0.5
    ) -> List[Tuple[VectorMemoryItem, float]]:
        """
        Search for similar items.

        Args:
            query: Query text to search for
            limit: Maximum number of results
            min_importance: Minimum importance score to include
            score_threshold: Minimum score threshold for results

        Returns:
            List of tuples (memory_item, score)
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)

        # Search in Qdrant (supports both modern query_points and legacy search)
        try:
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding.tolist(),
                    limit=limit,
                    score_threshold=score_threshold
                )
                search_result = getattr(response, "points", response)
            else:
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding.tolist(),
                    limit=limit,
                    score_threshold=score_threshold
                )
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            search_result = []

        # Convert results to memory items
        results = []
        for hit in search_result:
            payload = getattr(hit, "payload", {}) or {}
            item = VectorMemoryItem(
                id=str(hit.id),
                content=payload.get("content"),
                text_content=payload.get("text_content", ""),
                embedding=getattr(hit, "vector", None),
                metadata=payload.get("metadata", {}),
                importance=payload.get("importance", 0.5),
                timestamp=datetime.fromisoformat(payload["timestamp"]) if "timestamp" in payload else datetime.now()
            )
            results.append((item, getattr(hit, "score", 1.0)))

        return results

    def get_by_id(self, item_id: str) -> Optional[VectorMemoryItem]:
        """
        Get an item by ID.

        Args:
            item_id: ID of the item to retrieve

        Returns:
            The memory item or None if not found
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[item_id]
            )
            if result:
                payload = result[0].payload
                return VectorMemoryItem(
                    id=result[0].id,
                    content=payload["content"],
                    text_content=payload["text_content"],
                    embedding=result[0].vector,
                    metadata=payload.get("metadata", {}),
                    importance=payload.get("importance", 0.5),
                    timestamp=datetime.fromisoformat(payload["timestamp"])
                )
            return None
        except Exception as e:
            logger.error(f"Error retrieving item {item_id}: {e}")
            return None

    def update_item(
        self,
        item_id: str,
        text_content: Optional[str] = None,
        content: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        importance: Optional[float] = None
    ) -> Optional[VectorMemoryItem]:
        """
        Update an existing vector memory item.

        Args:
            item_id: ID of the item to update
            text_content: New text content (optional)
            content: New content (optional)
            metadata: New metadata (optional)
            importance: New importance (optional)

        Returns:
            The updated memory item or None if not found
        """
        # First get the existing item
        existing_item = self.get_by_id(item_id)
        if not existing_item:
            logger.warning(f"Vector memory item not found: {item_id}")
            return None

        # Update fields if provided
        if text_content is not None:
            existing_item.text_content = text_content
            # Re-embed if text content changed
            existing_item.embedding = self.embedding_model.encode(text_content).tolist()
        if content is not None:
            existing_item.content = content
        if metadata is not None:
            existing_item.metadata = metadata
        if importance is not None:
            existing_item.importance = importance

        # Update in Qdrant
        point = PointStruct(
            id=item_id,
            vector=existing_item.embedding,
            payload={
                "content": str(existing_item.content),
                "text_content": existing_item.text_content,
                "metadata": existing_item.metadata,
                "importance": existing_item.importance,
                "timestamp": existing_item.timestamp.isoformat()
            }
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        logger.info(f"Updated vector memory item: {item_id}")
        return existing_item

    def delete_item(self, item_id: str) -> bool:
        """
        Delete a vector memory item.

        Args:
            item_id: ID of the item to delete

        Returns:
            True if item was deleted, False if not found
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector={"ids": [item_id]}
            )
            logger.info(f"Deleted vector memory item: {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting item {item_id}: {e}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector memory."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vector_size": self.vector_size,
                "total_points": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting vector memory stats: {e}")
            return {
                "collection_name": self.collection_name,
                "vector_size": self.vector_size,
                "total_points": 0,
                "status": "error"
            }