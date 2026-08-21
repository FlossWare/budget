#!/bin/bash
# Install budget-ai from GitHub
set -e

pip install "git+https://github.com/FlossWare/budget-ai.git"

echo "budget-ai installed successfully"
echo "Verify: python3 -c 'import budget_ai; print(budget_ai.__version__)'"
