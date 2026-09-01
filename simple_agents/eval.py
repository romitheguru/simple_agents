"""Lightweight evaluation helpers for agent outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class EvalResult:
    passed: bool
    score: float
    message: str


class Evaluator:
    """Run simple checks on agent completions."""

    def check_nonempty(self, text: str) -> EvalResult:
        passed = bool(text and text.strip())
        return EvalResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            message="response is non-empty" if passed else "response is empty",
        )

    def check_contains(self, text: str, substring: str) -> EvalResult:
        passed = substring.lower() in text.lower()
        return EvalResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            message=f"contains '{substring}'" if passed else f"missing '{substring}'",
        )

    def check_min_length(self, text: str, min_len: int) -> EvalResult:
        passed = len(text.strip()) >= min_len
        return EvalResult(
            passed=passed,
            score=min(1.0, len(text.strip()) / max(min_len, 1)),
            message=f"length >= {min_len}" if passed else f"length < {min_len}",
        )

    def run_all(self, text: str, checks: list[Callable[[str], EvalResult]]) -> list[EvalResult]:
        return [check(text) for check in checks]
