/// <reference types="vitest" />

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000"
    }
  },
  test: {
    environment: "jsdom",
    exclude: ["**/*.spec.ts", "node_modules/**", "dist/**"],
    globals: true,
    setupFiles: ["./tests/setup.ts"]
  }
});
