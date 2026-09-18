#!/usr/bin/env bash
set -euo pipefail
REPO_URL="https://github.com/Haklyne-dev/InventorySystem.git"
APP_DIR="$HOME/.local/share/InventorySystem"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/InventorySystem"

mkdir -p "$APP_DIR" "$BIN_DIR"

echo "Pulling latest version..."
if [ -d "$APP_DIR/repo/.git" ]; then
    git -C "$APP_DIR/repo" pull --ff-only
else
    git clone "$REPO_URL" "$APP_DIR/repo"
fi

LATEST_TAG=$(git -C "$APP_DIR/repo" tag --sort=-v:refname | head -n1)
git -C "$APP_DIR/repo" checkout "$LATEST_TAG"

echo "Setting up virtual environment..."
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/repo/requirements.txt"

echo "Creating launcher script..."
cat > "$LAUNCHER" << 'EOF'
#!/usr/bin/env bash
APP_DIR="$HOME/.local/share/InventorySystem"
"$APP_DIR/venv/bin/python" "$APP_DIR/repo/src/main.py" "$@"
EOF
chmod +x "$LAUNCHER"

echo "Installed InventorySystem $LATEST_TAG"
echo "Start the server by running 'InventorySystem' from the command line."