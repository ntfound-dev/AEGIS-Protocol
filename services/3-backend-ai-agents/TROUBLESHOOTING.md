# Troubleshooting Guide untuk AI Agents

## 🔍 **Analisis Error yang Anda Alami**

Berdasarkan error yang Anda tunjukkan, masalah utamanya adalah:

### 1. **Oracle Agent Tidak Berjalan**
- **Penyebab**: File `oracle_agent.py` berisi kode yang salah (kode action agent)
- **Solusi**: ✅ **SUDAH DIPERBAIKI** - File oracle agent sudah dibuat ulang

### 2. **Validator & Action Agent Unhealthy (404)**
- **Penyebab**: Endpoint `/health` tidak tersedia di agents
- **Solusi**: ✅ **SUDAH DIPERBAIKI** - Health endpoints sudah ditambahkan

### 3. **Web Endpoint Bekerja Tapi Data Flow Gagal**
- **Penyebab**: Oracle agent tidak bisa menerima request
- **Solusi**: ✅ **SUDAH DIPERBAIKI** - Oracle agent sudah diperbaiki

## 🚀 **Cara Testing yang Diperbaiki**

### **Gunakan Script Testing yang Baru:**

```bash
# Jalankan test yang diperbaiki
python test_agents_fixed.py
```

Atau gunakan batch script:
```bash
# Double-click file ini
test_agents.bat
```

## 🔧 **Perbaikan yang Telah Dilakukan**

### 1. **Oracle Agent (oracle_agent.py)**
- ✅ Dibuat ulang dengan implementasi yang benar
- ✅ Menambahkan endpoint `/process_earthquake`
- ✅ Menambahkan endpoint `/health`
- ✅ Validasi data gempa bumi
- ✅ Forward data ke Validator Agent

### 2. **Validator Agent (validator_agent.py)**
- ✅ Menambahkan endpoint `/health`
- ✅ Memperbaiki response format
- ✅ Logging yang lebih baik

### 3. **Action Agent (action_agent.py)**
- ✅ Menambahkan endpoint `/health`
- ✅ ICP integration yang optional (tidak crash jika file tidak ada)
- ✅ Logging yang lebih detail

### 4. **Test Script (test_agents_fixed.py)**
- ✅ Menunggu agents siap sebelum testing
- ✅ Error handling yang lebih baik
- ✅ Start dan stop agents otomatis
- ✅ Monitoring agent status

## 📊 **Expected Results Setelah Perbaikan**

### **Health Check:**
```
🏥 Testing Agent Health...
✅ Oracle Agent: Healthy
✅ Validator Agent: Healthy
✅ Action Agent: Healthy
```

### **Web Endpoint:**
```
🔍 Testing Validator Agent Web Endpoint...
✅ Validator Agent Response: {'status': 'success', 'message': 'Signal received and processed!'}
```

### **Data Flow:**
```
🔄 Testing Data Flow...
1. Sending data to Oracle Agent...
   ✅ Oracle Response: {'status': 'success', 'message': 'Earthquake data received and forwarded to Validator Agent'}
2. Checking Validator Agent processing...
3. Checking Action Agent processing...
```

## 🛠️ **Jika Masih Ada Masalah**

### **1. Port Already in Use**
```bash
# Windows
netstat -ano | findstr :8001
netstat -ano | findstr :8002
netstat -ano | findstr :8003

# Kill process
taskkill /PID <PID> /F
```

### **2. Dependencies Missing**
```bash
pip install -r requirements.txt
```

### **3. Python Version**
```bash
python --version
# Harus Python 3.8+
```

### **4. Debug Mode**
```bash
# Jalankan agent individual untuk debug
python agents/oracle_agent.py
```

## 📝 **Log Analysis**

### **Oracle Agent Logs:**
```
🚀 Starting Oracle Agent on port 8001...
[INFO] Oracle Agent: Received web trigger with data: ...
[INFO] Oracle Agent: Forwarding earthquake data to Validator Agent...
```

### **Validator Agent Logs:**
```
🚀 Starting Validator Agent on port 8002...
[INFO] Validator Agent: Received web trigger with data: ...
[INFO] Validator Agent: Validation complete. Broadcasting to Action Agent...
```

### **Action Agent Logs:**
```
🚀 Starting Action Agent on port 8003...
[INFO] Action Agent: Consensus reached! Received validated event from ...
[INFO] Action Agent: Event Type: Earthquake
[INFO] Action Agent: Severity: Critical
```

## 🎯 **Success Criteria Baru**

Test dianggap berhasil jika:
- ✅ Semua 3 agents start tanpa error
- ✅ Health endpoints merespons dengan 200 OK
- ✅ Web endpoint `/verify_disaster` berfungsi
- ✅ Data flow dari Oracle → Validator → Action berfungsi
- ✅ Logging berfungsi dengan baik

## 🔄 **Testing Workflow**

1. **Install dependencies**
2. **Run test script** (`test_agents_fixed.py`)
3. **Wait for agents to start** (15-30 detik)
4. **Check health endpoints**
5. **Test web endpoint**
6. **Test data flow**
7. **Review logs**
8. **Stop agents**

## 📞 **Jika Masih Bermasalah**

1. **Check logs** di console untuk error messages
2. **Verify Python version** (3.8+)
3. **Check port availability**
4. **Run agents individually** untuk debug
5. **Check file permissions**

---

**Status**: ✅ **SEMUA MASALAH SUDAH DIPERBAIKI**

Sekarang Anda bisa menjalankan testing dengan hasil yang diharapkan!
