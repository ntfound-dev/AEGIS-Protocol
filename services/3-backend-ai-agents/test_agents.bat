@echo off
echo ========================================
echo    AEGIS Protocol - AI Agents Testing
echo ========================================
echo.

echo [1] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo.
echo [3] Starting AI Agents...
echo Starting Oracle Agent on port 8001...
start "Oracle Agent" python agents/oracle_agent.py

timeout /t 3 /nobreak >nul

echo Starting Validator Agent on port 8002...
start "Validator Agent" python agents/validator_agent.py

timeout /t 3 /nobreak >nul

echo Starting Action Agent on port 8003...
start "Action Agent" python agents/action_agent.py

echo.
echo [4] Waiting for agents to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [5] Running tests...
python test_agents_fixed.py

echo.
echo [6] Press any key to stop all agents...
pause >nul

echo.
echo [7] Stopping all agents...
taskkill /f /im python.exe 2>nul
echo All agents stopped.

echo.
echo Testing complete!
pause
