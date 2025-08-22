import { defineConfig } from "vite";
import path from "path";
import fs from "fs";

// Fungsi untuk mendapatkan path ke file canister_ids.json
function getCanisterIds() {
  const network = process.env.DFX_NETWORK || "local";
  const canisterIdsPath = path.resolve(__dirname, "..", ".dfx", network, "canister_ids.json");

  if (!fs.existsSync(canisterIdsPath)) {
    throw new Error("Could not find canister_ids.json. Make sure you have deployed your canisters.");
  }

  const canisterIds = JSON.parse(fs.readFileSync(canisterIdsPath, "utf8"));
  return canisterIds;
}

// Fungsi untuk membuat variabel lingkungan untuk Vite
function createEnvVars() {
  const canisterIds = getCanisterIds();
  const env = {};
  for (const canisterName in canisterIds) {
    const key = `process.env.CANISTER_ID_${canisterName.toUpperCase()}`;
    env[key] = JSON.stringify(canisterIds[canisterName][process.env.DFX_NETWORK || "local"]);
  }
  return env;
}

// Konfigurasi Vite
export default defineConfig({
  // INI DARI SOLUSI SEBELUMNYA (JANGAN DIHAPUS)
  define: createEnvVars(),

  // ===== TAMBAHKAN BLOK INI =====
  resolve: {
    alias: {
      "dfx:canisters": path.resolve(__dirname, "..", ".dfx", "local", "canisters"),
    },
  },
  // ===============================

  // INI JUGA DARI SOLUSI SEBELUMNYA (JANGAN DIHAPUS)
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:4943",
        changeOrigin: true,
      },
    },
  },
});