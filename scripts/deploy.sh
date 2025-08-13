#!/bin/bash

# --- PERBAIKAN ---
# Baris ini secara manual memuat path untuk perintah dfx.
# Ini memperbaiki eror "dfx: command not found".
source "$HOME/.local/share/dfx/env"

# deploy.sh
# Skrip yang sudah disesuaikan dengan struktur folder baru Anda.

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Aegis Protocol deployment...${NC}"

# --- Langkah 1: Navigasi ke direktori ICP ---
# --- DIUBAH ---
echo "Navigating to ICP execution layer..."
cd packages/execlayer_icp || { echo "Error: Directory 'packages/execlayer_icp' not found."; exit 1; }

# --- Langkah 2: Mulai replika lokal (jika belum berjalan) ---
if ! dfx ping > /dev/null 2>&1; then
  echo "Starting local DFINITY replica..."
  dfx start --background --clean
else
  echo "Local DFINITY replica is already running."
fi

# --- Langkah 3: Deploy semua canister ---
echo -e "${YELLOW}Deploying all canisters to the local replica...${NC}"
dfx deploy

# Cek apakah deployment berhasil
if [ $? -ne 0 ]; then
  echo "Error: DFX deployment failed."
  exit 1
fi

echo -e "${GREEN}Canisters deployed successfully.${NC}"

# --- Langkah 4: Ekstrak Canister ID ---
echo "Extracting Event Factory canister ID..."
EVENT_FACTORY_ID=$(dfx canister id event_factory)

if [ -z "$EVENT_FACTORY_ID" ]; then
  echo "Error: Could not retrieve Event Factory canister ID."
  exit 1
fi

echo "Event Factory Canister ID: $EVENT_FACTORY_ID"

# --- Langkah 5: Konfigurasi Lingkungan Fetch.ai ---
echo "Configuring Fetch.ai intelligence layer environment..."
cd ../../ # Kembali ke root direktori

# --- DIUBAH ---
FETCH_AI_DIR="packages/AI_fetchai"
ENV_FILE="$FETCH_AI_DIR/.env"

# Buat file .env jika belum ada, dari contoh
if [ ! -f "$ENV_FILE" ]; then
  cp "$FETCH_AI_DIR/.env.example" "$ENV_FILE"
  echo "Created .env file from .env.example."
fi

# Hapus baris lama jika ada dan tambahkan yang baru
sed -i.bak '/EVENT_FACTORY_CANISTER_ID/d' "$ENV_FILE"
echo "EVENT_FACTORY_CANISTER_ID=$EVENT_FACTORY_ID" >> "$ENV_FILE"
rm "${ENV_FILE}.bak"

echo "Updated .env file with the new canister ID."

echo -e "${GREEN}✅ Deployment and configuration complete!${NC}"
echo "You can now start the Fetch.ai agents."
