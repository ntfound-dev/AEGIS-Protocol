# Gunakan base image Python yang ringan
FROM python:3.12-slim

# Set working directory di dalam container
WORKDIR /app

# Install dependensi sistem minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt lebih dulu supaya caching efisien
COPY requirements.txt .

# Install dependensi Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code
COPY . .

# Tambahkan services/ai_agent ke PYTHONPATH agar bisa import ai_agent.*
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Non-root user untuk keamanan
RUN useradd -m appuser
USER appuser

# Healthcheck bawaan Docker (cek service HTTP tiap 30s)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (bisa dioverride di docker-compose.yml)
CMD ["python", "ai_agent/agents/action_agent.py"]
