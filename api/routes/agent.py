"""
Agent API Routes

Endpoints for interacting with the self-learning AI agent.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    learning: Optional[Dict[str, Any]] = None

class AgentStatusResponse(BaseModel):
    status: str
    components: Dict[str, str]
    stats: Dict[str, Any]


@router.post("/execute", response_model=TaskResponse)
async def execute_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a task using the self-learning AI agent.
    """
    try:
        logger.info(f"Received task execution request: {request.task}")

        # Get the app state (in a real implementation, you'd use dependency injection)
        # For now, we'll access it globally - in practice, use proper dependency injection
        from api.main import app

        brain = app.state.brain
        planner = app.state.planner
        executor = app.state.executor
        evaluator = app.state.evaluator
        learner = app.state.learner
        short_term_memory = app.state.short_term_memory
        long_term_memory = app.state.long_term_memory
        vector_memory = app.state.vector_memory

        # Prepare context
        context = request.context or {}
        context["task"] = request.task

        # Add relevant memories to context
        short_term_items = short_term_memory.get_recent_items(
            session_id=context.get("session_id", "default"),
            limit=5
        )
        context["short_term_memory"] = [item.content for item in short_term_items]

        # Get relevant long-term memories
        long_term_items = long_term_memory.get_items(limit=5)
        context["long_term_memory"] = [item.content for item in long_term_items]

        # Get relevant vector memories
        vector_results = vector_memory.search_similar(
            query=request.task,
            limit=3
        )
        context["vector_memory"] = [item.content for item, _ in vector_results]

        # Use the brain to reason about the task
        reasoning_result = await brain.reason(
            task=request.task,
            context=context
        )

        # Create a task plan from the reasoning
        # In a full implementation, this would be more sophisticated
        task_plan = [{
            "id": "main_task",
            "tool_name": reasoning_result.get("next_action", {}).get("type", "reasoning"),
            "parameters": reasoning_result.get("next_action", {}).get("parameters", {}),
            "description": reasoning_result.get("next_action", {}).get("description", "")
        }]

        # Execute the task
        execution_results = await executor.execute_plan(task_plan, context)

        # Get the final result
        final_result = execution_results[-1].output if execution_results else None
        execution_success = execution_results[-1].success if execution_results else False

        # Evaluate the result
        evaluation = await evaluator.evaluate(
            task=request.task,
            result=final_result,
            context=context
        )

        # Learn from the experience
        experience = learner.learn_from_experience(
            task=request.task,
            actions=[{
                "type": "reasoning",
                "reasoning": reasoning_result.get("thoughts", ""),
                "plan": reasoning_result.get("plan", [])
            }],
            result=final_result,
            evaluation={
                "success": evaluation.success,
                "score": evaluation.score,
                "feedback": evaluation.feedback,
                "suggestions": evaluation.suggestions
            },
            reflection={
                "learnings": "Task completed with evaluation score: {}".format(evaluation.score),
                "future_strategies": "Continue with similar approach" if evaluation.score > 0.7 else "Consider alternative approaches"
            }
        )

        # Store relevant information in memory
        # Short-term memory for conversation context
        short_term_memory.add_item(
            content={
                "task": request.task,
                "result": final_result,
                "evaluation_score": evaluation.score
            },
            session_id=context.get("session_id", "default"),
            turn_number=len(short_term_memory.get_recent_items("default", 100)) + 1,
            importance=0.7 if evaluation.success else 0.3
        )

        # Long-term memory for successful outcomes
        if evaluation.success:
            long_term_memory.add_item(
                content={
                    "task": request.task,
                    "approach": reasoning_result.get("plan", []),
                    "result": str(final_result)[:500],  # Limit size
                    "learnings": experience.strategy
                },
                category="successful_tasks",
                tags=["success", "learned"],
                importance=min(0.9, 0.5 + evaluation.score * 0.4)
            )

        # Vector memory for similarity search
        vector_memory.add_item(
            text_content=request.task,
            content={
                "task": request.task,
                "result": str(final_result)[:200],
                "success": evaluation.success
            },
            importance=0.6 if evaluation.success else 0.3
        )

        # Prepare response
        response = TaskResponse(
            task_id=f"task_{len(execution_results)}",
            status="completed" if execution_success else "failed",
            result=final_result,
            learning={
                "experience_id": len(learner.experiences),
                "success": evaluation.success,
                "score": evaluation.score,
                "feedback": evaluation.feedback,
                "strategy_used": experience.strategy
            }
        )

        logger.info(f"Task execution completed. Success: {execution_success}, Score: {evaluation.score}")
        return response

    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """
    Get the current status of the agent system.
    """
    try:
        from api.main import app

        # Get learning stats
        learning_stats = app.state.learner.get_learning_stats()

        # Get memory stats
        short_term_stats = app.state.short_term_memory.get_memory_stats()
        long_term_stats = app.state.long_term_memory.get_memory_stats()
        vector_stats = app.state.vector_memory.get_memory_stats()

        return AgentStatusResponse(
            status="running",
            components={
                "brain": "ok",
                "planner": "ok",
                "executor": "ok",
                "evaluator": "ok",
                "learner": "ok",
                "short_term_memory": "ok",
                "long_term_memory": "ok",
                "vector_memory": "ok"
            },
            stats={
                "learning": learning_stats,
                "short_term_memory": short_term_stats,
                "long_term_memory": long_term_stats,
                "vector_memory": vector_stats
            }
        )

    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_agent():
    """
    Reset the agent's memory and learning state.
    """
    try:
        from api.main import app

        # Reset learning
        app.state.learner = type(app.state.learner)()

        # Reset memory systems
        app.state.short_term_memory = type(app.state.short_term_memory)()
        # Note: Long-term and vector memory persistence would require more careful handling

        return {"message": "Agent reset successfully"}

    except Exception as e:
        logger.error(f"Error resetting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))