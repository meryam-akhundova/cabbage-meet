#!/usr/bin/env bash
# Create a project virtualenv in .venv (WSL) and install backend requirements
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -d ".venv" ]; then
  echo ".venv already exists. Activating and installing packages..."
else
  echo "Creating virtualenv at .venv..."
  python3 -m venv .venv
fi

echo "Installing backend requirements..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r src/backend/requirements.txt

echo "Done. Use the interpreter: $ROOT_DIR/.venv/bin/python"
