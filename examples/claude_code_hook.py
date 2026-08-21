#!/usr/bin/env python3
"""Claude Code hook example: warn about budget status after LLM-related edits."""
from __future__ import annotations

import sys

EXPENSIVE_KEYWORDS = ["llm", "model", "api", "chat", "completion", "generate"]


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    file_path = sys.argv[1].lower()
    if any(kw in file_path for kw in EXPENSIVE_KEYWORDS):
        print(f"[budget-ai] LLM-related file edited: {sys.argv[1]}")
        print("[budget-ai] Ensure budget tracking is enabled:")
        print("  from budget_ai import track_budget, enforce_budget")
        print("  @track_budget(tracker=tracker)")
        print("  @enforce_budget(tracker=tracker)")


if __name__ == "__main__":
    main()
