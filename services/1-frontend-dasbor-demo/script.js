// Menunggu seluruh halaman HTML dimuat sebelum menjalankan skrip
document.addEventListener('DOMContentLoaded', () => {
    // Menghubungkan variabel JavaScript ke elemen di HTML
    const eventDataTextArea = document.getElementById('eventData');
    const sendSignalButton = document.getElementById('sendSignalButton');
    const statusLog = document.getElementById('statusLog');

    // Menyiapkan contoh data JSON untuk memudahkan pengujian
    const exampleEvent = {
        "source": "Manual Demo from Web",
        "magnitude": 7.8,
        "location": "Haiti Web Demo",
        "lat": 18.4,
        "lon": -72.4,
        "timestamp": Math.floor(Date.now() / 1000)
    };
    // Menampilkan contoh data di kotak teks saat halaman pertama kali dimuat
    eventDataTextArea.value = JSON.stringify(exampleEvent, null, 2);


    // Fungsi untuk menampilkan pesan di panel status
    function logStatus(message, isError = false) {
        console.log(message);
        statusLog.textContent = message;
        statusLog.style.color = isError ? 'var(--error-color)' : 'var(--success-color)';
    }


    // Menambahkan "pendengar" ke tombol. Fungsi ini akan berjalan saat tombol diklik.
    sendSignalButton.addEventListener('click', async () => {
        // Alamat dari Validator Agent yang berjalan di Docker
        // Port 8002 adalah yang kita definisikan di docker-compose.yml
       const agentUrl = 'http://localhost:8002/verify_disaster';
        
        let eventData;
        try {
            // Mengambil teks dari kotak dan mengubahnya menjadi objek JavaScript
            eventData = JSON.parse(eventDataTextArea.value);
            logStatus('Mencoba mengirim sinyal...');
        } catch (error) {
            logStatus('Error: Format JSON tidak valid!', true);
            return; // Berhenti jika JSON salah
        }

        try {
            // Mengirim data ke agen AI menggunakan fetch() API
            const response = await fetch(agentUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(eventData)
            });
            
            // Periksa apakah respons dari server berhasil (kode 2xx)
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Jika berhasil, tampilkan pesan sukses
            logStatus('Sinyal berhasil dikirim ke Validator Agent!\n\nCek log terminal Docker untuk melihat kelanjutannya.');

        } catch (error) {
            // Jika terjadi error koneksi atau server, tampilkan pesan error
            logStatus(`Gagal mengirim sinyal: ${error.message}\n\nPastikan semua container Docker sedang berjalan.`, true);
        }
    });
});