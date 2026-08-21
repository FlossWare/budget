"""Budget tracker and cost estimator protocols for budget-ai.

Defines the structural interfaces that any backend must satisfy in order
to be used with the budget tracking and cost estimation utilities.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from budget_ai.types import BudgetStatus, ChatMessage, ChatResponse, CostReport, TokenUsage


@runtime_checkable
class BudgetTracker(Protocol):
    """Protocol for asynchronous budget trackers.

    Any object that provides ``record_usage``, ``remaining``,
    ``set_budget``, and ``cost_report`` methods with the following
    signatures satisfies this protocol via structural subtyping.
    """

    async def record_usage(
        self, model: str, usage: TokenUsage, *, task_id: str | None = None
    ) -> None:
        """Record token consumption for a model invocation."""
        ...

    async def remaining(self) -> BudgetStatus:
        """Return the current budget status."""
        ...

    async def set_budget(
        self, *, max_tokens: int | None = None, max_cost: float | None = None
    ) -> None:
        """Set or update budget limits."""
        ...

    async def cost_report(self) -> CostReport:
        """Return an aggregated cost breakdown."""
        ...


@runtime_checkable
class CostEstimator(Protocol):
    """Protocol for token cost estimation.

    Any object that provides a ``estimate`` method satisfies this
    protocol via structural subtyping.
    """

    def estimate(self, model: str, usage: TokenUsage) -> float:
        """Return the estimated cost for a model invocation."""
        ...


@runtime_checkable
class LLMBackend(Protocol):
    """Protocol for asynchronous LLM backends.

    Any object that provides an async ``chat`` method with the
    following signature satisfies this protocol via structural
    subtyping.
    """

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str = "",
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send *messages* to the specified *model* and return a response."""
        ...
