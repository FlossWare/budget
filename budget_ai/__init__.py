"""budget-ai -- Token usage tracking, cost estimation, and budget enforcement for LLM applications.

Public API
----------
Types:
    ChatMessage, ChatResponse, TokenUsage, BudgetStatus,
    CostReport, BudgetExceeded

Protocols:
    BudgetTracker, CostEstimator, LLMBackend

Budget Tracking:
    InMemoryBudgetTracker

Cost Estimation:
    SimpleCostEstimator

Decorators (ADR-0006):
    track_budget, enforce_budget
"""

from __future__ import annotations

from budget_ai.budget import InMemoryBudgetTracker
from budget_ai.decorators import enforce_budget, track_budget
from budget_ai.estimator import SimpleCostEstimator
from budget_ai.protocols import BudgetTracker, CostEstimator, LLMBackend
from budget_ai.types import (
    BudgetExceeded,
    BudgetStatus,
    ChatMessage,
    ChatResponse,
    CostReport,
    TokenUsage,
)

__all__ = [
    "BudgetExceeded",
    "BudgetStatus",
    "BudgetTracker",
    "ChatMessage",
    "ChatResponse",
    "CostEstimator",
    "CostReport",
    "InMemoryBudgetTracker",
    "LLMBackend",
    "SimpleCostEstimator",
    "TokenUsage",
    "enforce_budget",
    "track_budget",
]

__version__ = "0.1"
