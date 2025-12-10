# Testing Quick Start Guide

## Installation

```bash
# Install test dependencies
pip install -r requirements-dev.txt
```

## Run All Tests

```bash
# Option 1: Use the test runner script (recommended)
./run_tests.sh

# Option 2: Run pytest directly
pytest

# Option 3: Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing
```

## Run Specific Tests

```bash
# Run a single test file
pytest tests/unit/test_config.py

# Run a single test class
pytest tests/unit/test_config.py::TestConfig

# Run a single test function
pytest tests/unit/test_config.py::TestConfig::test_default_port

# Run tests matching a pattern
pytest -k "test_config"

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x
```

## View Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open the report (macOS)
open htmlcov/index.html

# Open the report (Linux)
xdg-open htmlcov/index.html

# View coverage in terminal
pytest --cov=. --cov-report=term-missing
```

## Test File Structure

```
tests/
├── conftest.py                    # Shared fixtures
└── unit/
    ├── test_config.py             # Config tests
    ├── test_main.py               # Main app tests
    ├── test_polling_service.py    # Polling service tests
    ├── test_tuya_service.py       # Tuya service tests
    ├── test_whatsapp_service.py   # WhatsApp service tests
    ├── test_health_route.py       # Health endpoint tests
    ├── test_device_route.py       # Device endpoints tests
    └── test_response_utils.py     # Response utils tests
```

## Common pytest Options

```bash
# Show test output (print statements)
pytest -s

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Generate JUnit XML report
pytest --junit-xml=report.xml

# Show local variables on failure
pytest -l

# Only run failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Show coverage for specific module
pytest --cov=services/tuya_service.py

# Show detailed coverage report
pytest --cov=. --cov-report=term-missing:skip-covered
```

## Coverage Thresholds

```bash
# Fail if coverage below 90%
pytest --cov=. --cov-report=term --cov-fail-under=90

# Check coverage without running tests
coverage report

# Erase previous coverage data
coverage erase
```

## Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of each test
pytest --trace

# Show test durations
pytest --durations=10

# Show slowest 10 tests
pytest --durations=10 --durations-min=1.0
```

## Watch Mode (requires pytest-watch)

```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw
```

## CI/CD Integration

### GitHub Actions
See `.github/workflows/tests.yml`

### GitLab CI
```yaml
test:
  script:
    - pip install -r requirements-dev.txt
    - pytest --cov=. --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Jenkins
```groovy
stage('Test') {
    steps {
        sh 'pip install -r requirements-dev.txt'
        sh 'pytest --cov=. --cov-report=xml --junit-xml=report.xml'
    }
}
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
cd /path/to/window-door-sensor-tuya

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install in development mode
pip install -e .
```

### Module Not Found
```bash
# Clear pytest cache
pytest --cache-clear

# Remove __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Coverage Not Working
```bash
# Reinstall coverage
pip install --force-reinstall coverage pytest-cov

# Check .coveragerc configuration
cat .coveragerc
```

## Test Coverage Goals

- Target: 100% code coverage
- Minimum: 90% code coverage
- Current: Run `pytest --cov=. --cov-report=term` to check

## Best Practices

1. Run tests before committing
2. Add tests for new features
3. Keep tests fast and isolated
4. Mock external dependencies
5. Use descriptive test names
6. One assertion per test (when possible)
7. Follow AAA pattern (Arrange, Act, Assert)

## Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest -k pattern` | Run tests matching pattern |
| `pytest --cov=.` | Run with coverage |
| `pytest --lf` | Run last failed tests |
| `pytest --pdb` | Debug on failure |
| `./run_tests.sh` | Run all tests with coverage |

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Docs](https://coverage.readthedocs.io/)
- [Test Suite README](tests/README.md)
- [Test Summary](TEST_SUMMARY.md)