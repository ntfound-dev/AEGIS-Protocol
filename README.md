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

## 🚀 Cara Menjalankan Proyek (Pengembangan Lokal)

Proyek ini menggunakan *Docker Compose* untuk menyederhanakan proses setup.

*1. Prasyarat:*
   - [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
   - Git

*2. Jalankan Proyek:*
```bash
# Clone Repositori
git clone [https://github.com/ntfound-dev/AEGIS-Protocol.git](https://github.com/ntfound-dev/AEGIS-Protocol.git)
cd AEGIS-Protocol

# Buat kunci identitas  Action Agent
./scripts/generate-keys.sh

# Build & run semua layanan backend
docker-compose up --build
 
## 📂 Struktur Proyek

Proyek ini dibagi menjadi tiga layanan utama:

services/
├── 1-frontend-flutter/       <-- Tim Frontend (Flutter)
├── 2-backend-blockchain-icp/ <-- Tim Blockchain (Motoko/ICP)
└── 3-backend-ai-agents/      <-- Tim AI & Integrasi (Python/Fetch.ai)


## 🎯 Rencana Masa Depan (Pasca-Hackathon)

* *Q4 2025:* Peluncuran Testnet, mengundang 5 NGO mitra pertama untuk uji coba.
* *Q1 2026:* Audit Keamanan & Peluncuran Mainnet Beta dengan frontend Flutter.
* *Q2 2026:* Pengembangan Tokenomics $AEGIS untuk tata kelola dan staking.
* *Q3 2026:* Ekspansi Global melalui kemitraan dengan badan kemanusiaan internasional.

## 🧗 Tantangan Selama Hackathon

1.  *Interoperabilitas Ekosistem:* Merancang protokol komunikasi yang andal antara agen Python di Fetch.ai dengan canister Motoko di ICP.
2.  *Simulasi Real-time:* Mengintegrasikan sumber data untuk simulasi deteksi bencana oleh Oracle Agent.
3.  *Alur Kerja Tim:* Mengkoordinasikan tim dengan keahlian berbeda (Blockchain, AI, Frontend) dalam waktu singkat.
