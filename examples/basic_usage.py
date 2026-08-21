#!/usr/bin/env python3
"""Basic budget-ai usage: token tracking, cost estimation, and budget enforcement."""
from __future__ import annotations

import asyncio

from budget_ai import (
    InMemoryBudgetTracker,
    SimpleCostEstimator,
    TokenUsage,
)


async def main():
    # 1. Configure tracker with per-model rates
    tracker = InMemoryBudgetTracker(
        model_rates={
            "gpt-4o": 0.03,
            "gpt-4o-mini": 0.0002,
            "claude-sonnet": 0.015,
            "gemini-flash": 0.0001,
        }
    )
    await tracker.set_budget(max_tokens=100_000, max_cost=5.00)

    # 2. Record some usage
    usages = [
        ("gpt-4o", TokenUsage(2000, 500, 2500), "code-gen"),
        ("claude-sonnet", TokenUsage(1500, 300, 1800), "review"),
        ("gpt-4o-mini", TokenUsage(5000, 1000, 6000), "summarize"),
    ]
    for model, usage, task in usages:
        await tracker.record_usage(model, usage, task_id=task)

    # 3. Check status
    status = await tracker.remaining()
    print("Budget Status:")
    print(f"  Tokens used: {status.tokens_used:,}")
    print(f"  Tokens remaining: {status.tokens_remaining:,}")
    print(f"  Cost used: ${status.cost_used:.4f}")
    print(f"  Cost remaining: ${status.cost_remaining:.4f}")

    # 4. Cost report
    report = await tracker.cost_report()
    print(f"\nCost Report (total: ${report.total_cost:.4f}):")
    print("  By model:")
    for model, cost in report.by_model.items():
        print(f"    {model}: ${cost:.6f}")
    print("  By provider:")
    for provider, cost in report.by_provider.items():
        print(f"    {provider}: ${cost:.6f}")
    print("  By task:")
    for task, cost in report.by_task.items():
        print(f"    {task}: ${cost:.6f}")

    # 5. Cost estimator
    estimator = SimpleCostEstimator(
        model_rates={"gpt-4o": 0.03, "gpt-4o-mini": 0.0002}
    )
    future_usage = TokenUsage(10000, 5000, 15000)
    est_cost = estimator.estimate("gpt-4o", future_usage)
    print(f"\nEstimated cost for 15K tokens on gpt-4o: ${est_cost:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
