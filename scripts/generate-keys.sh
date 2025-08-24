#!/bin/bash

# scripts/generate-keys.sh
# Script to create new PEM private key for Action Agent in project root folder.

# Colors for output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Generating new identity for Action Agent...${NC}"

# This script must be run from the project root folder (AEGIS_Protocol)
OUTPUT_PATH="identity.pem"

# Check if openssl is installed
if ! command -v openssl &> /dev/null
then
    echo "Error: openssl could not be found. Please install it."
    exit 1
fi

# Generate new EC (Elliptic Curve) private key using secp256k1 curve
# This is the type of key used by Internet Computer
openssl ecparam -name secp256k1 -genkey -noout -out "$OUTPUT_PATH"

# Check if file was successfully created
if [ -f "$OUTPUT_PATH" ]; then
  echo -e "${GREEN}✅ New key file '$OUTPUT_PATH' created successfully in the project root directory.${NC}"
  echo "🔒 Please ensure this file is listed in your .gitignore and is kept secure."
else
  echo "Error: Failed to create key file."
  exit 1
fi