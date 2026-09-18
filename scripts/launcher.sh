#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/.local/share/InventorySystem"
VENV_PY="$APP_DIR/venv/bin/python"

if [ "${1:-}" = "--version" ]; then
    git -C "$APP_DIR/repo" describe --tags --always
    exit 0
fi

if [ "${1:-}" = "update" ]; then
    exec bash "$APP_DIR/repo/scripts/update.sh"
fi

cd "$APP_DIR/repo/src"
"$VENV_PY" main.py "$@"
status=$?

if [ "$status" -eq 42 ]; then
    echo "Server requested an update, updating now..."
    bash "$APP_DIR/repo/scripts/update.sh"
    exec "$VENV_PY" "$APP_DIR/repo/main.py" "$@"
fi

exit "$status"