#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="$(pwd)"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
