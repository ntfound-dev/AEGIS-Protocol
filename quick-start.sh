#!/bin/bash

# Quick start script for AEGIS Protocol
# This script sets up the environment and starts the protocol with automatic deployment

echo "🚀 AEGIS Protocol Quick Start"
echo "================================"

# Check if .env exists, if not create it from template
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created with automatic deployment mode"
else
    echo "✅ .env file already exists"
fi

# Ensure automatic deployment mode is set
if ! grep -q "DEPLOY_MODE=auto" .env; then
    echo "🔧 Setting automatic deployment mode..."
    echo "DEPLOY_MODE=auto" >> .env
fi

echo ""
echo "🐳 Starting Docker containers..."
echo "   This will:"
echo "   1. Build AI agent containers"
echo "   2. Start DFX replica"
echo "   3. Automatically deploy canisters"
echo "   4. Start AI agents with race condition protection"
echo ""

docker-compose up -d --build

echo ""
echo "⏳ Monitoring deployment progress..."
echo "   Press Ctrl+C to stop monitoring (containers will keep running)"
echo ""

# Monitor deployment in parallel
docker logs aegis-dfx-replica -f &
DFX_PID=$!

# Wait a bit then show agent logs
sleep 10
echo ""
echo "📋 Agent startup logs:"
docker logs aegis-action-agent

# Clean up background process on exit
trap "kill $DFX_PID 2>/dev/null" EXIT

wait $DFX_PID
