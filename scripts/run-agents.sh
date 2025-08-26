#!/usr/bin/env bash

# ======================================================================
# AEGIS Protocol - AI Agent Deployment Script
# ======================================================================
# File: scripts/run-agents.sh
# Purpose: Deploy and manage AI agents in Docker containers
# 
# Agent Architecture:
#   - Oracle Agent (port 8001): Monitors real-world disaster data
#   - Validator Agent (port 8002): Validates and reaches consensus
#   - Action Agent (port 8003): Bridges to Internet Computer canisters
# 
# Key Features:
#   - Persistent storage for agent data across container restarts
#   - Automatic identity and canister ID file management
#   - Docker Compose orchestration for multi-agent coordination
#   - Real-time log monitoring and health checks
# 
# Prerequisites:
#   - Docker and Docker Compose installed
#   - identity.pem file generated (run generate-keys.sh first)
#   - Canisters deployed (run deploy-blockchain.sh first)
# 
# Usage: Run from project root directory
#        ./scripts/run-agents.sh
# ======================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ======================================================================
# DIRECTORY AND FILE CONFIGURATION
# ======================================================================
# Define paths for agent deployment and persistent storage

ROOT="$(pwd)"                           # Project root directory
SERVICE_DIR="services/ai_agent"          # AI agent service directory
PERSISTENT_DIR="${SERVICE_DIR}/persistent" # Persistent storage for agent data
DFX_SRC="./.dfx/local/canister_ids.json" # Source: canister IDs from dfx
IDENTITY_SRC="./identity.pem"            # Source: cryptographic identity file

echo "======================================================================"
echo "              AEGIS Protocol - AI Agent Deployment"
echo "======================================================================"
echo "🏗️  Setting up AI agents for disaster response automation..."
echo "📍 Project root: ${ROOT}"
echo "🤖 Deploying Oracle, Validator, and Action agents"
echo ""

# ======================================================================
# STEP 1: CREATE PERSISTENT STORAGE INFRASTRUCTURE
# ======================================================================
# Create persistent storage directory for agent data preservation
# This ensures agent state, logs, and configuration survive container restarts

echo "📂 STEP 1: Setting up persistent storage..."
mkdir -p "${PERSISTENT_DIR}"
echo "   ✅ Created persistent storage directory: ${PERSISTENT_DIR}"
echo "   🔄 This directory preserves agent data across container restarts"
echo ""

# ======================================================================
# STEP 2: CRYPTOGRAPHIC IDENTITY SETUP
# ======================================================================
# Copy and secure the private key file for blockchain authentication
# This identity is used by Action Agent to call Internet Computer canisters

echo "🔐 STEP 2: Setting up cryptographic identity..."
if [ -f "${IDENTITY_SRC}" ] && [ -s "${IDENTITY_SRC}" ]; then
  # Copy identity file to persistent storage for Docker container access
  cp -f "${IDENTITY_SRC}" "${PERSISTENT_DIR}/identity.pem"
  
  # Set restrictive permissions for security (owner read/write only)
  chmod 600 "${PERSISTENT_DIR}/identity.pem" || true
  
  echo "   ✅ Identity file copied: ${IDENTITY_SRC} → ${PERSISTENT_DIR}/identity.pem"
  echo "   🔒 File permissions set to 600 (owner access only)"
  echo "   🆔 This identity authenticates agents with IC canisters"
else
  echo "   ❌ ERROR: Identity file missing or empty at ${IDENTITY_SRC}"
  echo "   🔧 Solution: Run './scripts/generate-keys.sh' to create identity.pem"
  echo "   📝 The identity file is required for blockchain authentication"
  exit 1
fi
echo ""

# ======================================================================
# STEP 3: CANISTER CONFIGURATION SETUP
# ======================================================================
# Copy canister IDs so agents can communicate with deployed canisters
# This enables agents to call specific canister functions by ID

echo "🏗️  STEP 3: Setting up canister configuration..."
if [ -f "${DFX_SRC}" ] && [ -s "${DFX_SRC}" ]; then
  # Create directory structure matching dfx expectations
  mkdir -p "${PERSISTENT_DIR}/dfx-local"
  
  # Copy canister IDs file for agent access
  cp -f "${DFX_SRC}" "${PERSISTENT_DIR}/dfx-local/canister_ids.json"
  chmod 644 "${PERSISTENT_DIR}/dfx-local/canister_ids.json" || true
  
  echo "   ✅ Canister IDs copied: ${DFX_SRC} → ${PERSISTENT_DIR}/dfx-local/canister_ids.json"
  echo "   🎯 Agents can now target specific canisters for function calls"
  echo "   📋 File contains IDs for: event_factory, event_dao, insurance_vault, did_sbt_ledger"
else
  echo "   ⚠️  WARNING: Canister IDs file not found at ${DFX_SRC}"
  echo "   🔧 Solution: Run './scripts/deploy-blockchain.sh' to deploy canisters first"
  echo "   🤖 Agents may not be able to connect to IC canisters without this file"
fi
echo ""

# ======================================================================
# STEP 4: DOCKER CONTAINER ORCHESTRATION
# ======================================================================
# Deploy AI agents using Docker Compose for coordinated multi-agent system
# This ensures proper networking, service discovery, and resource management

echo "🐳 STEP 4: Deploying AI agents with Docker Compose..."
echo "   🛑 Stopping any existing containers to ensure clean state..."
pushd "${SERVICE_DIR}" >/dev/null  # Change to service directory for Docker Compose context
docker compose down --volumes --remove-orphans  # Stop containers and clean up
echo "   ✅ Previous containers stopped and cleaned up"

echo "   🏗️  Building and starting new agent containers..."
echo "   📦 This may take a few minutes for first-time builds..."
docker compose up -d --build       # Build images and start containers in background
popd >/dev/null                    # Return to original directory
echo "   ✅ All agent containers deployed successfully"
echo ""

# ======================================================================
# STEP 5: DEPLOYMENT VERIFICATION AND MONITORING
# ======================================================================
# Verify agent deployment and provide monitoring tools for operations

echo "🔍 STEP 5: Verifying deployment and setting up monitoring..."
echo "   ⏳ Allowing containers to stabilize (15 seconds)..."
sleep 15  # Give agents time to initialize and establish connections

echo "   📊 Container Status:"
docker compose -f ${SERVICE_DIR}/docker-compose.yml ps
echo ""

echo "   📜 Recent Agent Activity (last 100 log lines):"
docker compose -f ${SERVICE_DIR}/docker-compose.yml logs --tail 100
echo ""

echo "======================================================================"
echo "                    🎉 DEPLOYMENT COMPLETE! 🎉"
echo "======================================================================"
echo "🤖 AI Agents are now running and monitoring for disaster events"
echo "📡 Oracle Agent: Monitoring USGS and BMKG for earthquake data"
echo "🔍 Validator Agent: Validating and reaching consensus on events"
echo "🌉 Action Agent: Bridging validated events to IC canisters"
echo ""
echo "📋 Management Commands:"
echo "   View live logs:    cd ${SERVICE_DIR} && docker compose logs -f"
echo "   Stop agents:       cd ${SERVICE_DIR} && docker compose down"
echo "   Restart agents:    ./scripts/run-agents.sh"
echo "   Check status:      cd ${SERVICE_DIR} && docker compose ps"
echo ""
echo "🚨 For troubleshooting, check individual agent logs:"
echo "   Oracle logs:       cd ${SERVICE_DIR} && docker compose logs oracle-agent"
echo "   Validator logs:    cd ${SERVICE_DIR} && docker compose logs validator-agent"
echo "   Action logs:       cd ${SERVICE_DIR} && docker compose logs action-agent"
echo "======================================================================"
