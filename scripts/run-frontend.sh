#!/usr/bin/env bash
# run-frontend.sh
# Versi: 1.0
# Tujuan: men-setup dan menjalankan frontend (vite + paket @dfinity/*)
set -euo pipefail

# Konfigurasi singkat
FRONTEND_DIR="frontend"
DFINITY_PKGS=( "@dfinity/agent" "@dfinity/auth-client" "@dfinity/candid" "@dfinity/principal" )
VITE_PACKAGE="vite"

# Jika ingin hanya melakukan instalasi tanpa menjalankan dev server:
# SKIP_START=1 ./run-frontend.sh
SKIP_START="${SKIP_START:-0}"

# Cek npm & node
if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm tidak ditemukan. Install node/npm dulu." >&2
  exit 2
fi
if ! command -v node >/dev/null 2>&1; then
  echo "Error: node tidak ditemukan. Install node/npm dulu." >&2
  exit 2
fi

# Masuk ke direktori frontend
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Direktori '$FRONTEND_DIR' tidak ditemukan. Buat dulu atau jalankan dari lokasi yang benar." >&2
  exit 3
fi
cd "$FRONTEND_DIR"

echo "Working dir: $(pwd)"

# npm init jika package.json belum ada
if [ ! -f package.json ]; then
  echo "package.json tidak ditemukan — menjalankan: npm init -y"
  npm init -y
else
  echo "package.json sudah ada — lewati npm init"
fi

# Install vite sebagai dev dependency (cek dulu apakah sudah terpasang)
if npm list --depth=0 2>/dev/null | grep -q " ${VITE_PACKAGE}@"; then
  echo "vite sudah terpasang (devDependency) — lewati"
else
  echo "Menginstall vite sebagai devDependency..."
  npm install --save-dev "$VITE_PACKAGE"
fi

# Install paket-paket @dfinity jika belum ada
for pkg in "${DFINITY_PKGS[@]}"; do
  if npm list --depth=0 2>/dev/null | grep -q " ${pkg}@"; then
    echo "$pkg sudah terpasang — lewati"
  else
    echo "Menginstall $pkg ..."
    npm install "$pkg"
  fi
done

# Tambahkan skrip "dev": "vite" ke package.json jika belum ada
has_dev_script=$(node -e "let p=require('./package.json'); console.log(p.scripts && p.scripts.dev ? '1' : '0');")
if [ "$has_dev_script" = "1" ]; then
  echo "Script 'dev' sudah ada di package.json — lewati penambahan"
else
  echo "Menambahkan script 'dev' ke package.json..."
  node -e "let p=require('./package.json'); p.scripts=p.scripts||{}; p.scripts.dev='vite'; require('fs').writeFileSync('package.json', JSON.stringify(p,null,2)); console.log('added dev script to package.json');"
fi

# Jalankan dev server kecuali diminta untuk skip
if [ "$SKIP_START" != "1" ]; then
  echo "Menjalankan: npm run dev"
  # Jalankan npm run dev (tidak dijalankan di background — ini akan menahan terminal)
  npm run dev
else
  echo "SKIP_START=1 terdeteksi — setup selesai, tidak menjalankan 'npm run dev'."
fi
