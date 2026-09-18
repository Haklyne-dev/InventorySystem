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

git -C "$APP_DIR/repo" fetch --tags --all



LATEST_TAG=$(git -C "$APP_DIR/repo" tag --sort=-v:refname | head -n1)

if [ -n "$LATEST_TAG" ]; then
    echo "Tag found. Checking out: $LATEST_TAG"
    git -C "$APP_DIR/repo" checkout "$LATEST_TAG"
else
    # 3. Fallback if the tag variable is empty
    echo "No tags found. Falling back to main branch..."
    git -C "$APP_DIR/repo" checkout main
fi

echo "Setting up virtual environment..."
python3 -m venv "$APP_DIR/venv"

# Determine the correct path to the virtual environment's Python executable
if [ -d "$APP_DIR/venv/Scripts" ]; then
    VENV_BIN="$APP_DIR/venv/Scripts"
else
    VENV_BIN="$APP_DIR/venv/bin"
fi

"$VENV_BIN/python" -m pip install --upgrade pip
"$VENV_BIN/python" -m pip install -r "$APP_DIR/repo/requirements.txt"

echo "Creating launcher script..."
cat > "$LAUNCHER" << 'EOF'
#!/usr/bin/env bash
APP_DIR="$HOME/.local/share/InventorySystem"
"$APP_DIR/venv/bin/python" "$APP_DIR/repo/src/main.py" "$@"
EOF
chmod +x "$LAUNCHER"

echo "Installed InventorySystem $LATEST_TAG"
echo "Start the server by running 'InventorySystem' from the command line."