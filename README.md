## README.md

````markdown
# AEGIS Protocol

Project ini menggunakan **Docker Compose** untuk menjalankan environment Internet Computer (ICP) dan agent-agent pendukung.  
Dengan setup ini, seluruh tim bisa menjalankan project tanpa harus install DFINITY SDK (`dfx`) secara manual di host.

---

## 📦 Prasyarat
Sebelum memulai, pastikan sudah ter-install di sistem:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git (untuk clone repo)

---

## 🚀 Cara Menjalankan Project

1. **Clone repo**
   ```bash
   git clone https://github.com/maliks1/AEGIS-Protocol.git
   cd AEGIS-Protocol
````

2. **Build image Docker**

   > Gunakan `--no-cache` jika ingin memastikan build ulang dari awal.

   ```bash
   docker-compose build --no-cache
   ```

3. **Jalankan semua service**

   ```bash
   docker-compose up
   ```

   Ini akan:

   * Membuat container `dfx-replica` untuk ICP local replica.
   * Menjalankan `dfx start` di dalam container.
   * Deploy semua canister.
   * Menyalakan `oracle-agent`, `validator-agent`, dan `action-agent`.

4. **Cek service**

   * ICP Local Replica → [http://localhost:4943](http://localhost:4943)
   * Oracle Agent → [http://localhost:8001](http://localhost:8001)
   * Validator Agent → [http://localhost:8002](http://localhost:8002)
   * Action Agent → [http://localhost:8003](http://localhost:8003)

---

## 🛠️ Perintah Tambahan

* **Stop semua service**

  ```bash
  docker-compose down
  ```

* **Masuk ke container `dfx-replica`**

  ```bash
  docker exec -it aegis-dfx-replica bash
  ```

  Cek versi `dfx`:

  ```bash
  dfx --version
  ```

---

## ❗ Problem Solving

### 1. **Error: `pull access denied for dfinity/sdk`**

* Penyebab: Image `dfinity/sdk` tidak tersedia publik.
* Solusi: Project ini sudah memakai `Dockerfile.dfx` untuk build image `dfx` secara lokal. Pastikan pakai:

  ```bash
  docker-compose build --no-cache
  ```

### 2. **Error: `failed to interact with console` saat build**

* Penyebab: Installer `dfx` butuh input interaktif.
* Solusi: Gunakan `ENV DFXVM_INIT_YES=1` di `Dockerfile.dfx` (sudah disiapkan di repo).

### 3. **Perubahan tidak terbaca saat build**

* Gunakan:

  ```bash
  docker-compose build --no-cache
  ```

### 4. **Port 4943 sudah terpakai**

* Cek service lain yang memakai port tersebut, lalu matikan:

  ```bash
  sudo lsof -i :4943
  kill -9 <PID>
  ```

---

## 📄 Struktur Repo

```
AEGIS-Protocol/
├── Dockerfile.dfx          # Image builder untuk DFINITY SDK
├── docker-compose.yml      # Konfigurasi service Docker
├── packages/
│   ├── execlayer_icp/      # Canister code & config ICP
│   └── AI_fetchai/         # Agent Python code
```

---

## 👥 Kontribusi

1. Fork repo ini
2. Buat branch baru
3. Commit perubahan
4. Push dan buat Pull Request

---

## 📜 Lisensi

MIT License.

```

---
