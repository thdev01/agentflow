"""Supervisor orchestration pattern."""

import json
from typing import Any, Dict, List, Optional, Union

from agentflow.agents.agent import Agent
from agentflow.llm.base import LLMProvider, Message, Role
from agentflow.llm.openai_provider import OpenAIProvider


class Supervisor:
    """Supervisor that coordinates multiple agents to complete tasks.

    The supervisor uses an LLM to decide which agent should handle each subtask,
    then delegates work to the appropriate agents and synthesizes their outputs.
    """

    def __init__(
        self,
        agents: List[Agent],
        llm: Optional[Union[str, LLMProvider]] = None,
        max_rounds: int = 5,
        verbose: bool = False,
    ) -> None:
        """Initialize the Supervisor.

        Args:
            agents: List of agents to coordinate
            llm: LLM for supervisor decision-making
            max_rounds: Maximum coordination rounds
            verbose: Enable verbose logging
        """
        self.agents = {agent.config.name: agent for agent in agents}
        self.max_rounds = max_rounds
        self.verbose = verbose

        # Initialize supervisor LLM
        if llm is None:
            self.llm = OpenAIProvider(model="gpt-4")
        elif isinstance(llm, str):
            if "gpt" in llm.lower():
                self.llm = OpenAIProvider(model=llm)
            elif "claude" in llm.lower():
                from agentflow.llm.anthropic_provider import AnthropicProvider

                self.llm = AnthropicProvider(model=llm)
            else:
                self.llm = OpenAIProvider(model=llm)
        else:
            self.llm = llm

        self.conversation_history: List[Message] = []
        self._build_system_prompt()

    def _build_system_prompt(self) -> None:
        """Build the supervisor's system prompt."""
        agent_descriptions = []
        for name, agent in self.agents.items():
            tools_str = ", ".join([t.name for t in agent.tools]) if agent.tools else "none"
            agent_descriptions.append(
                f"- {name}: {agent.config.role} (tools: {tools_str})"
            )

        prompt = """You are a supervisor coordinating a team of AI agents to complete tasks.

Your team:
{}

Your responsibilities:
1. Break down complex tasks into subtasks
2. Assign each subtask to the most appropriate agent
3. Coordinate agents to work together effectively
4. Synthesize results from multiple agents into a final answer

When delegating, respond with JSON in this format:
{{
    "agent": "agent_name",
    "task": "specific task description"
}}

When you have enough information to provide a final answer, respond with:
{{
    "final_answer": "your comprehensive answer"
}}
""".format(
            "\n".join(agent_descriptions)
        )

        self.conversation_history.append(Message(role=Role.SYSTEM, content=prompt))

    def execute(self, task: str) -> str:
        """Execute a task using the agent team.

        Args:
            task: The task to complete

        Returns:
            Final result
        """
        if self.verbose:
            print(f"[Supervisor] Starting task: {task}")

        # Add user task
        self.conversation_history.append(Message(role=Role.USER, content=task))

        for round_num in range(self.max_rounds):
            if self.verbose:
                print(f"\n[Supervisor] Round {round_num + 1}/{self.max_rounds}")

            # Get supervisor decision
            response = self.llm.complete(messages=self.conversation_history)

            if self.verbose:
                print(f"[Supervisor] Response: {response.content}")

            # Parse supervisor decision
            try:
                decision = json.loads(response.content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                content = response.content.strip()
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                try:
                    decision = json.loads(content)
                except json.JSONDecodeError:
                    decision = {"final_answer": response.content}

            # Check if we have a final answer
            if "final_answer" in decision:
                if self.verbose:
                    print(f"[Supervisor] Task completed: {decision['final_answer']}")
                return decision["final_answer"]

            # Delegate to agent
            if "agent" in decision and "task" in decision:
                agent_name = decision["agent"]
                agent_task = decision["task"]

                if agent_name in self.agents:
                    if self.verbose:
                        print(f"[Supervisor] Delegating to {agent_name}: {agent_task}")

                    agent = self.agents[agent_name]
                    result = agent.execute(agent_task)

                    if self.verbose:
                        print(f"[Supervisor] {agent_name} completed: {result}")

                    # Add result to supervisor's history
                    self.conversation_history.append(
                        Message(
                            role=Role.ASSISTANT,
                            content=f"Delegated to {agent_name}: {agent_task}",
                        )
                    )
                    self.conversation_history.append(
                        Message(
                            role=Role.USER,
                            content=f"Result from {agent_name}: {result}",
                        )
                    )
                else:
                    error_msg = f"Agent {agent_name} not found"
                    if self.verbose:
                        print(f"[Supervisor] Error: {error_msg}")
                    self.conversation_history.append(
                        Message(role=Role.USER, content=error_msg)
                    )
            else:
                # Invalid format, ask for clarification
                self.conversation_history.append(
                    Message(
                        role=Role.ASSISTANT,
                        content=response.content,
                    )
                )
                self.conversation_history.append(
                    Message(
                        role=Role.USER,
                        content="Please provide a valid delegation in JSON format or a final answer.",
                    )
                )

        # Max rounds reached
        return "Task could not be completed within the maximum number of rounds."

    async def aexecute(self, task: str) -> str:
        """Async version of execute.

        Args:
            task: The task to complete

        Returns:
            Final result
        """
        if self.verbose:
            print(f"[Supervisor] Starting task: {task}")

        # Add user task
        self.conversation_history.append(Message(role=Role.USER, content=task))

        for round_num in range(self.max_rounds):
            if self.verbose:
                print(f"\n[Supervisor] Round {round_num + 1}/{self.max_rounds}")

            # Get supervisor decision
            response = await self.llm.acomplete(messages=self.conversation_history)

            if self.verbose:
                print(f"[Supervisor] Response: {response.content}")

            # Parse supervisor decision
            try:
                decision = json.loads(response.content)
            except json.JSONDecodeError:
                content = response.content.strip()
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                try:
                    decision = json.loads(content)
                except json.JSONDecodeError:
                    decision = {"final_answer": response.content}

            # Check if we have a final answer
            if "final_answer" in decision:
                if self.verbose:
                    print(f"[Supervisor] Task completed: {decision['final_answer']}")
                return decision["final_answer"]

            # Delegate to agent
            if "agent" in decision and "task" in decision:
                agent_name = decision["agent"]
                agent_task = decision["task"]

                if agent_name in self.agents:
                    if self.verbose:
                        print(f"[Supervisor] Delegating to {agent_name}: {agent_task}")

                    agent = self.agents[agent_name]
                    result = await agent.aexecute(agent_task)

                    if self.verbose:
                        print(f"[Supervisor] {agent_name} completed: {result}")

                    # Add result to supervisor's history
                    self.conversation_history.append(
                        Message(
                            role=Role.ASSISTANT,
                            content=f"Delegated to {agent_name}: {agent_task}",
                        )
                    )
                    self.conversation_history.append(
                        Message(
                            role=Role.USER,
                            content=f"Result from {agent_name}: {result}",
                        )
                    )
                else:
                    error_msg = f"Agent {agent_name} not found"
                    if self.verbose:
                        print(f"[Supervisor] Error: {error_msg}")
                    self.conversation_history.append(
                        Message(role=Role.USER, content=error_msg)
                    )
            else:
                # Invalid format, ask for clarification
                self.conversation_history.append(
                    Message(
                        role=Role.ASSISTANT,
                        content=response.content,
                    )
                )
                self.conversation_history.append(
                    Message(
                        role=Role.USER,
                        content="Please provide a valid delegation in JSON format or a final answer.",
                    )
                )

        # Max rounds reached
        return "Task could not be completed within the maximum number of rounds."

    def reset(self) -> None:
        """Reset the supervisor and all agents."""
        self.conversation_history = []
        self._build_system_prompt()
        for agent in self.agents.values():
            agent.reset()
