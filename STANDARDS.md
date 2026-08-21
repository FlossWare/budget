# FlossWare Engineering Standards Compliance

This package adheres to the following ADRs from [FlossWare/engineering-standards](https://github.com/FlossWare/engineering-standards):

## ADR-0001: Explicit Opt-In

Budget tracking, cost estimation, and budget enforcement never activate automatically.
All capabilities require explicit instantiation or decorator application by the developer.

- `InMemoryBudgetTracker` must be instantiated and methods called explicitly.
- `SimpleCostEstimator` must be instantiated with model rates.
- `@track_budget` and `@enforce_budget` decorators are opt-in.
- When no budget is set, tracking runs without enforcement (unlimited mode).

## ADR-0006: Cross-Cutting Decorators

Convenience decorators in `budget_ai.decorators`:

- `@track_budget(tracker=t)` -- wraps an async LLM call to auto-record token usage from the response.
- `@enforce_budget(tracker=t)` -- checks budget limits before each call, raises `BudgetExceeded` if exhausted.

## ADR-0008: Free-First

Zero external dependencies at runtime. The package uses only the Python standard library (`asyncio`, `dataclasses`, `functools`, `typing`).

Development dependencies (pytest, pytest-asyncio) are optional.

## ADR-0009: Core Principles

- **Modular**: Each concern (tracking, estimation, enforcement) is a separate module.
- **Composable**: Components can be used independently or combined.
- **Contracts over implementations**: The `BudgetTracker` and `CostEstimator` Protocols define the interfaces; any conforming object works.

## ADR-0014: Token Budget Management

`InMemoryBudgetTracker` implements the token budget management described in ADR-0014:

- Tracks token usage per model, provider, and task.
- Supports configurable per-model cost rates.
- Budget limits (token and cost) with enforcement via `@enforce_budget`.
- Cost reports with breakdowns by model, provider, and task.
- Provider extraction from model identifiers (e.g., `openai/gpt-4o` -> `openai`).

## ADR-0017: Agent-Neutral

The package works with any agent runtime. The `LLMBackend` Protocol is the only integration point -- any agent framework that can provide an async `chat()` method is compatible.

No assumptions are made about the calling agent's architecture, event loop, or lifecycle.

## ADR-0020: Capability-Protocol Separation

Budget capabilities are transport-independent:

- `BudgetTracker` and `CostEstimator` Protocols define what is needed, not how it is delivered.
- No HTTP, gRPC, or other transport assumptions baked in.
- The same budget logic works whether the backend is a local mock, an API client, or an agent-internal router.
