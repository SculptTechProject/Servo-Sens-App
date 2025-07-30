/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
export const useWs = (wsId: number, onMsg: (m: any) => void) => {
  const cfg = useRuntimeConfig();

  let base = (cfg.public as any).wsBase as string | undefined;
  if (!base) {
    const apiBase = (cfg.public.apiBase as string) || "";
    if (apiBase.startsWith("http")) {
      base = apiBase.replace(/\/api\/?$/i, "").replace(/^http(s?):/i, "ws$1:");
    } else {
      // apiBase względne (np. '/api') -> użyj origin strony
      base = window.location.origin.replace(/^http(s?):/i, "ws$1:");
    }
  }

  const url = `${base.replace(/\/$/, "")}/ws/workspaces/${wsId}/`;

  const ws = shallowRef<WebSocket | null>(null);
  let retry = 0;

  const connect = () => {
    const sock = new WebSocket(url);
    ws.value = sock;

    sock.onopen = () => {
      retry = 0;
      if (import.meta.dev) console.log("[WS] OPEN", url);
    };
    sock.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        onMsg(data);
      } catch (err) {
        console.warn("[WS] bad message", e.data);
      }
    };
    sock.onerror = (e) => {
      console.warn("[WS] ERROR", e);
    };
    sock.onclose = () => {
      if (import.meta.dev) console.log("[WS] CLOSE, reconnect…");
      setTimeout(connect, Math.min(5000, 500 * 2 ** retry++));
    };
  };

  onMounted(connect);
  onBeforeUnmount(() => ws.value?.close());

  return { ws };
};
