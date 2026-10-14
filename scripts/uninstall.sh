#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/.local/share/InventorySystem"
BIN_DIR="$HOME/.local/bin"

echo "Warning: This will uninstall all aplication files"
echo "It will NOT delete the database, all data is preserved"

read -p "Do you want to proceed? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 1
        fi

echo "Uninstalling $APP_DIR..."
rm -rf "$APP_DIR"

echo "Uninstalling Launcher[$BIN_DIR/InventorySystem]..."
rm -rf "$BIN_DIR/InventorySystem"

echo "Finished uninstalling InventorySystem"