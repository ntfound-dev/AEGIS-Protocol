#!/bin-bash

# scripts/run-agents.sh
# Skrip untuk menjalankan semua agen Python di lingkungan lokal (WSL/Ubuntu).
# Skrip ini akan membuka tab terminal baru untuk setiap agen.

# Arahkan ke direktori agen AI
AGENT_DIR="services/3-backend-ai-agents"

cd "$AGENT_DIR" || { echo "Error: Directory '$AGENT_DIR' not found."; exit 1; }

echo "Starting all AI Agents in separate terminals..."

# Cek apakah berada di dalam Windows Terminal untuk membuka tab baru
if [ -n "$WT_SESSION" ]; then
    # Jalankan setiap agen di tab baru
    wt new-tab --title "Oracle Agent" -- bash -c "echo '--- ORACLE AGENT ---'; python agents/oracle_agent.py; exec bash"
    wt new-tab --title "Validator Agent" -- bash -c "echo '--- VALIDATOR AGENT ---'; python agents/validator_agent.py; exec bash"
    wt new-tab --title "Action Agent" -- bash -c "echo '--- ACTION AGENT ---'; python agents/action_agent.py; exec bash"
else
    echo "This script works best inside Windows Terminal to open new tabs."
    echo "Please start each agent manually in a separate terminal:"
    echo "1. python agents/oracle_agent.py"
    echo "2. python agents/validator_agent.py"
    echo "3. python agents/action_agent.py"
fi