#!/bin/bash

# services/3-backend-ai-agents/init_script.sh
# Initialization script to ensure proper startup order

set -e

echo "🚀 Starting AEGIS Agent Initialization..."

# Wait for dfx-replica to be available
echo "⏳ Waiting for dfx-replica service to be ready..."
while ! nc -z dfx-replica 4943; do
    echo "Waiting for dfx-replica:4943..."
    sleep 2
done
echo "✅ dfx-replica is ready!"

# Check if canister_ids.json exists and is valid
CANISTER_IDS_PATH="/app/dfx-local/canister_ids.json"
MAX_WAIT=300  # 5 minutes
WAIT_TIME=0

echo "⏳ Waiting for canister deployment..."
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if [ -f "$CANISTER_IDS_PATH" ]; then
        # Check if the file contains valid JSON with local deployments
        if python3 -c "
import json, sys
try:
    with open('$CANISTER_IDS_PATH', 'r') as f:
        data = json.load(f)
    # Check if there's at least one canister with local deployment
    for name, info in data.items():
        if isinstance(info, dict) and 'local' in info:
            print(f'Found local deployment for {name}')
            sys.exit(0)
    sys.exit(1)
except:
    sys.exit(1)
" 2>/dev/null; then
            echo "✅ Canister deployment detected!"
            break
        fi
    fi
    
    echo "⏳ Still waiting for canister deployment... (${WAIT_TIME}s/${MAX_WAIT}s)"
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo "⚠️  Timeout waiting for canister deployment. Starting agent anyway..."
    echo "   ICP integration will be disabled until deployment completes."
fi

# Copy canister_ids.json to the expected location for backward compatibility
if [ -f "$CANISTER_IDS_PATH" ]; then
    cp "$CANISTER_IDS_PATH" "/app/canister_ids.json"
    echo "✅ Copied canister_ids.json to agent directory"
fi

echo "🚀 Starting $1..."
exec "$@"
