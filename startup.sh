#!/bin/bash
set -e

# Run tests
pytest --cov=app --cov-report=term-missing -vv

# Start the app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
