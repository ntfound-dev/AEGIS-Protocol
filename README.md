# Aegis Protocol - A Decentralized Disaster Response Framework

[![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D88D3)](https://dorahacks.io/buidl/13593)

Aegis Protocol is an autonomous digital institution that serves as a global safety net for humanity. This project combines decentralized AI with blockchain technology for fast, transparent, and decentralized disaster response.

---

## 🏛 Architecture

The Aegis Protocol architecture consists of two main layers that communicate with each other:

1.  *Intelligence Layer (Fetch.ai):* Functions as the "nervous system" of the protocol. This decentralized network of autonomous AI agents proactively monitors global data to detect and validate disasters.
2.  *Execution Layer (Internet Computer):* Functions as the "backbone" of execution and trust. Running on Internet Computer, this layer manages DAO creation, fund treasury, voting, and on-chain reputation systems.

* *Detailed Architecture Diagram:* [View here](./docs/diagrams/endgame_architecture.mermaid)

---

## ✨ Main Features & Innovation

### ICP Features Used
- *Canister Smart Contracts:* All backend logic, including DAO and insurance vaults, deployed as canisters running entirely on-chain.
- *"Reverse Gas" Model:* Users (donors, NGOs) can interact with the application without paying gas fees, removing adoption barriers.
- *On-Chain Web Serving:* Capability to host frontend interfaces directly from canisters, creating fully decentralized applications.
- *On-Chain Identity & Assets:* Managing identity (DID) and reputation assets (SBTs) permanently on the blockchain.

### Fetch.ai Features Used
- *uAgents (Micro-agents):* Building autonomous AI agents (oracle, validator, action) that can communicate and act independently.
- *Agentverse / ASI:One:* Providing a platform for communication and interaction between agents, including implementation of *Chat Protocol* needed for demo.
- *Decentralized AI Network:* Leveraging the Fetch.ai network as a foundation for intelligent and censorship-resistant decentralized oracles.

---

## 🤖 Fetch.ai Agent Details (For Judges)

Here are the details of the agents running on Fetch.ai, according to hackathon requirements.

* **Oracle Agent (oracle_agent_usgs)**
    * *Address:* Address will be generated when the agent is run.
    * *Task:* Monitor external data sources (USGS) to detect disaster anomalies.

* **Validator Agent (validator_agent_alpha)**
    * *Address:* agent1q2gwxq52k8wecuvj3sksv9sszefaqpmq42u0mf6z0q5z4e0a9z0wz9z0q
    * *Task:* Receive raw data, perform validation, and reach consensus. This agent implements *Fetch.ai Chat Protocol* and can interact through Agentverse/ASI:One.

* **Action Agent (action_agent_bridge)**
    * *Address:* Address will be generated when the agent is run.
    * *Task:* Receive consensus results and call smart contracts on Internet Computer.

---

# 🚀 How to Run the Project (Local Development) – *WSL Version*

This project uses **Docker Compose** to simplify the setup and execution process.
**⚠️ All `bash` commands are run in different terminals (different WSL tabs/instances).**

---

### 1. Prasyarat

Pastikan perangkat Anda sudah terinstal:

* Docker & Docker Compose
* Git
* (Opsional, jika menggunakan WSL) instal `dos2unix` untuk menghindari masalah line ending (CRLF) pada file `.sh`:

```bash
sudo apt update && sudo apt install dos2unix -y
```

---

### 2. Clone Repositori

```bash
git clone https://github.com/ntfound-dev/AEGIS-Protocol.git
cd AEGIS-Protocol
```

---

### 3. Konversi Line Ending (Khusus Pengguna WSL/Windows)

Jika Anda meng-clone repo ini di Windows lalu menjalankannya di WSL, beberapa file `.sh` mungkin tidak bisa dijalankan karena format line ending. Jalankan:

```bash
dos2unix scripts/*.sh
```

---

### 4. Buat File Environment

Sebelum menjalankan service, buat file `.env` dari contoh yang sudah ada:

```bash
cp env.example .env
```

File `.env` ini harus berada di **root project**.

---

### 5. Identitas & Principal (**Jalankan terlebih dahulu**)

Untuk mendapatkan **principal identitas**, jalankan:

```bash
dfx identity get-principal
```

Saat diminta password, gunakan default: `Mei2000`.

> ⚠️ **Catatan**: Langkah ini dilakukan dulu sebelum menjalankan service lainnya.

---

### 6. Buat Kunci Identitas Action Agent

Buka **terminal WSL baru**, lalu jalankan:

```bash
bash scripts/generate-keys.sh
```

---

### 7. Jalankan Seluruh Skrip Manual (Wajib, Terminal Terpisah)

Setiap komponen dalam proyek ini saling bergantung dan harus dijalankan secara paralel. Oleh karena itu, **seluruh skrip berikut wajib dijalankan satu per satu pada terminal WSL yang berbeda (terpisah)**.

Buka tiga terminal WSL terpisah, lalu jalankan perintah berikut secara berurutan (masing-masing pada terminalnya sendiri):

* **Terminal 1:**

```bash
bash ./scripts/deploy-blockchain.sh
```

* **Terminal 2:**

```bash
bash ./scripts/run-agents.sh
```

* **Terminal 3:**

```bash
bash ./scripts/run-frontend.sh
```

> ⚠️ Catatan: Jangan menjalankan skrip-skrip ini dalam satu terminal yang sama, karena seluruh proses tersebut merupakan bagian dari satu proyek kesatuan yang harus berjalan secara bersamaan.


---

### 8. Jalankan Layanan Backend (Docker) – *Opsional / Terakhir*

Karena saat ini Docker masih ada sedikit error, langkah ini dipindahkan ke akhir.
Jika ingin mencoba, jalankan di **terminal WSL baru**:

```bash
# Build service utama
docker-compose build dfx-replica

# Jalankan semua layanan
docker-compose up --build
```

---



## 📂 Struktur Proyek
```
aegis-protocol/
├── .gitignore                    # Mengabaikan file yang tidak perlu (build artifacts, .env, .pem, dll.)
├── README.md                     # Dokumentasi utama: cara instalasi, setup, dan menjalankan setiap layanan.
├── Dockerfile                    # Docker configuration untuk root project
├── dfx.json                      # File konfigurasi utama untuk DFINITY SDK (dfx)
├── mops.toml                     # Motoko package manager configuration
├── .env                          # Environment variables (generated dari env.example)
├── env.example                   # Template file environment
├── identity.pem                  # Kunci identitas utama (diabaikan oleh gitignore)
├── install-mops.sh               # Script untuk menginstall Motoko package manager
├── .ic-assets.json5              # Internet Computer assets configuration
│
├── docs/                         # Dokumentasi lengkap proyek
│   ├── architecture.md           # Penjelasan teknis arsitektur secara mendalam
│   ├── concepts.md               # Penjelasan visi dan konsep inti dari Aegis Protocol
│   ├── diagram.md                # Dokumentasi diagram
│   ├── diagram.mermaid           # File diagram Mermaid
│   └── problem_and_solution_technical.md  # Analisis teknis masalah dan solusi
│
├── frontend/                     # <------------ [ UNTUK TIM FRONTEND ]
│   ├── index.html                # Halaman utama untuk Dashboard Demo
│   ├── main.js                   # Logika utama frontend (menggantikan script.js)
│   ├── style.css                 # Styling halaman
│   ├── package.json              # Node.js dependencies untuk frontend
│   ├── package-lock.json         # Lock file untuk dependencies
│   ├── vite.config.js            # Vite configuration untuk development server
│   └── node_modules/             # Node.js modules (auto-generated)
│
├── src/                          # <------------ [ UNTUK TIM BLOCKCHAIN ]
│   ├── declarations/             # Auto-generated TypeScript/JavaScript bindings
│   │   ├── did_sbt_ledger/       # TypeScript declarations untuk DID SBT Ledger
│   │   ├── event_dao/            # TypeScript declarations untuk Event DAO
│   │   ├── event_factory/        # TypeScript declarations untuk Event Factory
│   │   ├── frontend/             # TypeScript declarations untuk Frontend canister
│   │   └── insurance_vault/      # TypeScript declarations untuk Insurance Vault
│   ├── did_sbt_ledger/
│   │   └── main.mo               # Canister untuk identitas dan reputasi (DID & SBT)
│   ├── event_dao/
│   │   ├── main.mo               # Template canister untuk setiap bencana
│   │   ├── event_defs.mo         # Definisi event dan struktur data
│   │   └── types.mo              # Type definitions untuk Event DAO
│   ├── event_factory/
│   │   ├── main.mo               # Canister (pabrik) untuk membuat EventDAO
│   │   └── types.mo              # Type definitions untuk Event Factory
│   ├── insurance_vault/
│   │   └── main.mo               # Canister brankas asuransi parametrik
│   └── types/                    # Shared type definitions
│
├── services/                     # Layanan backend dan deployment
│   ├── backend/                  # <------------ [UNTUK TIM AI]
│   │   ├── requirements.txt      # Dependensi Python (uagents, requests, ic-py)
│   │   ├── Dockerfile            # Resep untuk membuat container Docker untuk agen
│   │   ├── docker-compose.yml    # Docker Compose configuration untuk backend services
│   │   ├── .env.example          # Template environment untuk backend
│   │   ├── persistent/           # Data persisten untuk development
│   │   │   ├── dfx-local/        # Local dfx data
│   │   │   └── identity.pem      # Identity key untuk backend agents
│   │   └── agents/               # Folder semua AI agents
│   │       ├── oracle_agent.py   # Agen yang memantau data dunia nyata
│   │       ├── validator_agent.py # Agen yang memvalidasi data bencana
│   │       ├── action_agent.py   # Agen yang menjembatani ke ICP
│   │       └── chatbotrepair/    # Chatbot repair agents
│   │           ├── asi_one.py    # ASI.One integration agent
│   │           └── functions.py  # Utility functions untuk chatbot
│   └── dfx/
│       └── Dockerfile            # Docker configuration untuk DFX service
│
├── .dfx/                         # Folder yang dibuat otomatis oleh dfx (build artifacts)
│   ├── local/                    # Local deployment artifacts
│   └── network/                  # Network deployment artifacts
│
└── scripts/                      # Automation scripts
    ├── deploy-blockchain.sh      # Skrip untuk deploy semua canister
    ├── run-agents.sh             # Skrip untuk menjalankan semua agen Python
    ├── run-frontend.sh           # Skrip untuk menjalankan frontend development server
    └── generate-keys.sh          # Skrip untuk membuat identity.pem baru
```


## 🎯 Rencana Masa Depan (Pasca-Hackathon)

* *Q4 2025:* Peluncuran Testnet, mengundang 5 NGO mitra pertama untuk uji coba.
* *Q1 2026:* Audit Keamanan & Peluncuran Mainnet Beta dengan frontend Flutter.
* *Q2 2026:* Pengembangan Tokenomics $AEGIS untuk tata kelola dan staking.
* *Q3 2026:* Ekspansi Global melalui kemitraan dengan badan kemanusiaan internasional.

## 🧗 Tantangan Selama Hackathon

1.  *Interoperabilitas Ekosistem:* Merancang protokol komunikasi yang andal antara agen Python di Fetch.ai dengan canister Motoko di ICP.
2.  *Simulasi Real-time:* Mengintegrasikan sumber data untuk simulasi deteksi bencana oleh Oracle Agent.
3.  *Alur Kerja Tim:* Mengkoordinasikan tim dengan keahlian berbeda (Blockchain, AI, Frontend) dalam waktu singkat.
