#!/bin/bash
if git status --porcelain | grep -q '\.py$'; then
  make format
fi
