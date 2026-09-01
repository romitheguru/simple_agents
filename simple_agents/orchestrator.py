"""Orchestrator coordinates sub-agents through a multi-step workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from simple_agents.agent import Agent, AgentResult
from simple_agents.eval import EvalResult, Evaluator
from simple_agents.memory import Memory
from simple_agents.model import Message, ModelProvider


@dataclass
class WorkflowStep:
    """One step in a sequential workflow."""

    agent_name: str
    task: str  # may include `{task}` placeholder for the root user task


@dataclass
class WorkflowResult:
    task: str
    steps: list[AgentResult] = field(default_factory=list)
    final_output: str = ""
    evaluations: list[EvalResult] = field(default_factory=list)


class Orchestrator:
    """
    The orchestrator owns shared memory, delegates work to sub-agents,
    and can plan or follow a fixed multi-agent pipeline.
    """

    def __init__(
        self,
        name: str,
        provider: ModelProvider,
        agents: dict[str, Agent],
        evaluator: Evaluator | None = None,
    ) -> None:
        self.name = name
        self.provider = provider
        self.agents = agents
        self.evaluator = evaluator or Evaluator()
        self.memory = Memory()

    def plan(self, task: str) -> str:
        """Ask the orchestrator model how to break down a task (educational demo)."""
        messages = [
            Message(
                role="system",
                content=(
                    f"You are {self.name}, an orchestrator. "
                    "Describe a short multi-agent plan for the user's task."
                ),
            ),
            Message(role="user", content=f"Task: {task}\n\nDescribe the agent workflow."),
        ]
        plan = self.provider.complete(messages)
        self.memory.remember("plan", plan)
        return plan

    def delegate(self, agent_name: str, task: str, context: str = "") -> AgentResult:
        if agent_name not in self.agents:
            raise KeyError(f"Unknown agent '{agent_name}'. Available: {list(self.agents)}")
        agent = self.agents[agent_name]
        result = agent.run(task, context=context, memory=self.memory)
        self.memory.add_event(self.name, f"delegated to {agent_name}")
        return result

    def run_workflow(
        self,
        task: str,
        steps: list[WorkflowStep],
        eval_checks: list[Callable[[str], EvalResult]] | None = None,
    ) -> WorkflowResult:
        """
        Run sub-agents sequentially. Each step sees accumulated context
        from all prior completions — the core multi-agent pattern.
        """
        results: list[AgentResult] = []
        context = ""

        for step in steps:
            step_task = step.task.replace("{task}", task)
            result = self.delegate(step.agent_name, step_task, context=context)
            results.append(result)
            context = f"{context}\n\n[{result.agent_name}]: {result.content}".strip()

        final_output = results[-1].content if results else ""
        checks = eval_checks or [self.evaluator.check_nonempty]
        evaluations = self.evaluator.run_all(final_output, checks)

        self.memory.remember("final_output", final_output)
        return WorkflowResult(
            task=task,
            steps=results,
            final_output=final_output,
            evaluations=evaluations,
        )
