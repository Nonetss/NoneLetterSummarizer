// @ts-check
import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  integrations: [react()],
  vite: {
    envPrefix: "VITE_", // Asegura que solo se expongan variables con el prefijo "VITE_"
  },
});

