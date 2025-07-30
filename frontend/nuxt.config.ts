// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

const isDev = process.env.NODE_ENV !== "production";

export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  css: ["~/assets/css/main.css"],
  vite: { plugins: [tailwindcss()] },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "/api",
      wsBase: process.env.NUXT_PUBLIC_WS_BASE || "/ws",
    },
  },

  nitro: {
    routeRules: {
      "/api/**": { proxy: "http://127.0.0.1:8000/api/**" },
      "/ws/**": { proxy: "http://127.0.0.1:8000/ws/**" },
    },
  },
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
        "connect-src": isDev
          ? ["'self'", "http:", "https:", "ws:", "wss:"]
          : ["'self'"],
      },
    },
  },
});
