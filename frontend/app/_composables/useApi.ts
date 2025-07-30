export const useApi = () => {
  const { public: publicConfig } = useRuntimeConfig();
  const baseURL = (publicConfig.apiBase ?? "http://localhost:8000") as string;

  return $fetch.create({
    baseURL,
    onRequest({ options }) {
      if (import.meta.client) {
        const t = localStorage.getItem("token");
        if (t) {
          const h = new Headers(options.headers as HeadersInit);
          h.set("Authorization", `Token ${t}`);
          options.headers = h;
        }
      }
    },
    onResponseError({ response }) {
      if (response?.status === 401 && import.meta.client) {
        localStorage.removeItem("token");
        navigateTo("/login");
      }
    },
  });
};
