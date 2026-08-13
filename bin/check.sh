#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$DIR/.venv/bin"

echo "==> Running concise checks..."
$VENV/ruff check --quiet src tests
$VENV/mypy --no-error-summary src/asciidoctype
$VENV/pytest -q --tb=short
echo "==> All checks passed cleanly!"
