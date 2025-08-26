#!/bin/bash

# ======================================================================
# AEGIS Protocol - Identity Key Generation Script
# ======================================================================
# File: scripts/generate-keys.sh
# Purpose: Creates a new secp256k1 private key for Action Agent
#          to authenticate with Internet Computer canisters
# 
# Security Context:
#   - Generates cryptographic keys for blockchain authentication
#   - Keys are used by Python AI agents to call IC canister functions
#   - Must be kept secure and never committed to version control
# 
# Usage: Run from project root directory
#        ./scripts/generate-keys.sh
# 
# Output: Creates identity.pem in project root
# Dependencies: OpenSSL for key generation
# ======================================================================

# ======================================================================
# CONFIGURATION AND INITIALIZATION
# ======================================================================

# Terminal color codes for user-friendly output
YELLOW='\033[1;33m'  # Warning/info messages
GREEN='\033[0;32m'   # Success messages
NC='\033[0m'         # Reset to default color

echo -e "${YELLOW}Generating new identity for Action Agent...${NC}"

# Output file path - must be in project root for agents to find it
# This file will be copied to Docker containers by run-agents.sh
OUTPUT_PATH="identity.pem"

# ======================================================================
# DEPENDENCY VERIFICATION
# ======================================================================
# Verify OpenSSL is available for cryptographic key generation

if ! command -v openssl &> /dev/null
then
    echo "Error: openssl could not be found. Please install it."
    echo "Ubuntu/Debian: sudo apt-get install openssl"
    echo "macOS: brew install openssl (or use system version)"
    echo "Windows: Install OpenSSL or use WSL"
    exit 1
fi

# ======================================================================
# CRYPTOGRAPHIC KEY GENERATION
# ======================================================================
# Generate elliptic curve private key using secp256k1 curve
# 
# Why secp256k1?
#   - Same curve used by Bitcoin and Ethereum
#   - Supported by Internet Computer for authentication
#   - Provides 128-bit security level
#   - Well-tested and widely adopted
# 
# Key format: PEM (Privacy Enhanced Mail)
#   - Standard format for storing cryptographic keys
#   - Base64 encoded with headers/footers
#   - Compatible with IC identity libraries

openssl ecparam -name secp256k1 -genkey -noout -out "$OUTPUT_PATH"

# ======================================================================
# VERIFICATION AND SECURITY GUIDANCE
# ======================================================================
# Verify key file was created successfully and provide security guidance

if [ -f "$OUTPUT_PATH" ]; then
  echo -e "${GREEN}✅ New key file '$OUTPUT_PATH' created successfully in the project root directory.${NC}"
  echo "🔒 SECURITY IMPORTANT: Please ensure this file is listed in your .gitignore and is kept secure."
  echo "📋 Key Details:"
  echo "   - Algorithm: ECDSA with secp256k1 curve"
  echo "   - Format: PEM (Privacy Enhanced Mail)"
  echo "   - Usage: Internet Computer canister authentication"
  echo "   - Location: $(pwd)/$OUTPUT_PATH"
  echo ""
  echo "⚠️  NEVER share this private key or commit it to version control!"
  echo "💡 The corresponding public key will be derived automatically by the IC agent."
else
  echo "❌ Error: Failed to create key file."
  echo "   Check OpenSSL installation and write permissions in current directory."
  exit 1
fi