#!/bin/bash

# Resolve the backend directory (one level up from _ops/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up Python environment in: $BACKEND_DIR"
cd "$BACKEND_DIR"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
else
  echo "Virtual environment already exists, skipping creation."
fi

# Activate and install dependencies
source .venv/bin/activate
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip -q
pip install -r requirements.txt

# Copy .env if not present
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo ".env created from .env.example — update it with your production values."
  else
    echo "WARNING: No .env or .env.example found. Create a .env file before running."
  fi
else
  echo ".env already exists, skipping."
fi

echo ""
echo "Setup complete. To start the server:"
echo "  source $BACKEND_DIR/.venv/bin/activate"

