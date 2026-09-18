#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/.local/share/InventorySystem"
REPO="$APP_DIR/repo"

if [ "${MYAPP_UPDATE_REEXECED:-0}" != "1" ]; then
    git -C "$REPO" fetch --tags --quiet

    CURRENT_TAG=$(git -C "$REPO" describe --tags --exact-match 2>/dev/null || echo "unknown")
    LATEST_TAG=$(git -C "$REPO" tag --sort=-v:refname | head -n1)

    if [ "$CURRENT_TAG" = "$LATEST_TAG" ]; then
        echo "Already up to date ($CURRENT_TAG)."
        exit 0
    fi

    echo "Updating $CURRENT_TAG -> $LATEST_TAG"
    git -C "$REPO" checkout "$LATEST_TAG"

    exec env MYAPP_UPDATE_REEXECED=1 bash "$REPO/scripts/update.sh" "$@"
fi

if [ -d "$APP_DIR/venv/Scripts" ]; then
    VENV_BIN="$APP_DIR/venv/Scripts"
else
    VENV_BIN="$APP_DIR/venv/bin"
fi

"$VENV_BIN/python" -m pip install --upgrade -r "$REPO/requirements.txt"

install -m 755 "$REPO/scripts/launcher_template.sh" "$HOME/.local/bin/myapp"

echo "Updated to $(git -C "$REPO" rev-parse --short HEAD)"