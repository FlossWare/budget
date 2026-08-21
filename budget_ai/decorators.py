"""Convenience decorators for budget-ai (ADR-0006: Cross-Cutting Decorators).

Provides ``@track_budget`` and ``@enforce_budget`` decorators that wrap
async LLM call functions with automatic token usage recording and budget
enforcement.

Users must explicitly opt in by applying the decorator and configuring
the tracker (ADR-0001: Explicit Opt-In).
"""

from __future__ import annotations

import functools
from typing import Any, Callable

from budget_ai.types import BudgetExceeded, TokenUsage


def track_budget(
    *,
    tracker: Any,
    model_kwarg: str = "model",
    task_id: str | None = None,
) -> Callable:
    """Decorator that records token usage after each async LLM call.

    The decorated function must return an object with a ``usage`` dict
    containing ``prompt_tokens``, ``completion_tokens``, and
    ``total_tokens`` keys (standard LLM response format).

    Parameters
    ----------
    tracker:
        A :class:`~budget_ai.protocols.BudgetTracker` implementation.
    model_kwarg:
        Name of the keyword argument that carries the model identifier
        (default ``"model"``).
    task_id:
        Optional task identifier to associate with the recorded usage.
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await fn(*args, **kwargs)

            model = kwargs.get(model_kwarg, "unknown")
            if isinstance(result, dict):
                usage_dict = result.get("usage", {})
            else:
                usage_dict = getattr(result, "usage", {})
            if isinstance(usage_dict, dict) and "total_tokens" in usage_dict:
                usage = TokenUsage(
                    prompt_tokens=usage_dict.get("prompt_tokens", 0),
                    completion_tokens=usage_dict.get("completion_tokens", 0),
                    total_tokens=usage_dict["total_tokens"],
                )
                await tracker.record_usage(model, usage, task_id=task_id)

            return result

        return wrapper

    return decorator


def enforce_budget(
    *,
    tracker: Any,
) -> Callable:
    """Decorator that checks budget before each async LLM call.

    Raises :class:`~budget_ai.types.BudgetExceeded` if the tracker
    reports that either the token or cost budget has been exhausted.

    Parameters
    ----------
    tracker:
        A :class:`~budget_ai.protocols.BudgetTracker` implementation.
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            status = await tracker.remaining()

            if status.tokens_remaining is not None and status.tokens_remaining <= 0:
                raise BudgetExceeded(status, "Token budget exhausted")

            if status.cost_remaining is not None and status.cost_remaining <= 0.0:
                raise BudgetExceeded(status, "Cost budget exhausted")

            return await fn(*args, **kwargs)

        return wrapper

    return decorator
