# Tuya Door/Window Sensor Monitor

[![Tests](https://github.com/sumitroajiprabowo/window-door-sensor-tuya/actions/workflows/tests.yml/badge.svg)](https://github.com/sumitroajiprabowo/window-door-sensor-tuya/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/sumitroajiprabowo/window-door-sensor-tuya/branch/main/graph/badge.svg)](https://codecov.io/gh/sumitroajiprabowo/window-door-sensor-tuya)
[![Docker](https://img.shields.io/docker/v/sumitroajiprabowo/door-sensor-monitor?label=docker&logo=docker)](https://hub.docker.com/r/sumitroajiprabowo/door-sensor-monitor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Flask-based REST API to monitor Tuya Contact Sensors (Window/Door sensors) with real-time event monitoring and WhatsApp notification integration.

## Features

- Real-time door/window state monitoring via HTTP polling
- Direct WhatsApp notifications on door state changes
- Battery level monitoring
- Docker & Docker Compose support
- Kubernetes deployment support with ArgoCD
- Production-ready with security best practices
- HTTP REST API for device status and commands
- Configurable polling intervals and alert messages

## Prerequisites

Before setup, ensure you have:
1. A Tuya IoT Platform account (https://iot.tuya.com/)
2. A Cloud Project created in Tuya Console
3. **IMPORTANT**: Your project must subscribe to these services:
   - **IoT Core** (for HTTP API)
   - **Message Subscription** (for WebSocket real-time events)
4. Your door/window sensor linked to the project

## Quick Start with Docker (Recommended)

### 1. Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

### 2. Run with Docker Compose

```bash
docker-compose up -d
```

### 3. View Logs

```bash
docker-compose logs -f door-sensor-monitor
```

### 4. Stop the service

```bash
docker-compose down
```

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials. See `.env.example` for all available options.

**Required Configuration:**
- `TUYA_ACCESS_ID` - From Tuya IoT Console
- `TUYA_ACCESS_SECRET` - From Tuya IoT Console
- `TUYA_ENDPOINT` - API endpoint for your region
- `DEVICE_ID` - Your door sensor device ID
- `WA_API_URL` - WhatsApp API endpoint
- `WA_API_USER` - WhatsApp API username
- `WA_API_PASSWORD` - WhatsApp API password
- `WA_GROUP_ID` - WhatsApp group ID for notifications

**Optional WhatsApp Configuration:**
- `WA_MESSAGE_DOOR_OPENED` - Custom message when door opens (default: "DOOR OPENED - Server room accessed")
- `WA_MESSAGE_DOOR_CLOSED` - Custom message when door closes (default: "DOOR CLOSED - Server room secured")
- `WA_MESSAGE_SENSOR_INITIALIZED` - Custom message when monitoring starts (default: "SENSOR IS WORKING - Monitoring started")
- `WA_IS_FORWARDED` - Set to `true` to mark messages as forwarded (default: `false`)
- `WA_DURATION` - Message duration in seconds, 0 to exclude from payload (default: `0`)

**Data Center Endpoints** (choose based on your region):
- Singapore: `https://openapi-sg.iotbing.com`
- US East: `https://openapi.tuyaus.com`
- Europe: `https://openapi.tuyaeu.com`
- China: `https://openapi.tuyacn.com`

### 3. Run Application

```bash
python3 main.py
```

## Log Output Examples

When the app is running, you'll see clear log messages:

```
============================================================
Door Sensor Monitoring System
Environment: production
Debug Mode: False
============================================================

2025-12-09 10:30:15 - root - INFO - Configuration validation passed
2025-12-09 10:30:15 - root - INFO - Starting Door Sensor Monitor...
2025-12-09 10:30:15 - root - INFO - Starting Flask server on 0.0.0.0:5001

[Door Sensor Poller] Starting with interval: 2 seconds
Monitoring device: your_device_id_here
```

**When monitoring first starts (initialization):**
```
[SENSOR INITIALIZED] First reading
   Current state: Door CLOSED
   Timestamp: 1765254458464
   Device ID: a38604452b1ae187fXXXX
   Battery: 100%
Sending WhatsApp message: 'SENSOR IS WORKING - Monitoring started'
```

**When door opens:**
```
[DOOR STATE CHANGE] Door was closed, now opened
DOOR OPENED (doorcontact_state = True)
   Timestamp: 1765254512345
   Device ID: a38604452b1ae187fXXXX
   Battery: 100%
Sending WhatsApp message: 'DOOR OPENED - Server room accessed'
```

**When door closes:**
```
[DOOR STATE CHANGE] Door was opened, now closed
DOOR CLOSED (doorcontact_state = False)
   Timestamp: 1765254567890
   Device ID: a38604452b1ae187feagf3
   Battery: 100%
Sending WhatsApp message: 'DOOR CLOSED - Server room secured'
```

## Troubleshooting

### Error: 401 Unauthorized (WebSocket)

**Symptom**: `ERROR:websocket:Handshake status 401 Unauthorized`

**Cause**: Your Tuya project is not subscribed to "Message Subscription" service.

**Solution**:
1. Login to https://iot.tuya.com/
2. Select your Cloud Project
3. Go to "Service API" tab
4. Subscribe to **"Message Subscription"** or **"IoT Data Analytics"**
5. Wait 1-2 minutes for activation
6. Restart the application

### HTTP API works but WebSocket doesn't

This is normal if you haven't subscribed to Message Subscription service. The HTTP API only needs "IoT Core" service, while WebSocket needs "Message Subscription".

### No events received

1. Verify device is online in Tuya app
2. Trigger the sensor manually (open/close door)
3. Check device ID matches in `.env`
4. Verify device is linked to your Cloud Project

## WhatsApp Integration

This project uses the [go-whatsapp-web-multidevice](https://github.com/aldinokemal/go-whatsapp-web-multidevice) module for WhatsApp notifications.

### WhatsApp API Setup

1. Deploy the WhatsApp service using the [go-whatsapp-web-multidevice](https://github.com/aldinokemal/go-whatsapp-web-multidevice) project
2. Configure the WhatsApp API endpoint in your `.env` file:
   - `WA_API_URL` - Your WhatsApp API endpoint (e.g., `http://whatsapp-service:3000/send/message`)
   - `WA_API_USER` - API username for authentication
   - `WA_API_PASSWORD` - API password for authentication
   - `WA_GROUP_ID` - WhatsApp group ID or phone number to receive notifications

### WhatsApp API Documentation

Full WhatsApp API documentation is available at:
- **API Reference**: [https://bump.sh/aldinokemal/doc/go-whatsapp-web-multidevice/group/endpoint-app](https://bump.sh/aldinokemal/doc/go-whatsapp-web-multidevice/group/endpoint-app)
- **GitHub Repository**: [https://github.com/aldinokemal/go-whatsapp-web-multidevice](https://github.com/aldinokemal/go-whatsapp-web-multidevice)

### Customizing WhatsApp Messages

You can customize the notification messages by setting these environment variables:
- `WA_MESSAGE_DOOR_OPENED` - Message sent when door opens
- `WA_MESSAGE_DOOR_CLOSED` - Message sent when door closes
- `WA_MESSAGE_SENSOR_INITIALIZED` - Message sent when monitoring starts

## Kubernetes Deployment

This project includes full Kubernetes deployment support with ArgoCD for GitOps-based deployments.

### Quick Start with Kubernetes

```bash
# Deploy to development
kubectl apply -k k8s/overlays/development

# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to production
kubectl apply -k k8s/overlays/production
```

### ArgoCD Deployment

For production-grade GitOps deployments:

1. Update repository URLs in `k8s/argocd/application-*.yaml` files
2. Apply ArgoCD Applications:
   ```bash
   kubectl apply -f k8s/argocd/application-development.yaml
   kubectl apply -f k8s/argocd/application-staging.yaml
   kubectl apply -f k8s/argocd/application-production.yaml
   ```

See [k8s/README.md](k8s/README.md) for complete Kubernetes deployment documentation.

## API Documentation

See [doc.md](doc.md) for full REST API documentation.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run linter
make lint
```

### Using Makefile

The project includes a Makefile for common development tasks:

```bash
make install          # Install dependencies
make test            # Run unit tests
make test-coverage   # Run tests with coverage report
make lint            # Run code linter
make format          # Format code with black
make docker-build    # Build Docker image
make docker-up       # Start with docker-compose
make docker-down     # Stop docker-compose
make clean           # Clean build artifacts
```

## Project Structure

```
.
├── config/
│   └── Config.py           # Configuration loader
├── routes/
│   ├── health.py           # Health check endpoint
│   └── device.py           # Device endpoints
├── services/
│   ├── tuya_service.py     # Tuya HTTP API client
│   ├── tuya_listener.py    # Pulsar WebSocket listener (currently disabled)
│   ├── polling_service.py  # HTTP polling service (active)
│   └── whatsapp_service.py # WhatsApp notification service
├── utils/
│   └── response.py         # Response formatters
├── tests/
│   └── unit/               # Unit tests with 100% coverage
├── main.py                 # Application entry point
├── test_connection.py      # Connection test utility
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose configuration
├── Makefile                # Development automation
├── .env.example            # Environment variable template
└── .env                    # Configuration (not in git)
```

## License

[MIT](LICENSE)
