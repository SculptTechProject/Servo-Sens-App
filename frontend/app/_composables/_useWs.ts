// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const useWs = (wsId: number, onMsg: (m: any) => void) => {
  const { public: pub } = useRuntimeConfig();
  const url =
    (pub.apiBase || "http://localhost:8000").replace("http", "ws") +
    `/ws/workspaces/${wsId}/`;
  const ws = shallowRef<WebSocket | null>(null);
  let retry = 0;
  const connect = () => {
    ws.value = new WebSocket(url);
    ws.value.onopen = () => {
      retry = 0;
    };
    ws.value.onmessage = (e) => onMsg(JSON.parse(e.data));
    ws.value.onclose = () =>
      setTimeout(connect, Math.min(5000, 500 * 2 ** retry++));
  };
  onMounted(connect);
  onBeforeUnmount(() => ws.value?.close());
  return { ws };
};
