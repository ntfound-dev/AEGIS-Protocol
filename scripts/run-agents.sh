#!/usr/bin/env bash

set -euo pipefail

ROOT="$(pwd)"
SERVICE_DIR="services/ai_agent"
PERSISTENT_DIR="${SERVICE_DIR}/persistent"
DFX_SRC="./.dfx/local/canister_ids.json"
IDENTITY_SRC="./identity.pem"

echo "==== Running Agents (Long-term Setup) ===="
echo "Project root: ${ROOT}"
echo

# --- STEP 1: CREATE STORAGE FOLDER ---
# Docker needs this folder to store agent data so it doesn't get lost when container stops.
mkdir -p "${PERSISTENT_DIR}"
echo "- Ensuring ${PERSISTENT_DIR} folder exists."

# --- STEP 2: COPY IDENTITY KEY ---
# Check if identity.pem exists and is not empty, then copy it to storage folder.
if [ -f "${IDENTITY_SRC}" ] && [ -s "${IDENTITY_SRC}" ]; then
  cp -f "${IDENTITY_SRC}" "${PERSISTENT_DIR}/identity.pem"
  chmod 600 "${PERSISTENT_DIR}/identity.pem" || true # Set file permissions for security
  echo "- Copying identity.pem -> ${PERSISTENT_DIR}/identity.pem (permissions 600)"
else
  echo "ERROR: identity.pem not found or empty at ${IDENTITY_SRC}."
  echo "Please create a valid identity.pem file in the project root before continuing."
  exit 1
fi

# --- STEP 3: COPY CANISTER IDs ---
# Check if canister_ids.json exists, then copy it so agents inside Docker can read it.
if [ -f "${DFX_SRC}" ] && [ -s "${DFX_SRC}" ]; then
  mkdir -p "${PERSISTENT_DIR}/dfx-local"
  cp -f "${DFX_SRC}" "${PERSISTENT_DIR}/dfx-local/canister_ids.json"
  chmod 644 "${PERSISTENT_DIR}/dfx-local/canister_ids.json" || true
  echo "- Copying canister_ids.json -> ${PERSISTENT_DIR}/dfx-local/canister_ids.json"
else
  # Give warning if file doesn't exist, but don't stop the script.
  echo "WARNING: canister_ids.json not found at ${DFX_SRC}. Agents might not be able to connect to local canisters."
fi

# --- STEP 4: RESTART DOCKER CONTAINERS ---
echo "- Stopping old containers if any (docker compose down)..."
pushd "${SERVICE_DIR}" >/dev/null # Temporarily move into service folder
docker compose down               # This command stops & removes old containers to ensure clean restart
echo "- Building and starting new containers (docker compose up -d --build)..."
docker compose up -d --build      # Run docker compose to create new ones
popd >/dev/null                   # Return to original folder

# --- STEP 5: WAIT AND DISPLAY LOGS ---
echo "- Waiting for containers to stabilize (about 20 seconds) ..."
sleep 10
docker compose -f ${SERVICE_DIR}/docker-compose.yml ps

echo "- Displaying last 150 log lines:"
docker compose -f ${SERVICE_DIR}/docker-compose.yml logs --tail 150

echo
echo "Done. To view logs in real-time, use:"
echo "  cd ${SERVICE_DIR}"
echo "  docker compose logs -f"
