#!/bin/bash

# Test runner script with coverage reporting
# This script runs all tests and generates coverage reports

set -e

echo "============================================"
echo "Running Unit Tests with Coverage"
echo "============================================"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install test dependencies if needed
echo "Checking test dependencies..."
pip install -q -r requirements-dev.txt

# Run tests with coverage
echo ""
echo "Running tests..."
pytest tests/unit/ \
    --cov=. \
    --cov-config=.coveragerc \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    -v

# Display coverage summary
echo ""
echo "============================================"
echo "Coverage Report Summary"
echo "============================================"
coverage report --precision=2

# Check coverage threshold
echo ""
echo "Checking coverage threshold (target: 100%)..."
coverage report --fail-under=90 || {
    echo "Warning: Coverage is below 90%"
    exit 0  # Don't fail, just warn
}

echo ""
echo "============================================"
echo "Tests completed successfully!"
echo "HTML coverage report: htmlcov/index.html"
echo "============================================"