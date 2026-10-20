import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, Vite manda /api al backend (docker compose lo expone en :8000).
// En el cluster lo hace el Ingress, y en el contenedor, nginx.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": process.env.BACKEND_URL || "http://localhost:8000",
    },
  },
});
