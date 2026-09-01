"""LLM provider abstraction — swap models or use mocks for learning."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    role: str
    content: str


class ModelProvider(ABC):
    """Any completion backend implements `complete(messages) -> text`."""

    @abstractmethod
    def complete(self, messages: list[Message], **kwargs: Any) -> str:
        ...


class MockProvider(ModelProvider):
    """
    Deterministic responses so you can run demos without an API key.
    Each mock agent role gets a predictable completion.
    """

    _ROLE_RESPONSES: dict[str, str] = {
        "researcher": (
            "RESEARCH NOTES:\n"
            "- Quantum computers use qubits instead of classical bits.\n"
            "- Qubits can exist in superposition (0 and 1 at once).\n"
            "- Entanglement links qubits so their states correlate.\n"
            "- Useful for cryptography, simulation, and optimization."
        ),
        "writer": (
            "SUMMARY:\n"
            "Quantum computing applies quantum mechanics to computation. "
            "Unlike classical bits, qubits leverage superposition and entanglement "
            "to explore many solutions in parallel, enabling breakthroughs in "
            "fields like drug discovery and secure communication."
        ),
        "critic": (
            "REVIEW:\n"
            "The summary correctly explains qubits, superposition, and applications. "
            "It is concise and accurate. Score: 9/10."
        ),
        "orchestrator": (
            "WORKFLOW PLAN:\n"
            "1. Researcher gathers facts about the topic.\n"
            "2. Writer produces a clear summary from those facts.\n"
            "3. Critic reviews the summary for accuracy and clarity."
        ),
    }

    def complete(self, messages: list[Message], **kwargs: Any) -> str:
        system = next((m.content for m in messages if m.role == "system"), "")
        user = next((m.content for m in reversed(messages) if m.role == "user"), "")

        system_lower = system.lower()
        for role, response in self._ROLE_RESPONSES.items():
            if role in system_lower:
                return response

        if "plan" in user.lower():
            return self._ROLE_RESPONSES["orchestrator"]

        return f"[mock completion] Processed: {user[:120]}"


class OpenAIProvider(ModelProvider):
    """OpenAI Chat Completions API (or any OpenAI-compatible endpoint)."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None, base_url: str | None = None):
        from openai import OpenAI

        self.model = model
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"), base_url=base_url)

    def complete(self, messages: list[Message], **kwargs: Any) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            **kwargs,
        )
        return response.choices[0].message.content or ""


def create_provider(
    provider: str = "auto",
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
    base_url: str | None = None,
) -> ModelProvider:
    """
    Factory for model providers.

    - `auto`: use OpenAI when OPENAI_API_KEY is set, otherwise mock.
    - `mock`: always use deterministic mock responses.
    - `openai`: require a real API key.
    """
    if provider == "mock":
        return MockProvider()

    if provider == "openai":
        return OpenAIProvider(model=model, api_key=api_key, base_url=base_url)

    if provider == "auto":
        if os.environ.get("OPENAI_API_KEY"):
            return OpenAIProvider(model=model, api_key=api_key, base_url=base_url)
        return MockProvider()

    raise ValueError(f"Unknown provider: {provider}. Use 'auto', 'mock', or 'openai'.")
