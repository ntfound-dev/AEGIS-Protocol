#!/bin/bash

# test.sh
# Skrip untuk menjalankan simulasi end-to-end dengan memulai semua agen.

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

FETCH_AI_DIR="packages/2-intelligence-layer-fetchai/agents"

# Fungsi untuk membersihkan proses yang berjalan di latar belakang saat skrip dihentikan
cleanup() {
    echo -e "\n${YELLOW}Stopping all agents...${NC}"
    # Menggunakan pkill untuk menghentikan proses Python yang menjalankan file agen
    pkill -f "python $FETCH_AI_DIR/oracle_agent.py"
    pkill -f "python $FETCH_AI_DIR/validator_agent.py"
    pkill -f "python $FETCH_AI_DIR/action_agent.py"
    echo "Cleanup complete."
    exit 0
}

# Menangkap sinyal interupsi (Ctrl+C) untuk menjalankan fungsi cleanup
trap cleanup INT

echo -e "${YELLOW}Starting all Aegis Protocol agents in the background...${NC}"

# Memulai setiap agen sebagai proses latar belakang dan mengarahkan output ke file log
python "$FETCH_AI_DIR/oracle_agent.py" > oracle_agent.log 2>&1 &
ORACLE_PID=$!
echo "Oracle Agent started with PID $ORACLE_PID. Log: oracle_agent.log"

python "$FETCH_AI_DIR/validator_agent.py" > validator_agent.log 2>&1 &
VALIDATOR_PID=$!
echo "Validator Agent started with PID $VALIDATOR_PID. Log: validator_agent.log"

python "$FETCH_AI_DIR/action_agent.py" > action_agent.log 2>&1 &
ACTION_PID=$!
echo "Action Agent started with PID $ACTION_PID. Log: action_agent.log"

echo -e "\n${GREEN}All agents are running.${NC}"
echo -e "You can monitor their activity with the following command:"
echo -e "${CYAN}tail -f *.log${NC}"
echo -e "\n------------------------------------------------------------"
echo -e "To simulate an event, the Oracle Agent is currently polling the USGS API."
echo -e "It will automatically detect significant earthquakes (>= 6.0 magnitude)."
echo -e "Watch the logs to see the system in action when an event occurs."
echo -e "------------------------------------------------------------\n"

echo -e "${YELLOW}Press Ctrl+C to stop all agents and clean up.${NC}"

# Menjaga skrip tetap berjalan agar proses latar belakang tidak mati
wait
