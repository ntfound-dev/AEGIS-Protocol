#!/bin/bash
# Setup script untuk testing AI Agents dengan Docker

echo "========================================"
echo "   AEGIS Protocol - Docker Setup"
echo "========================================"
echo

# Check if Docker is running
echo "[1] Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✅ Docker is running"

# Check if docker-compose is available
echo
echo "[2] Checking docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi
echo "✅ docker-compose is available"

# Check if dfx-replica is running
echo
echo "[3] Checking dfx-replica..."
if ! docker ps | grep -q "aegis-dfx-replica"; then
    echo "⚠️ dfx-replica is not running. Starting it..."
    cd ../../  # Go to project root
    docker-compose up -d dfx-replica
    echo "✅ dfx-replica started"
else
    echo "✅ dfx-replica is already running"
fi

# Check if identity.pem exists
echo
echo "[4] Checking identity.pem..."
if [ ! -f "identity.pem" ]; then
    echo "⚠️ identity.pem not found. Creating a test identity..."
    echo "This is a test identity file for development only." > identity.pem
    echo "In production, you should use a proper ICP identity."
    echo "✅ Test identity.pem created"
else
    echo "✅ identity.pem exists"
fi

# Check if .dfx directory exists
echo
echo "[5] Checking .dfx directory..."
if [ ! -d "../../services/2-backend-blockchain-icp/.dfx" ]; then
    echo "⚠️ .dfx directory not found. This is needed for canister IDs."
    echo "You may need to deploy the blockchain contracts first."
    echo "Run: cd ../../services/2-backend-blockchain-icp && dfx deploy"
else
    echo "✅ .dfx directory exists"
fi

# Build AI agents Docker image
echo
echo "[6] Building AI agents Docker image..."
cd ../../  # Go to project root
docker-compose build oracle-agent validator-agent action-agent
if [ $? -eq 0 ]; then
    echo "✅ AI agents Docker image built successfully"
else
    echo "❌ Failed to build AI agents Docker image"
    exit 1
fi

# Start AI agents
echo
echo "[7] Starting AI agents..."
docker-compose up -d oracle-agent validator-agent action-agent
if [ $? -eq 0 ]; then
    echo "✅ AI agents started successfully"
else
    echo "❌ Failed to start AI agents"
    exit 1
fi

# Wait for agents to be ready
echo
echo "[8] Waiting for agents to be ready..."
sleep 10

# Check agent status
echo
echo "[9] Checking agent status..."
cd services/3-backend-ai-agents

# Test health endpoints
for port in 8001 8002 8003; do
    echo -n "Testing port $port... "
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ Failed"
    fi
done

echo
echo "========================================"
echo "   Setup Complete!"
echo "========================================"
echo
echo "You can now run the test script:"
echo "python test_with_docker.py"
echo
echo "Or check individual agents:"
echo "docker-compose logs oracle-agent"
echo "docker-compose logs validator-agent"
echo "docker-compose logs action-agent"
