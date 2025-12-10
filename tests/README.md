# Test Suite Documentation

## Overview

This directory contains comprehensive unit tests for the Door Sensor Monitoring System. The test suite is designed to achieve 100% code coverage and validate all functionality.

## Test Structure

```
tests/
├── __init__.py                          # Tests package init
├── conftest.py                          # Pytest fixtures and configuration
├── unit/                                # Unit tests
│   ├── __init__.py
│   ├── test_config.py                   # Tests for config/Config.py
│   ├── test_main.py                     # Tests for main.py
│   ├── test_polling_service.py          # Tests for services/polling_service.py
│   ├── test_tuya_service.py             # Tests for services/tuya_service.py
│   ├── test_whatsapp_service.py         # Tests for services/whatsapp_service.py
│   ├── test_health_route.py             # Tests for routes/health.py
│   ├── test_device_route.py             # Tests for routes/device.py
│   └── test_response_utils.py           # Tests for utils/response.py
└── README.md                            # This file
```

## Running Tests

### Quick Start

Run all tests with coverage:
```bash
./run_tests.sh
```

### Manual Execution

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/unit/test_config.py
```

Run specific test class:
```bash
pytest tests/unit/test_config.py::TestConfig
```

Run specific test:
```bash
pytest tests/unit/test_config.py::TestConfig::test_default_port
```

### Coverage Reports

Generate coverage report:
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

View HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Generate XML coverage report (for CI/CD):
```bash
pytest --cov=. --cov-report=xml
```

## Test Categories

### Configuration Tests (`test_config.py`)
- Environment variable loading
- Default values
- Configuration validation
- Missing configuration handling

**Coverage**: Config class, TuyaConfig class, WhatsAppConfig class

### Main Application Tests (`test_main.py`)
- Flask app creation
- Blueprint registration
- Configuration validation
- Logging setup
- Reloader detection

**Coverage**: create_app(), validate_configuration(), start_listener()

### Polling Service Tests (`test_polling_service.py`)
- Poller initialization
- HTTP polling loop
- Door state detection
- Alert triggering
- Error handling
- Thread management

**Coverage**: DoorSensorPoller class, door_poller singleton

### Tuya Service Tests (`test_tuya_service.py`)
- API initialization
- Connection management
- Authentication verification
- Device status retrieval
- Command sending
- Error handling

**Coverage**: TuyaService class, tuya_service singleton

### WhatsApp Service Tests (`test_whatsapp_service.py`)
- Message sending
- API authentication
- Payload formatting
- Door opened alerts
- Door closed alerts
- Error handling
- Network failures

**Coverage**: send_whatsapp_message(), send_door_opened_alert(), send_door_closed_alert()

### Health Route Tests (`test_health_route.py`)
- Health check endpoint
- Response format
- HTTP methods
- Idempotency

**Coverage**: /health endpoint

### Device Route Tests (`test_device_route.py`)
- Device status endpoint
- Command sending endpoint
- Request validation
- Error responses
- API integration

**Coverage**: /devices/<id>/status, /devices/<id>/commands

### Response Utils Tests (`test_response_utils.py`)
- Success response formatting
- Error response formatting
- Status codes
- JSON structure
- Edge cases

**Coverage**: success_response(), error_response()

## Test Fixtures

### Available Fixtures (from `conftest.py`)

- `mock_env_vars`: Sets up all required environment variables
- `mock_tuya_api`: Mock TuyaOpenAPI instance
- `sample_device_status`: Sample successful device status response
- `sample_error_response`: Sample error response
- `flask_test_client`: Flask test client for endpoint testing

## Mocking Strategy

### External Dependencies
- **Tuya API**: Mocked using `unittest.mock.Mock` and `patch`
- **WhatsApp API**: Mocked using `patch('requests.post')`
- **Environment Variables**: Mocked using `pytest.monkeypatch`
- **Threading**: Mocked using `patch('threading.Thread')`
- **Time Functions**: Mocked using `patch('time.sleep')`

### Key Patterns
1. **Service Mocking**: Mock external services to isolate unit under test
2. **Environment Isolation**: Each test gets fresh environment variables
3. **Thread Safety**: Thread operations are mocked to prevent actual threading
4. **API Calls**: All HTTP requests are mocked to prevent network calls

## Coverage Goals

- **Target**: 100% code coverage
- **Minimum**: 90% code coverage
- **Current**: Run `pytest --cov` to see current coverage

### Excluded from Coverage
- Debug scripts (`debug_*.py`)
- Test files (`test_*.py`)
- Virtual environment (`.venv/`)
- Third-party packages

## Best Practices

### Writing New Tests

1. **Test Naming**: Use descriptive names following pattern `test_<what>_<condition>`
   ```python
   def test_send_command_with_valid_device_id():
       """Test that send_command works with valid device ID."""
   ```

2. **Docstrings**: Always include docstrings explaining what the test does
   ```python
   def test_validation_failure(self):
       """Test that validation fails when required fields are missing."""
   ```

3. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   # Arrange
   mock_service.get_status.return_value = {'success': True}

   # Act
   result = service.check_status()

   # Assert
   assert result is True
   ```

4. **Mock External Calls**: Never make real API calls or network requests
   ```python
   @patch('services.whatsapp_service.requests.post')
   def test_send_message(self, mock_post):
       mock_post.return_value = Mock(status_code=200)
   ```

5. **Test Edge Cases**: Include tests for error conditions
   ```python
   def test_handles_network_timeout():
       """Test that service handles network timeout gracefully."""
   ```

## Continuous Integration

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Install test dependencies: `pip install -r requirements-dev.txt`

2. **Module Not Found**
   - Check that `conftest.py` adds project root to path
   - Verify `__init__.py` files exist in test directories

3. **Mock Not Working**
   - Verify patch path matches actual import path
   - Use `patch('module.function')` not `patch('function')`

4. **Coverage Not 100%**
   - Run with `--cov-report=term-missing` to see missing lines
   - Check `.coveragerc` for excluded files

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage percentage
4. Update this README if adding new test categories

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)