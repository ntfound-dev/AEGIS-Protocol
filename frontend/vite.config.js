import { defineConfig } from "vite";
import path from "path";
import fs from "fs";

// Function to get path to canister_ids.json file
function getCanisterIds() {
  const network = process.env.DFX_NETWORK || "local";
  const canisterIdsPath = path.resolve(__dirname, "..", ".dfx", network, "canister_ids.json");

  if (!fs.existsSync(canisterIdsPath)) {
    throw new Error("Could not find canister_ids.json. Make sure you have deployed your canisters.");
  }

  const canisterIds = JSON.parse(fs.readFileSync(canisterIdsPath, "utf8"));
  return canisterIds;
}

// Function to create environment variables for Vite
function createEnvVars() {
  const canisterIds = getCanisterIds();
  const env = {};
  for (const canisterName in canisterIds) {
    const key = `process.env.CANISTER_ID_${canisterName.toUpperCase()}`;
    env[key] = JSON.stringify(canisterIds[canisterName][process.env.DFX_NETWORK || "local"]);
  }
  return env;
}

// Vite Configuration
export default defineConfig({
  // This section is already correct for environment variables
  define: createEnvVars(),

  // ===== REVISED BLOCK =====
  resolve: {
    alias: {
      // ".." means "go up one folder level" (from /frontend to /)
      // then enter "src/declarations"
      "@declarations": path.resolve(__dirname, "..", "src", "declarations"),
    },
  },
  // ============================

  // Your proxy server configuration is already correct
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:4943",
        changeOrigin: true,
      },
    },
  },
});