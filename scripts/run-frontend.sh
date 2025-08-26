#!/usr/bin/env bash

# ======================================================================
# AEGIS Protocol - Frontend Development Server Script
# ======================================================================
# File: scripts/run-frontend.sh
# Purpose: Set up and run the AEGIS Protocol frontend development server
# 
# Frontend Architecture:
#   - Vite: Modern build tool for fast development and hot reloading
#   - @dfinity/*: Internet Computer SDK for blockchain integration
#   - Vanilla JS: Lightweight frontend without heavy framework overhead
# 
# Key Features:
#   - Automatic dependency installation and version management
#   - Hot module replacement for instant development feedback
#   - IC agent integration for canister communication
#   - Gasless user interactions via IC reverse gas model
# 
# Development Benefits:
#   - Fast refresh during development (sub-second updates)
#   - Direct integration with local IC replica
#   - No complex build pipeline - serves static assets efficiently
# 
# Usage: Run from project root directory
#        ./scripts/run-frontend.sh
# Environment Variables:
#        SKIP_START=1 ./scripts/run-frontend.sh  # Setup only, don't start server
# ======================================================================
# ======================================================================
# SCRIPT CONFIGURATION AND SAFETY
# ======================================================================
set -euo pipefail  # Exit on error, undefined variables, or pipe failures

# ======================================================================
# FRONTEND DEPENDENCIES AND CONFIGURATION
# ======================================================================
# Define required packages and build tools for AEGIS frontend

# Core frontend directory containing HTML, CSS, JS assets
FRONTEND_DIR="frontend"

# Internet Computer SDK packages for blockchain integration
# These provide the necessary tools for IC canister communication
DFINITY_PKGS=( 
  "@dfinity/agent"      # Core IC agent for canister calls
  "@dfinity/auth-client" # User authentication and identity management
  "@dfinity/candid"      # Candid interface definition language support
  "@dfinity/principal"   # Principal ID handling and validation
)

# Modern build tool for fast development experience
VITE_PACKAGE="vite"

# Environment variable to control script behavior
# Set SKIP_START=1 to only install dependencies without starting dev server
# Useful for CI/CD pipelines or when preparing environment only
SKIP_START="${SKIP_START:-0}"

# ======================================================================
# DEVELOPMENT ENVIRONMENT VERIFICATION
# ======================================================================
# Ensure required development tools are available

echo "======================================================================"
echo "              AEGIS Protocol - Frontend Development Setup"
echo "======================================================================"
echo "🏛️  Preparing modern web frontend for disaster response interface..."
echo ""

# Verify Node.js runtime is available
if ! command -v npm >/dev/null 2>&1; then
  echo "❌ Error: npm not found. Node.js package manager is required." >&2
  echo "🔧 Installation options:" >&2
  echo "   - Ubuntu/Debian: sudo apt update && sudo apt install nodejs npm" >&2
  echo "   - macOS: brew install node" >&2
  echo "   - Windows: Download from https://nodejs.org/" >&2
  echo "   - Or use Node Version Manager (nvm) for version management" >&2
  exit 2
fi

# Verify Node.js itself is available (npm might exist without node)
if ! command -v node >/dev/null 2>&1; then
  echo "❌ Error: node not found. Node.js runtime is required." >&2
  echo "🔧 Please install Node.js runtime alongside npm" >&2
  exit 2
fi

echo "✅ Node.js and npm are available"
echo "   Node version: $(node --version)"
echo "   npm version:  $(npm --version)"
echo ""

# ======================================================================
# FRONTEND DIRECTORY SETUP
# ======================================================================
# Navigate to frontend directory and verify project structure

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "❌ Directory '$FRONTEND_DIR' not found in current location." >&2
  echo "🔧 Ensure you're running this script from the AEGIS project root directory." >&2
  echo "📋 Expected structure: ./frontend/ containing HTML, CSS, and JS files" >&2
  exit 3
fi

cd "$FRONTEND_DIR"
echo "📍 Working directory: $(pwd)"
echo "📁 Setting up frontend in: $FRONTEND_DIR/"
echo ""

# ======================================================================
# NPM PROJECT INITIALIZATION
# ======================================================================
# Initialize package.json if it doesn't exist for dependency management

echo "📦 Checking NPM project configuration..."
if [ ! -f package.json ]; then
  echo "   🆕 package.json not found - initializing new NPM project"
  echo "   🔨 Running: npm init -y (creates basic package.json)"
  npm init -y
  echo "   ✅ NPM project initialized successfully"
else
  echo "   ✅ package.json already exists - skipping initialization"
  echo "   📝 Project: $(node -e "console.log(require('./package.json').name || 'unnamed')")"
  echo "   🏷️  Version: $(node -e "console.log(require('./package.json').version || 'unknown')")"
fi
echo ""

# ======================================================================
# VITE BUILD TOOL INSTALLATION
# ======================================================================
# Install Vite as development dependency for fast build and dev server

echo "⚡ Setting up Vite build tool..."
if npm list --depth=0 2>/dev/null | grep -q " ${VITE_PACKAGE}@"; then
  echo "   ✅ Vite already installed as devDependency - skipping installation"
  echo "   📊 Installed version: $(npm list $VITE_PACKAGE --depth=0 | grep $VITE_PACKAGE | sed 's/.*@//')"
else
  echo "   🔄 Installing Vite as devDependency for development server..."
  echo "   📝 Vite provides fast HMR (Hot Module Replacement) and efficient bundling"
  npm install --save-dev "$VITE_PACKAGE"
  echo "   ✅ Vite installed successfully"
fi
echo ""

# ======================================================================
# INTERNET COMPUTER SDK INSTALLATION
# ======================================================================
# Install @dfinity packages for blockchain integration capabilities

echo "🌐 Setting up Internet Computer SDK packages..."
echo "🔗 These packages enable direct communication with IC canisters"

for pkg in "${DFINITY_PKGS[@]}"; do
  if npm list --depth=0 2>/dev/null | grep -q " ${pkg}@"; then
    echo "   ✅ $pkg already installed - skipping"
  else
    echo "   🔄 Installing $pkg for IC integration..."
    case "$pkg" in
      "@dfinity/agent")
        echo "      🤖 Core IC agent for making canister calls"
        ;;
      "@dfinity/auth-client")
        echo "      🔐 User authentication and identity management"
        ;;
      "@dfinity/candid")
        echo "      📜 Candid interface definitions for type safety"
        ;;
      "@dfinity/principal")
        echo "      🆔 Principal ID utilities for addressing"
        ;;
    esac
    npm install "$pkg"
    echo "   ✅ $pkg installed successfully"
  fi
done
echo ""

# ======================================================================
# DEVELOPMENT SCRIPT CONFIGURATION
# ======================================================================
# Add 'dev' script to package.json for easy development server startup

echo "🔧 Configuring development scripts..."
has_dev_script=$(node -e "let p=require('./package.json'); console.log(p.scripts && p.scripts.dev ? '1' : '0');")
if [ "$has_dev_script" = "1" ]; then
  echo "   ✅ 'dev' script already exists in package.json"
  echo "   📋 Current dev script: $(node -e "console.log(require('./package.json').scripts.dev)")"
else
  echo "   🔄 Adding 'dev' script to package.json for Vite development server..."
  node -e "let p=require('./package.json'); p.scripts=p.scripts||{}; p.scripts.dev='vite'; require('fs').writeFileSync('package.json', JSON.stringify(p,null,2)); console.log('   ✅ Added dev script: vite');"
fi
echo ""

# ======================================================================
# DEVELOPMENT SERVER STARTUP
# ======================================================================
# Start Vite development server unless explicitly skipped

if [ "$SKIP_START" != "1" ]; then
  echo "======================================================================"
  echo "                    🚀 STARTING DEVELOPMENT SERVER"
  echo "======================================================================"
  echo "🌐 Starting Vite development server for AEGIS Protocol frontend..."
  echo "🔥 Features enabled:"
  echo "   ⚡ Hot Module Replacement (instant updates on file changes)"
  echo "   🔄 Fast refresh for rapid development cycles"
  echo "   🌐 Integration with local IC replica (if running)"
  echo "   📱 Responsive design for desktop and mobile access"
  echo ""
  echo "📝 Access URLs (will be displayed by Vite):"
  echo "   Local:   http://localhost:[port]     (for development)"
  echo "   Network: http://[ip]:[port]         (for testing on devices)"
  echo ""
  echo "🚨 Development Notes:"
  echo "   - Press Ctrl+C to stop the development server"
  echo "   - Server will automatically restart on configuration changes"
  echo "   - For production deployment, assets are served from IC canister"
  echo ""
  echo "======================================================================"
  
  # Start development server (this will hold the terminal)
  npm run dev
else
  echo "======================================================================"
  echo "                    ✅ SETUP COMPLETE"
  echo "======================================================================"
  echo "🏁 Frontend environment setup completed successfully!"
  echo "🛑 Development server startup skipped (SKIP_START=1 detected)"
  echo ""
  echo "📋 Manual startup commands:"
  echo "   Start dev server:    cd frontend && npm run dev"
  echo "   Build for production: cd frontend && npm run build"
  echo "   Install new deps:    cd frontend && npm install [package]"
  echo ""
  echo "🌐 When ready to start development:"
  echo "   1. Ensure IC replica is running (./scripts/deploy-blockchain.sh)"
  echo "   2. Start development server (cd frontend && npm run dev)"
  echo "   3. Open browser to localhost URL displayed by Vite"
  echo "======================================================================"
fi
