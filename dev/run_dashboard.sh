#!/usr/bin/env bash
# Local Web dashboard (reads DB config from project root .env)
set -euo pipefail
DEV_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DEV_DIR/.." && pwd)"
REQ_FILE="$DEV_DIR/requirements-dashboard.txt"
ENV_FILE="$ROOT/.env"

read_dashboard_port() {
  local port=8080
  if [[ -f "$ENV_FILE" ]]; then
    local val
    val="$(grep -E '^[[:space:]]*WEB_DASHBOARD_PORT[[:space:]]*=' "$ENV_FILE" | tail -1 | sed -E 's/^[^=]*=[[:space:]]*"?([0-9]+)"?.*/\1/')"
    [[ -n "$val" ]] && port="$val"
  fi
  echo "$port"
}

stop_listen_port() {
  local port="$1"
  local pids=""
  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  elif command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" 2>/dev/null && return 0 || true
  elif [[ "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* ]]; then
    pids="$(netstat -ano 2>/dev/null | grep ":${port} " | grep LISTENING | awk '{print $NF}' | sort -u || true)"
  fi
  if [[ -n "$pids" ]]; then
    echo "[INFO] Port ${port} in use, stopping: ${pids}"
    # shellcheck disable=SC2086
    kill -9 $pids 2>/dev/null || true
    sleep 0.5
  fi
}

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[hint] No .env found. Copy: cp example.env .env"
fi

PORT="$(read_dashboard_port)"
stop_listen_port "$PORT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

if ! "$PYTHON" -c "import fastapi" 2>/dev/null; then
  echo "[INFO] Installing dashboard deps: $REQ_FILE"
  "$PYTHON" -m pip install -r "$REQ_FILE"
fi

cd "$ROOT/scripts"
export PYTHONUNBUFFERED=1

cleanup() {
  if [[ -n "${DASH_PID:-}" ]] && kill -0 "$DASH_PID" 2>/dev/null; then
    kill -INT "$DASH_PID" 2>/dev/null || kill -TERM "$DASH_PID" 2>/dev/null || true
    wait "$DASH_PID" 2>/dev/null || true
  fi
}
trap cleanup INT TERM

"$PYTHON" -u run_dashboard.py &
DASH_PID=$!
wait "$DASH_PID"
exit $?
