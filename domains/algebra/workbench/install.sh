#!/usr/bin/env bash
set -e

WORKBENCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKBENCH_DIR"

echo "=== Installing Algebra EKC Workbench ==="

# 1. Verify python3.12 availability
if ! command -v python3.12 &> /dev/null; then
    echo "Error: python3.12 executable is required but not found on PATH."
    exit 1
fi

echo "Python executable: $(which python3.12)"

# 2. Create Python virtual environment using python3.12 -m venv .venv
if [ ! -d ".venv" ]; then
    echo "Creating Python 3.12 virtual environment in .venv..."
    python3.12 -m venv .venv
else
    echo "Virtual environment .venv already exists."
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# 3. Upgrade pip and install backend requirements
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Install npm packages and build frontend static distribution assets
if command -v npm &> /dev/null; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    echo "Building frontend React SPA assets..."
    npm run build
    cd "$WORKBENCH_DIR"
else
    echo "Warning: npm not found. Skipping frontend build. Backend will serve API."
fi

echo "=== Installation Completed Successfully! ==="
