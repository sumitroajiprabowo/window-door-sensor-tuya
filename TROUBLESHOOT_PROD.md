# Troubleshooting PROD Topic - No Events Received

## Issue
Setelah switch dari TEST ke PROD topic, events tidak muncul lagi.

## Kemungkinan Penyebab & Solusi

### 1. ⚠️ PROD Topic Belum Di-Enable di Tuya Console

**Gejala**: Koneksi berhasil tapi tidak ada message

**Cek di Tuya Console**:
1. Login ke https://iot.tuya.com/
2. Pilih Cloud Project Anda
3. Go to **Service API** > **Message Subscription**
4. Cek **Topic Type**:
   - ✅ Jika ada pilihan PROD: pastikan PROD di-enable
   - ⚠️ Jika hanya ada TEST: Anda harus menggunakan TEST topic

**Solusi**:
- Jika hanya tersedia TEST topic, kembalikan code ke TEST
- Jika PROD tersedia tapi belum di-enable, enable PROD topic

### 2. 🔴 Tuya Console Test Channel Masih Terbuka (PROD)

**Gejala**: Sama seperti sebelumnya - hanya 1 consumer allowed

**Cek**:
1. Buka Tuya Console
2. Go to **Message Subscription**
3. Cek apakah ada **Test Channel** atau **Debug Console** yang terbuka
4. **PASTIKAN SEMUA TEST CHANNEL DI-CLOSE**

**Catatan**: Limitation 1 consumer berlaku untuk PROD maupun TEST

### 3. 📡 Subscription Configuration Salah

**Gejala**: Tidak ada error 401, tapi tidak terima message

**Cek di Tuya Console**:
```
Service API > Message Subscription > Subscription Configuration
```

Pastikan:
- ✅ **Status**: Enabled
- ✅ **Topic**: PROD (bukan TEST)
- ✅ **Message Type**: Device Status Report
- ✅ **Encryption**: ECB

### 4. 🔐 Encryption Mode Berbeda antara TEST dan PROD

**Kemungkinan**: TEST dan PROD menggunakan encryption berbeda

**Cek**:
- TEST topic: ECB encryption
- PROD topic: Mungkin menggunakan AES-GCM?

**Solusi**: Cek di Tuya Console, pastikan PROD juga menggunakan ECB

### 5. 🌐 Regional Endpoint Issue

**Kemungkinan**: PROD dan TEST menggunakan endpoint berbeda

**Cek .env**:
```bash
# Pastikan endpoint sesuai region
TUYA_PULSAR_ENDPOINT=wss://mqe-sg.iotbing.com:8285/
```

**Regional Endpoints**:
- Singapore: `wss://mqe-sg.iotbing.com:8285/`
- US East: `wss://mqe.tuyaus.com:8285/`
- Europe: `wss://mqe.tuyaeu.com:8285/`
- China: `wss://mqe.tuyacn.com:8285/`

---

## 🔍 Debugging Steps

### Step 1: Cek Connection Status

Jalankan aplikasi dan lihat output:
```bash
python3 main.py
```

**Expected Output**:
```
============================================================
Starting Tuya Pulsar Listener...
Endpoint: wss://mqe-sg.iotbing.com:8285/
Monitoring Device: your_device_id
Topic: PROD Environment           ← Harus tertulis PROD
Encryption: ECB Mode
============================================================
Connecting to Pulsar WebSocket...
Pulsar connection started!       ← Koneksi berhasil
```

### Step 2: Enable Debug Logging

Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

Restart aplikasi dan cek log untuk:
- `[DEBUG] Raw message received: ...` ← Jika muncul, berarti messages datang
- `[DEBUG] Unknown message format: ...` ← Format message berbeda
- `[DEBUG] Ignored message from different device: ...` ← Device ID tidak match

### Step 3: Test dengan Door Sensor

1. Buka/tutup door sensor beberapa kali
2. Tunggu 5-10 detik
3. Cek console output

**Jika TIDAK ADA OUTPUT sama sekali**:
- ❌ Message tidak sampai ke aplikasi
- Kemungkinan: Consumer lain masih aktif atau PROD topic belum enabled

**Jika ADA OUTPUT tapi TIDAK MATCH**:
- ⚠️ Message datang tapi format atau device ID berbeda
- Cek debug log untuk detail

### Step 4: Cek Tuya Console Logs

Di Tuya Console:
1. Go to **Message Subscription** > **Logs**
2. Cek apakah ada message yang dikirim ke PROD topic
3. Lihat timestamp message

**Jika Logs Kosong**:
- Device tidak mengirim message ke PROD topic
- Kemungkinan: Device subscription hanya ke TEST topic

### Step 5: Verify Device Subscription

Di Tuya Console:
1. Go to **Devices**
2. Pilih door sensor Anda
3. Cek **Message Subscription** settings
4. Pastikan device ter-subscribe ke **PROD topic**

---

## 🔄 Solusi Cepat: Kembalikan ke TEST

Jika PROD tidak bekerja dan Anda butuh solusi cepat:

### Edit `services/tuya_listener.py` line 45-46:

**Kembalikan ke TEST**:
```python
self.open_pulsar = TuyaOpenPulsar(
    self.access_id, self.access_secret, self.endpoint, TuyaCloudPulsarTopic.TEST
)
```

**Dan line 222**:
```python
print(f"Topic: TEST Environment")
```

Restart aplikasi - seharusnya events muncul lagi.

---

## 📋 Checklist Troubleshooting

Gunakan checklist ini untuk debug:

- [ ] Tuya Console Test Channel sudah di-close SEMUA
- [ ] PROD topic tersedia dan enabled di Tuya Console
- [ ] Device ter-subscribe ke PROD topic (bukan hanya TEST)
- [ ] Encryption mode PROD = ECB (sama dengan TEST)
- [ ] Regional endpoint sesuai dengan region Anda
- [ ] LOG_LEVEL=DEBUG untuk melihat raw messages
- [ ] Tidak ada consumer lain yang aktif
- [ ] Door sensor online dan berfungsi (test di Tuya app)
- [ ] Device ID di .env sesuai dengan device yang ditest

---

## 🆘 Jika Masih Tidak Bisa

### Option 1: Gunakan TEST Topic (Recommended)
Jika TEST bekerja dengan baik, gunakan TEST topic saja.
TEST dan PROD fungsinya sama, hanya berbeda environment.

### Option 2: Contact Tuya Support
Kemungkinan ada limitation atau configuration khusus untuk PROD topic di account Anda.

### Option 3: Cek Message Service Subscription Plan
Beberapa plan mungkin hanya support TEST topic.
Cek di **Console** > **Billing** > **Message Service Plan**

---

## 📞 Command untuk Debug

### Cek apakah Pulsar SDK bisa detect topic:
```python
from tuya_connector import TuyaCloudPulsarTopic
print(f"TEST topic: {TuyaCloudPulsarTopic.TEST}")
print(f"PROD topic: {TuyaCloudPulsarTopic.PROD}")
```

Output seharusnya:
```
TEST topic: <enum value>
PROD topic: <enum value>
```

---

## 💡 Tips

1. **Jangan panik** - TEST dan PROD secara functional identik
2. **TEST topic bukan "testing mode"** - ini fully functional untuk production
3. **Single consumer limit** berlaku untuk TEST dan PROD
4. Jika TEST bekerja sempurna, tidak ada masalah menggunakannya untuk production

---

**Last Updated**: 2024-12-16
**Status**: Troubleshooting Guide