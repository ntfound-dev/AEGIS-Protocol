#!/bin/bash

# services/3-backend-ai-agents/auto_deploy.sh
# Automatic deployment script for DFX canisters

set -e

echo "🚀 Starting automatic DFX deployment..."

# Change to the dfx project directory
cd /work

# Check if dfx is available
if ! command -v dfx &> /dev/null; then
    echo "❌ dfx command not found"
    exit 1
fi

echo "⏳ Starting dfx replica..."
dfx start --background --clean --host 0.0.0.0

# Wait for replica to be ready
echo "⏳ Waiting for replica to be ready..."
sleep 10

# Check replica status
while ! dfx ping; do
    echo "Waiting for replica to respond..."
    sleep 2
done
echo "✅ Replica is ready!"

echo "📦 Installing dependencies..."
if [ -f "install-mops.sh" ]; then
    chmod +x install-mops.sh
    ./install-mops.sh
else
    echo "ℹ️  No install-mops.sh found, skipping dependency installation"
fi

echo "🚀 Deploying canisters..."
dfx deploy --yes

echo "✅ Deployment completed!"
echo "📋 Canister information:"
dfx canister status --all

# Keep the script running to maintain the replica
echo "🔄 Keeping replica running..."
tail -f /dev/null
