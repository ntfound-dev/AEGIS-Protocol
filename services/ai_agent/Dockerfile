# =====================================================================
# AEGIS Protocol - AI Agent Container
# =====================================================================
# Purpose: Multi-agent Python container for disaster monitoring system
# 
# Container Architecture:
#   - Lightweight Python runtime for efficient resource usage
#   - Multi-agent deployment (Oracle, Validator, Action)
#   - Secure non-root execution environment
#   - Health monitoring and automatic restart capabilities
# 
# Security Features:
#   - Non-root user execution for container security
#   - Minimal system dependencies to reduce attack surface
#   - Read-only filesystem with specific writable areas
#   - Resource limits for denial-of-service protection
# 
# Integration Points:
#   - Internet Computer: Blockchain communication via ic-py
#   - Fetch.ai Network: Agent communication via uagents
#   - External APIs: Disaster data sources (USGS, BMKG)
# =====================================================================

# Base image: Python 3.12 slim for optimal size/functionality balance
# Slim variant provides essential Python runtime without unnecessary packages
FROM python:3.12-slim

# Set working directory for all container operations
# All subsequent commands will execute in this directory
WORKDIR /app

# =====================================================================
# SYSTEM DEPENDENCIES INSTALLATION
# =====================================================================
# Install minimal system packages required for Python dependencies
# and blockchain/cryptographic operations

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# =====================================================================
# PYTHON DEPENDENCIES MANAGEMENT
# =====================================================================
# Copy requirements first for efficient Docker layer caching
# This enables dependency cache reuse when only source code changes
COPY requirements.txt .

# Install Python dependencies with optimization flags
# - No cache: Reduces image size by not storing pip cache
# - Upgrade pip: Ensures latest pip version for security and features
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =====================================================================
# APPLICATION SOURCE CODE
# =====================================================================
# Copy all application source code into the container
# This includes agent implementations and configuration files
COPY . .

# =====================================================================
# PYTHON PATH CONFIGURATION
# =====================================================================
# Configure Python module resolution for agent imports
# Enables proper import resolution for agent modules
ENV PYTHONPATH="/app:${PYTHONPATH}"

# =====================================================================
# SECURITY CONFIGURATION
# =====================================================================
# Create and switch to non-root user for enhanced container security
# Prevents privilege escalation attacks and follows security best practices
RUN useradd -m appuser
USER appuser

# =====================================================================
# HEALTH MONITORING
# =====================================================================
# Configure container health checks for automatic restart and monitoring
# Checks agent responsiveness every 30 seconds for operational status
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# =====================================================================
# DEFAULT CONTAINER COMMAND
# =====================================================================
# Default command for container startup (overrideable in docker-compose)
# Points to Action Agent as the primary blockchain bridge component
CMD ["python", "agents/action_agent.py"]
