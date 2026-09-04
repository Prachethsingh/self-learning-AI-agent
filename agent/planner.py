"""
Planner Module - Task Planning and Decomposition

Handles breaking down complex tasks into manageable steps.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task to be completed."""
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: List[str] = None
    priority: int = 1
    estimated_time: Optional[float] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class Planner:
    """
    Handles task planning and decomposition.
    """

    def __init__(self):
        self.task_queue: List[Task] = []
        self.completed_tasks: List[str] = []  # Store task IDs

    def add_task(
        self,
        description: str,
        dependencies: Optional[List[str]] = None,
        priority: int = 1,
        estimated_time: Optional[float] = None
    ) -> Task:
        """Add a new task to the queue."""
        task = Task(
            description=description,
            dependencies=dependencies or [],
            priority=priority,
            estimated_time=estimated_time
        )
        self.task_queue.append(task)
        logger.info(f"Added task: {task.description}")
        return task

    def get_next_task(self) -> Optional[Task]:
        """Get the next task to work on."""
        # Sort tasks by priority and estimated time
        sorted_tasks = sorted(
            self.task_queue,
            key=lambda x: (-x.priority, x.estimated_time or float('inf'))
        )

        # Find a task with all dependencies completed
        for task in sorted_tasks:
            if all(dep in self.completed_tasks for dep in task.dependencies):
                return task

        return None

    def mark_task_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        # Find the task in the queue
        for i, task in enumerate(self.task_queue):
            if task.id == task_id:
                task.status = "completed"
                task.completed_at = datetime.now()
                self.task_queue.pop(i)
                self.completed_tasks.append(task_id)
                logger.info(f"Completed task: {task.description}")
                break

    def delete_task(self, task_id: str) -> bool:
        """Delete a task from the queue."""
        for i, task in enumerate(self.task_queue):
            if task.id == task_id:
                self.task_queue.pop(i)
                logger.info(f"Deleted task: {task.description}")
                return True
        return False

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks (pending and completed)."""
        # Return pending tasks first, then completed
        pending = [task for task in self.task_queue if task.status == "pending"]
        completed = [task for task in self.task_queue if task.status == "completed"]
        return pending + completed

    def get_task_stats(self) -> Dict[str, Any]:
        """Get statistics about tasks."""
        total = len(self.task_queue)
        pending = len([task for task in self.task_queue if task.status == "pending"])
        completed = len([task for task in self.task_queue if task.status == "completed"])

        return {
            "total_tasks": total,
            "pending_tasks": pending,
            "completed_tasks": completed,
            "completion_rate": completed / total if total > 0 else 0.0
        }

    def decompose_task(self, task: str, context: Dict[str, Any]) -> List[Task]:
        """
        Decompose a complex task into smaller subtasks.

        Args:
            task: The complex task to decompose
            context: Context information including memory, previous actions, etc.

        Returns:
            List of decomposed tasks
        """
        # This is a simplified version - in a real implementation,
        # you would use the LLM to break down the task
        logger.info(f"Decomposing task: {task}")

        # Example decomposition
        if "build a web application" in task.lower():
            return [
                Task(
                    description="Design the application architecture",
                    priority=2,
                    estimated_time=4.0
                ),
                Task(
                    description="Set up development environment",
                    priority=1,
                    estimated_time=2.0
                ),
                Task(
                    description="Implement core features",
                    dependencies=[
                        "Design the application architecture",
                        "Set up development environment"
                    ],
                    priority=3,
                    estimated_time=16.0
                ),
                Task(
                    description="Write tests",
                    dependencies=["Implement core features"],
                    priority=2,
                    estimated_time=8.0
                ),
                Task(
                    description="Deploy the application",
                    dependencies=[
                        "Write tests",
                        "Implement core features"
                    ],
                    priority=1,
                    estimated_time=2.0
                )
            ]

        # Default decomposition - just return the original task
        return [Task(description=task)]

    def replan(self, context: Dict[str, Any]) -> None:
        """
        Replan tasks based on new context.

        Args:
            context: Updated context information
        """
        logger.info("Replanning tasks based on new context")
        # In a real implementation, this would analyze the context
        # and adjust the task queue accordingly
        pass