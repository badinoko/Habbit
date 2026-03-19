#!/usr/bin/env sh
set -eu

HOST="${APP_HOST:-0.0.0.0}"
PORT="${APP_PORT:-8000}"

case "${DEBUG:-false}" in
  [Tt]rue|1)
    exec uvicorn src.main:app --host "$HOST" --port "$PORT" --reload
    ;;
  *)
    exec uvicorn src.main:app --host "$HOST" --port "$PORT"
    ;;
esac
