import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const api = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: { host: "127.0.0.1", port: 5173, proxy: { "/chat": api, "/confirm": api, "/health": api } },
  test: { environment: "jsdom", globals: false },
});
