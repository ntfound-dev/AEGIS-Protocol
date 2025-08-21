# Docker Testing Guide untuk AI Agents

## 📋 **Overview**

Karena Anda sudah menjalankan `dfx-replica` dengan Docker Compose, AI agents seharusnya dijalankan sebagai Docker containers juga untuk integrasi yang tepat dengan blockchain ICP.

## 🚀 **Setup dan Testing dengan Docker**

### **1. Setup Awal (Satu Kali)**

#### **Windows:**
```bash
# Double-click file ini
setup_docker_testing.bat
```

#### **Linux/Mac:**
```bash
# Jalankan script setup
chmod +x setup_docker_testing.sh
./setup_docker_testing.sh
```

### **2. Testing dengan Docker**

```bash
# Jalankan test script yang mendukung Docker
python test_with_docker.py
```

## 🔧 **Manual Setup (Jika Script Tidak Berfungsi)**

### **Step 1: Pastikan dfx-replica Berjalan**
```bash
# Check status
docker ps | grep dfx-replica

# Jika tidak berjalan, start:
docker-compose up -d dfx-replica
```

### **Step 2: Buat File identity.pem**
```bash
# Di folder services/3-backend-ai-agents
echo "This is a test identity file for development only." > identity.pem
```

### **Step 3: Build dan Start AI Agents**
```bash
# Build Docker images
docker-compose build oracle-agent validator-agent action-agent

# Start agents
docker-compose up -d oracle-agent validator-agent action-agent
```

### **Step 4: Test Agents**
```bash
# Test health endpoints
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Run comprehensive test
python test_with_docker.py
```

## 📊 **Expected Results**

### **Docker Services Status:**
```
🔍 Checking Docker services...
✅ dfx-replica: Running
✅ oracle-agent: Running
✅ validator-agent: Running
✅ action-agent: Running
```

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

## 🐳 **Docker Commands**

### **Check Container Status:**
```bash
# List all containers
docker ps

# Check specific container logs
docker-compose logs oracle-agent
docker-compose logs validator-agent
docker-compose logs action-agent
```

### **Restart Services:**
```bash
# Restart all AI agents
docker-compose restart oracle-agent validator-agent action-agent

# Restart specific agent
docker-compose restart oracle-agent
```

### **Stop Services:**
```bash
# Stop all services
docker-compose down

# Stop only AI agents
docker-compose stop oracle-agent validator-agent action-agent
```

## 🔍 **Troubleshooting**

### **1. Container Tidak Start**
```bash
# Check logs
docker-compose logs oracle-agent

# Check if ports are available
netstat -ano | findstr :8001
netstat -ano | findstr :8002
netstat -ano | findstr :8003
```

### **2. dfx-replica Tidak Terhubung**
```bash
# Check dfx-replica status
docker ps | grep dfx-replica

# Check if port 4943 is accessible
curl http://localhost:4943
```

### **3. Identity File Error**
```bash
# Check if identity.pem exists
ls -la identity.pem

# Create test identity if missing
echo "Test identity for development" > identity.pem
```

### **4. Canister ID Not Found**
```bash
# Check if .dfx directory exists
ls -la ../../services/2-backend-blockchain-icp/.dfx

# Deploy blockchain contracts if needed
cd ../../services/2-backend-blockchain-icp
dfx deploy
```

## 📝 **Log Analysis**

### **Oracle Agent Logs:**
```bash
docker-compose logs oracle-agent
```
Expected output:
```
🚀 Starting Oracle Agent on port 8001...
[INFO] Oracle Agent: Received web trigger with data: ...
[INFO] Oracle Agent: Forwarding earthquake data to Validator Agent...
```

### **Validator Agent Logs:**
```bash
docker-compose logs validator-agent
```
Expected output:
```
🚀 Starting Validator Agent on port 8002...
[INFO] Validator Agent: Received web trigger with data: ...
[INFO] Validator Agent: Validation complete. Broadcasting to Action Agent...
```

### **Action Agent Logs:**
```bash
docker-compose logs action-agent
```
Expected output:
```
🚀 Starting Action Agent on port 8003...
[INFO] Action Agent: Consensus reached! Received validated event from ...
[INFO] Action Agent: Event Type: Earthquake
[INFO] Action Agent: Severity: Critical
```

## 🎯 **Success Criteria**

Test dianggap berhasil jika:
- ✅ dfx-replica container berjalan
- ✅ Semua 3 AI agent containers berjalan
- ✅ Health endpoints merespons dengan 200 OK
- ✅ Web endpoint `/verify_disaster` berfungsi
- ✅ Data flow dari Oracle → Validator → Action berfungsi
- ✅ Logging berfungsi dengan baik

## 🔄 **Testing Workflow**

1. **Setup Docker environment** (`setup_docker_testing.bat` atau `.sh`)
2. **Verify dfx-replica is running**
3. **Start AI agents** (otomatis dengan setup script)
4. **Wait for agents to be ready** (10-30 detik)
5. **Run comprehensive test** (`test_with_docker.py`)
6. **Check logs** jika ada masalah
7. **Stop services** jika diperlukan

## 📞 **Jika Masih Bermasalah**

1. **Check Docker status**: `docker info`
2. **Check container logs**: `docker-compose logs <service-name>`
3. **Verify ports**: `netstat -ano | findstr :8001`
4. **Check dfx-replica**: `curl http://localhost:4943`
5. **Restart services**: `docker-compose restart`

---

**Status**: ✅ **DOCKER SETUP READY**

Sekarang Anda bisa testing AI agents dengan integrasi blockchain ICP yang lengkap!
