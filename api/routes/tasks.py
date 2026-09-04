"""
Tasks API Routes

Endpoints for managing tasks and task queues.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class TaskRequest(BaseModel):
    description: str
    dependencies: Optional[List[str]] = None
    priority: Optional[int] = 1
    estimated_time: Optional[float] = None

class TaskResponse(BaseModel):
    id: str
    description: str
    dependencies: List[str]
    priority: int
    estimated_time: Optional[float]
    status: str
    created_at: str
    completed_at: Optional[str] = None


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskRequest
):
    """
    Create a new task.
    """
    try:
        from api.main import app

        planner = app.state.planner

        task = planner.add_task(
            description=request.description,
            dependencies=request.dependencies or [],
            priority=request.priority or 1,
            estimated_time=request.estimated_time
        )

        return TaskResponse(
            id=task.id,
            description=task.description,
            dependencies=task.dependencies or [],
            priority=task.priority,
            estimated_time=task.estimated_time,
            status=task.status,
            created_at=task.created_at.isoformat(),
            completed_at=task.completed_at.isoformat() if task.completed_at else None
        )

    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List tasks with optional filtering.
    """
    try:
        from api.main import app

        planner = app.state.planner

        # Get all tasks
        tasks = planner.get_all_tasks()

        # Filter by status if specified
        if status:
            tasks = [task for task in tasks if task.status == status]

        # Limit results
        tasks = tasks[:limit]

        return {
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "dependencies": task.dependencies or [],
                    "priority": task.priority,
                    "estimated_time": task.estimated_time,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in tasks
            ],
            "count": len(tasks)
        }

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next")
async def get_next_task():
    """
    Get the next task to work on.
    """
    try:
        from api.main import app

        planner = app.state.planner
        task = planner.get_next_task()

        if task is None:
            return {"message": "No tasks available", "task": None}

        return {
            "task": {
                "id": task.id,
                "description": task.description,
                "dependencies": task.dependencies or [],
                "priority": task.priority,
                "estimated_time": task.estimated_time,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        }

    except Exception as e:
        logger.error(f"Error getting next task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}/complete")
async def complete_task(task_id: str):
    """
    Mark a task as completed.
    """
    try:
        from api.main import app

        planner = app.state.planner
        planner.mark_task_completed(task_id)

        return {"message": f"Task {task_id} marked as completed"}

    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a task.
    """
    try:
        from api.main import app

        planner = app.state.planner
        success = planner.delete_task(task_id)

        if not success:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": f"Task {task_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replan")
async def replan_tasks():
    """
    Replan tasks based on current context.
    """
    try:
        from api.main import app

        planner = app.state.planner
        # In a real implementation, you'd pass current context
        planner.replan({})

        return {"message": "Tasks replanned successfully"}

    except Exception as e:
        logger.error(f"Error replanning tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_task_stats():
    """
    Get statistics about tasks.
    """
    try:
        from api.main import app

        planner = app.state.planner
        stats = planner.get_task_stats()

        return stats

    except Exception as e:
        logger.error(f"Error getting task stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))