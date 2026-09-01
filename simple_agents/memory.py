"""A tiny in-memory store shared across agents in one workflow run."""

from __future__ import annotations

from typing import Any


class Memory:
    """Key-value memory plus a chronological event log."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._history: list[dict[str, str]] = []

    def remember(self, key: str, value: Any) -> None:
        self._store[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def add_event(self, agent: str, event: str) -> None:
        self._history.append({"agent": agent, "event": event})

    @property
    def history(self) -> list[dict[str, str]]:
        return list(self._history)

    def snapshot(self) -> dict[str, Any]:
        return {"store": dict(self._store), "history": list(self._history)}
