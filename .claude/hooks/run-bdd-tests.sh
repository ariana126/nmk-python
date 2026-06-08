#!/bin/bash
if git status --porcelain | grep -q '^.. src/'; then
  output=$(PYTHONPATH=src .venv/bin/pytest features/ -v -m "not wip" 2>&1)
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "$output"
  fi
  exit $exit_code
fi
