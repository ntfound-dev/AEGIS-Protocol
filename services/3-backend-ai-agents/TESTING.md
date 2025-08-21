# Testing Guide untuk AI Agents

## 📋 Overview

Folder `3-backend-ai-agents` berisi 3 AI agents yang bekerja bersama untuk sistem deteksi dan respons bencana:

1. **Oracle Agent** (Port 8001) - Menerima data gempa bumi
2. **Validator Agent** (Port 8002) - Memvalidasi dan mengklasifikasikan data
3. **Action Agent** (Port 8003) - Menjalankan aksi berdasarkan hasil validasi

## 🚀 Cara Testing

### 1. Persiapan

```bash
# Install dependencies
cd services/3-backend-ai-agents
pip install -r requirements.txt
```

### 2. Testing Individual Agents

#### Test Oracle Agent:
```bash
python agents/oracle_agent.py
```

#### Test Validator Agent:
```bash
python agents/validator_agent.py
```

#### Test Action Agent:
```bash
python agents/action_agent.py
```

### 3. Testing Semua Agents Bersamaan

```bash
# Jalankan semua agents
python run_all_agents.py

# Dalam terminal terpisah, jalankan test
python test_agents.py
```

### 4. Testing dengan Docker

```bash
# Build dan jalankan dengan Docker
docker build -t aegis-ai-agents .
docker run -p 8001:8001 -p 8002:8002 -p 8003:8003 aegis-ai-agents
```

## 🧪 Test Scenarios

### Scenario 1: Data Flow Test
1. Kirim data gempa bumi ke Oracle Agent
2. Oracle Agent mengirim data ke Validator Agent
3. Validator Agent memvalidasi dan mengirim ke Action Agent
4. Action Agent menjalankan aksi (menyimpan ke blockchain)

### Scenario 2: Web Endpoint Test
1. Kirim POST request ke `http://localhost:8002/verify_disaster`
2. Validator Agent memproses data
3. Hasil dikirim ke Action Agent

### Scenario 3: Error Handling Test
1. Kirim data invalid
2. Test response error
3. Verifikasi logging

## 📊 Expected Results

### Validator Agent Response:
```json
{
  "status": "success",
  "message": "Event validated and sent to Action Agent",
  "severity": "Critical",
  "confidence_score": 0.95
}
```

### Health Check Response:
```json
{
  "status": "healthy",
  "agent": "validator_agent_alpha",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 Troubleshooting

### Common Issues:

1. **Port Already in Use**
   ```bash
   # Kill process on port
   lsof -ti:8001 | xargs kill -9
   lsof -ti:8002 | xargs kill -9
   lsof -ti:8003 | xargs kill -9
   ```

2. **Missing Dependencies**
   ```bash
   pip install uagents requests ic-py python-dotenv
   ```

3. **Agent Not Starting**
   - Check logs for error messages
   - Verify port availability
   - Check Python version (requires 3.8+)

### Debug Mode:

Untuk debugging, tambahkan environment variable:
```bash
export DEBUG=true
python agents/oracle_agent.py
```

## 📈 Performance Testing

### Load Test:
```bash
# Test dengan multiple requests
for i in {1..10}; do
  curl -X POST http://localhost:8002/verify_disaster \
    -H "Content-Type: application/json" \
    -d '{"source":"USGS","magnitude":7.5,"location":"Test","lat":0,"lon":0,"timestamp":1234567890}'
done
```

### Memory Usage:
```bash
# Monitor memory usage
ps aux | grep python
```

## 🎯 Success Criteria

Test dianggap berhasil jika:
- ✅ Semua 3 agents berjalan tanpa error
- ✅ Data flow berfungsi dari Oracle → Validator → Action
- ✅ Web endpoint merespons dengan benar
- ✅ Error handling berfungsi
- ✅ Logging berfungsi dengan baik

## 📝 Log Analysis

Logs akan muncul di console dengan format:
```
[INFO] Oracle Agent: Received earthquake data from USGS
[INFO] Validator Agent: Validation complete. Broadcasting to Action Agent
[INFO] Action Agent: Consensus reached! Received validated event
```

## 🔄 Continuous Testing

Untuk continuous testing, gunakan script:
```bash
# Run tests every 30 seconds
watch -n 30 python test_agents.py
```
