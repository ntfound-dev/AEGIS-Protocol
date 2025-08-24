#!/usr/bin/env bash
# scripts/deploy-blockchain.sh
# Deploy ICP canisters in local environment (WSL/Ubuntu).
# Run from project root folder.
set -euo pipefail
IFS=$'\n\t'

# ---------- Color configuration & helpers ----------
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log(){ echo -e "${YELLOW}[INFO]${NC} $*"; }
ok(){ echo -e "${GREEN}[OK]${NC} $*"; }
warn(){ echo -e "${RED}[WARN]${NC} $*"; }

# ---------- Load DFX env ----------
if [ -f "$HOME/.local/share/dfx/env" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.local/share/dfx/env"
  log "Loaded dfx environment from $HOME/.local/share/dfx/env"
else
  warn "DFX environment not found at $HOME/.local/share/dfx/env. Make sure dfx is installed."
  exit 1
fi

PROJECT_ROOT="$(pwd)"
LOG_FILE="${PROJECT_ROOT}/aegis_test_run.log"

log "Starting Canister Deployment from project root: ${PROJECT_ROOT}"

# ---------- Stop existing dfx/replica if any ----------
if pgrep -f "dfx" >/dev/null 2>&1 || pgrep -f "replica" >/dev/null 2>&1; then
  log "Existing dfx/replica detected — stopping..."
  dfx stop >/dev/null 2>&1 || true
  sleep 1
  log "All local network processes stopped"
fi

# ---------- Remove project .dfx directory ----------
if [ -d "${PROJECT_ROOT}/.dfx" ]; then
  log "Removing project .dfx directory: ${PROJECT_ROOT}/.dfx"
  rm -rf "${PROJECT_ROOT}/.dfx"
  log "Removed ${PROJECT_ROOT}/.dfx"
else
  log "No ${PROJECT_ROOT}/.dfx directory to remove"
fi

# ---------- Ensure dfx version (optional) ----------
if ! dfx cache show > /dev/null 2>&1; then
  log "dfx cache not available locally. Attempting to set default via dfxvm (ignored if not installed)..."
  dfxvm default 0.29.0 >/dev/null 2>&1 || true
fi

# ---------- Start local replica ----------
log "Starting local DFINITY replica..."
dfx start --background --clean

# Wait until replica listening on 127.0.0.1:4943 (timeout ~30s)
log "Waiting for replica to become available (127.0.0.1:4943)..."
for i in {1..30}; do
  if (echo > /dev/tcp/127.0.0.1/4943) >/dev/null 2>&1; then
    log "Replica is listening on 127.0.0.1:4943"
    break
  fi
  sleep 1
  if [ "$i" -eq 30 ]; then
    warn "Replica not responsive after 30 seconds. Check 'dfx start' output."
    exit 1
  fi
done

# ---------- Admin principal ----------
ADMIN_PRINCIPAL=$(dfx identity get-principal)
log "Admin principal: $ADMIN_PRINCIPAL"

# ---------- Remove previous identities (as requested) ----------
log "Removing previous identities (if exist): funder, organizer, community_a, community_b"
dfx identity remove funder >/dev/null 2>&1 || true
dfx identity remove organizer >/dev/null 2>&1 || true
dfx identity remove community_a >/dev/null 2>&1 || true
dfx identity remove community_b >/dev/null 2>&1 || true
log "Removal commands executed."

# ---------- Create new identities (try non-interactive then fallback interactive) ----------
log "Creating identities: funder, organizer, community_a, community_b"
for ID in funder organizer community_a community_b; do
  if dfx identity new "$ID" --storage-mode=plaintext >/dev/null 2>&1; then
    log "Created identity '$ID' with --storage-mode=plaintext"
  else
    log "Could not create '$ID' with --storage-mode=plaintext — falling back to interactive creation (enter passphrase if prompted)"
    # This may prompt for passphrase; allow it but don't fail script on user cancel
    dfx identity new "$ID" || true
  fi
done

# ---------- Collect principals (if exist) ----------
get_principal_safe(){
  local id="$1"
  if dfx identity list | grep -qx "$id"; then
    dfx --identity "$id" identity get-principal 2>/dev/null || echo ""
  else
    echo ""
  fi
}

FUNDER_PRINCIPAL=$(get_principal_safe funder || true)
ORGANIZER_PRINCIPAL=$(get_principal_safe organizer || true)
COMMUNITY_A_PRINCIPAL=$(get_principal_safe community_a || true)
COMMUNITY_B_PRINCIPAL=$(get_principal_safe community_b || true)

log "Principals (may be <none> if not created):"
log "  funder:    ${FUNDER_PRINCIPAL:-<none>}"
log "  organizer: ${ORGANIZER_PRINCIPAL:-<none>}"
log "  community_a: ${COMMUNITY_A_PRINCIPAL:-<none>}"
log "  community_b: ${COMMUNITY_B_PRINCIPAL:-<none>}"

# ---------- Deploy: interactive by default, or auto-answer if AUTO_INIT_PRINCIPAL set ----------
if [ -n "${AUTO_INIT_PRINCIPAL:-}" ]; then
  P="${AUTO_INIT_PRINCIPAL}"
  log "AUTO_INIT_PRINCIPAL set — will auto-answer init prompts with: ${P}"
  # Build answers: did_sbt_ledger expects 1 principal + confirm
  # frontend expects 3 principals + confirm (adjust if your project differs)
  ANSWERS="${P}\ny\n${P}\n${P}\n${P}\ny\n"
  log "Running non-interactive 'dfx deploy' with automated answers..."
  # show masked preview to log file for debug (first 200 chars)
  printf "%b" "$ANSWERS" | sed -n '1,5p' | sed 's/^/   /' >> "${LOG_FILE}" 2>/dev/null || true
  if ! printf "%b" "$ANSWERS" | dfx deploy; then
    warn "dfx deploy (auto-answer mode) failed. Check prompts/order or try deploy interactive."
    exit 1
  fi
else
  log "Deploying all canisters (interactive). If prompted for principal, enter the desired principal once only."
  dfx deploy
fi

# ---------- Generate declarations ----------
dfx generate

# ---------- Save principals to log ----------
{
  echo "--- SAVE PRINCIPALS ---"
  echo "Admin/Default: $ADMIN_PRINCIPAL"
  echo "Funder:        ${FUNDER_PRINCIPAL:-<none>}"
  echo "Organizer:     ${ORGANIZER_PRINCIPAL:-<none>}"
  echo "Community A:   ${COMMUNITY_A_PRINCIPAL:-<none>}"
  echo "Community B:   ${COMMUNITY_B_PRINCIPAL:-<none>}"
  echo "------------------------------------"
} | tee -a "${LOG_FILE}"

ok "Canisters deployed successfully."
log "Replica is running in the background. Use 'dfx stop' to stop it."

# End of script
