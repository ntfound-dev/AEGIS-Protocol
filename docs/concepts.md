Konsep dan Terminologi Inti Aegis Protocol
Dokumen ini berfungsi sebagai kamus untuk memahami istilah-istilah kunci dan komponen fundamental yang membentuk ekosistem Aegis Protocol.

Konsep Off-Chain (Dunia AI Agents)
Komponen-komponen ini berjalan di luar blockchain (di server/Docker) dan bertugas mengamati serta berinteraksi dengan dunia nyata.

Oracle Agent
Analogi: Seorang pengintai di menara pengawas.

Tugas: Tugasnya sangat spesifik: terus-menerus memantau sumber data eksternal yang telah ditentukan (API gempa USGS, BMKG, dll.). Ketika ia melihat "sesuatu" (data baru), ia tidak menganalisisnya, ia hanya meneriakkan apa yang ia lihat ("Laporan baru dari USGS!") ke Validator Agent. Ia adalah mata dan telinga sistem.

Validator Agent
Analogi: Seorang analis intelijen di ruang komando.

Tugas: Ia menerima laporan mentah dari para pengintai (Oracle Agent) dan juga dari operator manusia (input chat di frontend). Tugasnya adalah:

Memfilter Kebisingan: Memastikan laporan tersebut memiliki format yang benar.

Menganalisis Signifikansi: Menerapkan logika (saat ini berdasarkan magnitudo) untuk memutuskan apakah laporan ini cukup penting untuk ditindaklanjuti.

Menyusun Laporan Resmi: Mengubah data mentah yang berantakan menjadi sebuah laporan standar yang bersih dan terstruktur (ValidatedEvent).

Memberi Perintah: Jika sebuah laporan dianggap valid dan signifikan, ia akan memberi perintah kepada Action Agent untuk bertindak.

Action Agent (The Bridge)
Analogi: Seorang utusan resmi dengan segel kerajaan.

Tugas: Ia adalah satu-satunya entitas off-chain yang dipercaya untuk berbicara langsung dengan dunia on-chain (blockchain). Ia tidak memiliki kecerdasan untuk menganalisis, ia hanya mengeksekusi perintah. Ketika Validator Agent memberinya laporan resmi (ValidatedEvent), ia akan pergi ke Event Factory di blockchain, menunjukkan "segel"-nya (identity.pem), dan berkata, "Atas perintah dari ruang komando, nyatakan peristiwa darurat ini!"

Konsep On-Chain (Dunia Blockchain/Canisters)
Komponen-komponen ini hidup di Internet Computer. Mereka adalah fondasi yang transparan dan tidak dapat diubah dari sistem.

Internet Identity
Analogi: Paspor digital universal.

Tugas: Ini adalah sistem otentikasi terdesentralisasi dari Internet Computer. Pengguna tidak membuat username/password di aplikasi kita. Sebaliknya, mereka login menggunakan Internet Identity mereka, yang memberikan mereka sebuah Principal ID (seperti nomor paspor) yang unik dan aman di seluruh ekosistem IC.

Event Factory
Analogi: Sebuah pabrik perakitan otomatis.

Tugas: Canister ini hanya memiliki satu pekerjaan: menerima perintah yang sah dari Action Agent. Ketika perintah diterima, "lini perakitan" di pabrik ini akan secara otomatis membuat dan men-deploy sebuah Event DAO baru yang sudah dikonfigurasi sepenuhnya.

Insurance Vault
Analogi: Sebuah brankas bank yang diasuransikan.

Tugas: Ini adalah canister tempat para penyandang dana (funder) menyimpan dana likuiditas awal. Ketika Event Factory membuat DAO baru, ia memiliki otorisasi untuk menarik sejumlah dana awal dari brankas ini (berdasarkan tingkat keparahan bencana) untuk "menyuntikkan modal" ke perbendaharaan DAO yang baru dibuat.

Event DAO
Analogi: Sebuah ruang rapat darurat dan rekening bank transparan untuk satu bencana spesifik.

Tugas: Ini adalah pusat komando on-chain untuk satu peristiwa. Di dalamnya, para pemangku kepentingan yang terverifikasi dapat:

Mengajukan Proposal: "Kami butuh dana sebesar X untuk membeli Y."

Memberikan Suara (Vote): Menyetujui atau menolak proposal.

Memberikan Donasi: Menambah dana ke perbendaharaan (treasury_balance).
Semua aktivitas ini tercatat secara publik dan permanen.

DID/SBT Ledger
Analogi: Kantor catatan sipil dan album prestasi di blockchain.

Tugas:

DIDProfile (Akta Kelahiran): Mencatat pendaftaran identitas seorang pengguna atau organisasi, mengaitkan Principal ID mereka dengan nama.

SBT (Lencana/Sertifikat Prestasi): Ketika seorang pengguna melakukan aksi penting (seperti berdonasi di sebuah Event DAO), canister ini akan mencetak "lencana" digital yang tidak bisa dipindahtangankan untuk mereka. Ini membangun rekam jejak reputasi yang terverifikasi.