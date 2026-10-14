import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",               // render components in the simulated browser
    setupFiles: ["./src/setupTests.ts"], // runs before every test file
  },
});
