# Aegis Protocol - A Decentralized Disaster Response Framework

[![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D88D3)](https://dorahacks.io/buidl/13593)

Aegis Protocol is an autonomous digital institution that serves as a global safety net for humanity. This project combines decentralized AI with blockchain technology for fast, transparent, and decentralized disaster response.

---

## 🏛 Architecture

The Aegis Protocol architecture consists of two main layers that communicate with each other:

1. **Intelligence Layer (Fetch.ai):** Functions as the "nervous system" of the protocol. This decentralized network of autonomous AI agents proactively monitors global data to detect and validate disasters.
2. **Execution Layer (Internet Computer):** Functions as the "backbone" of execution and trust. Running on Internet Computer, this layer manages DAO creation, fund treasury, voting, and on-chain reputation systems.

- **Detailed Architecture Diagram:** [View here](./docs/diagrams/endgame_architecture.mermaid)

---

## ✨ Main Features & Innovation

### ICP Features Used
- **Canister Smart Contracts:** All backend logic, including DAO and insurance vaults, deployed as canisters running entirely on-chain.
- **"Reverse Gas" Model:** Users (donors, NGOs) can interact with the application without paying gas fees, removing adoption barriers.
- **On-Chain Web Serving:** Capability to host frontend interfaces directly from canisters, creating fully decentralized applications.
- **On-Chain Identity & Assets:** Managing identity (DID) and reputation assets (SBTs) permanently on the blockchain.

### Fetch.ai Features Used
- **uAgents (Micro-agents):** Building autonomous AI agents (oracle, validator, action) that can communicate and act independently.
- **Agentverse / ASI:One:** Providing a platform for communication and interaction between agents, including implementation of **Chat Protocol** needed for demo.
- **Decentralized AI Network:** Leveraging the Fetch.ai network as a foundation for intelligent and censorship-resistant decentralized oracles.

---

## 🤖 Fetch.ai Agent Details (For Judges)

Here are the details of the agents running on Fetch.ai, according to hackathon requirements.

- **Oracle Agent (oracle_agent_usgs)**
  - **Address:** Address will be generated when the agent is run.
  - **Task:** Monitor external data sources (USGS) to detect disaster anomalies.

- **Validator Agent (validator_agent_alpha)**
  - **Address:** `agent1q2gwxq52k8wecuvj3sksv9sszefaqpmq42u0mf6z0q5z4e0a9z0wz9z0q`
  - **Task:** Receive raw data, perform validation, and reach consensus. This agent implements **Fetch.ai Chat Protocol** and can interact through Agentverse/ASI:One.

- **Action Agent (action_agent_bridge)**
  - **Address:** Address will be generated when the agent is run.
  - **Task:** Receive consensus results and call smart contracts on Internet Computer.

---

## 🚀 How to Run the Project (Local Development) – WSL Version

This project uses **Docker Compose** to simplify the setup and execution process.
**⚠️ All `bash` commands are run in different terminals (different WSL tabs/instances).**

---

### 1. Prerequisites

Make sure your device has the following installed:

- Docker & Docker Compose
- Git
- (Optional, if using WSL) install `dos2unix` to avoid line ending issues (CRLF) on `.sh` files:

```bash
sudo apt update && sudo apt install dos2unix -y
```

---

### 2. Clone Repository

```bash
git clone https://github.com/ntfound-dev/AEGIS-Protocol.git
cd AEGIS-Protocol
```

---

### 3. Line Ending Conversion (WSL/Windows Users Only)

If you cloned this repo on Windows and then run it on WSL, some `.sh` files might not be executable due to line ending format. Run:

```bash
dos2unix scripts/*.sh
```

---

### 4. Create Environment File

Create a `.env` file in the root directory with the following content:

```bash
# API keys for external services (e.g., OpenAI, etc.)
# Get your own API keys and insert them here. NEVER share your .env file.
ASI_ONE_API_KEY=

# Canister name on Internet Computer
CANISTER_NAME=event_factory

# Seed phrases for generating agent private keys.
# Generate new seed phrases for each deployment. DO NOT use these examples.
# You can use online mnemonic generators or dedicated libraries for this.
VALIDATOR_AGENT_SEED=""
ACTION_AGENT_SEED=""
ORACLE_AGENT_SEED=""

# Agent addresses will be generated automatically when agents first run.
# After running docker compose up, copy agent addresses from logs and paste here for subsequent runs.
VALIDATOR_AGENT_ADDRESS=
ACTION_AGENT_ADDRESS=
ORACLE_AGENT_ADDRESS=

# Chain / Internet Computer configuration
# These defaults are usually suitable for local development.
CHAIN_ID="dorado-1"
ICP_URL="http://host.docker.internal:4943"
CANISTER_IDS_PATH="/app/dfx-local/canister_ids.json"
IDENTITY_PEM_PATH="/app/identity.pem"
```

The `.env` file must be located in the **root project**.

---

### 5. Identity & Principal (**Run this first**)

To get the **principal identity**, run:

```bash
dfx identity get-principal
```

When prompted for password, use default: `Mei2000`.

> ⚠️ **Note**: This step must be done first before running other services.

---

### 6. Create Action Agent Identity Keys

Open a **new WSL terminal**, then run:

```bash
bash scripts/generate-keys.sh
```

---

### 7. Run All Manual Scripts (Required, Separate Terminals)

Every component in this project is interdependent and must be run in parallel. Therefore, **all the following scripts must be run one by one in different WSL terminals (separate)**.

Open three separate WSL terminals, then run the following commands in sequence (each in its own terminal):

**Terminal 1:**
```bash
bash ./scripts/deploy-blockchain.sh
```

**Terminal 2:**
```bash
bash ./scripts/run-agents.sh
```

**Terminal 3:**
```bash
bash ./scripts/run-frontend.sh
```

> ⚠️ **Note:** Do not run these scripts in the same terminal, as all these processes are part of one unified project that must run simultaneously.

---

### 8. Run Backend Services (Docker) – Optional / Last

Since Docker currently has some minor errors, this step is moved to the end.
If you want to try, run in a **new WSL terminal**:

```bash
# Build main service
docker-compose build dfx-replica

# Run all services
docker-compose up --build
```

---

## 📂 Project Structure
```
aegis-protocol/
├── .gitignore                    # Ignore unnecessary files (build artifacts, .env, .pem, etc.)
├── README.md                     # Main documentation: installation, setup, and running each service
├── Dockerfile                    # Docker configuration for root project
├── dfx.json                      # Main configuration file for DFINITY SDK (dfx)
├── mops.toml                     # Motoko package manager configuration
├── .env                          # Environment variables (generated from env.example)
├── env.example                   # Environment file template
├── identity.pem                  # Main identity key (ignored by gitignore)
├── install-mops.sh               # Script to install Motoko package manager
├── .ic-assets.json5              # Internet Computer assets configuration
│
├── docs/                         # Complete project documentation
│   ├── architecture.md           # In-depth technical architecture explanation
│   ├── concepts.md               # Vision and core concepts explanation of Aegis Protocol
│   ├── diagram.md                # Diagram documentation
│   ├── diagram.mermaid           # Mermaid diagram file
│   └── problem_and_solution_technical.md  # Technical problem and solution analysis
│
├── frontend/                     # <------------ [ FOR FRONTEND TEAM ]
│   ├── index.html                # Main page for Dashboard Demo
│   ├── main.js                   # Main frontend logic (replaces script.js)
│   ├── style.css                 # Page styling
│   ├── package.json              # Node.js dependencies for frontend
│   ├── package-lock.json         # Dependencies lock file
│   ├── vite.config.js            # Vite configuration for development server
│   └── node_modules/             # Node.js modules (auto-generated)
│
├── src/                          # <------------ [ FOR BLOCKCHAIN TEAM ]
│   ├── declarations/             # Auto-generated TypeScript/JavaScript bindings
│   │   ├── did_sbt_ledger/       # TypeScript declarations for DID SBT Ledger
│   │   ├── event_dao/            # TypeScript declarations for Event DAO
│   │   ├── event_factory/        # TypeScript declarations for Event Factory
│   │   ├── frontend/             # TypeScript declarations for Frontend canister
│   │   └── insurance_vault/      # TypeScript declarations for Insurance Vault
│   ├── did_sbt_ledger/
│   │   └── main.mo               # Canister for identity and reputation (DID & SBT)
│   ├── event_dao/
│   │   ├── main.mo               # Template canister for each disaster
│   │   ├── event_defs.mo         # Event definitions and data structures
│   │   └── types.mo              # Type definitions for Event DAO
│   ├── event_factory/
│   │   ├── main.mo               # Canister (factory) for creating EventDAO
│   │   └── types.mo              # Type definitions for Event Factory
│   ├── insurance_vault/
│   │   └── main.mo               # Parametric insurance vault canister
│   └── types/                    # Shared type definitions
│
├── services/                     # Backend services and deployment
│   ├── ai_agent/                  # <------------ [FOR AI TEAM]
│   │   ├── requirements.txt      # Python dependencies (uagents, requests, ic-py)
│   │   ├── Dockerfile            # Recipe for creating Docker container for agents
│   │   ├── docker-compose.yml    # Docker Compose configuration for backend services
│   │   ├── .env.example          # Backend environment template
│   │   ├── persistent/           # Persistent data for development
│   │   │   ├── dfx-local/        # Local dfx data
│   │   │   └── identity.pem      # Identity key for backend agents
│   │   └── agents/               # All AI agents folder
│   │       ├── oracle_agent.py   # Agent that monitors real-world data
│   │       ├── validator_agent.py # Agent that validates disaster data
│   │       ├── action_agent.py   # Agent that bridges to ICP
│   │       └── chatbotrepair/    # Chatbot repair agents
│   │           ├── asi_one.py    # ASI.One integration agent
│   │           └── functions.py  # Utility functions for chatbot
│   └── dfx/
│       └── Dockerfile            # Docker configuration for DFX service
│
├── .dfx/                         # Folder automatically created by dfx (build artifacts)
│   ├── local/                    # Local deployment artifacts
│   └── network/                  # Network deployment artifacts
│
└── scripts/                      # Automation scripts
    ├── deploy-blockchain.sh      # Script to deploy all canisters
    ├── run-agents.sh             # Script to run all Python agents
    ├── run-frontend.sh           # Script to run frontend development server
    └── generate-keys.sh          # Script to create new identity.pem
```

---

## 🎯 Future Plans (Post-Hackathon)

- **Q4 2025:** Testnet Launch, inviting the first 5 NGO partners for trials.
- **Q1 2026:** Security Audit & Mainnet Beta Launch with Flutter frontend.
- **Q2 2026:** $AEGIS Tokenomics Development for governance and staking.
- **Q3 2026:** Global Expansion through partnerships with international humanitarian agencies.

## 🧗 Challenges During Hackathon

1. **Ecosystem Interoperability:** Designing reliable communication protocols between Python agents on Fetch.ai with Motoko canisters on ICP.
2. **Real-time Simulation:** Integrating data sources for disaster detection simulation by Oracle Agent.
3. **Team Workflow:** Coordinating teams with different expertise (Blockchain, AI, Frontend) in a short time.
