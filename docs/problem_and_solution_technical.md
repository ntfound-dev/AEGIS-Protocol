Analisis Teknis Masalah & Solusi Aegis Protocol
Dokumen ini menguraikan tantangan teknis fundamental yang dihadapi dalam membangun sistem tanggap darurat terdesentralisasi dan solusi arsitektural spesifik yang dipilih untuk mengatasinya dalam Aegis Protocol.

1. Masalah Teknis Fundamental
Masalah #1: The Oracle Problem
Tantangan: Smart contract di Internet Computer, seperti di blockchain lainnya, beroperasi dalam lingkungan yang terisolasi dan deterministik. Mereka tidak dapat secara native melakukan panggilan jaringan ke API eksternal (misalnya, API USGS untuk data gempa) tanpa mengorbankan keamanan dan konsensus. Bagaimana cara memasukkan data dunia nyata secara andal ke dalam blockchain untuk memicu aksi on-chain?

Masalah #2: Skalabilitas dan Isolasi Event
Tantangan: Setiap bencana adalah peristiwa unik dengan pemangku kepentingan, kebutuhan dana, dan alur proposal yang berbeda. Menggunakan satu canister monolitik untuk mengelola semua bencana akan menciptakan beberapa masalah:

Single Point of Failure: Bug atau eksploitasi pada satu canister dapat membahayakan dana dan operasi untuk semua bencana.

Kompleksitas State: State canister akan menjadi sangat besar dan rumit, mempersulit query dan pemeliharaan.

Kurangnya Fleksibilitas: Sulit untuk menyesuaikan aturan atau parameter untuk bencana tertentu tanpa mempengaruhi yang lain.

Masalah #3: Identitas Digital dan Reputasi
Tantangan: Dalam sistem terbuka, bagaimana kita bisa mempercayai para aktor (baik individu maupun organisasi)? Diperlukan sebuah mekanisme untuk:

Mengikat identitas digital (Principal ID) ke entitas dunia nyata.

Mencatat kontribusi dan partisipasi secara permanen dan tidak dapat dipalsukan untuk membangun reputasi dari waktu ke waktu.

Masalah #4: Jembatan Otomatis Off-Chain ke On-Chain
Tantangan: Logika validasi AI yang kompleks dan pengambilan data dari berbagai sumber paling efisien dilakukan di lingkungan off-chain (seperti Python). Namun, hasil dari proses off-chain ini harus dapat memicu transaksi on-chain secara otomatis dan aman, tanpa intervensi manual. Diperlukan sebuah "robot" atau bridge yang memiliki identitas kriptografisnya sendiri untuk bertindak atas nama sistem.

2. Solusi Arsitektural Aegis Protocol
Solusi untuk #1: Sistem Multi-Agent Off-Chain
Kami mengatasi The Oracle Problem dengan menggunakan arsitektur multi-agent berbasis uagents (Python) yang memisahkan tugas:

Oracle Agent: Bertindak sebagai lapisan akuisisi data murni. Tugasnya hanya mengambil data mentah dari API eksternal dan meneruskannya. Ini mengisolasi ketergantungan pada API luar dan menyederhanakan logikanya.

Validator Agent: Bertindak sebagai lapisan validasi dan logika bisnis. Ia menerima data dari berbagai sumber (termasuk Oracle dan input manual pengguna), membersihkannya, dan menerapkan logika untuk memutuskan apakah data tersebut valid dan signifikan. Ini mencegah "data sampah" membanjiri blockchain.

Solusi untuk #2: Pola Desain Factory Canister
Kami menerapkan pola desain factory untuk mengatasi masalah skalabilitas dan isolasi:

Event Factory Canister (event_factory.mo): Canister ini bertindak sebagai "pabrik" on-chain. Satu-satunya tujuannya adalah untuk membuat (instantiate) canister baru dari tipe EventDAO.

Event DAO Canister (event_dao.mo): Setiap kali Event Factory menerima sinyal bencana yang valid, ia akan men-deploy instance EventDAO yang baru dan terisolasi. Setiap DAO memiliki state, perbendaharaan (treasury_balance), dan set proposalnya sendiri. Ini menciptakan isolasi penuh antar peristiwa bencana.

Solusi untuk #3: DID dan Soul-Bound Tokens (SBT)
Kami membangun sistem identitas dan reputasi on-chain menggunakan:

DID/SBT Ledger Canister (did_sbt_ledger.mo): Canister ini berfungsi sebagai registri.

DIDProfile: Pengguna dapat mendaftarkan profil yang mengaitkan Principal ID mereka dengan nama atau organisasi.

SBT (Soul-Bound Token): Ketika seorang pengguna berpartisipasi dalam sebuah DAO (misalnya dengan berdonasi), EventDAO akan memanggil DID/SBT Ledger untuk mencetak SBT untuk pengguna tersebut. SBT ini adalah kredensial digital non-transferable yang berfungsi sebagai bukti partisipasi on-chain.

Solusi untuk #4: Action Agent sebagai Jembatan Kriptografis
Kami menciptakan jembatan yang aman dan otomatis menggunakan:

Action Agent (action_agent.py): Agent Python ini memiliki peran khusus. Saat diinisialisasi, ia memuat kunci privat dari file identity.pem.

Identitas Kriptografis: Menggunakan pustaka ic-py, kunci ini memberinya Principal ID sendiri di jaringan Internet Computer, sama seperti pengguna manusia.

Otorisasi: Action Agent ini diberi wewenang (melalui aturan di canister) untuk memanggil fungsi kritis declare_event di Event Factory. Dengan demikian, ia dapat secara otonom menerjemahkan hasil validasi AI off-chain menjadi transaksi on-chain yang aman dan terverifikasi.