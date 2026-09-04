"""
Memory API Routes

Endpoints for interacting with the agent's memory systems.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class MemoryItemRequest(BaseModel):
    content: Any
    category: Optional[str] = "general"
    tags: Optional[List[str]] = None
    source: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
    importance: Optional[float] = 0.5

class MemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    min_importance: Optional[float] = 0.3

class MemoryItemResponse(BaseModel):
    id: str
    content: Any
    timestamp: str
    metadata: Dict[str, Any]
    importance: float
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    access_count: Optional[int] = None
    last_accessed: Optional[str] = None


@router.post("/short-term", response_model=dict)
async def add_short_term_memory(
    request: MemoryItemRequest
):
    """
    Add an item to short-term memory.
    """
    try:
        from api.main import app

        short_term_memory = app.state.short_term_memory

        short_term_memory.add_item(
            content=request.content,
            session_id=request.metadata.get("session_id", "default") if request.metadata else "default",
            turn_number=request.metadata.get("turn_number", 0) if request.metadata else 0,
            metadata=request.metadata,
            importance=request.importance or 0.5
        )

        return {"message": "Item added to short-term memory"}

    except Exception as e:
        logger.error(f"Error adding to short-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/short-term/{session_id}")
async def get_short_term_memory(
    session_id: str,
    limit: int = 10
):
    """
    Get items from short-term memory for a session.
    """
    try:
        from api.main import app

        short_term_memory = app.state.short_term_memory
        items = short_term_memory.get_recent_items(session_id, limit)

        return {
            "session_id": session_id,
            "items": [
                {
                    "id": item.id,
                    "content": item.content,
                    "timestamp": item.timestamp.isoformat(),
                    "metadata": item.metadata,
                    "importance": item.importance,
                    "turn_number": item.turn_number
                }
                for item in items
            ]
        }

    except Exception as e:
        logger.error(f"Error getting short-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/short-term/{session_id}")
async def clear_short_term_memory(session_id: str):
    """
    Clear short-term memory for a session.
    """
    try:
        from api.main import app

        short_term_memory = app.state.short_term_memory
        short_term_memory.clear_session_memory(session_id)

        return {"message": f"Short-term memory cleared for session {session_id}"}

    except Exception as e:
        logger.error(f"Error clearing short-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/long-term", response_model=MemoryItemResponse)
async def add_long_term_memory(
    request: MemoryItemRequest
):
    """
    Add an item to long-term memory.
    """
    try:
        from api.main import app

        long_term_memory = app.state.long_term_memory
        item = long_term_memory.add_item(
            content=request.content,
            category=request.category or "general",
            tags=request.tags,
            source=request.source or "",
            metadata=request.metadata,
            importance=request.importance or 0.5
        )

        return MemoryItemResponse(
            id=item.id,
            content=item.content,
            timestamp=item.timestamp.isoformat(),
            metadata=item.metadata,
            importance=item.importance,
            category=item.category,
            tags=item.tags,
            source=item.source,
            access_count=item.access_count,
            last_accessed=item.last_accessed.isoformat() if item.last_accessed else None
        )

    except Exception as e:
        logger.error(f"Error adding to long-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/long-term")
async def get_long_term_memory(
    category: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated string
    limit: int = 10,
    min_importance: float = 0.3
):
    """
    Get items from long-term memory.
    """
    try:
        from api.main import app

        long_term_memory = app.state.long_term_memory

        tag_list = tags.split(",") if tags else None

        items = long_term_memory.get_items(
            category=category,
            tags=tag_list,
            limit=limit,
            min_importance=min_importance
        )

        return {
            "items": [
                {
                    "id": item.id,
                    "content": item.content,
                    "timestamp": item.timestamp.isoformat(),
                    "metadata": item.metadata,
                    "importance": item.importance,
                    "category": item.category,
                    "tags": item.tags,
                    "source": item.source,
                    "access_count": item.access_count,
                    "last_accessed": item.last_accessed.isoformat() if item.last_accessed else None
                }
                for item in items
            ],
            "count": len(items)
        }

    except Exception as e:
        logger.error(f"Error getting long-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/long-term/search")
async def search_long_term_memory(
    request: MemorySearchRequest
):
    """
    Search long-term memory.
    """
    try:
        from api.main import app

        long_term_memory = app.state.long_term_memory
        items = long_term_memory.search_items(
            query=request.query,
            limit=request.limit,
            min_importance=request.min_importance
        )

        return {
            "items": [
                {
                    "id": item.id,
                    "content": item.content,
                    "timestamp": item.timestamp.isoformat(),
                    "metadata": item.metadata,
                    "importance": item.importance,
                    "category": item.category,
                    "tags": item.tags,
                    "source": item.source,
                    "access_count": item.access_count,
                    "last_accessed": item.last_accessed.isoformat() if item.last_accessed else None
                }
                for item in items
            ],
            "count": len(items),
            "query": request.query
        }

    except Exception as e:
        logger.error(f"Error searching long-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/long-term/{item_id}")
async def update_long_term_memory(
    item_id: str,
    request: MemoryItemRequest
):
    """
    Update an item in long-term memory.
    """
    try:
        from api.main import app

        long_term_memory = app.state.long_term_memory
        item = long_term_memory.update_item(
            item_id=item_id,
            content=request.content,
            category=request.category,
            tags=request.tags,
            source=request.source,
            metadata=request.metadata,
            importance=request.importance
        )

        if item is None:
            raise HTTPException(status_code=404, detail="Memory item not found")

        return MemoryItemResponse(
            id=item.id,
            content=item.content,
            timestamp=item.timestamp.isoformat(),
            metadata=item.metadata,
            importance=item.importance,
            category=item.category,
            tags=item.tags,
            source=item.source,
            access_count=item.access_count,
            last_accessed=item.last_accessed.isoformat() if item.last_accessed else None
        )

    except Exception as e:
        logger.error(f"Error updating long-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/long-term/{item_id}")
async def delete_long_term_memory(item_id: str):
    """
    Delete an item from long-term memory.
    """
    try:
        from api.main import app

        long_term_memory = app.state.long_term_memory
        success = long_term_memory.delete_item(item_id)

        if not success:
            raise HTTPException(status_code=404, detail="Memory item not found")

        return {"message": f"Memory item {item_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting long-term memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector", response_model=dict)
async def add_vector_memory(
    request: MemoryItemRequest
):
    """
    Add an item to vector memory.
    """
    try:
        from api.main import app

        vector_memory = app.state.vector_memory

        # For vector memory, we need text content to embed
        text_content = request.metadata.get("text_content", str(request.content)) if request.metadata else str(request.content)

        item = vector_memory.add_item(
            text_content=text_content,
            content=request.content,
            metadata=request.metadata,
            importance=request.importance or 0.5
        )

        return {
            "message": "Item added to vector memory",
            "item_id": item.id
        }

    except Exception as e:
        logger.error(f"Error adding to vector memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector/search")
async def search_vector_memory(
    request: MemorySearchRequest
):
    """
    Search vector memory for similar items.
    """
    try:
        from api.main import app

        vector_memory = app.state.vector_memory
        results = vector_memory.search_similar(
            query=request.query,
            limit=request.limit,
            min_importance=request.min_importance
        )

        return {
            "results": [
                {
                    "item": {
                        "id": item.id,
                        "content": item.content,
                        "timestamp": item.timestamp.isoformat(),
                        "metadata": item.metadata,
                        "importance": item.importance,
                        "text_content": item.text_content
                    },
                    "score": score
                }
                for item, score in results
            ],
            "count": len(results),
            "query": request.query
        }

    except Exception as e:
        logger.error(f"Error searching vector memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_memory_stats():
    """
    Get statistics for all memory systems.
    """
    try:
        from api.main import app

        short_term_stats = app.state.short_term_memory.get_memory_stats()
        long_term_stats = app.state.long_term_memory.get_memory_stats()
        vector_stats = app.state.vector_memory.get_memory_stats()

        return {
            "short_term_memory": short_term_stats,
            "long_term_memory": long_term_stats,
            "vector_memory": vector_stats
        }

    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))