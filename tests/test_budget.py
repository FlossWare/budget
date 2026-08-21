"""Tests for InMemoryBudgetTracker."""

from __future__ import annotations

import pytest

from budget_ai import InMemoryBudgetTracker
from budget_ai.budget import _extract_provider
from budget_ai.types import TokenUsage


# -- _extract_provider -------------------------------------------------------


def test_extract_provider_with_slash():
    assert _extract_provider("openai/gpt-4o") == "openai"


def test_extract_provider_without_slash():
    assert _extract_provider("gpt-4o") == "gpt-4o"


def test_extract_provider_multiple_slashes():
    assert _extract_provider("openai/models/gpt-4o") == "openai"


# -- InMemoryBudgetTracker ---------------------------------------------------


@pytest.mark.asyncio
async def test_record_usage_basic():
    tracker = InMemoryBudgetTracker()
    usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    await tracker.record_usage("gpt-4o", usage)

    status = await tracker.remaining()
    assert status.tokens_used == 150
    assert status.cost_used == pytest.approx(150 * 0.01 / 1000)


@pytest.mark.asyncio
async def test_record_usage_with_task_id():
    tracker = InMemoryBudgetTracker()
    usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    await tracker.record_usage("gpt-4o", usage, task_id="task-1")

    report = await tracker.cost_report()
    assert "task-1" in report.by_task
    assert report.by_task["task-1"] == pytest.approx(150 * 0.01 / 1000)


@pytest.mark.asyncio
async def test_record_usage_multiple_models():
    tracker = InMemoryBudgetTracker()
    u1 = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    u2 = TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300)
    await tracker.record_usage("gpt-4o", u1)
    await tracker.record_usage("claude-sonnet", u2)

    report = await tracker.cost_report()
    assert len(report.by_model) == 2
    assert "gpt-4o" in report.by_model
    assert "claude-sonnet" in report.by_model
    assert report.total_cost == pytest.approx((150 + 300) * 0.01 / 1000)


@pytest.mark.asyncio
async def test_custom_model_rates():
    tracker = InMemoryBudgetTracker(
        model_rates={"gpt-4o": 0.03, "claude-sonnet": 0.015}
    )
    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    await tracker.record_usage("gpt-4o", usage)

    report = await tracker.cost_report()
    assert report.total_cost == pytest.approx(1000 * 0.03 / 1000)


@pytest.mark.asyncio
async def test_default_rate_fallback():
    tracker = InMemoryBudgetTracker(
        model_rates={"gpt-4o": 0.03}, default_rate=0.005
    )
    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    await tracker.record_usage("unknown-model", usage)

    report = await tracker.cost_report()
    assert report.total_cost == pytest.approx(1000 * 0.005 / 1000)


@pytest.mark.asyncio
async def test_set_budget_tokens():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_tokens=1000)

    status = await tracker.remaining()
    assert status.tokens_remaining == 1000


@pytest.mark.asyncio
async def test_set_budget_cost():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_cost=5.0)

    status = await tracker.remaining()
    assert status.cost_remaining == pytest.approx(5.0)


@pytest.mark.asyncio
async def test_remaining_decreases_after_usage():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_tokens=1000)

    usage = TokenUsage(prompt_tokens=300, completion_tokens=100, total_tokens=400)
    await tracker.record_usage("gpt-4o", usage)

    status = await tracker.remaining()
    assert status.tokens_remaining == 600


@pytest.mark.asyncio
async def test_remaining_never_negative():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_tokens=100)

    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    await tracker.record_usage("gpt-4o", usage)

    status = await tracker.remaining()
    assert status.tokens_remaining == 0


@pytest.mark.asyncio
async def test_no_budget_set_returns_none():
    tracker = InMemoryBudgetTracker()

    status = await tracker.remaining()
    assert status.tokens_remaining is None
    assert status.cost_remaining is None


@pytest.mark.asyncio
async def test_cost_report_by_provider():
    tracker = InMemoryBudgetTracker()
    u1 = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    u2 = TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300)
    await tracker.record_usage("openai/gpt-4o", u1)
    await tracker.record_usage("openai/gpt-4o-mini", u2)

    report = await tracker.cost_report()
    assert "openai" in report.by_provider
    assert report.by_provider["openai"] == pytest.approx((150 + 300) * 0.01 / 1000)


@pytest.mark.asyncio
async def test_cost_report_multiple_tasks():
    tracker = InMemoryBudgetTracker()
    u1 = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    u2 = TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300)
    await tracker.record_usage("gpt-4o", u1, task_id="task-a")
    await tracker.record_usage("gpt-4o", u2, task_id="task-b")

    report = await tracker.cost_report()
    assert len(report.by_task) == 2
    assert "task-a" in report.by_task
    assert "task-b" in report.by_task


@pytest.mark.asyncio
async def test_cost_report_no_task_id():
    tracker = InMemoryBudgetTracker()
    usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    await tracker.record_usage("gpt-4o", usage)

    report = await tracker.cost_report()
    assert len(report.by_task) == 0


@pytest.mark.asyncio
async def test_protocol_compliance():
    from budget_ai.protocols import BudgetTracker

    tracker = InMemoryBudgetTracker()
    assert isinstance(tracker, BudgetTracker)
