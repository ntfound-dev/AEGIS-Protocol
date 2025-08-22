# Deployment & Race Condition Fixes

## Overview

This document explains the race condition issues and their solutions in the AEGIS Protocol, particularly regarding the startup order between DFX replica, canister deployment, and AI agents.

## Race Condition Issues

### Problem 1: Agent Startup Before Canister Deployment

**Issue**: AI agents (particularly `action_agent.py`) start immediately when Docker Compose launches, but they expect canister IDs to be available in `/app/canister_ids.json`. If DFX hasn't deployed the canisters yet, this file doesn't exist, causing the agents to fail or operate without ICP integration.

**Root Cause**: Docker Compose starts all services simultaneously, but there's no guarantee that DFX deployment completes before agents start.

### Problem 2: Manual Deployment Requirement

**Issue**: The original setup required manual deployment steps:
1. Start containers with `docker-compose up`
2. Manually exec into dfx-replica container
3. Manually run `dfx start --background --clean`
4. Manually run `dfx deploy`

This created a poor developer experience and increased the chance of race conditions.

## Solutions Implemented

### 1. Intelligent Waiting Mechanism

Added `wait_for_canister_deployment()` function in `action_agent.py`:

```python
def wait_for_canister_deployment(timeout_seconds: int = 300) -> bool:
    """Wait for canister deployment to complete with proper timeout"""
    print(f"Waiting for canister deployment (timeout: {timeout_seconds}s)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        # Check if canister_ids.json exists and is not a directory
        if os.path.exists(CANISTER_IDS_PATH) and not os.path.isdir(CANISTER_IDS_PATH):
            try:
                # Verify the file is valid JSON and contains expected structure
                with open(CANISTER_IDS_PATH, "r") as f:
                    data = json.load(f)
                
                # Check if it contains at least one canister with local deployment
                for canister_name, canister_info in data.items():
                    if isinstance(canister_info, dict) and "local" in canister_info:
                        print(f"✅ Canister deployment detected! Found {canister_name}")
                        return True
                        
                print("📄 canister_ids.json exists but no local deployments found yet...")
                        
            except (json.JSONDecodeError, Exception) as e:
                print(f"📄 canister_ids.json exists but invalid: {e}")
        
        print(f"⏳ Waiting for canister deployment... ({int(time.time() - start_time)}s/{timeout_seconds}s)")
        time.sleep(5)  # Check every 5 seconds
    
    print("❌ Timeout waiting for canister deployment!")
    return False
```

**Benefits**:
- 5-minute timeout prevents infinite waiting
- Validates JSON structure, not just file existence
- Provides clear progress feedback
- Gracefully handles deployment failures

### 2. Initialization Script

Created `init_script.sh` that runs before each agent starts:

```bash
#!/bin/bash
# services/3-backend-ai-agents/init_script.sh

# Wait for dfx-replica to be available
while ! nc -z dfx-replica 4943; do
    echo "Waiting for dfx-replica:4943..."
    sleep 2
done

# Wait for canister deployment with timeout
# Validates canister_ids.json structure
# Copies file to expected location for backward compatibility
```

**Benefits**:
- Ensures network connectivity before starting agents
- Handles file path mapping between containers
- Provides consistent initialization across all agents

### 3. Automatic Deployment Mode

Enhanced `docker-compose.yml` with automatic deployment option:

```yaml
dfx-replica:
  environment:
    - DEPLOY_MODE=${DEPLOY_MODE:-auto}
  command: >
    bash -c "
      chmod +x /work/auto_deploy.sh;
      if [ \"$$DEPLOY_MODE\" = \"auto\" ]; then
        echo '🚀 Starting automatic deployment...';
        /work/auto_deploy.sh;
      else
        echo '📋 Manual deployment mode...';
        tail -f /dev/null;
      fi
    "
```

**Benefits**:
- `DEPLOY_MODE=auto`: Fully automated deployment (recommended for development)
- `DEPLOY_MODE=manual`: Traditional manual deployment (for debugging/production)
- Seamless switching between modes via environment variable

### 4. Auto-Deploy Script

Created `auto_deploy.sh` for fully automated DFX deployment:

```bash
#!/bin/bash
# services/3-backend-ai-agents/auto_deploy.sh

# Start dfx replica
dfx start --background --clean --host 0.0.0.0

# Wait for replica readiness
while ! dfx ping; do
    sleep 2
done

# Install dependencies
if [ -f "install-mops.sh" ]; then
    ./install-mops.sh
fi

# Deploy all canisters
dfx deploy --yes

# Keep replica running
tail -f /dev/null
```

**Benefits**:
- Zero manual intervention required
- Proper readiness checking
- Automatic dependency installation
- Maintains replica after deployment

## Usage Instructions

### Quick Start (Recommended)

1. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

2. Start with automatic deployment:
   ```bash
   docker-compose up -d --build
   ```

3. Monitor deployment:
   ```bash
   docker logs aegis-dfx-replica -f
   ```

4. Check agent status:
   ```bash
   docker logs aegis-action-agent -f
   ```

### Manual Deployment Mode

1. Set manual mode:
   ```bash
   echo "DEPLOY_MODE=manual" > .env
   ```

2. Start containers:
   ```bash
   docker-compose up -d --build
   ```

3. Deploy manually:
   ```bash
   docker exec -it aegis-dfx-replica bash
   dfx start --background --host 0.0.0.0
   dfx deploy
   ```

## Troubleshooting

### Issue: Agents still fail to connect to ICP

**Solution**: Check deployment status:
```bash
# Check if deployment completed
docker exec aegis-dfx-replica dfx canister status --all

# Check canister IDs are available
docker exec aegis-action-agent cat /app/canister_ids.json
```

### Issue: Timeout waiting for deployment

**Possible Causes**:
1. DFX build errors
2. Network connectivity issues
3. Resource constraints

**Solution**: Check deployment logs:
```bash
docker logs aegis-dfx-replica
```

### Issue: Agents restart repeatedly

**Cause**: Agents crash during canister waiting period

**Solution**: Check agent logs and increase timeout if needed:
```bash
docker logs aegis-action-agent
```

## Configuration Options

### Environment Variables

- `DEPLOY_MODE`: Controls deployment automation (`auto`/`manual`)
- `EVENT_FACTORY_CANISTER_ID`: Auto-populated after deployment
- `ICP_URL`: DFX replica URL (default: `http://dfx-replica:4943`)

### Timeouts

- Agent canister wait timeout: 300 seconds (5 minutes)
- DFX replica readiness timeout: No limit (retries every 2 seconds)
- Network connectivity timeout: No limit (retries every 2 seconds)

## Best Practices

1. **Use auto mode for development**: Eliminates manual steps and race conditions
2. **Use manual mode for debugging**: Allows step-by-step deployment troubleshooting
3. **Monitor logs during startup**: Watch for deployment progress and error messages
4. **Set proper resource limits**: Ensure sufficient CPU/memory for DFX compilation
5. **Test network connectivity**: Verify docker network communication between services
