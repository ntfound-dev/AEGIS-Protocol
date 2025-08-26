# 🛡️ Aegis Protocol: Sistem Respons Bencana Berbasis AI

Aegis Protocol adalah sistem respons bencana berbasis AI yang canggih dan terdesentralisasi, dirancang untuk mendeteksi, memvalidasi, dan merespons bencana secara real-time. [cite\_start]Proyek ini mengintegrasikan kecerdasan buatan, teknologi blockchain (khususnya Internet Computer Protocol/ICP), dan jaringan oracle terdesentralisasi (Decentralized Oracle Network/DON) untuk memastikan respons yang cepat dan transparan[cite: 5, 6].

-----

## ✨ Fitur Utama

  - [cite\_start]**Deteksi Cepat**: Menggunakan **Decentralized Oracle Network (DON)** untuk mengumpulkan data dari berbagai sumber tepercaya seperti BMKG, PetaBencana, NASA FIRMS, dan sinyal media sosial[cite: 1, 2].
  - **Validasi AI**: Mengintegrasikan **ASI:one**, sebuah lapisan kecerdasan buatan canggih, untuk memvalidasi data bencana dan menghasilkan wawasan prediktif.
  - **Respons Otomatis & Transparan**:
      - Memicu pencairan dana secara otomatis dari **Parametric Insurance Vault** setelah konsensus tercapai.
      - [cite\_start]Menciptakan **Event DAO (Decentralized Autonomous Organization)** untuk setiap bencana yang divalidasi, memungkinkan tata kelola (governance) yang transparan dan berbasis voting untuk alokasi dana dan sumber daya[cite: 1].
  - [cite\_start]**Tata Kelola On-Chain**: Sistem voting dan proposal transparan di mana partisipan seperti relawan, donor, dan LSM dapat memberikan suara pada keputusan penting[cite: 1].
  - [cite\_start]**Integrasi Blockchain**: Memanfaatkan **Internet Computer Protocol (ICP)** untuk mengelola transaksi dana darurat secara on-chain dan memastikan keamanan serta transparansi data[cite: 5, 6].
  - **Manajemen Kinerja**: Memantau metrik kinerja sistem secara real-time untuk memastikan kepatuhan terhadap Service Level Agreement (SLA) yang kritis, seperti waktu deteksi dan waktu notifikasi. [cite\_start]Metrik dikumpulkan dengan `prometheus-client` dan `psutil`[cite: 1, 3, 4, 5].

-----

## ⚙️ Cara Menjalankan Program

[cite\_start]Proyek ini dibangun menggunakan Python dengan framework FastAPI untuk API[cite: 1]. Ikuti langkah-langkah di bawah ini untuk menjalankannya dengan mudah.

### Prasyarat

Pastikan Anda telah menginstal:

  - Python 3.8+
  - `pip` (manajer paket Python)

### Langkah 1: Siapkan Virtual Environment 🐍

Untuk mengelola dependensi proyek secara terisolasi, disarankan untuk menggunakan **virtual environment** (`venv`). Buka terminal Anda dan ikuti langkah berikut:

1.  **Buat `venv`**:

    ```bash
    python -m venv venv
    ```

2.  **Aktifkan `venv`**:

      - **Di macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
      - **Di Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate
        ```
      - **Di Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```

Setelah diaktifkan, Anda akan melihat `(venv)` di awal prompt terminal Anda.

### Langkah 2: Instalasi Dependensi

[cite\_start]Dengan `venv` sudah aktif, instal semua pustaka yang diperlukan dari `enhanced_requirements.txt`[cite: 1].

```bash
pip install -r enhanced_requirements.txt
```

### Langkah 3: Menjalankan Server API 🚀

Server API berfungsi sebagai jembatan antara antarmuka pengguna (UI) dan logika backend. [cite\_start]Jalankan server menggunakan `uvicorn`[cite: 1]:

```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8080
```

  - `api_server:app`: Menginstruksikan `uvicorn` untuk menjalankan aplikasi `app` yang ada di dalam file `api_server.py`.
  - `--reload`: Memungkinkan server untuk memuat ulang secara otomatis ketika Anda membuat perubahan pada kode.
  - `--host 0.0.0.0`: Mengizinkan akses dari alamat IP eksternal (berguna untuk pengujian di jaringan lokal).
  - `--port 8080`: Menjalankan server pada port 8080.

### Langkah 4: Menggunakan Dashboard dan API 📊

Setelah server berjalan, Anda dapat berinteraksi dengan sistem Aegis melalui dua cara:

1.  **Dashboard Web**: Buka file `aegis_protocol.html` langsung di browser Anda. Dashboard ini akan secara otomatis terhubung ke server backend yang Anda jalankan.
2.  [cite\_start]**Dokumentasi API**: Akses dokumentasi interaktif Swagger UI untuk menguji endpoint API secara langsung[cite: 1]:
    [http://localhost:8080/docs](https://www.google.com/search?q=http://localhost:8080/docs)

-----

## 📂 Struktur Proyek

```
.
[cite_start]├── api_server.py             # Server API utama (FastAPI) [cite: 1]
[cite_start]├── aegis_protocol.html       # Dashboard web front-end [cite: 1]
[cite_start]├── enhanced_main.py          # File inti, mengintegrasikan semua komponen [cite: 1]
[cite_start]├── orchestrator.py           # Otak sistem, mengelola alur kerja [cite: 1]
[cite_start]├── asi_integration.py        # Lapisan integrasi dengan ASI:one [cite: 1]
├── oracle_network.py         # Implementasi Decentralized Oracle Network (DON)
├── parametric_vault.py       # Logika untuk Parametric Insurance Vault
[cite_start]├── governance_system.py      # Mengelola proposal dan voting DAO [cite: 1]
[cite_start]├── icp_integration.py        # Lapisan untuk interaksi ICP (mock) [cite: 1]
[cite_start]├── performance_monitor.py    # Melacak metrik kinerja sistem [cite: 1]
├── disaster_parsers.py       # Agen untuk mem-parsing data mentah
[cite_start]├── base_agent.py             # Kelas dasar dan struktur data umum [cite: 1]
[cite_start]├── communications.py         # Agen untuk notifikasi dan komunikasi [cite: 1]
[cite_start]└── enhanced_requirements.txt # Daftar dependensi Python [cite: 1]
```