#!/bin/bash
if git status --porcelain | grep -q '\.py$'; then
  .venv/bin/ruff check --fix .
  .venv/bin/ruff format .
fi
