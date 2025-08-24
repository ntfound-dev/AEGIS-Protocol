# Aegis Protocol - A Decentralized Disaster Response Framework

[![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D88D3)](https://dorahacks.io/buidl/13593)

Aegis Protocol adalah institusi digital otonom yang berfungsi sebagai jaring pengaman global untuk kemanusiaan. Proyek ini menggabungkan AI terdesentralisasi dengan teknologi blockchain untuk respons bencana yang cepat, transparan, dan terdesentralisasi.

---

## 🏛 Arsitektur

Arsitektur Aegis Protocol terdiri dari dua lapisan utama yang saling berkomunikasi:

1.  *Intelligence Layer (Fetch.ai):* Berfungsi sebagai "sistem saraf" protokol. Jaringan agen AI otonom yang terdesentralisasi ini secara proaktif memantau data global untuk mendeteksi dan memvalidasi bencana.
2.  *Execution Layer (Internet Computer):* Berfungsi sebagai "tulang punggung" eksekusi dan kepercayaan. Berjalan di atas Internet Computer, lapisan ini mengelola pembuatan DAO, perbendaharaan dana, voting, dan sistem reputasi on-chain.

* *Diagram Arsitektur Detail:* [Lihat di sini](./docs/diagrams/endgame_architecture.mermaid)

---

## ✨ Fitur Utama & Inovasi

### Fitur ICP yang Digunakan
- *Canister Smart Contracts:* Seluruh logika backend, termasuk DAO dan brankas asuransi, di-deploy sebagai canister yang berjalan sepenuhnya on-chain.
- *Model "Reverse Gas":* Pengguna (donatur, NGO) dapat berinteraksi dengan aplikasi tanpa perlu membayar biaya gas, menghilangkan hambatan adopsi.
- *Web Serving On-Chain:* Kemampuan untuk menghosting antarmuka frontend langsung dari canister, menciptakan aplikasi yang sepenuhnya terdesentralisasi.
- *Identitas & Aset On-Chain:* Mengelola identitas (DID) dan aset reputasi (SBTs) secara permanen di blockchain.

### Fitur Fetch.ai yang Digunakan
- *uAgents (Micro-agents):* Membangun agen-agen AI otonom (oracle, validator, action) yang dapat berkomunikasi dan bertindak secara mandiri.
- *Agentverse / ASI:One:* Menyediakan platform untuk komunikasi dan interaksi antar agen, termasuk implementasi *Protokol Obrolan* yang dibutuhkan untuk demo.
- *Decentralized AI Network:* Memanfaatkan jaringan Fetch.ai sebagai fondasi untuk orakel terdesentralisasi yang cerdas dan tahan sensor.

---

## 🤖 Detail Agen Fetch.ai (Untuk Juri)

Berikut adalah detail dari agen-agen yang berjalan di Fetch.ai, sesuai dengan persyaratan hackathon.

* **Oracle Agent (oracle_agent_usgs)**
    * *Alamat:* Alamat akan dihasilkan saat agen dijalankan.
    * *Tugas:* Memantau sumber data eksternal (USGS) untuk mendeteksi anomali bencana.

* **Validator Agent (validator_agent_alpha)**
    * *Alamat:* agent1q2gwxq52k8wecuvj3sksv9sszefaqpmq42u0mf6z0q5z4e0a9z0wz9z0q
    * *Tugas:* Menerima data mentah, melakukan validasi, dan mencapai konsensus. Agen ini menerapkan *Protokol Obrolan Fetch.ai* dan dapat berinteraksi melalui Agentverse/ASI:One.

* **Action Agent (action_agent_bridge)**
    * *Alamat:* Alamat akan dihasilkan saat agen dijalankan.
    * *Tugas:* Menerima hasil konsensus dan memanggil smart contract di Internet Computer.

---

# 🚀 Cara Menjalankan Proyek (Pengembangan Lokal) – *WSL Version*

Proyek ini menggunakan **Docker Compose** untuk mempermudah proses setup dan eksekusi.
**⚠️ Semua perintah `bash` dijalankan di terminal berbeda (tab/instance WSL berbeda).**

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
