# packages/2-intelligence-layer-fetchai/Dockerfile
# Dockerfile untuk membangun image bagi semua agen Python.

# Gunakan image dasar Python yang ringan
FROM python:3.10-slim

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching yang lebih baik
COPY requirements.txt .

# Instal semua dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode agen dan file lainnya
COPY . .

# Perintah default (dapat di-override oleh docker-compose.yml)
# CMD ["python", "agents/oracle_agent.py"]
