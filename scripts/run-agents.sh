#!/bin/bash

# scripts/run-agents.sh (Versi Anti-Gagal)
# Skrip untuk membersihkan, membangun, dan menjalankan semua agen AI.
# HARUS DIJALANKAN DARI ROOT FOLDER PROYEK.

# Warna untuk output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}--- AEGIS AI AGENT LAUNCH PROTOCOL ---${NC}"

# Tentukan path ke file docker-compose.yml
COMPOSE_FILE="./services/3-backend-ai-agents/docker-compose.yml"

# --- LANGKAH 1: BERSIHKAN SEMUA CONTAINER LAMA ---
echo ""
echo -e "${YELLOW}Step 1: Cleaning up old containers (docker-compose down)...${NC}"
# Perintah 'down' akan menghentikan dan menghapus container dari sesi sebelumnya.
# Flag -v juga akan menghapus volume anonim.
docker-compose -f "$COMPOSE_FILE" down -v

if [ $? -ne 0 ]; then
  echo -e "${RED}Warning: 'docker-compose down' failed. This might be okay if it's the first run.${NC}"
fi

# --- LANGKAH 2: BANGUN & JALANKAN CONTAINER BARU ---
echo ""
echo -e "${YELLOW}Step 2: Building and starting all AI agents (docker-compose up)...${NC}"
docker-compose -f "$COMPOSE_FILE" up --build

echo ""
echo -e "${GREEN}✅ Launch sequence complete.${NC}"