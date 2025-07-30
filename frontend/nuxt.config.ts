// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  css: ["~/assets/css/main.css"],
  vite: { plugins: [tailwindcss()] },
  runtimeConfig: { public: { apiBase: process.env.NUXT_PUBLIC_API_BASE } },
  modules: [
    "@nuxt/content",
    "@nuxt/eslint",
    "@nuxt/image",
    "@nuxt/scripts",
    "@nuxt/test-utils",
    "@nuxt/ui",
    "@pinia/nuxt",
    "nuxt-icon",
    "nuxt-security",
  ],
  security: {
    headers: {
      contentSecurityPolicy: {
        "connect-src": [
          "'self'",
          "http://localhost:8000",
          "ws://localhost:8000",
          "http://127.0.0.1:8000",
          "ws://127.0.0.1:8000",
        ],
      },
    },
  },
});
