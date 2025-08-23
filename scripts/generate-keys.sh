#!/bin/bash

# scripts/generate-keys.sh
# Skrip untuk membuat kunci privat PEM baru untuk Action Agent di root folder proyek.

# Warna untuk output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Generating new identity for Action Agent...${NC}"

# --- PERBAIKAN: Tentukan path output langsung di root folder ---
# Skrip ini harus dijalankan dari root folder proyek (AEGIS_Protocol)
OUTPUT_PATH="identity.pem"

# Cek apakah openssl terinstal
if ! command -v openssl &> /dev/null
then
    echo "Error: openssl could not be found. Please install it."
    exit 1
fi

# Hasilkan kunci privat EC (Elliptic Curve) baru menggunakan kurva secp256k1
# Ini adalah jenis kunci yang digunakan oleh Internet Computer
openssl ecparam -name secp256k1 -genkey -noout -out "$OUTPUT_PATH"

# Cek apakah file berhasil dibuat
if [ -f "$OUTPUT_PATH" ]; then
  echo -e "${GREEN}✅ New key file '$OUTPUT_PATH' created successfully in the project root directory.${NC}"
  echo "🔒 Please ensure this file is listed in your .gitignore and is kept secure."
else
  echo "Error: Failed to create key file."
  exit 1
fi