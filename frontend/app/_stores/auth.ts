import { defineStore } from "pinia";
import { useApi } from "~/_composables/useApi";
type Me = { email: string; name: string };

export const useAuthStore = defineStore("auth", {
  state: () => ({ user: null as Me | null }),
  actions: {
    async login(email: string, password: string) {
      const api = useApi();
      const { token } = await api<{ token: string }>("/api/user/token/", {
        method: "POST",
        body: { email, password },
      });
      localStorage.setItem("token", token);
      await this.fetchMe();
    },
    async fetchMe() {
      const api = useApi();
      this.user = await api<Me>("/api/user/me/");
    },
    logout() {
      localStorage.removeItem("token");
      this.user = null;
      navigateTo("/login");
    },
    async register(payload: { name: string; email: string; password: string }) {
      const api = useApi();
      await api("/api/user/create/", { method: "POST", body: payload });
      // Automatically log in after registration
      await this.login(payload.email, payload.password);
    },
  },
});
