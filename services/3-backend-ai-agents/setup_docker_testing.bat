@echo off
echo ========================================
echo    AEGIS Protocol - Docker Setup
echo ========================================
echo.

echo [1] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)
echo ✅ Docker is running

echo.
echo [2] Checking docker-compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose not found. Please install docker-compose.
    pause
    exit /b 1
)
echo ✅ docker-compose is available

echo.
echo [3] Checking dfx-replica...
docker ps | findstr "aegis-dfx-replica" >nul
if %errorlevel% neq 0 (
    echo ⚠️ dfx-replica is not running. Starting it...
    cd ..\..
    docker-compose up -d dfx-replica
    if %errorlevel% neq 0 (
        echo ❌ Failed to start dfx-replica
        pause
        exit /b 1
    )
    echo ✅ dfx-replica started
) else (
    echo ✅ dfx-replica is already running
)

echo.
echo [4] Checking identity.pem...
if not exist "identity.pem" (
    echo ⚠️ identity.pem not found. Creating a test identity...
    echo This is a test identity file for development only. > identity.pem
    echo In production, you should use a proper ICP identity. >> identity.pem
    echo ✅ Test identity.pem created
) else (
    echo ✅ identity.pem exists
)

echo.
echo [5] Checking .dfx directory...
if not exist "..\..\services\2-backend-blockchain-icp\.dfx" (
    echo ⚠️ .dfx directory not found. This is needed for canister IDs.
    echo You may need to deploy the blockchain contracts first.
    echo Run: cd ..\..\services\2-backend-blockchain-icp ^&^& dfx deploy
) else (
    echo ✅ .dfx directory exists
)

echo.
echo [6] Building AI agents Docker image...
cd ..\..
docker-compose build oracle-agent validator-agent action-agent
if %errorlevel% neq 0 (
    echo ❌ Failed to build AI agents Docker image
    pause
    exit /b 1
)
echo ✅ AI agents Docker image built successfully

echo.
echo [7] Starting AI agents...
docker-compose up -d oracle-agent validator-agent action-agent
if %errorlevel% neq 0 (
    echo ❌ Failed to start AI agents
    pause
    exit /b 1
)
echo ✅ AI agents started successfully

echo.
echo [8] Waiting for agents to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [9] Checking agent status...
cd services\3-backend-ai-agents

echo Testing port 8001...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Oracle Agent OK
) else (
    echo ❌ Oracle Agent Failed
)

echo Testing port 8002...
curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Validator Agent OK
) else (
    echo ❌ Validator Agent Failed
)

echo Testing port 8003...
curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Action Agent OK
) else (
    echo ❌ Action Agent Failed
)

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo You can now run the test script:
echo python test_with_docker.py
echo.
echo Or check individual agents:
echo docker-compose logs oracle-agent
echo docker-compose logs validator-agent
echo docker-compose logs action-agent
echo.
pause
