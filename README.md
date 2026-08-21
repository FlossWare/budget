# budget-ai

Token usage tracking, cost estimation, and budget enforcement for LLM applications.

## Features

- **Token tracking**: Record per-model, per-provider, per-task token consumption
- **Cost estimation**: Configurable per-model rates with fallback defaults
- **Budget enforcement**: Set token and cost limits, raise `BudgetExceeded` when exhausted
- **Decorator patterns**: `@track_budget` and `@enforce_budget` for async LLM calls
- **Zero dependencies**: Python stdlib only (ADR-0008)
- **Protocol-based**: `BudgetTracker` and `CostEstimator` via `typing.Protocol` (ADR-0020)

## Install

```bash
pip install "git+https://github.com/FlossWare/budget-ai.git"
```

## Quick Start

```python
import asyncio
from budget_ai import InMemoryBudgetTracker, SimpleCostEstimator, TokenUsage

async def main():
    tracker = InMemoryBudgetTracker(
        model_rates={"gpt-4o": 0.03, "claude-sonnet": 0.015}
    )
    await tracker.set_budget(max_tokens=100_000, max_cost=5.00)

    usage = TokenUsage(prompt_tokens=500, completion_tokens=200, total_tokens=700)
    await tracker.record_usage("gpt-4o", usage, task_id="summarize")

    status = await tracker.remaining()
    print(f"Tokens remaining: {status.tokens_remaining}")
    print(f"Cost remaining: ${status.cost_remaining:.4f}")

    report = await tracker.cost_report()
    print(f"Total cost: ${report.total_cost:.4f}")
    print(f"By model: {report.by_model}")

asyncio.run(main())
```

## Decorators

```python
from budget_ai import track_budget, enforce_budget, InMemoryBudgetTracker

tracker = InMemoryBudgetTracker()

@track_budget(tracker=tracker)
@enforce_budget(tracker=tracker)
async def my_llm_call(prompt: str, *, model: str = "gpt-4o"):
    return await backend.chat([{"role": "user", "content": prompt}], model=model)
```

## License

MIT
