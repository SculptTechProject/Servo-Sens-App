<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { useApi } from "~/_composables/useApi";
import { useWs } from "~/_composables/_useWs";
import { onMounted, onBeforeUnmount } from "vue";
import { useHistoryStore } from "~/_plugins/pinia/history";

const route = useRoute();
const router = useRouter();
const api = useApi();

const id = Number(route.params.id);
const history = useHistoryStore();

const bufRead = [] as any[];
const bufEv = [] as any[];

const info = ref<{
  id: number;
  name: string;
  machines_count: number;
  sensors_count?: number;
} | null>(null);

const loadingInfo = ref(true);
const running = ref(false);
const readings = ref<any[]>([]);
const events = ref<any[]>([]);

async function loadInfo() {
  loadingInfo.value = true;
  try {
    info.value = await api(`/api/workspaces/${id}/`);
  } catch (e: any) {
    info.value = { id, name: `WS #${id}`, machines_count: 0 };
  } finally {
    loadingInfo.value = false;
  }
}

onMounted(() => {
  tick = window.setInterval(() => {
    if (bufRead.length) {
      // weź tylko ostatni odczyt z ostatniej sekundy
      const last = bufRead[bufRead.length - 1]
      history.addReading(last)
      bufRead.length = 0
    }
    if (bufEv.length) {
      const lastEv = bufEv[bufEv.length - 1]
      history.addEvent(lastEv)
      bufEv.length = 0
    }
  }, 5000)
})

useWs(id, (m) => {
  if (m.type === "reading") bufRead.push(m);
  if (m.type === "event") bufEv.push(m);
});

let tick: number;
onMounted(() => {
  tick = window.setInterval(() => {
    if (bufRead.length) {
      readings.value.unshift(...bufRead.splice(0));
      if (readings.value.length > 100) readings.value.splice(100);
    }
    if (bufEv.length) {
      events.value.unshift(...bufEv.splice(0));
      if (events.value.length > 100) events.value.splice(100);
    }
  }, 1000);
});
onBeforeUnmount(() => {
  clearInterval(tick);
});

async function seed() {
  const res = await api(`/api/workspaces/${id}/seed/`, { method: "POST" });
  info.value = res as {
    id: number;
    name: string;
    machines_count: number;
    sensors_count: number;
  };
}

async function start() {
  await api(`/api/sim/start/${id}/`, { method: "POST" });
  running.value = true;
}
async function stop() {
  await api(`/api/sim/stop/${id}/`, { method: "POST" });
  running.value = false;
}
async function seedAndStart() {
  await seed();
  await start();
}
function backToList() {
  router.push("/dashboard/workspaces");
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-950 text-gray-200">
    <AppHeader />
    <main class="container mx-auto px-4 py-8">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h2 class="text-2xl md:text-3xl font-bold">
          Workspace <span class="text-emerald-500">#{{ id }}</span>
        </h2>
        <div class="flex flex-wrap gap-3">
          <button
            class="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700 border border-gray-700"
            @click="backToList"
          >
            <Icon name="i-heroicons-arrow-left" class="w-5 h-5" /> Wróć do listy
          </button>

          <button
            class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
            @click="start"
          >
            Start
          </button>
          <button
            class="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700 border border-gray-700"
            @click="stop"
          >
            Stop
          </button>

          <span
            class="px-3 py-2 rounded text-sm"
            :class="
              running
                ? 'bg-emerald-900/40 text-emerald-300'
                : 'bg-gray-800 text-gray-300'
            "
          >
            Status: {{ running ? "Running" : "Idle" }}
          </span>
        </div>
        <div class="flex gap-4 mt-4">
          <button
            class="bg-emerald-900/40 text-emerald-300 px-4 py-2 rounded-md cursor-pointer transition-all"
            @click="history.clearReadings()"
          >
            Wyczyść odczyty
          </button>
          <button
            class="bg-emerald-900/40 text-emerald-300 px-4 py-2 rounded-md cursor-pointer transition-all"
            @click="history.clearEvents()"
          >
            Wyczyść zdarzenia
          </button>
        </div>
      </div>

      <!-- Info/Seed CTA -->
      <div v-if="loadingInfo" class="text-gray-400 mb-6">Ładuję…</div>

      <div
        v-else-if="info && (info.sensors_count ?? 0) === 0"
        class="mb-6 bg-amber-900/20 border border-amber-700 rounded-xl p-4"
      >
        <p class="mb-3">
          Ten workspace nie ma jeszcze sensorów. Możesz dodać przykładowe i
          wystartować symulator jednym kliknięciem.
        </p>
        <div class="flex flex-wrap gap-3">
          <button
            class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
            @click="seed"
          >
            Utwórz przykładowe sensory
          </button>
          <button
            class="px-4 py-2 rounded bg-emerald-700 hover:bg-emerald-600"
            @click="seedAndStart"
          >
            Seed + Start
          </button>
        </div>
      </div>

      <div class="grid gap-6 md:grid-cols-2">
        <div class="bg-gray-900 rounded-xl p-4 shadow">
          <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
            <Icon name="i-heroicons-chart-bar" class="text-emerald-500" />
            Odczyty (ostatnie 100)
          </h3>
          <div class="h-72 overflow-auto text-sm divide-y divide-gray-800">
            <div
              v-for="(r, i) in history.readings"
              :key="i"
              class="flex justify-between py-1"
            >
              <span class="text-gray-400">#{{ i + 1 }}</span>
              <span class="font-medium">{{ r.value }} {{ r.unit }}</span>
              <span class="text-gray-500">{{
                new Date().toLocaleTimeString()
              }}</span>
            </div>
            <div
              v-if="readings.length === 0"
              class="text-gray-400 py-8 text-center"
            >
              Brak danych — kliknij <b>Start</b>, aby uruchomić symulator.
            </div>
          </div>
        </div>

        <div class="bg-gray-900 rounded-xl p-4 shadow">
          <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
            <Icon name="i-heroicons-bell-alert" class="text-emerald-500" />
            Zdarzenia
          </h3>
          <div class="h-72 overflow-auto text-sm divide-y divide-gray-800">
            <div v-for="(ev, i) in history.events" :key="i" class="py-1">
              <div class="flex items-center justify-between">
                <span
                  class="px-2 py-0.5 rounded text-xs bg-amber-900/40 text-amber-300"
                >
                  {{ ev.level || "INFO" }}
                </span>
                <span class="text-gray-500">{{
                  new Date().toLocaleTimeString()
                }}</span>
              </div>
              <div class="mt-1">{{ ev.message }}</div>
            </div>
            <div
              v-if="events.length === 0"
              class="text-gray-400 py-8 text-center"
            >
              Brak zdarzeń.
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
