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

# Cleanup background processes on exit
cleanup() {
    echo "Shutting down backend and frontend dev servers..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Launch Uvicorn backend server in background
echo "Starting FastAPI Backend server at http://localhost:8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend &

# Launch Vite frontend dev server
echo "Starting Vite Live Dev server at http://localhost:5173..."
cd frontend && npm run dev
