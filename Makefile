.PHONY: help install test test-coverage test-unit test-integration lint format clean docker-build docker-up docker-down docker-logs run dev

# Default target - show help
help:
	@echo "Available targets:"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run all tests with coverage"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-coverage    - Run tests and generate coverage report"
	@echo "  make lint             - Run code linting"
	@echo "  make format           - Format code with black"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start Docker container"
	@echo "  make docker-down      - Stop Docker container"
	@echo "  make docker-logs      - View Docker container logs"
	@echo "  make run              - Run application in production mode"
	@echo "  make dev              - Run application in development mode"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run all tests with coverage (minimum 100%)
test: test-coverage

# Run unit tests only
test-unit:
	.venv/bin/python -m pytest tests/unit -v

# Run tests with coverage report
test-coverage:
	.venv/bin/python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=100
	@echo "Coverage report generated in htmlcov/index.html"

# Run linting checks
lint:
	.venv/bin/python -m pylint **/*.py --disable=C0114,C0115,C0116

# Format code with black
format:
	.venv/bin/python -m black .

# Clean up temporary files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete

# Build Docker image
docker-build:
	docker-compose build

# Start Docker container in background
docker-up:
	docker-compose up -d

# Stop Docker container
docker-down:
	docker-compose down

# View Docker container logs
docker-logs:
	docker-compose logs -f door-sensor-monitor

# Run application in production mode
run:
	ENV=production FLASK_DEBUG=False python -u main.py

# Run application in development mode
dev:
	ENV=development FLASK_DEBUG=True python -u main.py

# Setup development environment
setup-dev: install
	cp .env.example .env || true
	@echo "Development environment ready. Please update .env with your credentials."
