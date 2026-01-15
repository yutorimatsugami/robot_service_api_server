#!/bin/bash
set -e

echo "🚀 Starting Robot Service API Server..."

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start server
cd src
uvicorn main:app --reload --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
