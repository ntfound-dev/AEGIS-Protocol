#!/usr/bin/env bash
# run-frontend.sh
# Versi: 1.0
# Purpose: setup and run frontend (vite + @dfinity/* packages)
set -euo pipefail

# Brief configuration
FRONTEND_DIR="frontend"
DFINITY_PKGS=( "@dfinity/agent" "@dfinity/auth-client" "@dfinity/candid" "@dfinity/principal" )
VITE_PACKAGE="vite"

# If you want to only install without running dev server:
# SKIP_START=1 ./run-frontend.sh
SKIP_START="${SKIP_START:-0}"

# Check npm & node
if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm not found. Install node/npm first." >&2
  exit 2
fi
if ! command -v node >/dev/null 2>&1; then
  echo "Error: node not found. Install node/npm first." >&2
  exit 2
fi

# Enter frontend directory
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Directory '$FRONTEND_DIR' not found. Create it first or run from the correct location." >&2
  exit 3
fi
cd "$FRONTEND_DIR"

echo "Working dir: $(pwd)"

# npm init if package.json doesn't exist yet
if [ ! -f package.json ]; then
  echo "package.json not found — running: npm init -y"
  npm init -y
else
  echo "package.json already exists — skip npm init"
fi

# Install vite as dev dependency (check first if already installed)
if npm list --depth=0 2>/dev/null | grep -q " ${VITE_PACKAGE}@"; then
  echo "vite already installed (devDependency) — skip"
else
  echo "Installing vite as devDependency..."
  npm install --save-dev "$VITE_PACKAGE"
fi

# Install @dfinity packages if not yet available
for pkg in "${DFINITY_PKGS[@]}"; do
  if npm list --depth=0 2>/dev/null | grep -q " ${pkg}@"; then
    echo "$pkg already installed — skip"
  else
    echo "Installing $pkg ..."
    npm install "$pkg"
  fi
done

# Add "dev": "vite" script to package.json if not yet available
has_dev_script=$(node -e "let p=require('./package.json'); console.log(p.scripts && p.scripts.dev ? '1' : '0');")
if [ "$has_dev_script" = "1" ]; then
  echo "'dev' script already exists in package.json — skip addition"
else
  echo "Adding 'dev' script to package.json..."
  node -e "let p=require('./package.json'); p.scripts=p.scripts||{}; p.scripts.dev='vite'; require('fs').writeFileSync('package.json', JSON.stringify(p,null,2)); console.log('added dev script to package.json');"
fi

# Run dev server unless asked to skip
if [ "$SKIP_START" != "1" ]; then
  echo "Running: npm run dev"
  # Run npm run dev (not run in background — this will hold the terminal)
  npm run dev
else
  echo "SKIP_START=1 detected — setup complete, not running 'npm run dev'."
fi
