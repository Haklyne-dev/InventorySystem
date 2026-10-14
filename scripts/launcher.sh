#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/.local/share/InventorySystem"

if [ -d "$APP_DIR/venv/Scripts" ]; then
    VENV_BIN="$APP_DIR/venv/Scripts"
else
    VENV_BIN="$APP_DIR/venv/bin"
fi

if [[ "${1:-}" = "--version" || "${1:-}" = "-v" ]]; then
    git -C "$APP_DIR/repo" describe --tags --always
    exit 0
fi

if [[ "${1:-}" = "--help" || "${1:-}" = "-h" ]]; then
    echo "Usage: InventorySystem [options]"
    echo "Options:"
    echo "  -h, --help     Display this help message"
    echo "  -v, --version  Display the current version"
    echo "  update         Update the application to the latest version"
    echo "  uninstall      Remove the application and launcher"
    exit 0
fi

if [ "${1:-}" = "update" ]; then
    exec bash "$APP_DIR/repo/scripts/update.sh"
fi

if [ "${1:-}" = "uninstall" ]; then
    exec bash "$APP_DIR/repo/scripts/uninstall.sh"
fi

cd "$APP_DIR/repo/src"
"$VENV_BIN/python" main.py "$@"
status=$?

if [ "$status" -eq 42 ]; then
    echo "Server requested an update, updating now..."
    bash "$APP_DIR/repo/scripts/update.sh"
    exec "$VENV_BIN/python" "$APP_DIR/repo/main.py" "$@"
fi

exit "$status"