#!/bin-bash

# scripts/deploy-blockchain.sh
# Skrip untuk men-deploy semua canister ICP di lingkungan lokal (WSL/Ubuntu).

# --- PERBAIKAN PENTING ---
# Baris ini secara manual memuat path untuk perintah dfx,
# memperbaiki eror "dfx: command not found".
source "$HOME/.local/share/dfx/env"

# Warna untuk output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Canister Deployment...${NC}"

# Arahkan ke direktori backend blockchain
BLOCKCHAIN_DIR="services/2-backend-blockchain-icp"

cd "$BLOCKCHAIN_DIR" || { echo "Error: Directory '$BLOCKCHAIN_DIR' not found."; exit 1; }

# Setel versi dfx default jika belum diatur
if ! dfx cache show > /dev/null 2>&1; then
    echo "Setting default dfx version..."
    dfxvm default 0.28.0 # Ganti dengan versi dfx Anda jika berbeda
fi

# Mulai replika lokal di latar belakang
echo "Starting local DFINITY replica..."
dfx start --background --clean

# Deploy semua canister yang terdefinisi di dfx.json
echo "Deploying all canisters..."
dfx deploy

if [ $? -ne 0 ]; then
  echo "Error: DFX deployment failed."
  dfx stop # Matikan replika jika deploy gagal
  exit 1
fi

echo -e "${GREEN}✅ Canisters deployed successfully.${NC}"
echo "You can now share the generated .did and canister_ids.json files with other teams."
echo "Replica is still running in the background. Use 'dfx stop' to turn it off."