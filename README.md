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

Oke, ini versi README kamu yang sudah aku perbarui, termasuk langkah penggunaan `dos2unix` untuk WSL dan penyesuaian path terbaru pada `generate-keys.sh`:

---

## 🚀 Cara Menjalankan Proyek (Pengembangan Lokal)

Proyek ini menggunakan *Docker Compose* untuk menyederhanakan proses setup.

### 1. Prasyarat

* [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
* Git
* **(Jika menggunakan WSL)** pastikan tersedia `dos2unix` untuk konversi file dengan line ending Windows.

### 2. Jalankan Proyek

```bash
# Clone Repositori
git clone https://github.com/ntfound-dev/AEGIS-Protocol.git
cd AEGIS-Protocol
```

> **Catatan untuk pengguna WSL:**
> Jika Anda meng-clone repo ini di Windows dan menjalankannya di WSL, beberapa file `.sh` mungkin menggunakan line ending CRLF yang tidak dikenali Bash.
> Jalankan perintah berikut sebelum menjalankan skrip:

```bash
sudo apt update && sudo apt install dos2unix -y
dos2unix scripts/*.sh
```

```bash
# Buat kunci identitas Action Agent
bash scripts/generate-keys.sh
```

```bash
# Build & jalankan semua layanan backend
docker-compose build dfx-replica
docker-compose up --build
```

## 📂 Struktur Proyek
```
aegis-protocol/
├── .gitignore           # Mengabaikan file yang tidak perlu (build artifacts, .env, .pem, dll.)
├── README.md            # Dokumentasi utama: cara instalasi, setup, dan menjalankan setiap layanan.
├── docker-compose.yml   #Untuk menjalankan semua layanan backend dengan satu perintah.
│
├── docs/
│   ├── architecture.md # Penjelasan teknis arsitektur secara mendalam.
│   ├── concepts.md          # Penjelasan visi dan konsep inti dari Aegis Protocol.
│    └── diagrams/      
│       └── endgame_architecture.mermaid    # File diagram Mermaid 
│
├── services/  <-- FOLDER UTAMA SEMUA KODE APLIKASI
│   │
│   ├── 1-frontend-dasbor-demo/  <------------ [ UNTUK TIM FRONTEND ]
│   │   ├── index.html            # Halaman utama untuk Dasbor Demo.
│   │   ├── style.css             # styling halaman.
│   │   └── script.js             # Logika untuk mengirim "pesan obrolan" ke agen AI.
│   │                             # kalau ada tambahan lain silahkan 
│   ├── 2-backend-blockchain-icp/  <---------- [ UNTUK TIM BLOCKCHAIN ]
│   │   ├── dfx.json              # File konfigurasi utama untuk DFINITY SDK (dfx).
│   │   ├── src/                  # Folder semua source code canister.
│   │   │   ├── event_factory/    
│   │   │   │   └── main.mo       # Canister (pabrik) untuk membuat EventDAO. 
│   │   │   ├── event_dao/        
│   │   │   │   └── main.mo       # Template canister untuk setiap bencana.
│   │   │   ├── did_sbt_ledger/   
│   │   │   │   └── main.mo       # Canister untuk identitas dan reputasi.
│   │   │   └── insurance_vault/
│   │   │       └── main.mo       # Canister brankas asuransi parametrik.
│   │   └── .dfx/                 # Folder yang dibuat otomatis oleh dfx, berisi hasil build.
│   │       └── local/            
│   │           ├── canister_ids.json  # File PENTING: berisi ID canister setelah deploy
│   │           └── canisters/         #Berisi file .did (API) dan .wasm (kode terkompilasi).
│   │
│   └── 3-backend-ai-agents/      <------------ [UNTUK TIM AI]
│       ├── requirements.txt       # Dependensi Python (uagents, requests, ic-py).     
│       ├── Dockerfile             # Resep untuk membuat container Docker untuk agen. 
│       ├── .env.example           # Contoh file environment.
│       ├── identity.pem           # Kunci identitas untuk Action Agent (diabaikan oleh gitignore).
│       └── agents/ 
│           ├── oracle_agent.py     # Agen yang memantau data dunia nyata.
│           ├── validator_agent.py  # Agen yang memvalidasi data bencana.
│           └── action_agent.py     # Agen yang menjadi jembatan ke ICP.
│
└── scripts/
    ├── deploy-blockchain.sh   # Skrip untuk deploy semua canister di 2-backend-blockchain-icp.
    ├── run-agents.sh          # Skrip untuk jalankan semua agen Python di 3-backend-ai-agents.    
    └──  generate-keys.sh      # Skrip untuk membuat identity.pem baru.
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
