#!/bin/bash
if git status --porcelain | grep -q '\.py$'; then
  docker compose exec -T app ruff check --fix .
  docker compose exec -T app ruff format .
fi
