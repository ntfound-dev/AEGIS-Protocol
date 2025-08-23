Desain Arsitektur Tingkat Tinggi Aegis Protocol
Arsitektur Aegis Protocol dirancang secara sengaja dengan pendekatan hibrida berlapis (layered hybrid approach) untuk memaksimalkan kekuatan komputasi off-chain yang fleksibel dan keamanan serta transparansi dari komputasi on-chain.

Lapisan 1: Frontend (Presentation Layer)
Lapisan ini adalah titik interaksi utama bagi pengguna manusia. Ia berjalan sepenuhnya di browser klien.

Tujuan: Menyediakan antarmuka yang reaktif dan intuitif untuk memonitor, berinteraksi, dan mengelola respons darurat.

Teknologi Utama:

HTML5 & CSS3: Untuk struktur dan gaya antarmuka.

JavaScript (ES6 Modules): Untuk semua logika di sisi klien.

Vite: Sebagai build tool dan development server modern.

@dfinity/auth-client: Pustaka resmi untuk integrasi dengan sistem otentikasi Internet Identity.

@dfinity/agent: Pustaka inti untuk membuat Actor dan berkomunikasi dengan canister di Internet Computer.

Tanggung Jawab Utama:

Manajemen Sesi Pengguna: Menangani alur login dan logout melalui Internet Identity.

Interaksi Langsung dengan Canister: Membuat Actor untuk memanggil fungsi query (membaca data) dan update (mengubah data) pada canister EventDAO dan DID/SBT Ledger atas nama pengguna yang terotentikasi.

Komunikasi dengan Lapisan Off-Chain: Mengirim perintah dalam bahasa alami (chat) atau data terstruktur melalui fetch API ke endpoint yang disediakan oleh Validator Agent.

Rendering State: Menampilkan data dari canister (seperti daftar proposal) dan pesan dari AI Agent secara real-time di UI.

Lapisan 2: Layanan Off-Chain (AI Agents & Business Logic Layer)
Lapisan ini adalah "otak" dan "sistem saraf" dari protokol. Ia berjalan di lingkungan server yang terkontrol (di-deploy menggunakan Docker) dan tidak terekspos langsung ke dunia luar selain melalui endpoint API yang spesifik.

Tujuan: Mengotomatiskan akuisisi data, melakukan validasi kompleks, dan bertindak sebagai jembatan yang aman antara dunia nyata dan blockchain.

Teknologi Utama:

Python 3: Bahasa pemrograman utama untuk semua agent.

uagents Framework: Kerangka kerja untuk membangun agen-agen otonom yang dapat berkomunikasi satu sama lain.

ic-py: Pustaka untuk memungkinkan skrip Python berinteraksi (membuat transaksi, memanggil canister) dengan jaringan Internet Computer.

Docker & Docker Compose: Untuk mengemas, mengisolasi, dan mengorkestrasi ketiga service agent.

Tanggung Jawab Utama:

Akuisisi Data (Oracle Agent): Mengambil data dari berbagai API eksternal secara berkala.

Validasi dan Pengayaan (Validator Agent): Menerapkan logika bisnis untuk memfilter dan memvalidasi data. Ini adalah tempat di mana model AI/ML dapat diintegrasikan di masa depan.

Eksposur API: Menyediakan endpoint HTTP (misalnya /chat) yang aman untuk dikonsumsi oleh frontend.

Eksekusi Otomatis On-Chain (Action Agent): Bertindak sebagai proksi terpercaya yang memiliki identitas kriptografis (identity.pem) untuk memanggil fungsi yang memerlukan otorisasi khusus di lapisan blockchain.

Lapisan 3: Blockchain (On-Chain Logic & Persistence Layer)
Lapisan ini adalah fondasi kepercayaan dari sistem. Ia berjalan di jaringan terdesentralisasi Internet Computer.

Tujuan: Menyediakan platform yang transparan, tidak dapat diubah, dan selalu aktif untuk tata kelola, manajemen dana, dan pencatatan identitas.

Teknologi Utama:

Motoko: Bahasa pemrograman yang dirancang khusus untuk Internet Computer, menawarkan keamanan tipe yang kuat.

Internet Computer (IC): Platform blockchain yang menjalankan smart contract (canisters) pada kecepatan web.

dfx SDK: Perangkat baris perintah untuk mengelola siklus hidup pengembangan canister (membuat, men-deploy, meng-upgrade).

Tanggung Jawab Utama:

Pabrik Smart Contract (Event Factory): Secara dinamis men-deploy canister baru sebagai respons terhadap peristiwa yang divalidasi.

Tata Kelola Terdesentralisasi (Event DAO): Mengelola proposal, voting, dan perbendaharaan dana secara transparan untuk setiap bencana.

Manajemen Likuiditas (Insurance Vault): Menyimpan dan mencairkan dana awal secara terprogram.

Registri Identitas (DID/SBT Ledger): Bertindak sebagai sumber kebenaran tunggal untuk profil pengguna dan kredensial reputasi mereka.

Penyimpanan State Permanen: Semua data penting (transaksi, suara, profil) disimpan secara permanen di state canister.