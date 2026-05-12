#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR"
FRONTEND_DIR="$ROOT_DIR/frontend"

install_node() {
  if command -v npm >/dev/null 2>&1; then
    return 0
  fi

  if command -v brew >/dev/null 2>&1; then
    brew install node
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y nodejs npm
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y nodejs npm
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Syu --noconfirm nodejs npm
  elif command -v winget >/dev/null 2>&1; then
    winget install -e --id OpenJS.NodeJS
  elif command -v choco >/dev/null 2>&1; then
    choco install -y nodejs
  else
    echo "No supported package manager found to install Node.js/npm."
    echo "Please install Node.js/npm manually and re-run this script."
    exit 1
  fi
}

if command -v python3 >/dev/null 2>&1; then
  if [ ! -d "$BACKEND_DIR/.venv" ]; then
    python3 -m venv "$BACKEND_DIR/.venv"
  fi

  if [ -f "$BACKEND_DIR/.venv/bin/activate" ]; then
    # Unix/macOS
    source "$BACKEND_DIR/.venv/bin/activate"
  elif [ -f "$BACKEND_DIR/.venv/Scripts/activate" ]; then
    # Windows (Git Bash/WSL)
    source "$BACKEND_DIR/.venv/Scripts/activate"
  else
    echo "Virtual environment activation script not found."
    exit 1
  fi

  python -m pip install --upgrade pip
  python -m pip install -r "$BACKEND_DIR/requirements.txt"
else
  echo "python3 not found"
  exit 1
fi

install_node
if [ -d "$FRONTEND_DIR" ]; then
  (cd "$FRONTEND_DIR" && npm install)
else
  echo "frontend directory not found: $FRONTEND_DIR"
  exit 1
fi

echo "Dependency installation completed."
