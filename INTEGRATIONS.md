# budget-ai Integrations

Install from GitHub:

```bash
pip install "git+https://github.com/FlossWare/budget-ai.git"
```

---

## Claude Code

### CLAUDE.md Snippet

```markdown
## Budget Tracking (budget-ai)

This project uses `budget-ai` for token usage tracking and cost management.

- Tracker: `from budget_ai import InMemoryBudgetTracker, TokenUsage`
- Estimator: `from budget_ai import SimpleCostEstimator`
- Decorators: `from budget_ai import track_budget, enforce_budget`
- Use `@track_budget(tracker=t)` to auto-record token usage from LLM responses
- Use `@enforce_budget(tracker=t)` to raise `BudgetExceeded` when limits hit
- Zero external dependencies (stdlib only)
```

### Hook Example

Create `.claude/hooks/post-tool-edit.py` to warn about costly operations:

```python
#!/usr/bin/env python3
"""Post-edit hook: flag files that involve expensive model calls."""
from __future__ import annotations

import sys

EXPENSIVE_PATTERNS = ["gpt-4o", "claude-opus", "gemini-pro"]


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    file_path = sys.argv[1].lower()
    if any(p in file_path for p in ["llm", "model", "api", "chat"]):
        print(f"[budget-ai] LLM-related file: {sys.argv[1]}")
        print("[budget-ai] Consider adding budget tracking:")
        print("  from budget_ai import track_budget, enforce_budget")


if __name__ == "__main__":
    main()
```

### Skill Example

Create `.claude/skills/budget-check.md`:

```markdown
---
name: budget-check
description: Check current LLM budget status and cost breakdown
---

Use budget-ai to check token budget and cost:

\```python
import asyncio
from budget_ai import InMemoryBudgetTracker

tracker = InMemoryBudgetTracker()
status = asyncio.run(tracker.remaining())
report = asyncio.run(tracker.cost_report())
print(f"Tokens used: {status.tokens_used}")
print(f"Cost: ${report.total_cost:.4f}")
print(f"By model: {report.by_model}")
\```
```

---

## OpenAI Codex

### AGENTS.md Snippet

```markdown
## Budget Management

Use budget-ai for token tracking and cost control:
- Install: `pip install "git+https://github.com/FlossWare/budget-ai.git"`
- Tracker: `InMemoryBudgetTracker(model_rates={"gpt-4o": 0.03})`
- Decorator: `@track_budget(tracker=t)` auto-records usage
- Enforcement: `@enforce_budget(tracker=t)` raises `BudgetExceeded`
- Reports: `await tracker.cost_report()` for model/provider/task breakdowns
```

### Tool Definition

```python
from budget_ai import InMemoryBudgetTracker, SimpleCostEstimator, TokenUsage

tracker = InMemoryBudgetTracker(model_rates={"gpt-4o": 0.03, "gpt-4o-mini": 0.0002})
await tracker.set_budget(max_tokens=500_000, max_cost=10.00)

usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
await tracker.record_usage("gpt-4o", usage, task_id="code-review")

report = await tracker.cost_report()
print(f"Total: ${report.total_cost:.4f}")
print(f"By task: {report.by_task}")
```

---

## Cursor

### .cursorrules Snippet

```
When making LLM calls, use budget-ai for cost tracking:

- Import: from budget_ai import track_budget, enforce_budget, InMemoryBudgetTracker
- Tracker: InMemoryBudgetTracker(model_rates={"gpt-4o": 0.03})
- Decorator: @track_budget(tracker=t) to auto-record token usage
- Enforcement: @enforce_budget(tracker=t) to prevent budget overruns
- Reports: await tracker.cost_report() for breakdowns
- Zero dependencies - stdlib only
- Install: pip install "git+https://github.com/FlossWare/budget-ai.git"
```

---

## Crush

### Configuration

```python
# crush.config.py
from budget_ai import InMemoryBudgetTracker, SimpleCostEstimator, TokenUsage

tracker = InMemoryBudgetTracker(
    model_rates={
        "gpt-4o": 0.03,
        "gpt-4o-mini": 0.0002,
        "claude-sonnet": 0.015,
    }
)

estimator = SimpleCostEstimator(
    model_rates={
        "gpt-4o": 0.03,
        "gpt-4o-mini": 0.0002,
        "claude-sonnet": 0.015,
    }
)


async def check_budget():
    """Check remaining budget before expensive operations."""
    status = await tracker.remaining()
    if status.cost_remaining is not None and status.cost_remaining < 0.50:
        print(f"WARNING: Only ${status.cost_remaining:.2f} remaining")
    return status
```

---

## Generic Python Agent

### Budget Tracking

```python
import asyncio
from budget_ai import (
    InMemoryBudgetTracker,
    SimpleCostEstimator,
    TokenUsage,
    track_budget,
    enforce_budget,
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
    await tracker.set_budget(max_tokens=1_000_000, max_cost=25.00)

    # 2. Record usage from LLM calls
    usage = TokenUsage(prompt_tokens=2000, completion_tokens=500, total_tokens=2500)
    await tracker.record_usage("gpt-4o", usage, task_id="code-gen")

    # 3. Check status
    status = await tracker.remaining()
    print(f"Tokens used: {status.tokens_used:,}")
    print(f"Tokens remaining: {status.tokens_remaining:,}")
    print(f"Cost used: ${status.cost_used:.4f}")
    print(f"Cost remaining: ${status.cost_remaining:.4f}")

    # 4. Get cost breakdown
    report = await tracker.cost_report()
    print(f"\nTotal cost: ${report.total_cost:.4f}")
    for model, cost in report.by_model.items():
        print(f"  {model}: ${cost:.4f}")


asyncio.run(main())
```

### Decorator Pattern

```python
from budget_ai import track_budget, enforce_budget, InMemoryBudgetTracker

tracker = InMemoryBudgetTracker(model_rates={"gpt-4o": 0.03})

@track_budget(tracker=tracker)
@enforce_budget(tracker=tracker)
async def generate_code(prompt: str, *, model: str = "gpt-4o"):
    """Token usage is tracked and budget is enforced automatically."""
    return await backend.chat([{"role": "user", "content": prompt}], model=model)
```

---

## Cross-Package Integration

### budget-ai + resilience-ai

Track costs with retry resilience:

```python
from budget_ai import track_budget, enforce_budget
from resilience_ai import with_retry, with_circuit_breaker

@track_budget(tracker=tracker)
@enforce_budget(tracker=tracker)
@with_retry(max_attempts=3)
@with_circuit_breaker(provider="openai")
async def resilient_call(prompt: str, *, model: str = "gpt-4o"):
    return await backend.chat([{"role": "user", "content": prompt}], model=model)
```

### budget-ai + observability-ai

Track costs alongside execution telemetry:

```python
from budget_ai import track_budget
from observability_ai import track_execution

@track_budget(tracker=budget_tracker)
@track_execution(telemetry=telemetry)
async def monitored_call(prompt: str, *, model: str = "gpt-4o"):
    return await backend.chat([{"role": "user", "content": prompt}], model=model)
```

### Full Stack: All Packages

```python
from budget_ai import track_budget, enforce_budget
from evaluation_ai import adversarial_verify
from consensus_ai import with_consensus
from structured_output_ai import structured_output
from resilience_ai import with_retry, with_circuit_breaker
from observability_ai import track_execution

@structured_output(schema=SCHEMA)       # parse into typed object
@track_budget(tracker=budget)           # track token costs
@track_execution(telemetry=t)           # track timing
@adversarial_verify(backend=eval_b)     # verify correctness
@with_consensus(models=models)          # multi-model vote
@enforce_budget(tracker=budget)         # check budget first
@with_retry(max_attempts=3)             # retry on failure
@with_circuit_breaker(provider="llm")   # circuit break per provider
async def production_query(prompt, *, model="default"):
    return await backend.chat([{"role": "user", "content": prompt}], model=model)
```
