"""Shared data types for the budget-ai package.

All types are plain ``dataclasses`` with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Token counts for a single LLM invocation."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class BudgetStatus:
    """Current budget consumption and remaining allowance."""

    tokens_used: int
    tokens_remaining: int | None
    cost_used: float
    cost_remaining: float | None


@dataclass
class CostReport:
    """Aggregated cost breakdown across models, providers, and tasks."""

    total_cost: float
    by_model: dict[str, float] = field(default_factory=dict)
    by_provider: dict[str, float] = field(default_factory=dict)
    by_task: dict[str, float] = field(default_factory=dict)


@dataclass
class ChatMessage:
    """A single chat message exchanged with a language model."""

    role: str
    content: str


@dataclass
class ChatResponse:
    """Response returned by an LLM backend."""

    content: str
    model: str = ""
    provider: str = ""
    usage: dict = field(default_factory=dict)


class BudgetExceeded(Exception):
    """Raised when a budget limit (token or cost) has been exceeded."""

    def __init__(self, status: BudgetStatus, message: str = "") -> None:
        self.status = status
        super().__init__(message or f"Budget exceeded: {status}")
