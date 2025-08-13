#!/bin/bash

# generate-keys.sh
# Skrip untuk membuat kunci privat PEM baru untuk Action Agent.
# Kunci ini digunakan untuk mengautentikasi panggilan ke Internet Computer.

# Warna untuk output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Generating new identity for Action Agent...${NC}"

FETCH_AI_DIR="packages/2-intelligence-layer-fetchai"
KEY_FILE="$FETCH_AI_DIR/identity.pem"

# Cek apakah openssl terinstal
if ! command -v openssl &> /dev/null
then
    echo "Error: openssl could not be found. Please install it."
    exit 1
fi

# Navigasi ke direktori yang benar
cd "$FETCH_AI_DIR" || { echo "Error: Directory '$FETCH_AI_DIR' not found."; exit 1; }

# Hasilkan kunci privat EC (Elliptic Curve) baru menggunakan kurva secp256k1
# Ini adalah jenis kunci yang digunakan oleh Internet Computer
openssl ecparam -name secp256k1 -genkey -noout -out identity.pem

# Cek apakah file berhasil dibuat
if [ -f "identity.pem" ]; then
  echo -e "${GREEN}✅ New key file 'identity.pem' created successfully in '$FETCH_AI_DIR'.${NC}"
  echo "🔒 Please ensure this file is listed in your .gitignore and is kept secure."
else
  echo "Error: Failed to create key file."
  exit 1
fi
