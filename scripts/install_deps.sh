#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR"
FRONTEND_DIR="$ROOT_DIR/frontend"

if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install --upgrade pip
  python3 -m pip install \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    psycopg2-binary \
    pydantic \
    python-dotenv \
    httpx \
    opencv-python \
    cloudinary \
    google-generativeai
else
  echo "python3 not found"
  exit 1
fi

if command -v npm >/dev/null 2>&1; then
  if [ -d "$FRONTEND_DIR" ]; then
    (cd "$FRONTEND_DIR" && npm install)
  else
    echo "frontend directory not found: $FRONTEND_DIR"
    exit 1
  fi
else
  echo "npm not found"
  exit 1
fi

echo "Dependency installation completed."
