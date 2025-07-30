import { useAuthStore } from "~/_stores/auth";

export default defineNuxtRouteMiddleware(async () => {
  if (!import.meta.client) return;
  const auth = useAuthStore();
  const token = localStorage.getItem("token");
  if (!token) return navigateTo("/login");

  if (!auth.user) {
    try {
      await auth.fetchMe();
    } catch {
      localStorage.removeItem("token");
      return navigateTo("/login");
    }
  }
});
