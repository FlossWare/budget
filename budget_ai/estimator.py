"""Simple cost estimator for budget-ai.

Provides a configurable per-model cost estimator that satisfies the
:class:`~budget_ai.protocols.CostEstimator` protocol via structural
subtyping.

Classes
-------
SimpleCostEstimator -- per-model cost estimation with configurable rates
"""

from __future__ import annotations

from budget_ai.types import TokenUsage

_DEFAULT_RATE_PER_1K = 0.01


class SimpleCostEstimator:
    """Estimate cost for model invocations using per-model rates.

    Satisfies :class:`~budget_ai.protocols.CostEstimator` via
    structural subtyping.

    Parameters
    ----------
    model_rates:
        Mapping of model name to cost-per-1k-tokens.  Models not
        listed fall back to *default_rate*.
    default_rate:
        Cost charged per 1 000 tokens for unlisted models.
    """

    def __init__(
        self,
        *,
        model_rates: dict[str, float] | None = None,
        default_rate: float = _DEFAULT_RATE_PER_1K,
    ) -> None:
        self._model_rates: dict[str, float] = dict(model_rates or {})
        self._default_rate = default_rate

    def rate_for(self, model: str) -> float:
        """Return the per-1k-token rate for *model*."""
        return self._model_rates.get(model, self._default_rate)

    def estimate(self, model: str, usage: TokenUsage) -> float:
        """Return the estimated cost for a model invocation."""
        return usage.total_tokens * self.rate_for(model) / 1000.0

    def estimate_prompt(self, model: str, prompt_tokens: int) -> float:
        """Estimate cost for prompt tokens only."""
        return prompt_tokens * self.rate_for(model) / 1000.0

    def estimate_completion(self, model: str, completion_tokens: int) -> float:
        """Estimate cost for completion tokens only."""
        return completion_tokens * self.rate_for(model) / 1000.0
