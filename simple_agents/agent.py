"""Single agent — one role, one completion call per `run`."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from simple_agents.memory import Memory
from simple_agents.model import Message, ModelProvider


@dataclass
class AgentResult:
    agent_name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent:
    """
    An agent is a named role backed by a completion API.

    Each `run` builds a message list (system + optional context + task),
    calls the provider's `complete`, and returns the text response.
    """

    def __init__(self, name: str, role: str, provider: ModelProvider) -> None:
        self.name = name
        self.role = role
        self.provider = provider

    def run(self, task: str, context: str = "", memory: Memory | None = None) -> AgentResult:
        messages: list[Message] = [
            Message(
                role="system",
                content=f"You are {self.name}, a {self.role}. Respond concisely and stay in role.",
            ),
        ]
        if context.strip():
            messages.append(Message(role="user", content=f"Context from prior agents:\n{context}"))
        messages.append(Message(role="user", content=task))

        content = self.provider.complete(messages)
        if memory is not None:
            memory.remember(f"{self.name}/last_output", content)
            memory.add_event(self.name, f"completed task: {task[:80]}")

        return AgentResult(agent_name=self.name, content=content)
