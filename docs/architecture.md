# Arsitektur Teknis Aegis Protocol

Arsitektur Aegis Protocol dirancang dengan pendekatan modular berbasis layanan, yang terdiri dari dua lapisan utama yang saling berinteraksi: **Intelligence Layer** yang berjalan di Fetch.ai dan **Execution Layer** yang berjalan di Internet Computer (ICP).

## 1. Intelligence Layer (Fetch.ai)

Lapisan ini berfungsi sebagai "sistem saraf" protokol yang proaktif dan terdesentralisasi. Tugas utamanya adalah merasakan, memvalidasi, dan memicu respons terhadap bencana.

- **`oracle_agent.py` (Oracle Agent):** Agen ini adalah "mata" dan "telinga" sistem. Mereka secara terus-menerus memantau berbagai sumber data eksternal (API publik, sensor IoT, citra satelit) untuk mendeteksi anomali yang mengindikasikan potensi bencana.
- **`validator_agent.py` (Validator Agent):** Berfungsi sebagai "otak" pengambil keputusan. Ia menerima laporan dari berbagai Oracle Agent, menerapkan logika validasi (dalam skenario penuh, menggunakan model AI), dan mencapai konsensus untuk memastikan sinyal bencana tersebut akurat dan bukan alarm palsu. Agen ini mengimplementasikan **Protokol Obrolan Fetch.ai** untuk interaksi.
- **`action_agent.py` (Action Agent):** Bertindak sebagai "kurir" terpercaya yang menjadi jembatan antara dunia AI dan dunia Blockchain. Setelah konsensus tercapai, agen ini memformat data yang sudah divalidasi dan secara aman memanggil `smart contract` di Internet Computer menggunakan kunci identitas (`identity.pem`).

## 2. Execution Layer (Internet Computer)

Lapisan ini adalah "tulang punggung" yang tidak bisa diubah dan sepenuhnya transparan. Semua eksekusi, manajemen dana, dan tata kelola terjadi di sini.

- **`event_factory.mo` (Event Factory Canister):** Ini adalah satu-satunya pintu masuk ke lapisan eksekusi. Saat dipanggil oleh Action Agent, canister ini secara otonom men-deploy sebuah instance `EventDAO` baru.
- **`event_dao.mo` (Event DAO Canister):** Setiap bencana memiliki "posko bantuan digital"-nya sendiri. Canister ini mengelola perbendaharaan dana, menerima donasi, serta memfasilitasi pengajuan proposal dan proses voting oleh komunitas.
- **`insurance_vault.mo` (Insurance Vault Canister):** Sebuah brankas digital yang didanai oleh penyedia likuiditas. Ia secara otomatis menyuntikkan dana darurat awal ke setiap `EventDAO` baru berdasarkan pemicu parametrik (tingkat keparahan bencana).
- **`did_sbt_ledger.mo` (DID & SBT Ledger Canister):** Berfungsi sebagai "buku catatan reputasi". Ia mengelola pendaftaran identitas digital (DID) untuk para aktor (NGO, relawan) dan mencetak lencana kontribusi permanen (Soulbound Tokens) setelah sebuah misi selesai.

## Alur Interaksi

1.  **Deteksi:** `Oracle Agent` mendeteksi sinyal dan mengirimkannya ke `Validator Agent`.
2.  **Validasi:** `Validator Agent` memvalidasi sinyal dan mengirimkan perintah ke `Action Agent`.
3.  **Pemicu:** `Action Agent` memanggil fungsi `declare_event` di `EventFactory`.
4.  **Eksekusi:** `EventFactory` men-deploy `EventDAO` baru dan memicu `InsuranceVault` untuk mengirimkan dana.
5.  **Partisipasi:** Komunitas global berinteraksi dengan `EventDAO` melalui antarmuka frontend.