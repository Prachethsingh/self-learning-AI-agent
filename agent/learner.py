"""
Learner Module - Learning and Memory Updates

Handles learning from experiences and updating memory systems.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Represents a learning experience."""
    task: str
    actions: List[Dict[str, Any]]
    result: Any
    success: bool
    reason: str
    strategy: str
    timestamp: datetime
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "task": self.task,
            "actions": self.actions,
            "result": str(self.result) if self.result is not None else None,
            "success": self.success,
            "reason": self.reason,
            "strategy": self.strategy,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experience":
        """Create from dictionary."""
        return cls(
            task=data["task"],
            actions=data["actions"],
            result=data["result"],
            success=data["success"],
            reason=data["reason"],
            strategy=data["strategy"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            confidence=data.get("confidence", 0.0)
        )


class Learner:
    """
    Handles learning from experiences and updating memory systems.
    """

    def __init__(self):
        self.experiences = []
        self.strategies = {}

    def learn_from_experience(
        self,
        task: str,
        actions: List[Dict[str, Any]],
        result: Any,
        evaluation: Dict[str, Any],
        reflection: Dict[str, Any]
    ) -> Experience:
        """
        Learn from a completed task execution.

        Args:
            task: The original task
            actions: List of actions taken
            result: The result of the task
            evaluation: Evaluation of the result
            reflection: Reflection on the task

        Returns:
            The experience that was learned from
        """
        logger.info(f"Learning from experience: {task}")

        # Determine success based on evaluation
        success = evaluation.get("success", False) if isinstance(evaluation, dict) else evaluation.success

        # Extract reason and strategy from reflection
        reason = reflection.get("learnings", "No specific reason identified") if isinstance(reflection, dict) else getattr(reflection, 'learnings', "No specific reason identified")
        strategy = reflection.get("future_strategies", "Continue with current approach") if isinstance(reflection, dict) else getattr(reflection, 'future_strategies', "Continue with current approach")

        # Create experience
        experience = Experience(
            task=task,
            actions=actions,
            result=result,
            success=success,
            reason=reason,
            strategy=strategy,
            timestamp=datetime.now(),
            confidence=evaluation.get("score", 0.5) if isinstance(evaluation, dict) else getattr(evaluation, 'score', 0.5)
        )

        # Store the experience
        self.experiences.append(experience)

        # Update strategies based on success/failure
        self._update_strategies(task, experience)

        logger.info(f"Stored experience: {task} - Success: {success}")
        return experience

    def _update_strategies(self, task: str, experience: Experience) -> None:
        """Update strategies based on experience."""
        task_key = self._normalize_task_key(task)

        if task_key not in self.strategies:
            self.strategies[task_key] = []

        # Add the new strategy if it's successful
        if experience.success:
            self.strategies[task_key].append({
                "strategy": experience.strategy,
                "confidence": experience.confidence,
                "timestamp": experience.timestamp.isoformat()
            })
            # Keep only top strategies
            self.strategies[task_key].sort(key=lambda x: x["confidence"], reverse=True)
            self.strategies[task_key] = self.strategies[task_key][:5]  # Top 5 strategies
        else:
            # For failures, we might want to avoid certain strategies
            pass

    def get_relevant_experiences(
        self,
        task: str,
        limit: int = 5
    ) -> List[Experience]:
        """
        Get relevant past experiences for a task.

        Args:
            task: The current task
            limit: Maximum number of experiences to return

        Returns:
            List of relevant experiences
        """
        task_key = self._normalize_task_key(task)

        # Filter experiences by task similarity
        relevant = [
            exp for exp in self.experiences
            if self._tasks_similar(exp.task, task)
        ]

        # Sort by recency and success rate
        relevant.sort(
            key=lambda x: (x.success, x.timestamp),
            reverse=True
        )

        return relevant[:limit]

    def get_best_strategy(self, task: str) -> Optional[str]:
        """
        Get the best strategy for a task based on past experiences.

        Args:
            task: The task to get a strategy for

        Returns:
            The best strategy or None if no experience
        """
        task_key = self._normalize_task_key(task)

        if task_key in self.strategies and self.strategies[task_key]:
            # Return the strategy with highest confidence
            best = max(self.strategies[task_key], key=lambda x: x["confidence"])
            return best["strategy"]

        return None

    def _tasks_similar(self, task1: str, task2: str) -> bool:
        """
        Check if two tasks are similar.

        Args:
            task1: First task
            task2: Second task

        Returns:
            True if tasks are similar
        """
        # Simple similarity check - in practice, you'd use embeddings
        task1_lower = task1.lower()
        task2_lower = task2.lower()

        # Check for common keywords
        keywords1 = set(task1_lower.split())
        keywords2 = set(task2_lower.split())

        # Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        if union == 0:
            return False

        similarity = intersection / union
        return similarity > 0.3  # Threshold for similarity

    def _normalize_task_key(self, task: str) -> str:
        """Normalize task for use as a dictionary key."""
        # Simple normalization - remove extra spaces, lowercase
        return " ".join(task.lower().split())

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning system."""
        total_experiences = len(self.experiences)
        successful_experiences = sum(1 for exp in self.experiences if exp.success)

        return {
            "total_experiences": total_experiences,
            "successful_experiences": successful_experiences,
            "success_rate": successful_experiences / total_experiences if total_experiences > 0 else 0.0,
            "unique_tasks": len(set(exp.task for exp in self.experiences)),
            "strategies_learned": sum(len(strategies) for strategies in self.strategies.values())
        }

    def save_experiences(self, filepath: str) -> None:
        """Save experiences to a file."""
        data = [exp.to_dict() for exp in self.experiences]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self.experiences)} experiences to {filepath}")

    def load_experiences(self, filepath: str) -> None:
        """Load experiences from a file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.experiences = [Experience.from_dict(item) for item in data]
            logger.info(f"Loaded {len(self.experiences)} experiences from {filepath}")
        except FileNotFoundError:
            logger.warning(f"No experience file found at {filepath}")
        except Exception as e:
            logger.error(f"Error loading experiences: {e}")