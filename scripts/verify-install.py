#!/usr/bin/env python3
"""Verify budget-ai installation and run a quick smoke test."""
import sys


def main():
    try:
        from budget_ai import (
            BudgetExceeded,
            BudgetStatus,
            BudgetTracker,
            ChatMessage,
            ChatResponse,
            CostEstimator,
            CostReport,
            InMemoryBudgetTracker,
            LLMBackend,
            SimpleCostEstimator,
            TokenUsage,
            enforce_budget,
            track_budget,
        )
    except ImportError as e:
        print(f"FAIL: Could not import budget_ai: {e}")
        print("Install: pip install 'git+https://github.com/FlossWare/budget-ai.git'")
        sys.exit(1)

    import budget_ai

    print(f"budget-ai v{budget_ai.__version__} installed successfully")
    print(f"Exports: {len(budget_ai.__all__)} public symbols")

    # Smoke test: create tracker
    tracker = InMemoryBudgetTracker(model_rates={"gpt-4o": 0.03})
    print(f"Smoke test: InMemoryBudgetTracker created: {tracker}")

    # Smoke test: create estimator
    estimator = SimpleCostEstimator(model_rates={"gpt-4o": 0.03})
    usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    cost = estimator.estimate("gpt-4o", usage)
    print(f"Smoke test: estimate('gpt-4o', 150 tokens) = ${cost:.6f}")

    # Smoke test: protocol compliance
    assert isinstance(tracker, BudgetTracker), "tracker must satisfy BudgetTracker"
    assert isinstance(estimator, CostEstimator), "estimator must satisfy CostEstimator"
    print("Smoke test: protocol compliance verified")

    # Smoke test: decorators callable
    assert callable(track_budget), "track_budget must be callable"
    assert callable(enforce_budget), "enforce_budget must be callable"
    print("Smoke test: decorators are callable")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
