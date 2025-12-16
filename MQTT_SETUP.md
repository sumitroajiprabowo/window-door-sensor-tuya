# 📡 MQTT Event-Driven Monitoring Setup Guide

## Why MQTT for Door Sensor?

### The Problem with Polling:

```
Polling (Current):
- Check every 60-300 seconds
- Door opened 1x/week (4 events/month)
- API calls: 14,000-43,000/month
- Wasted: 99.97% of calls! ❌
- Delay: Up to 5 minutes
```

### The MQTT Solution:

```
MQTT (Event-Driven):
- Device pushes event when state changes
- Door opened 1x/week (4 events/month)
- API calls: ~4-8/month (only when events occur)
- Wasted: 0% ✅
- Delay: 0-1 seconds (instant!) ✅
```

**For infrequent events (like your door), MQTT is 99.97% more efficient!** 🎉

---

## ⚠️ Requirements

### 1. Tuya IoT Platform - Message Subscription Service

**Current Status:**
- ❌ Free Trial Edition: Message Subscription NOT AVAILABLE
- ✅ Standard Plan: $30-50/month - MQTT support included
- ✅ Enterprise Plan: Custom pricing

**What's Included:**
- MQTT Protocol support
- Pulsar (WebSocket) support
- Webhook support
- 100,000 - 1,000,000 API calls/month
- Real-time device events
- Production-grade reliability

---

## 🚀 Setup Steps

### Step 1: Upgrade Tuya IoT Plan

1. **Login to Tuya IoT Console:**
   ```
   https://iot.tuya.com/
   ```

2. **Navigate to Your Cloud Project:**
   - Click on your project name
   - Go to "Overview" tab

3. **Check Current Services:**
   - Go to "Service API" tab
   - Look for "Message Subscription" service

4. **Upgrade Plan:**
   - Click "Upgrade" or "Purchase"
   - Select **Standard Plan** ($30-50/month)
   - Complete payment

5. **Subscribe to Message Subscription:**
   - After upgrade, go to "Service API" tab
   - Find "Message Subscription"
   - Click "Subscribe"
   - Wait 1-2 minutes for activation

### Step 2: Enable MQTT Protocol

1. **In Tuya Console:**
   - Go to Cloud → "Message Subscription"
   - Click "Configure"
   - Enable **MQTT** protocol
   - Note down:
     - MQTT Endpoint
     - Client ID format
     - Authentication method

2. **Verify MQTT Access:**
   - Status should show "Active"
   - MQTT endpoint should be visible

### Step 3: Update Application to Use MQTT

#### Option A: Environment Variable Switch (Recommended)

Update `.env` file:

```bash
# Monitoring Method
# Options: "polling" or "mqtt"
MONITORING_METHOD=mqtt

# MQTT Configuration (only needed if MONITORING_METHOD=mqtt)
# These are provided by Tuya console after enabling Message Subscription
TUYA_MQTT_ENDPOINT=mqtt://mqtt-{region}.iotbing.com:1883
TUYA_MQTT_CLIENT_ID=your_client_id_here
```

#### Option B: Code Modification

Edit `main.py`:

```python
# Change from polling to MQTT
if is_reloader_child or not is_debug:
    logger.info("Starting Door Sensor Monitor...")

    # Use MQTT instead of polling
    from services.mqtt_service import door_mqtt
    door_mqtt.start()

    # OLD (Polling):
    # from services.polling_service import door_poller
    # door_poller.start()
```

### Step 4: Deploy to Kubernetes

Update secret with MQTT configuration:

```bash
kubectl create secret generic door-sensor-jebed-secrets \
  --namespace=production \
  --from-literal=MONITORING_METHOD='mqtt' \
  --from-literal=TUYA_ACCESS_ID='jetuy3mq93hc7vpe45pj' \
  --from-literal=TUYA_ACCESS_SECRET='e4ed453936b44ac488fe5b5cb7b5588d' \
  --from-literal=TUYA_ENDPOINT='https://openapi-sg.iotbing.com' \
  --from-literal=DEVICE_ID='a38604452b1ae187feagf3' \
  --from-literal=FLASK_HOST='0.0.0.0' \
  --from-literal=FLASK_PORT='5001' \
  --from-literal=FLASK_DEBUG='False' \
  --from-literal=ENV='production' \
  --from-literal=WA_API_URL='http://wa.ckt.co.id/send/message' \
  --from-literal=WA_API_USER='admin' \
  --from-literal=WA_API_PASSWORD='./Karepe123' \
  --from-literal=WA_GROUP_ID='62811297782-1595952810@g.us' \
  --from-literal=WA_MESSAGE_DOOR_OPENED='JEBED SERVER DOOR IS OPEN - Room accessed' \
  --from-literal=WA_MESSAGE_DOOR_CLOSED='JEBED SERVER DOOR IS CLOSED - Room secured' \
  --from-literal=WA_MESSAGE_SENSOR_INITIALIZED='SENSOR IS WORKING - Monitoring started' \
  --from-literal=LOG_LEVEL='INFO' \
  -n production \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/door-sensor-monitor -n production
```

---

## 📊 Expected Behavior

### MQTT Mode Startup:

```bash
============================================================
Door Sensor Monitoring System
Environment: production
Debug Mode: False
============================================================

============================================================
Initializing MQTT Event-Driven Monitoring
Device ID: a38604452b1ae187feagf3
============================================================

✅ MQTT monitoring started successfully!
Listening for real-time door events...
============================================================

[SENSOR INITIALIZED] First event
   Current state: Door CLOSED
   Timestamp: 1765592684422
   Device ID: a38604452b1ae187feagf3
   Battery: 100%
```

### When Door Opens:

```bash
============================================================
[MQTT EVENT RECEIVED]
============================================================
[DOOR STATE CHANGE] Door was closed, now opened
🚪 DOOR OPENED (doorcontact_state = True)
   Timestamp: 1765592734567
   Device ID: a38604452b1ae187feagf3
   Battery: 100%
============================================================

Sending WhatsApp message: 'JEBED SERVER DOOR IS OPEN - Room accessed'
✅ WhatsApp notification sent
```

**Delay: 0-1 seconds** (instant!) vs 1-5 minutes with polling

---

## 💰 Cost-Benefit Analysis

### For Your Use Case (Door opened 1x/week):

| Metric | Polling (Current) | MQTT (Recommended) |
|--------|------------------|-------------------|
| **Monthly Cost** | $0 (free tier) | $30-50 (paid plan) |
| **API Calls** | 14,400-43,200/month | ~4-8/month |
| **Notification Delay** | 1-5 minutes | 0-1 seconds ✅ |
| **Quota Worries** | Constant ⚠️ | None ✅ |
| **Efficiency** | 99.97% wasted | 100% efficient ✅ |
| **Battery Life** | N/A | Better for battery devices |

### When MQTT Makes Sense:

✅ **Worth upgrading if:**
- Critical security monitoring (server room access)
- Need instant alerts (< 5 second response)
- Multiple devices to monitor (spread cost)
- Business/production environment
- Budget allows $30-50/month
- Peace of mind is important

❌ **Not worth upgrading if:**
- Non-critical monitoring
- 3-5 minute delay is acceptable
- Budget very tight ($0 preferred)
- Testing/hobby project
- Single device monitoring

---

## 🔄 Migration Path (Polling → MQTT)

### Phase 1: Test MQTT Locally

```bash
# 1. Upgrade Tuya plan and enable Message Subscription
# 2. Update .env
MONITORING_METHOD=mqtt

# 3. Run locally to test
python3 main.py

# 4. Open/close door to verify instant notifications
```

### Phase 2: Deploy to Production

```bash
# 1. Update Kubernetes secret
kubectl create secret ... --from-literal=MONITORING_METHOD='mqtt'

# 2. Restart deployment
kubectl rollout restart deployment/door-sensor-monitor -n production

# 3. Monitor logs
kubectl logs -n production -l app=door-sensor-monitor -f

# 4. Test door open/close
```

### Phase 3: Verify & Monitor

```bash
# Check MQTT is working
kubectl logs -n production -l app=door-sensor-monitor | grep "MQTT"

# Expected:
# ✅ MQTT monitoring started successfully!
# [MQTT EVENT RECEIVED]
# 🚪 DOOR OPENED (doorcontact_state = True)
```

---

## 🐛 Troubleshooting

### Issue 1: MQTT Connection Failed

**Error:**
```
❌ Failed to start MQTT monitoring: Connection refused
```

**Possible Causes:**
- Message Subscription service not activated
- MQTT endpoint incorrect
- Credentials invalid

**Solution:**
```bash
# 1. Verify service is active in Tuya console
# 2. Check MQTT endpoint format
# 3. Verify ACCESS_ID and ACCESS_SECRET
# 4. Wait 5 minutes after service activation
```

### Issue 2: No Events Received

**Symptom:**
```
✅ MQTT monitoring started successfully!
[No events when door opens/closes]
```

**Possible Causes:**
- Device not linked to Cloud Project
- MQTT subscription not configured for device
- Network connectivity issues

**Solution:**
```bash
# 1. Verify device is online in Tuya app
# 2. Check device is linked to Cloud Project
# 3. Manually trigger sensor to test
# 4. Check MQTT subscription includes device
```

### Issue 3: Authentication Failed

**Error:**
```
❌ MQTT authentication failed
```

**Solution:**
```bash
# 1. Regenerate ACCESS_ID and ACCESS_SECRET
# 2. Update secret in Kubernetes
# 3. Restart pod
```

---

## 📈 Monitoring MQTT Health

### Check Connection Status:

```bash
# View MQTT client status
kubectl logs -n production -l app=door-sensor-monitor --tail=50 | grep MQTT

# Expected healthy output:
# ✅ MQTT monitoring started successfully!
# Listening for real-time door events...
```

### Monitor Event Reception:

```bash
# Watch for incoming events
kubectl logs -n production -l app=door-sensor-monitor -f

# When door opens, should see immediately:
# [MQTT EVENT RECEIVED]
# 🚪 DOOR OPENED
```

---

## 🎯 Recommendation

For your use case (door opened **1x/week**):

### Option 1: Upgrade to MQTT (Best for Production)

**Cost:** $30-50/month

**Benefits:**
- ✅ Instant notifications (0-1 sec delay)
- ✅ 99.97% more efficient
- ✅ No quota worries
- ✅ Production-grade
- ✅ Peace of mind

### Option 2: Stay with Polling (Budget-Friendly)

**Cost:** $0/month

**Settings:**
```bash
POLL_INTERVAL=180  # 3 minutes
# Acceptable delay for non-critical monitoring
# Stays close to free tier quota
```

**When to upgrade:**
- If delay becomes unacceptable
- If adding more devices
- If business grows and budget increases

---

## 📚 References

- [Tuya MQTT Documentation](https://developer.tuya.com/en/docs/iot/message-subscription?id=Kavqd7rgk5x5h)
- [TuyaOpenMQ Python SDK](https://github.com/tuya/tuya-connector-python)
- [MQTT Protocol](https://mqtt.org/)

---

**Status:** MQTT implementation ready - waiting for Tuya plan upgrade

*Last Updated: 2025-12-12*
