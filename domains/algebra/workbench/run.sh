#!/usr/bin/env bash
set -e

WORKBENCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKBENCH_DIR"

if [ ! -d ".venv" ]; then
    echo "Virtual environment .venv not found. Running install.sh first..."
    ./install.sh
fi

echo "Activating virtual environment..."
source .venv/bin/activate

export PYTHONPATH="$WORKBENCH_DIR/backend:$PYTHONPATH"

# Run migrations
echo "Running Alembic database migrations..."
cd backend
alembic upgrade head

# Seed database if needed
echo "Initializing/verifying database seed..."
python -m app.db.seed
cd "$WORKBENCH_DIR"

# Launch Uvicorn server
echo "Starting Algebra EKC Workbench server at http://localhost:8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
