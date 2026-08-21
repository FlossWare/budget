"""Tests for budget-ai decorators."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from budget_ai import InMemoryBudgetTracker, enforce_budget, track_budget
from budget_ai.types import BudgetExceeded, TokenUsage


@dataclass
class MockResponse:
    content: str = "hello"
    model: str = "gpt-4o"
    usage: dict = field(default_factory=lambda: {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
    })


# -- @track_budget -----------------------------------------------------------


@pytest.mark.asyncio
async def test_track_budget_records_usage():
    tracker = InMemoryBudgetTracker()

    @track_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    result = await my_llm_call("hello", model="gpt-4o")
    assert result.content == "hello"

    status = await tracker.remaining()
    assert status.tokens_used == 150


@pytest.mark.asyncio
async def test_track_budget_custom_model_kwarg():
    tracker = InMemoryBudgetTracker()

    @track_budget(tracker=tracker, model_kwarg="llm_model")
    async def my_llm_call(prompt: str, *, llm_model: str = "gpt-4o"):
        return MockResponse(model=llm_model)

    await my_llm_call("hello", llm_model="claude-sonnet")

    report = await tracker.cost_report()
    assert "claude-sonnet" in report.by_model


@pytest.mark.asyncio
async def test_track_budget_with_task_id():
    tracker = InMemoryBudgetTracker()

    @track_budget(tracker=tracker, task_id="summarize")
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    await my_llm_call("hello")

    report = await tracker.cost_report()
    assert "summarize" in report.by_task


@pytest.mark.asyncio
async def test_track_budget_no_usage_in_response():
    tracker = InMemoryBudgetTracker()

    @track_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return type("Resp", (), {"content": "hi", "usage": {}})()

    await my_llm_call("hello")

    status = await tracker.remaining()
    assert status.tokens_used == 0


@pytest.mark.asyncio
async def test_track_budget_no_usage_attr():
    tracker = InMemoryBudgetTracker()

    @track_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return "raw string"

    await my_llm_call("hello")

    status = await tracker.remaining()
    assert status.tokens_used == 0


@pytest.mark.asyncio
async def test_track_budget_multiple_calls():
    tracker = InMemoryBudgetTracker()

    @track_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    await my_llm_call("hello", model="gpt-4o")
    await my_llm_call("world", model="gpt-4o")

    status = await tracker.remaining()
    assert status.tokens_used == 300


# -- @enforce_budget ---------------------------------------------------------


@pytest.mark.asyncio
async def test_enforce_budget_allows_within_limit():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_tokens=1000)

    @enforce_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    result = await my_llm_call("hello")
    assert result.content == "hello"


@pytest.mark.asyncio
async def test_enforce_budget_raises_on_token_exceeded():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_tokens=100)

    usage = TokenUsage(prompt_tokens=50, completion_tokens=60, total_tokens=110)
    await tracker.record_usage("gpt-4o", usage)

    @enforce_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    with pytest.raises(BudgetExceeded, match="Token budget exhausted"):
        await my_llm_call("hello")


@pytest.mark.asyncio
async def test_enforce_budget_raises_on_cost_exceeded():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_cost=0.001)

    usage = TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000)
    await tracker.record_usage("gpt-4o", usage)

    @enforce_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    with pytest.raises(BudgetExceeded, match="Cost budget exhausted"):
        await my_llm_call("hello")


@pytest.mark.asyncio
async def test_enforce_budget_no_limit_set():
    tracker = InMemoryBudgetTracker()

    @enforce_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    result = await my_llm_call("hello")
    assert result.content == "hello"


@pytest.mark.asyncio
async def test_combined_track_and_enforce():
    tracker = InMemoryBudgetTracker()
    await tracker.set_budget(max_tokens=200)

    @track_budget(tracker=tracker)
    @enforce_budget(tracker=tracker)
    async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
        return MockResponse(model=model)

    result = await my_llm_call("hello")
    assert result.content == "hello"

    status = await tracker.remaining()
    assert status.tokens_used == 150
    assert status.tokens_remaining == 50

    # Second call: enforce_budget sees 50 remaining (>0), allows the call.
    # track_budget then records 150 more, total = 300, remaining clamped to 0.
    result2 = await my_llm_call("second call goes through, but exhausts budget")
    assert result2.content == "hello"

    status2 = await tracker.remaining()
    assert status2.tokens_used == 300
    assert status2.tokens_remaining == 0

    # Third call: enforce_budget sees 0 remaining, raises BudgetExceeded.
    with pytest.raises(BudgetExceeded):
        await my_llm_call("third call blocked")
