#!/bin/bash
# Add budget-ai integration to your CLAUDE.md
set -e

CLAUDE_MD="${CLAUDE_MD:-./CLAUDE.md}"

if [ ! -f "$CLAUDE_MD" ]; then
    echo "Creating $CLAUDE_MD"
    touch "$CLAUDE_MD"
fi

cat >> "$CLAUDE_MD" << 'EOF'

## Budget Tracking (budget-ai)

This project uses [budget-ai](https://github.com/FlossWare/budget-ai) for token usage tracking and cost management.

**Install:** `pip install "git+https://github.com/FlossWare/budget-ai.git"`

**Key imports:**
```python
from budget_ai import InMemoryBudgetTracker, SimpleCostEstimator, TokenUsage, track_budget, enforce_budget
```

**Usage patterns:**
- Tracker: `InMemoryBudgetTracker(model_rates={"gpt-4o": 0.03})`
- Budget: `await tracker.set_budget(max_tokens=100_000, max_cost=5.00)`
- Record: `await tracker.record_usage("gpt-4o", usage, task_id="task-1")`
- Decorator: `@track_budget(tracker=t)` auto-records usage from responses
- Enforcement: `@enforce_budget(tracker=t)` raises `BudgetExceeded`
- Reports: `await tracker.cost_report()` for model/provider/task breakdowns
- Zero external dependencies (stdlib only)
EOF

echo "Added budget-ai integration to $CLAUDE_MD"
