#!/usr/bin/env bash
# Memastikan skrip berhenti jika ada error
set -euo pipefail

# --- PENGATURAN AWAL ---
# Mendefinisikan path-path penting agar mudah dibaca
ROOT="$(pwd)"
SERVICE_DIR="services/backend"
PERSISTENT_DIR="${SERVICE_DIR}/persistent"
DFX_SRC="./.dfx/local/canister_ids.json" # <-- INI SUDAH BENAR, mencari canister_ids.json di lokasi yang tepat
IDENTITY_SRC="./identity.pem"

echo "==== Menjalankan Agents (Setup Jangka Panjang) ===="
echo "Project root: ${ROOT}"
echo

# --- LANGKAH 1: MEMBUAT FOLDER PENYIMPANAN ---
# Docker butuh folder ini untuk menyimpan data agent agar tidak hilang saat container mati.
mkdir -p "${PERSISTENT_DIR}"
echo "- Memastikan folder ${PERSISTENT_DIR} ada."

# --- LANGKAH 2: MENYALIN KUNCI IDENTITAS ---
# Memeriksa apakah identity.pem ada dan tidak kosong, lalu menyalinnya ke folder penyimpanan.
if [ -f "${IDENTITY_SRC}" ] && [ -s "${IDENTITY_SRC}" ]; then
  cp -f "${IDENTITY_SRC}" "${PERSISTENT_DIR}/identity.pem"
  chmod 600 "${PERSISTENT_DIR}/identity.pem" || true # Mengatur izin file agar aman
  echo "- Menyalin identity.pem -> ${PERSISTENT_DIR}/identity.pem (izin 600)"
else
  echo "ERROR: identity.pem tidak ditemukan atau kosong di ${IDENTITY_SRC}."
  echo "Harap buat file identity.pem yang valid di root proyek sebelum melanjutkan."
  exit 1
fi

# --- LANGKAH 3: MENYALIN ID CANISTER ---
# Memeriksa apakah canister_ids.json ada, lalu menyalinnya agar bisa dibaca oleh agent di dalam Docker.
if [ -f "${DFX_SRC}" ] && [ -s "${DFX_SRC}" ]; then
  mkdir -p "${PERSISTENT_DIR}/dfx-local"
  cp -f "${DFX_SRC}" "${PERSISTENT_DIR}/dfx-local/canister_ids.json"
  chmod 644 "${PERSISTENT_DIR}/dfx-local/canister_ids.json" || true
  echo "- Menyalin canister_ids.json -> ${PERSISTENT_DIR}/dfx-local/canister_ids.json"
else
  # Memberi peringatan jika file tidak ada, tapi tidak menghentikan skrip.
  echo "PERINGATAN: canister_ids.json tidak ditemukan di ${DFX_SRC}. Agent mungkin tidak bisa terhubung ke canister lokal."
fi

# --- LANGKAH 4: MERESTART CONTAINER DOCKER ---
echo "- Menghentikan container lama jika ada (docker compose down)..."
pushd "${SERVICE_DIR}" >/dev/null # Pindah sementara ke dalam folder service
docker compose down               # Perintah ini menghentikan & menghapus container lama untuk memastikan restart bersih
echo "- Membangun dan memulai container baru (docker compose up -d --build)..."
docker compose up -d --build      # Menjalankan docker compose untuk membuat yang baru
popd >/dev/null                   # Kembali ke folder awal

# --- LANGKAH 5: MENUNGGU DAN MENAMPILKAN LOG ---
echo "- Menunggu container stabil (sekitar 20 detik) ..."
sleep 10
docker compose -f ${SERVICE_DIR}/docker-compose.yml ps

echo "- Menampilkan 150 baris log terakhir:"
docker compose -f ${SERVICE_DIR}/docker-compose.yml logs --tail 150

echo
echo "Selesai. Untuk melihat log secara langsung, gunakan:"
echo "  cd ${SERVICE_DIR}"
echo "  docker compose logs -f"
