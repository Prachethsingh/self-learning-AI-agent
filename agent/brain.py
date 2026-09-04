"""
Brain Module - LLM Integration and Reasoning

Handles the core LLM interactions, reasoning, and decision-making for the agent.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from openai import OpenAI
from anthropic import Anthropic
import json

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    api_key: str
    max_tokens: int = 4000
    temperature: float = 0.7
    base_url: Optional[str] = None


class Brain:
    """
    The brain of the self-learning agent.
    Handles LLM interactions and reasoning.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._initialize_client()

    def _initialize_client(self) -> Union[OpenAI, Anthropic]:
        """Initialize the appropriate LLM client."""
        if self.config.provider == LLMProvider.OPENAI:
            return OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return Anthropic(
                api_key=self.config.api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")

    async def reason(
        self,
        task: str,
        context: Dict[str, Any],
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Perform reasoning on a task with given context.

        Args:
            task: The task to reason about
            context: Context information including memory, previous actions, etc.
            tools: Available tools for the agent to use

        Returns:
            Reasoning result containing thoughts and actions
        """
        system_prompt = self._build_system_prompt(context, tools)

        if self.config.provider == LLMProvider.OPENAI:
            response = await self._call_openai(system_prompt, task)
        else:
            response = await self._call_anthropic(system_prompt, task)

        return self._parse_response(response)

    def _build_system_prompt(
        self,
        context: Dict[str, Any],
        tools: Optional[List[Dict]] = None
    ) -> str:
        """Build the system prompt for the LLM."""

        prompt = f"""You are a self-learning AI agent. Your goal is to accomplish tasks effectively and learn from your experiences.

Current Context:
- Task: {context.get('task', 'No task specified')}
- Previous Actions: {context.get('previous_actions', [])}
- Available Memory: {context.get('memory', [])}
- Tools Available: {tools or ['Basic reasoning capabilities']}

You should:
1. Analyze the task carefully
2. Break it down into manageable steps
3. Use available tools when appropriate
4. Provide clear reasoning for your decisions
5. Learn from past experiences mentioned in memory

Format your response as JSON with the following structure:
{{
    "thoughts": "Your reasoning process",
    "plan": ["Step 1", "Step 2", ...],
    "next_action": {{
        "type": "tool_use" | "reasoning" | "complete",
        "tool_name": "tool_name" if using a tool,
        parameters": {{}} if using a tool,
        "description": "What you plan to do next"
    }},
    "confidence": 0.0 to 1.0
}}
"""

        # Add examples from memory if available
        if 'examples' in context:
            prompt += f"\n\nRelevant Examples from Past Experience:\n"
            for example in context['examples'][-3:]:  # Last 3 examples
                prompt += f"- {example}\n"

        return prompt

    async def _call_openai(self, system_prompt: str, task: str) -> str:
        """Call OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _call_anthropic(self, system_prompt: str, task: str) -> str:
        """Call Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": task}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format."""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                # OpenAI might return JSON directly
                return json.loads(response)
            else:
                # Anthropic returns plain text, need to extract JSON
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != -1:
                    return json.loads(response[start:end])
                else:
                    raise ValueError("No JSON found in response")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {e}")
            # Return a default structure
            return {
                "thoughts": "Failed to parse LLM response",
                "plan": [],
                "next_action": {
                    "type": "reasoning",
                    "description": "Need to retry with better prompt"
                },
                "confidence": 0.0
            }

    async def reflect(
        self,
        task: str,
        actions: List[Dict[str, Any]],
        result: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on completed task to extract learnings.

        Args:
            task: The original task
            actions: List of actions taken
            result: The result of the task
            evaluation: Evaluation of the result

        Returns:
            Reflection with learnings and improvements
        """
        reflection_prompt = f"""Reflect on the following task completion:

Task: {task}
Actions Taken: {json.dumps(actions, indent=2)}
Result: {json.dumps(result, indent=2)}
Evaluation: {json.dumps(evaluation, indent=2)}

Provide a reflection that includes:
1. What went well
2. What could be improved
3. Key learnings
4. Strategies for similar tasks in the future

Format your response as JSON:
{{
    "success_factors": ["factor1", "factor2"],
    "improvements": ["improvement1", "improvement2"],
    "learnings": "Key insights from this experience",
    "future_strategies": "Strategies for similar tasks",
    "confidence_improvement": 0.0 to 1.0
}}
"""

        if self.config.provider == LLMProvider.OPENAI:
            response = await self._call_openai(reflection_prompt, "")
        else:
            response = await self._call_anthropic(reflection_prompt, "")

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "success_factors": [],
                "improvements": [],
                "learnings": "Failed to parse reflection",
                "future_strategies": "",
                "confidence_improvement": 0.0
            }