"""
Evaluator Module - Result Evaluation

Handles evaluating task results and providing feedback for learning.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Represents the evaluation of a task result."""
    success: bool
    score: float  # 0.0 to 1.0
    feedback: List[str]
    suggestions: List[str]
    criteria_met: Dict[str, bool]


class Evaluator:
    """
    Handles evaluation of task results and provides feedback for learning.
    """

    def __init__(self):
        self.evaluation_criteria = {
            "completeness": self._evaluate_completeness,
            "accuracy": self._evaluate_accuracy,
            "efficiency": self._evaluate_efficiency,
            "quality": self._evaluate_quality
        }

    async def evaluate(
        self,
        task: str,
        result: Any,
        context: Dict[str, Any],
        expected_outcome: Optional[Any] = None
    ) -> EvaluationResult:
        """
        Evaluate the result of a task.

        Args:
            task: The original task
            result: The result of the task execution
            context: Context information including memory, previous actions, etc.
            expected_outcome: Expected outcome for comparison (if available)

        Returns:
            Evaluation result with score and feedback
        """
        logger.info(f"Evaluating task: {task}")

        scores = {}
        feedback = []
        suggestions = []
        criteria_met = {}

        # Evaluate each criterion
        for criterion, evaluator_func in self.evaluation_criteria.items():
            try:
                score, fb, sugg = await evaluator_func(
                    task, result, context, expected_outcome
                )
                scores[criterion] = score
                feedback.extend(fb)
                suggestions.extend(sugg)
                criteria_met[criterion] = score >= 0.7  # Threshold for meeting criteria
            except Exception as e:
                logger.error(f"Error evaluating criterion {criterion}: {e}")
                scores[criterion] = 0.0
                feedback.append(f"Error evaluating {criterion}: {str(e)}")
                suggestions.append(f"Fix evaluation logic for {criterion}")
                criteria_met[criterion] = False

        # Calculate overall score (weighted average)
        weights = {
            "completeness": 0.3,
            "accuracy": 0.3,
            "efficiency": 0.2,
            "quality": 0.2
        }

        overall_score = sum(
            scores[criterion] * weights[criterion]
            for criterion in scores
        )

        success = overall_score >= 0.7  # Overall threshold for success

        logger.info(f"Evaluation complete. Score: {overall_score:.2f}, Success: {success}")

        return EvaluationResult(
            success=success,
            score=overall_score,
            feedback=list(set(feedback)),  # Remove duplicates
            suggestions=list(set(suggestions)),  # Remove duplicates
            criteria_met=criteria_met
        )

    async def _evaluate_completeness(
        self,
        task: str,
        result: Any,
        context: Dict[str, Any],
        expected_outcome: Optional[Any] = None
    ) -> tuple[float, List[str], List[str]]:
        """Evaluate if the task was completed completely."""
        feedback = []
        suggestions = []

        # Check if result exists and is not None
        if result is None:
            feedback.append("No result produced")
            suggestions.append("Ensure task execution produces a result")
            return 0.0, feedback, suggestions

        # Simple heuristic: check if result has content
        if isinstance(result, str) and len(result.strip()) == 0:
            feedback.append("Empty result produced")
            suggestions.append("Task should produce meaningful output")
            return 0.2, feedback, suggestions

        # If we have expected outcome, compare
        if expected_outcome is not None:
            if result == expected_outcome:
                return 1.0, ["Result matches expected outcome"], []
            else:
                feedback.append("Result does not match expected outcome")
                suggestions.append("Review task logic to match expected outcome")
                return 0.5, feedback, suggestions

        # Default: assume reasonable completeness if we got a result
        return 0.8, ["Task completed with result"], ["Consider verifying completeness"]

    async def _evaluate_accuracy(
        self,
        task: str,
        result: Any,
        context: Dict[str, Any],
        expected_outcome: Optional[Any] = None
    ) -> tuple[float, List[str], List[str]]:
        """Evaluate the accuracy of the result."""
        feedback = []
        suggestions = []

        if expected_outcome is not None:
            # Direct comparison
            if result == expected_outcome:
                return 1.0, ["Result is accurate"], []
            else:
                feedback.append("Result differs from expected outcome")
                suggestions.append("Verify calculations and logic")
                return 0.3, feedback, suggestions
        else:
            # Heuristic-based evaluation
            if isinstance(result, dict) and "error" in result:
                feedback.append("Result contains error")
                suggestions.append("Fix the source of the error")
                return 0.2, feedback, suggestions
            elif isinstance(result, str) and ("error" in result.lower() or "failed" in result.lower()):
                feedback.append("Result indicates failure")
                suggestions.append("Investigate the cause of failure")
                return 0.3, feedback, suggestions
            else:
                return 0.7, ["No obvious inaccuracies detected"], ["Consider adding validation checks"]

    async def _evaluate_efficiency(
        self,
        task: str,
        result: Any,
        context: Dict[str, Any],
        expected_outcome: Optional[Any] = None
    ) -> tuple[float, List[str], List[str]]:
        """Evaluate the efficiency of the task execution."""
        feedback = []
        suggestions = []

        # Check execution time if available
        execution_time = context.get("execution_time", 0)
        if execution_time > 0:
            # Simple heuristic: under 5 seconds is good, under 30 seconds is acceptable
            if execution_time < 5:
                return 1.0, [f"Fast execution ({execution_time:.2f}s)"], []
            elif execution_time < 30:
                return 0.7, [f"Reasonable execution time ({execution_time:.2f}s)"], [f"Consider optimizing to reduce time from {execution_time:.2f}s"]
            else:
                feedback.append(f"Slow execution ({execution_time:.2f}s)")
                suggestions.append("Optimize the task for better performance")
                return 0.4, feedback, suggestions
        else:
            return 0.6, ["Execution time not measured"], ["Add timing to measure efficiency"]

    async def _evaluate_quality(
        self,
        task: str,
        result: Any,
        context: Dict[str, Any],
        expected_outcome: Optional[Any] = None
    ) -> tuple[float, List[str], List[str]]:
        """Evaluate the quality of the result."""
        feedback = []
        suggestions = []

        # Basic quality checks
        if isinstance(result, str):
            # Check for completeness of sentences, proper formatting, etc.
            if len(result.strip()) > 10:
                if result.count('.') >= 1 or result.count('\n') >= 1:
                    return 0.8, ["Result appears well-formed"], ["Consider adding more detail or structure"]
                else:
                    return 0.6, ["Result is brief"], ["Expand the result with more details"]
            else:
                feedback.append("Result is too brief")
                suggestions.append("Provide more comprehensive output")
                return 0.3, feedback, suggestions
        elif isinstance(result, dict):
            # Check if dictionary has meaningful content
            if len(result) > 0:
                return 0.8, ["Dictionary result contains data"], ["Consider adding more fields or structure"]
            else:
                feedback.append("Empty dictionary result")
                suggestions.append("Populate result with meaningful data")
                return 0.2, feedback, suggestions
        elif isinstance(result, list):
            # Check if list has meaningful content
            if len(result) > 0:
                return 0.8, ["List result contains items"], ["Consider adding more items or details"]
            else:
                feedback.append("Empty list result")
                suggestions.append("Populate list with meaningful items")
                return 0.2, feedback, suggestions
        else:
            return 0.7, ["Result produced"], ["Consider enhancing result quality"]

    async def suggest_improvements(
        self,
        task: str,
        result: Any,
        evaluation: EvaluationResult,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Suggest improvements based on the evaluation.

        Args:
            task: The original task
            result: The result of the task execution
            evaluation: The evaluation result
            context: Context information

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Add suggestions from evaluation
        suggestions.extend(evaluation.suggestions)

        # Add specific suggestions based on failed criteria
        for criterion, met in evaluation.criteria_met.items():
            if not met:
                if criterion == "completeness":
                    suggestions.append("Ensure all aspects of the task are addressed")
                elif criterion == "accuracy":
                    suggestions.append("Verify the correctness of your approach")
                elif criterion == "efficiency":
                    suggestions.append("Look for ways to optimize performance")
                elif criterion == "quality":
                    suggestions.append("Improve the presentation and detail of your output")

        # Add context-based suggestions
        if context.get("retry_count", 0) > 0:
            suggestions.append("Consider trying a different approach based on previous attempts")

        return list(set(suggestions))  # Remove duplicates