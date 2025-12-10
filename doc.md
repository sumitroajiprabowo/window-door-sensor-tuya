# Tuya Contact Sensor API Documentation

This API provides an interface to interact with Tuya-based Contact Sensors (door/window sensors) and includes a Webhook feature for real-time event notifications.

## Base URL
`http://localhost:5001`

## Authentication
Ensure you have configured your `TUYA_ACCESS_ID` and `TUYA_ACCESS_SECRET` in the `.env` file.

---

## Endpoints

### 1. Health Check
Check if the API service is running.

- **URL**: `/health`
- **Method**: `GET`
- **Response**:
  ```json
  {
      "message": "Health check passed",
      "result": {
          "status": "ok"
      },
      "status": "success"
  }
  ```

### 2. Get Device Status
Retrieve the current status of the contact sensor.

- **URL**: `/devices/<device_id>/status`
- **Method**: `GET`
- **Path Parameters**:
    - `device_id` (string): The unique ID of the device (e.g., `your_device_id_here`).
- **Response**:
  ```json
  {
      "message": "Success",
      "result": [
          {
              "code": "doorcontact_state",
              "value": true
          },
          {
              "code": "battery_percentage",
              "value": 85
          },
           {
              "code": "temper_alarm",
              "value": false
          }
      ],
      "status": "success"
  }
  ```

### 3. Send Device Commands
Send commands to the device (if supported).

- **URL**: `/devices/<device_id>/commands`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
      "commands": [
          {
              "code": "example_code",
              "value": true
          }
      ]
  }
  ```
- **Response**:
  ```json
  {
      "message": "Command sent successfully",
      "result": true,
      "status": "success"
  }
  ```

---

## Webhook Integration

The application listens for real-time events from Tuya (via Pulsar WebSocket) and triggers a webhook when a door/window sensor state changes.

### Configuration
Set the following in your `.env` file:
```env
WEBHOOK_URL=https://your-webhook-url.com/webhook/door-sensor
WEBHOOK_API_KEY=your_api_key
TUYA_PULSAR_ENDPOINT=wss://mqe-sg.iotbing.com:8285/
```

### How It Works

1. Application connects to Tuya Pulsar WebSocket on startup
2. Listens for events from the configured `DEVICE_ID`
3. When `doorcontact_state` changes, triggers webhook automatically
4. Logs clear status messages to console

### Webhook Event

When the door/window sensor state changes, a POST request is sent to the configured `WEBHOOK_URL`.

- **Method**: `POST`
- **Headers**:
    - `Content-Type`: `application/json`
    - `x-api-key`: `<WEBHOOK_API_KEY>`
- **Payload**:
  ```json
  {
      "device_id": "your_device_id_here",
      "event": "door_contact",
      "state": true,
      "timestamp": 1733655123456
  }
  ```

**Field Descriptions**:
- `device_id`: The unique ID of the sensor device
- `event`: Always `"door_contact"` for door/window events
- `state`:
  - `true` = Door/window is **OPENED** (doorcontact_state = True)
  - `false` = Door/window is **CLOSED** (doorcontact_state = False)
- `timestamp`: Unix timestamp in milliseconds

### Log Output

The application provides clear visual feedback in logs:

**When Door Opens:**
```
📱 Event from device: your_device_id_here
🚪 DOOR OPENED (doorcontact_state = True)
   └─ Timestamp: 1733655123456
   └─ Device ID: your_device_id_here
🔔 Triggering webhook for door OPENED...
✅ Webhook delivered successfully (HTTP 200)
```

**When Door Closes:**
```
📱 Event from device: your_device_id_here
🔒 DOOR CLOSED (doorcontact_state = False)
   └─ Timestamp: 1733655456789
   └─ Device ID: your_device_id_here
🔔 Triggering webhook for door CLOSED...
✅ Webhook delivered successfully (HTTP 200)
```

### Understanding doorcontact_state

The `doorcontact_state` field from Tuya devices follows this logic:

| Value | Meaning | Physical State |
|-------|---------|----------------|
| `true` | Contact broken | Door/window is **OPEN** |
| `false` | Contact connected | Door/window is **CLOSED** |

This is based on magnetic contact sensor logic - when the magnet is separated from the sensor (door opens), the contact breaks and returns `true`.

---

## Standard Status Set
The Contact Sensor supports the following status codes:

| Code | Name | Type | Values |
|------|------|------|--------|
| `doorcontact_state` | Status of door window sensor | Boolean | `true` (open), `false` (closed) |
| `temper_alarm` | Tamper alarm | Boolean | `true`, `false` |
| `battery_percentage` | Battery capacity percentage | Integer | 0-100 |
| `battery_value` | Battery capacity value | Integer | 0-30000 |
| `battery_state` | Battery capacity status | Enum | `low`, `middle`, `high` |
| `signal_strength` | Signal strength | Integer | -255 to 255 |
