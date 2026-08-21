"""Tests for SimpleCostEstimator."""

from __future__ import annotations

import pytest

from budget_ai import SimpleCostEstimator
from budget_ai.protocols import CostEstimator
from budget_ai.types import TokenUsage


def test_estimate_default_rate():
    estimator = SimpleCostEstimator()
    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    cost = estimator.estimate("gpt-4o", usage)
    assert cost == pytest.approx(1000 * 0.01 / 1000)


def test_estimate_custom_rate():
    estimator = SimpleCostEstimator(model_rates={"gpt-4o": 0.03})
    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    cost = estimator.estimate("gpt-4o", usage)
    assert cost == pytest.approx(1000 * 0.03 / 1000)


def test_estimate_fallback_rate():
    estimator = SimpleCostEstimator(
        model_rates={"gpt-4o": 0.03}, default_rate=0.005
    )
    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    cost = estimator.estimate("unknown-model", usage)
    assert cost == pytest.approx(1000 * 0.005 / 1000)


def test_estimate_prompt_only():
    estimator = SimpleCostEstimator(model_rates={"gpt-4o": 0.03})
    cost = estimator.estimate_prompt("gpt-4o", 1000)
    assert cost == pytest.approx(1000 * 0.03 / 1000)


def test_estimate_completion_only():
    estimator = SimpleCostEstimator(model_rates={"gpt-4o": 0.06})
    cost = estimator.estimate_completion("gpt-4o", 500)
    assert cost == pytest.approx(500 * 0.06 / 1000)


def test_rate_for():
    estimator = SimpleCostEstimator(
        model_rates={"gpt-4o": 0.03, "claude-sonnet": 0.015}
    )
    assert estimator.rate_for("gpt-4o") == 0.03
    assert estimator.rate_for("claude-sonnet") == 0.015
    assert estimator.rate_for("unknown") == 0.01


def test_zero_tokens():
    estimator = SimpleCostEstimator()
    usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    cost = estimator.estimate("gpt-4o", usage)
    assert cost == 0.0


def test_protocol_compliance():
    estimator = SimpleCostEstimator()
    assert isinstance(estimator, CostEstimator)


def test_multiple_model_rates():
    estimator = SimpleCostEstimator(
        model_rates={
            "gpt-4o": 0.03,
            "gpt-4o-mini": 0.0002,
            "claude-opus": 0.075,
        }
    )
    u1 = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    assert estimator.estimate("gpt-4o", u1) == pytest.approx(0.03)
    assert estimator.estimate("gpt-4o-mini", u1) == pytest.approx(0.0002)
    assert estimator.estimate("claude-opus", u1) == pytest.approx(0.075)
