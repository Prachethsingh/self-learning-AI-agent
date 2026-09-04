"""
Executor Module - Task Execution

Handles executing tasks and managing the execution process.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Represents the result of a task execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class Executor:
    """
    Handles task execution and management.
    """

    def __init__(self, tools: Dict[str, Any]):
        self.tools = tools
        self.running_tasks = {}

    async def execute_task(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute a task with given context.

        Args:
            task: The task to execute
            context: Context information including memory, previous actions, etc.

        Returns:
            Execution result
        """
        task_id = task.get("id", "unknown")
        logger.info(f"Executing task: {task_id}")

        try:
            # Start timing
            start_time = asyncio.get_event_loop().time()

            # Get the appropriate tool
            tool_name = task.get("tool_name", "reasoning")
            tool = self.tools.get(tool_name)

            if tool is None:
                if tool_name in ["reasoning", "complete", "direct", "analysis"]:
                    output_msg = task.get("description") or task.get("parameters", {}).get("description") or f"Reasoning analysis completed for task {task_id}."
                    execution_time = asyncio.get_event_loop().time() - start_time
                    logger.info(f"Executed analytical reasoning step for {task_id}")
                    return ExecutionResult(
                        success=True,
                        output=output_msg,
                        execution_time=execution_time
                    )
                raise ValueError(f"Tool not found: {tool_name}")

            # Execute the tool
            result = await tool.execute(
                task.get("parameters", {}),
                context
            )

            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time

            logger.info(f"Task {task_id} completed successfully")
            return ExecutionResult(
                success=True,
                output=result,
                execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e)
            )

    async def execute_plan(
        self,
        plan: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """
        Execute a sequence of tasks as a plan.

        Args:
            plan: List of tasks to execute
            context: Context information including memory, previous actions, etc.

        Returns:
            List of execution results
        """
        results = []

        for task in plan:
            result = await self.execute_task(task, context)
            results.append(result)

            # Update context with the result
            context["last_result"] = result

            # If the task failed, stop the execution
            if not result.success:
                logger.warning(f"Task failed: {task.get('id', 'unknown')}")
                break

        return results

    def add_running_task(self, task_id: str, task: Any) -> None:
        """Add a task to the running tasks dictionary."""
        self.running_tasks[task_id] = task

    def remove_running_task(self, task_id: str) -> None:
        """Remove a task from the running tasks dictionary."""
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]

    def get_running_tasks(self) -> Dict[str, Any]:
        """Get the dictionary of running tasks."""
        return self.running_tasks