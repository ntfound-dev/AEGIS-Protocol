# Menggunakan image dasar Python yang ringan dan modern
FROM python:3.10-slim

# Menetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching yang lebih baik
COPY requirements.txt .

# Instal semua dependensi dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode agen dan file lainnya ke dalam container
COPY . .

# Perintah default ini tidak akan digunakan karena kita menentukannya di docker-compose.yml,
# tapi ini adalah praktik yang baik untuk menyertakannya.
CMD ["python", "agents/oracle_agent.py"]