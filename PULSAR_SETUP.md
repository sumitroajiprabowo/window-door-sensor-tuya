# Pulsar WebSocket Setup Guide

Panduan lengkap untuk mengaktifkan Pulsar WebSocket real-time monitoring sebagai pengganti HTTP Polling.

## Keuntungan Pulsar vs HTTP Polling

| Aspek | HTTP Polling | Pulsar WebSocket |
|-------|-------------|------------------|
| **Delay** | 5 menit | Real-time (0-1 detik) |
| **API Calls/bulan** | ~8,640 calls | ~50-100 calls |
| **Quota Usage** | Tinggi | Sangat rendah |
| **Battery Impact** | Rendah | Rendah |
| **Network** | Stabil | Perlu koneksi persistent |

## Prerequisites

✅ Message Service sudah di-enable di Tuya Console
✅ Encryption algorithm: **ECB** (bukan AES-GCM)
✅ tuya-connector-python 0.1.2 sudah terinstall
✅ .env sudah dikonfigurasi dengan benar

## Step 1: Verifikasi Konfigurasi

Pastikan `.env` Anda memiliki:

```bash
# Tuya Credentials
TUYA_ACCESS_ID=your_access_id
TUYA_ACCESS_SECRET=your_access_secret
TUYA_ENDPOINT=https://openapi-sg.iotbing.com
DEVICE_ID=your_device_id

# Pulsar WebSocket Endpoint
TUYA_PULSAR_ENDPOINT=wss://mqe-sg.iotbing.com:8285/
```

### Endpoint by Region:

| Region | Pulsar Endpoint |
|--------|----------------|
| **Singapore** | `wss://mqe-sg.iotbing.com:8285/` |
| **US East** | `wss://mqe.tuyaus.com:8285/` |
| **Europe** | `wss://mqe.tuyaeu.com:8285/` |
| **China** | `wss://mqe.tuyacn.com:8285/` |

**CATATAN PENTING:**
- Gunakan `wss://` bukan `pulsar+ssl://`
- Port `8285` bukan `7285`
- Format ini khusus untuk `tuya-connector-python` SDK

## Step 2: Test Koneksi Pulsar

Sebelum mengaktifkan full production, test dulu:

```bash
python3 test_pulsar.py
```

**Expected Output:**

```
============================================================
Pulsar Connection Test
============================================================

Configuration:
  ACCESS_ID: eb1234567...
  ACCESS_SECRET: **********
  PULSAR_ENDPOINT: wss://mqe-sg.iotbing.com:8285/
  DEVICE_ID: a38604452b1ae187feagf3

============================================================
Starting Pulsar listener...
============================================================

Waiting for messages...
Please open/close your door sensor to trigger an event.
Press Ctrl+C to stop.

============================================================
Starting Tuya Pulsar Listener...
Endpoint: wss://mqe-sg.iotbing.com:8285/
Monitoring Device: a38604452b1ae187feagf3
Topic: TEST Environment (change to PROD in code if needed)
Encryption: ECB Mode
============================================================
Waiting for door/window sensor events...
============================================================

Connecting to Pulsar WebSocket...
Pulsar connection started!
```

**Test the connection:**
1. Buka/tutup door sensor Anda
2. Lihat apakah pesan muncul di console
3. Jika muncul, berarti koneksi berhasil!

**Expected event output:**
```
[on_message] Message received from Pulsar!
Event from device: a38604452b1ae187feagf3
DOOR OPENED (doorcontact_state = True)
   Timestamp: 1765254512345
   Device ID: a38604452b1ae187feagf3
```

## Step 3: Switch dari Polling ke Pulsar

### Option A: Manual Switch (Recommended untuk testing)

Edit `main.py` line 123-131:

**Before:**
```python
# Use HTTP Polling service as the primary monitoring method
from services.polling_service import door_poller
door_poller.start()

# Alternative: Pulsar WebSocket listener (currently disabled)
# Uncomment below if Pulsar encryption issues are resolved
# start_listener()
```

**After:**
```python
# Use Pulsar WebSocket for real-time monitoring
start_listener()

# Alternative: HTTP Polling (fallback if Pulsar has issues)
# from services.polling_service import door_poller
# door_poller.start()
```

### Option B: Environment Variable Switch

Tambahkan ke `.env`:
```bash
# Monitoring Method: "polling" or "pulsar"
MONITORING_METHOD=pulsar
```

Lalu ubah `main.py`:
```python
from config.Config import Config

if Config.MONITORING_METHOD == "pulsar":
    logger.info("Using Pulsar WebSocket for monitoring")
    start_listener()
else:
    logger.info("Using HTTP Polling for monitoring")
    from services.polling_service import door_poller
    door_poller.start()
```

## Step 4: Run Production

```bash
python3 main.py
```

Monitor log output untuk memastikan koneksi berhasil.

## Troubleshooting

### Error: 401 Unauthorized

**Symptom:**
```
ERROR:websocket:Handshake status 401 Unauthorized
```

**Solutions:**
1. Cek kembali ACCESS_ID dan ACCESS_SECRET di .env
2. Pastikan Message Service sudah di-enable di Tuya Console
3. Tunggu 1-2 menit setelah enable Message Service
4. Pastikan endpoint sesuai dengan region Anda

### Error: Connection timeout

**Symptom:**
```
websocket._exceptions.WebSocketTimeoutException
```

**Solutions:**
1. Cek koneksi internet
2. Cek firewall tidak block port 8285
3. Pastikan endpoint benar (wss:// bukan ws://)

### Messages tidak diterima

**Symptom:** Koneksi berhasil tapi tidak ada pesan saat door dibuka/tutup

**Solutions:**
1. Pastikan device online di Tuya app
2. Cek DEVICE_ID di .env sesuai dengan device Anda
3. Pastikan device sudah di-link ke Cloud Project
4. Trigger sensor beberapa kali

### Received message tapi tidak ada WhatsApp alert

**Solutions:**
1. Cek WhatsApp service running
2. Cek credentials WhatsApp di .env
3. Lihat log error di console

## Rollback ke HTTP Polling

Jika ada masalah dengan Pulsar, kembalikan ke polling:

1. Edit `main.py` kembali ke HTTP Polling (lihat Option A)
2. Restart aplikasi
3. Polling akan langsung aktif kembali

## Message Format yang Diterima

**PENTING**: SDK `tuya-connector-python` sudah melakukan auto-decrypt, jadi format yang diterima langsung berupa payload yang sudah di-decrypt (tanpa nested 'data' field).

### Protocol 1000 (Newer format):
```json
{
  "bizCode": "devicePropertyMessage",
  "bizData": {
    "devId": "your_device_id",
    "properties": [
      {
        "code": "doorcontact_state",
        "value": true,
        "time": 1765254512345
      }
    ]
  },
  "ts": 1765254512345
}
```

### Protocol 4 (Older format):
```json
{
  "devId": "your_device_id",
  "status": [
    {
      "code": "doorcontact_state",
      "value": false,
      "t": 1765254512345
    }
  ],
  "t": 1765254512345
}
```

Kode `tuya_listener.py` sudah handle kedua format otomatis.

### CATATAN ENCRYPTION:
- **ECB Mode**: SDK auto-decrypt message, akses langsung ke `bizData`
- **AES-GCM Mode**: Membutuhkan manual decryption (tidak direkomendasikan)
- Gunakan ECB mode untuk kemudahan implementasi

## Recommendations

### Untuk Production:
1. ✅ Gunakan Pulsar jika Message Service tersedia
2. ✅ Monitor stability selama 24-48 jam pertama
3. ✅ Setup fallback ke polling jika Pulsar down
4. ✅ Monitor log untuk error patterns

### Untuk Development:
1. Test dengan polling dulu
2. Baru switch ke Pulsar setelah stable
3. Keep both options available untuk debugging

## Performance Metrics

Setelah switch ke Pulsar, Anda akan lihat:

**API Call Reduction:**
- Polling: ~288 calls/hari
- Pulsar: ~2-5 calls/hari (hanya untuk initial connection)
- **Savings: 98%+**

**Latency Improvement:**
- Polling: 30 detik - 5 menit delay
- Pulsar: 0-2 detik delay
- **Improvement: 99%+**

**Quota Impact:**
- Polling: ~8,640 calls/bulan
- Pulsar: ~50-100 calls/bulan
- **Savings: 99%+**

## References

- [Tuya Pulsar SDK Documentation](https://developer.tuya.com/en/docs/iot/Pulsar-SDK-get-message-python?id=Kawi5gt8ft5jx)
- [Message Service Guide](https://developer.tuya.com/en/docs/iot/message-service?id=K95zu0nzdw9cd)
- [tuya-connector-python GitHub](https://github.com/tuya/tuya-connector-python)
