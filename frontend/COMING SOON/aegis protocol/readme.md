🛡️ Aegis Protocol: AI Disaster Response System
Aegis Protocol adalah sistem respons bencana berbasis AI yang dirancang untuk mendeteksi, memvalidasi, dan mengelola peristiwa bencana secara real-time. Dengan memanfaatkan jaringan oracle terdesentralisasi (DON), analitik mutakhir, dan kontrak pintar, sistem ini mengotomatiskan alokasi sumber daya dan pembayaran asuransi, memastikan respons yang cepat dan efisien.

📋 Daftar Isi
Fitur Utama

Persyaratan

Cara Menjalankan

Struktur Proyek

Kontribusi

✨ Fitur Utama
Deteksi Bencana Berbasis AI: Menggunakan model AI untuk menganalisis data dari berbagai sumber (BMKG, NASA FIRMS, PetaBencana, media sosial) untuk mendeteksi bencana.

Jaringan Oracle Terdesentralisasi (DON): Jaringan validator yang dikelola AI untuk mencapai konsensus tentang validitas bencana.

Dashboard Real-time: Dashboard HTML/JavaScript yang menyediakan pemantauan status sistem secara langsung, log, dan kontrol simulasi.

Integrasi Backend FastAPI: API Python yang ringan dan cepat untuk menghubungkan dashboard dengan logika inti sistem.

Simulasi Bencana: Kemampuan untuk menjalankan simulasi bencana prasetel (misalnya, Banjir Jakarta, Gempa Cianjur) untuk menguji dan memantau kinerja sistem.

Asuransi Parametrik: Kontrak pintar (dimodelkan) yang secara otomatis melakukan pembayaran ketika kriteria bencana terverifikasi.

🛠️ Persyaratan
Pastikan Anda telah menginstal Docker Desktop di komputer Anda. Ini adalah satu-satunya prasyarat yang Anda butuhkan, karena ia akan mengelola semua dependensi dan lingkungan yang diperlukan. Proyek ini sudah dikonfigurasi dengan file enhanced_requirements.txt yang sudah diperbaiki, sehingga tidak ada pembaruan dependensi manual yang diperlukan.

🚀 Cara Menjalankan
Ikuti langkah-langkah di bawah ini untuk memulai proyek Aegis Protocol di mesin lokal Anda.

1. Salin File ke Satu Direktori
Pastikan semua file proyek (termasuk Dockerfile, docker-compose.yml, api_server.py, dan aegis_protocol.html) berada dalam satu folder.

2. Jalankan dengan Docker Compose
Buka terminal atau command prompt, navigasikan ke folder proyek Anda, lalu jalankan perintah berikut:

docker-compose up -d --build

Perintah ini akan membangun gambar Docker dari Dockerfile dan menjalankan kontainer di latar belakang. Proses ini mungkin memerlukan waktu beberapa menit untuk pertama kali.

3. Mengakses Dashboard
Setelah kontainer berjalan, buka browser web Anda dan navigasikan ke URL berikut untuk melihat dashboard:

http://localhost:8080

Anda juga dapat melihat dokumentasi API di:

http://localhost:8080/docs

Untuk menghentikan sistem, cukup jalankan perintah berikut di terminal:

docker-compose down

📁 Struktur Proyek
Dockerfile: Berisi instruksi untuk membuat gambar Docker, termasuk menginstal dependensi.

docker-compose.yml: Mendefinisikan layanan aegis-api untuk Docker, mengelola port, dan mount volume.

enhanced_requirements.txt: Daftar dependensi Python yang akan diinstal di dalam kontainer.

api_server.py: Mengatur server backend FastAPI, mendefinisikan semua endpoint API, dan mengelola WebSocket untuk komunikasi real-time.

aegis_protocol.html: Dashboard front-end yang terhubung ke server API untuk visualisasi dan kontrol sistem.

enhanced_main.py: Logika utama untuk menginisialisasi dan menjalankan semua komponen sistem Aegis Protocol.

asi_integration.py: Kelas untuk berinteraksi dengan ASI:one untuk analisis dan optimasi tingkat lanjut.

base_agent.py: Kelas dasar untuk semua agen AI dalam sistem, mendefinisikan struktur dan fungsionalitas umum.

disaster_parsers.py: Mengandung agen-agen yang bertanggung jawab untuk memproses data mentah dari berbagai sumber menjadi peristiwa bencana yang terstruktur.

communications.py: Mengelola notifikasi dan komunikasi publik.

🤝 Kontribusi
Selamat datang untuk semua kontribusi! Jika Anda menemukan bug atau memiliki saran untuk perbaikan, silakan buka issue atau buat pull request di repositori proyek ini.