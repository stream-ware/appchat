# ============================================================
# STREAMWARE MVP - Makefile
# ============================================================

.PHONY: help install dev prod test test-e2e lint format clean docker-build docker-up docker-down

# Default target
help:
	@echo "╔═══════════════════════════════════════════════════════════════╗"
	@echo "║   🎤 STREAMWARE MVP - Available Commands                      ║"
	@echo "╚═══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Run development server (hot reload)"
	@echo "  make prod        - Run production server"
	@echo "  make test        - Run unit/integration tests"
	@echo "  make test-e2e    - Run E2E tests with Playwright"
	@echo "  make lint        - Check code style"
	@echo "  make format      - Format code"
	@echo "  make clean       - Remove cache and temp files"
	@echo ""
	@echo "  Docker commands:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start with Docker Compose"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - Show Docker logs"
	@echo ""

# ============================================================
# Installation
# ============================================================

install:
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt 2>/dev/null || true
	@echo "✅ Installation complete"

install-e2e:
	@echo "📦 Installing E2E test dependencies..."
	pip install pytest pytest-asyncio playwright httpx websockets
	playwright install chromium
	@echo "✅ E2E dependencies installed"

# ============================================================
# Development
# ============================================================

dev:
	@echo "🔧 Starting development server..."
	python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

prod:
	@echo "🚀 Starting production server..."
	python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# ============================================================
# Testing
# ============================================================

test:
	@echo "🧪 Running tests..."
	python scripts/test_demo.py

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit -v

test-integration:
	@echo "🧪 Running integration tests..."
	python -m pytest tests/integration -v

test-e2e:
	@echo "🧪 Running E2E tests..."
	@echo "Starting server in background..."
	python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 &
	@sleep 3
	python -m pytest tests/e2e -v --headed || true
	@pkill -f "uvicorn backend.main:app" || true

test-e2e-headless:
	@echo "🧪 Running E2E tests (headless)..."
	python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 &
	@sleep 3
	python -m pytest tests/e2e -v || true
	@pkill -f "uvicorn backend.main:app" || true

test-all: test test-e2e-headless
	@echo "✅ All tests completed"

# ============================================================
# Code Quality
# ============================================================

lint:
	@echo "🔍 Checking code style..."
	python -m flake8 backend/ --max-line-length=100 --ignore=E501,W503
	python -m mypy backend/ --ignore-missing-imports || true

format:
	@echo "✨ Formatting code..."
	python -m black backend/ scripts/
	python -m isort backend/ scripts/

# ============================================================
# Docker
# ============================================================

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t streamware-mvp:latest .

docker-up:
	@echo "🐳 Starting with Docker Compose..."
	docker-compose up -d streamware
	@echo "✅ Server running at http://localhost:8000"

docker-dev:
	@echo "🐳 Starting dev mode with Docker..."
	docker-compose --profile dev up -d streamware-dev
	@echo "✅ Dev server running at http://localhost:8001"

docker-down:
	@echo "🐳 Stopping containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-test:
	@echo "🧪 Running tests in Docker..."
	docker-compose up -d streamware
	@sleep 5
	docker-compose --profile test run --rm test-runner

# ============================================================
# Cleanup
# ============================================================

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-all: clean
	rm -rf venv/ 2>/dev/null || true
	rm -rf data/documents/* data/cameras/* logs/* 2>/dev/null || true

# ============================================================
# Utilities
# ============================================================

shell:
	@echo "🐚 Starting Python shell..."
	python -c "from backend.main import *; import IPython; IPython.embed()" 2>/dev/null || python

logs:
	tail -f logs/*.log 2>/dev/null || echo "No logs found"

# Demo
demo:
	@echo "🎬 Running interactive demo..."
	python scripts/test_demo.py
