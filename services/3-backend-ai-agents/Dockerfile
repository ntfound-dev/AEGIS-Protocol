# Menggunakan image dasar Python yang ringan dan modern
FROM python:3.10-slim

# Menetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching yang lebih baik
COPY requirements.txt .

# Upgrade pip dan install dependensi dengan optimasi timeout & binary
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefer-binary --default-timeout=200 \
       -r requirements.txt \
       -i https://pypi.org/simple

# Salin semua kode agen dan file lainnya ke dalam container
COPY . .

# Perintah default
CMD ["python", "agents/oracle_agent.py"]
