# Gunakan image dasar Python 3.9 yang ramping
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements ke dalam kontainer
COPY enhanced_requirements.txt ./

# Instal semua dependensi
RUN pip install --no-cache-dir -r enhanced_requirements.txt

# Salin semua file proyek lainnya ke dalam kontainer
COPY . /app

# Paparkan port yang digunakan oleh aplikasi FastAPI
EXPOSE 8080

# Perintah untuk menjalankan aplikasi menggunakan Uvicorn
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]