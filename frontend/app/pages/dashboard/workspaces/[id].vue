<!-- pages/dashboard/workspaces/work/[id].vue -->
<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<template>
  <div class="min-h-screen flex flex-col bg-gray-950 text-gray-200">
    <AppHeader />

    <main class="container mx-auto py-6 grid gap-6 xl:grid-cols-3">
      <!-- LEWA: Canvas -->
      <section class="xl:col-span-2 space-y-3">
        <header class="flex items-center justify-between">
          <div>
            <h1 class="text-lg font-semibold">
              Workspace
              <span v-if="topo" class="text-emerald-400"
                >/ {{ topo.workspace.name }}</span
              >
            </h1>
            <p class="text-sm text-gray-400">
              Przesuń maszyny, przeciągnij sensor żeby podłączyć.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
              @click="start"
            >
              Start
            </button>
            <button
              class="px-3 py-2 rounded bg-gray-800 hover:bg-gray-700"
              @click="stop"
            >
              Stop
            </button>
            <button
              class="px-3 py-2 rounded bg-gray-800 hover:bg-gray-700"
              @click="loadTopology"
            >
              Odśwież
            </button>
          </div>
        </header>

        <div
          id="ws-canvas"
          class="relative h-[560px] rounded-xl border border-gray-800 overflow-hidden"
          :style="gridBgStyle"
        >
          <div
            v-if="loadingTopo"
            class="absolute inset-0 grid place-items-center text-gray-400"
          >
            Ładowanie…
          </div>

          <template v-if="topo && topo.machines.length">
            <div
              v-for="m in topo.machines"
              :key="m.id"
              class="absolute w-72 select-none"
              :style="mStyle(m)"
              @dragover="onMachineDragOver"
              @drop="(e) => onMachineDrop(e, m)"
            >
              <div
                class="bg-gray-900/90 backdrop-blur border border-gray-700 rounded-2xl shadow"
              >
                <!-- uchwyt do drag -->
                <div
                  class="flex items-center justify-between p-3 cursor-grab active:cursor-grabbing"
                  @pointerdown="(e) => onMachinePointerDown(e, m)"
                  @pointermove="(e) => onMachinePointerMove(e, m)"
                  @pointerup="(e) => onMachinePointerUp(e, m)"
                >
                  <div class="font-medium truncate">{{ m.name }}</div>
                  <span class="text-xs text-gray-400">{{ m.kind }}</span>
                </div>

                <div class="px-3 pb-3">
                  <div class="space-y-1">
                    <div
                      v-for="s in m.sensors"
                      :key="s.id"
                      class="flex items-center justify-between text-sm rounded px-2 py-1 bg-gray-800/70 border border-gray-700"
                      draggable="true"
                      title="Przeciągnij na inną maszynę"
                      @dragstart="(e) => onSensorDragStart(e, s)"
                    >
                      <div class="truncate">{{ s.name }}</div>
                      <span class="text-xs text-gray-400">{{ s.unit }}</span>
                    </div>
                  </div>

                  <div class="mt-2 text-[10px] text-gray-500">
                    x: {{ m.x }}, y: {{ m.y }}
                  </div>

                  <div class="mt-2 flex gap-2">
                    <button
                      class="px-2 py-1 text-xs rounded bg-gray-800 hover:bg-gray-700"
                      @pointerdown.stop
                      @mousedown.stop
                      @click.stop="openEditMachine(m)"
                    >
                      Edytuj
                    </button>
                    <button
                      class="px-2 py-1 text-xs rounded bg-red-900/60 hover:bg-red-800"
                      @pointerdown.stop
                      @mousedown.stop
                      @click.stop="deleteMachine(m)"
                    >
                      Usuń
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <div
            v-else-if="!loadingTopo"
            class="absolute inset-0 grid place-items-center text-gray-500"
          >
            Brak maszyn. Dodaj pierwszą maszynę przyciskiem poniżej.
          </div>

          <!-- FAB: dodaj maszynę -->
          <button
            class="absolute bottom-4 right-4 px-4 py-3 rounded-full shadow bg-emerald-600 hover:bg-emerald-500"
            @click="openAddMachine"
          >
            + Maszyna
          </button>
        </div>
      </section>

      <!-- PRAWA: Pula / Odczyty / Zdarzenia -->
      <aside class="space-y-6">
        <!-- Pula sensorów -->
        <div
          class="rounded-xl border border-gray-800 bg-gray-900 p-3"
          title="Upuść sensor, by odłączyć od maszyny"
          @dragover.prevent
          @drop="onPoolDrop"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold">Pula sensorów</h3>
            <button
              class="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700"
              @click="openAddSensor()"
            >
              + Sensor
            </button>
          </div>
          <div class="h-[220px] overflow-auto space-y-2 text-sm">
            <div
              v-for="s in unassigned"
              :key="s.id"
              class="flex items-center justify-between rounded px-2 py-1 bg-gray-800 border border-gray-700"
              draggable="true"
              title="Przeciągnij na maszynę"
              @dragstart="(e) => onSensorDragStart(e, s)"
            >
              <div class="truncate">{{ s.name }}</div>
              <span class="text-xs text-gray-400">{{ s.unit }}</span>
            </div>
            <div v-if="!unassigned.length" class="text-gray-500">
              Brak – wszystkie przypisane.
            </div>
          </div>
        </div>

        <!-- Odczyty (fallback + WS) -->
        <div class="rounded-xl border border-gray-800 bg-gray-900 p-3">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold">Odczyty (live)</h3>
            <button
              class="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700"
              @click="loadLatest"
            >
              Odśwież
            </button>
          </div>

          <div v-if="!Object.keys(latest).length" class="text-sm text-gray-500">
            Brak danych… (uruchom symulator lub poczekaj na pierwszy odczyt)
          </div>

          <div v-else class="grid gap-3 md:grid-cols-2">
            <div
              v-for="c in cards"
              :key="c.id"
              class="rounded-lg border p-3"
              :class="
                c.over
                  ? 'border-red-700 bg-red-900/20'
                  : 'border-gray-700 bg-gray-800/60'
              "
            >
              <div class="text-sm text-gray-300 mb-1 truncate">
                {{ c.title }}
              </div>
              <div class="flex items-end gap-2">
                <div class="text-2xl font-semibold">{{ c.value }}</div>
                <div class="text-gray-400">{{ c.unit }}</div>
                <div class="ml-auto text-xs text-gray-500">
                  · {{ timeAgo(c.ts) }} temu
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Zdarzenia -->
        <div class="rounded-xl border border-gray-800 bg-gray-900 p-3">
          <h3 class="font-semibold mb-2">Zdarzenia</h3>
          <div class="h-64 overflow-auto text-sm">
            <div
              v-for="(ev, i) in events"
              :key="i"
              class="py-1 border-b border-gray-800"
            >
              <span class="text-amber-400">{{ ev.level }}</span> —
              {{ ev.message }}
            </div>
            <div v-if="!events.length" class="text-gray-500">Brak zdarzeń.</div>
          </div>
        </div>
      </aside>
    </main>

    <!-- MODAL: Edycja/Dodanie maszyny + komponentów -->
    <transition name="fade">
      <div
        v-if="showMachineModal"
        class="fixed inset-0 bg-black/50 grid place-items-center z-50"
      >
        <div
          class="w-full max-w-2xl rounded-2xl bg-gray-900 border border-gray-800 p-4"
        >
          <h3 class="font-semibold mb-3">
            {{ machineForm.id ? "Edytuj maszynę" : "Dodaj maszynę" }}
          </h3>

          <div class="grid md:grid-cols-2 gap-4">
            <!-- Dane maszyny -->
            <div class="space-y-3">
              <div class="text-sm text-gray-400">Dane maszyny</div>
              <input
                v-model="machineForm.name"
                placeholder="Nazwa"
                class="w-full rounded bg-gray-800 p-2 outline-none"
              >
              <input
                v-model="machineForm.kind"
                placeholder="Typ (motor/pump/...)"
                class="w-full rounded bg-gray-800 p-2 outline-none"
              >
              <div class="flex justify-end gap-2">
                <button
                  class="px-3 py-2 rounded bg-gray-800 hover:bg-gray-700"
                  @click="closeMachineModal"
                >
                  Anuluj
                </button>
                <button
                  class="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
                  @click="saveMachine"
                >
                  Zapisz
                </button>
              </div>
            </div>

            <!-- Sensory tej maszyny -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <div class="text-sm text-gray-400">Sensory maszyny</div>
                <button
                  class="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700"
                  @click="openAddSensor(machineForm.id!)"
                >
                  + Sensor do maszyny
                </button>
              </div>

              <div
                v-if="editSensors.length === 0"
                class="text-sm text-gray-500"
              >
                Brak sensorów.
              </div>

              <div
                v-for="row in editSensors"
                :key="row.id"
                class="rounded border border-gray-700 p-2 bg-gray-800/50 space-y-2"
              >
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400 w-20"
                    >ID #{{ row.id }}</span
                  >
                  <select
                    v-model="row.kind"
                    class="flex-1 rounded bg-gray-800 p-2 outline-none"
                  >
                    <option value="temperature">temperature</option>
                    <option value="current">current</option>
                    <option value="vibration">vibration</option>
                  </select>
                </div>
                <div class="flex items-center gap-2">
                  <input
                    v-model="row.unit"
                    placeholder="Jednostka"
                    class="flex-1 rounded bg-gray-800 p-2 outline-none"
                  >
                  <input
                    v-model.number="row.threshold"
                    type="number"
                    step="any"
                    placeholder="Próg"
                    class="w-32 rounded bg-gray-800 p-2 outline-none"
                  >
                </div>
                <div class="flex justify-end gap-2">
                  <button
                    class="px-2 py-1 text-xs rounded bg-gray-800 hover:bg-gray-700"
                    @click="saveSensorRow(row)"
                  >
                    Zapisz
                  </button>
                  <button
                    class="px-2 py-1 text-xs rounded bg-red-900/60 hover:bg-red-800"
                    @click="removeSensorRow(row)"
                  >
                    Usuń
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- MODAL: Dodaj sensor (do puli lub do konkretnej maszyny) -->
    <transition name="fade">
      <div
        v-if="showSensorModal"
        class="fixed inset-0 bg-black/50 grid place-items-center z-50"
      >
        <div
          class="w-full max-w-md rounded-2xl bg-gray-900 border border-gray-800 p-4"
        >
          <h3 class="font-semibold mb-3">Dodaj sensor</h3>
          <div class="space-y-3">
            <input
              v-model="sensorForm.name"
              placeholder="Nazwa (opcjonalnie)"
              class="w-full rounded bg-gray-800 p-2 outline-none"
            >
            <select
              v-model="sensorForm.kind"
              class="w-full rounded bg-gray-800 p-2 outline-none"
            >
              <option value="temperature">temperature</option>
              <option value="current">current</option>
              <option value="vibration">vibration</option>
            </select>
            <input
              v-model="sensorForm.unit"
              placeholder="Jednostka (np. °C / A / mm/s)"
              class="w-full rounded bg-gray-800 p-2 outline-none"
            >
            <input
              v-model.number="sensorForm.threshold"
              type="number"
              step="any"
              placeholder="Próg (opcjonalnie)"
              class="w-full rounded bg-gray-800 p-2 outline-none"
            >
            <select
              v-model.number="sensorForm.machine"
              class="w-full rounded bg-gray-800 p-2 outline-none"
            >
              <option :value="null">— do puli (bez przypisania) —</option>
              <option
                v-for="m in topo?.machines || []"
                :key="m.id"
                :value="m.id"
              >
                {{ m.name }}
              </option>
            </select>
          </div>
          <div class="mt-4 flex justify-end gap-2">
            <button
              class="px-3 py-2 rounded bg-gray-800 hover:bg-gray-700"
              @click="closeSensorModal"
            >
              Anuluj
            </button>
            <button
              class="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
              @click="saveSensor"
            >
              Zapisz
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { useApi } from "~/_composables/useApi";
import { useWs } from "~/_composables/_useWs";

const route = useRoute();
const id = Number(route.params.id);
const api = useApi();

/** Typy */
type MachineMini = {
  id: number;
  name: string;
  kind: string;
  x: number;
  y: number;
};
type SensorMeta = {
  id: number;
  name: string;
  kind: string;
  unit: string;
  threshold: number | null;
  machine: MachineMini | null;
};
type MachineFull = MachineMini & { sensors: SensorMeta[] };
type Topology = {
  workspace: { id: number; name: string };
  machines: MachineFull[];
  sensors: SensorMeta[];
};
type LatestItem = {
  sensor_id: number;
  value: number | null;
  unit: string;
  ts: string | null;
  name: string;
  machine: string | null;
  threshold: number | null;
};

/** State */
const topo = ref<Topology | null>(null);
const sensorMap = ref<Record<number, SensorMeta>>({});
const loadingTopo = ref(true);
const topoErr = ref<string | null>(null);
const gridStep = ref(16);

/** WS + fallback latest */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const readings = ref<any[]>([]);
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const events = ref<any[]>([]);
const latest = ref<Record<number, LatestItem>>({});
const wsSeen = ref(false);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
useWs(id, (m: any) => {
  if (m.type === "reading") {
    readings.value.unshift(m);
    wsSeen.value = true;
    latest.value[m.sensor_id] = {
      sensor_id: m.sensor_id,
      value: m.value,
      unit: m.unit,
      ts: m.ts ?? new Date().toISOString(),
      name: sensorMap.value[m.sensor_id]?.name ?? `#${m.sensor_id}`,
      machine: sensorMap.value[m.sensor_id]?.machine?.name ?? null,
      threshold: sensorMap.value[m.sensor_id]?.threshold ?? null,
    };
  }
  if (m.type === "event") events.value.unshift(m);
  readings.value.splice(0, 100);
});

/** API: start/stop */
const start = () => api(`/api/sim/start/${id}/`, { method: "POST" });
const stop = () => api(`/api/sim/stop/${id}/`, { method: "POST" });

/** Load topology */
async function loadTopology() {
  loadingTopo.value = true;
  topoErr.value = null;
  try {
    const t = await api(`/api/workspaces/${id}/topology/`);
    const topology = t as Topology;
    topo.value = topology;
    sensorMap.value = Object.fromEntries(
      (topology.sensors as SensorMeta[]).map((s) => [s.id, s])
    );
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
    topoErr.value = e?.message || "Nie udało się pobrać topologii.";
  } finally {
    loadingTopo.value = false;
  }
}
onMounted(async () => {
  await loadTopology();
  await loadLatest();
  const h = setInterval(() => {
    if (!wsSeen.value) loadLatest();
  }, 5000);
  onBeforeUnmount(() => clearInterval(h));
});

/** Latest-readings fallback */
async function loadLatest() {
  try {
    const items = await api(`/api/workspaces/${id}/latest-readings/`);
    const map: Record<number, LatestItem> = {};
    for (const it of items as LatestItem[]) map[it.sensor_id] = it;
    latest.value = map;
  } catch {
    latest.value = {};
  }
}

/** Utils do Odczytów */
function timeAgo(ts?: string | null) {
  if (!ts) return "—";
  const diff = (Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return `${Math.max(0, Math.floor(diff))}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  return `${Math.floor(diff / 3600)}h`;
}
const cards = computed(() => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const arr: any[] = [];
  for (const sid of Object.keys(latest.value)) {
    const it = latest.value[+sid];
    const meta = sensorMap.value[+sid];
    const thr = it?.threshold ?? meta?.threshold ?? null;
    const over =
      typeof thr === "number" && it?.value != null
        ? Number(it.value) >= thr
        : false;
    arr.push({
      id: +sid,
      title: meta
        ? `${meta.name} → ${meta.machine?.name ?? "—"}`
        : (it?.name ?? `#${sid}`),
      value: it?.value ?? "—",
      unit: it?.unit ?? meta?.unit ?? "",
      ts: it?.ts,
      over,
    });
  }
  return arr.sort((a, b) => a.title.localeCompare(b.title));
});

/** Drag machines (tylko po headerze) */
const dragging = reactive<{
  id: number | null;
  offsetX: number;
  offsetY: number;
}>({ id: null, offsetX: 0, offsetY: 0 });
function onMachinePointerDown(e: PointerEvent, m: MachineFull) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
  dragging.id = m.id;
  dragging.offsetX = e.clientX - rect.left;
  dragging.offsetY = e.clientY - rect.top;
  (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
}
function onMachinePointerMove(e: PointerEvent, m: MachineFull) {
  if (dragging.id !== m.id || !topo.value) return;
  const canvas = document.getElementById("ws-canvas")!;
  const crect = canvas.getBoundingClientRect();
  const rawX = e.clientX - crect.left - dragging.offsetX;
  const rawY = e.clientY - crect.top - dragging.offsetY;
  const nx = Math.max(0, Math.min(crect.width - 288, rawX));
  const ny = Math.max(0, Math.min(crect.height - 120, rawY));
  const step = gridStep.value;
  m.x = Math.round(nx / step) * step;
  m.y = Math.round(ny / step) * step;
}
async function onMachinePointerUp(e: PointerEvent, m: MachineFull) {
  if (dragging.id !== m.id) return;
  dragging.id = null;
  try {
    await api(`/api/core/machines/${m.id}/`, {
      method: "PATCH",
      body: { x: m.x, y: m.y },
    });
  } catch {
    console.error("Nie udało się zapisać pozycji maszyny.");
  }
  (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
}

/** Drag sensors */
function onSensorDragStart(ev: DragEvent, s: SensorMeta) {
  ev.dataTransfer?.setData("text/plain", String(s.id));
  ev.dataTransfer?.setDragImage(new Image(), 0, 0);
}
function onMachineDragOver(ev: DragEvent) {
  ev.preventDefault();
}
async function onMachineDrop(ev: DragEvent, m: MachineFull) {
  ev.preventDefault();
  const sid = Number(ev.dataTransfer?.getData("text/plain"));
  const s = sensorMap.value[sid];
  if (!s) return;
  if (s.machine?.id === m.id) return;

  if (s.machine) {
    const prev = topo.value!.machines.find((mm) => mm.id === s.machine!.id);
    if (prev) prev.sensors = prev.sensors.filter((ss) => ss.id !== s.id);
  }
  s.machine = { id: m.id, name: m.name, kind: m.kind, x: m.x, y: m.y };
  m.sensors.push(s);

  try {
    await api(`/api/core/sensors/${sid}/`, {
      method: "PATCH",
      body: { machine: m.id },
    });
  } catch {
    console.error("Nie udało się przypisać sensora do maszyny.");
  }
}
/** Drop do puli (odłączenie) */
async function onPoolDrop(ev: DragEvent) {
  ev.preventDefault();
  const sid = Number(ev.dataTransfer?.getData("text/plain"));
  const s = sensorMap.value[sid];
  if (!s || !topo.value) return;
  if (s.machine) {
    const prev = topo.value.machines.find((mm) => mm.id === s.machine!.id);
    if (prev) prev.sensors = prev.sensors.filter((ss) => ss.id !== s.id);
  }
  s.machine = null;
  try {
    await api(`/api/core/sensors/${sid}/`, {
      method: "PATCH",
      body: { machine: null },
    });
  } catch {
    console.error("Nie udało się odłączyć sensora od maszyny.");
  }
}

/** ========== MODALE / FORMY ========== */
const showMachineModal = ref(false);
const machineForm = reactive<{ id: number | null; name: string; kind: string }>(
  { id: null, name: "", kind: "motor" }
);

// tablica edycyjna sensorów danej maszyny
const editSensors = ref<
  Array<{
    id: number;
    kind: "temperature" | "current" | "vibration";
    unit: string;
    threshold: number | null;
  }>
>([]);

function openAddMachine() {
  machineForm.id = null;
  machineForm.name = "";
  machineForm.kind = "motor";
  editSensors.value = [];
  showMachineModal.value = true;
}
function openEditMachine(m: MachineFull) {
  machineForm.id = m.id;
  machineForm.name = m.name;
  machineForm.kind = m.kind;
  editSensors.value = m.sensors.map((s) => ({
    id: s.id,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    kind: s.kind as any,
    unit: s.unit,
    threshold: s.threshold ?? null,
  }));
  showMachineModal.value = true;
}
function closeMachineModal() {
  showMachineModal.value = false;
}

async function saveMachine() {
  try {
    if (!topo.value) return;
    if (machineForm.id) {
      await api(`/api/core/machines/${machineForm.id}/`, {
        method: "PATCH",
        body: { name: machineForm.name, kind: machineForm.kind },
      });
    } else {
      const created = await api(`/api/core/machines/`, {
        method: "POST",
        body: {
          workspace: topo.value.workspace.id,
          name: machineForm.name || "Nowa maszyna",
          kind: machineForm.kind || "motor",
          x: 100,
          y: 100,
        },
      });
      topo.value.machines.push({ ...created, sensors: [] });
      // po dodaniu nowej – nic nie edytujemy
    }
    // zapisz ewentualne zmiany sensorów (jeśli były)
    await Promise.all(
      editSensors.value.map((row) =>
        api(`/api/core/sensors/${row.id}/`, {
          method: "PATCH",
          body: { kind: row.kind, unit: row.unit, threshold: row.threshold },
        })
      )
    );
    await loadTopology();
    showMachineModal.value = false;
  } catch (e) {
    console.error(e);
  }
}

async function saveSensorRow(row: {
  id: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  kind: any;
  unit: string;
  threshold: number | null;
}) {
  try {
    await api(`/api/core/sensors/${row.id}/`, {
      method: "PATCH",
      body: { kind: row.kind, unit: row.unit, threshold: row.threshold },
    });
    await loadTopology();
  } catch (e) {
    console.error(e);
  }
}
async function removeSensorRow(row: { id: number }) {
  if (!confirm(`Usunąć sensor #${row.id}?`)) return;
  try {
    await api(`/api/core/sensors/${row.id}/`, { method: "DELETE" });
    await loadTopology();
    // zdejmij z modalowej listy
    editSensors.value = editSensors.value.filter((r) => r.id !== row.id);
  } catch (e) {
    console.error(e);
  }
}

/** MODAL: dodaj sensor (do puli lub do konkretnej maszyny) */
const showSensorModal = ref(false);
const sensorForm = reactive<{
  name: string;
  kind: "temperature" | "current" | "vibration";
  unit: string;
  threshold: number | null;
  machine: number | null;
}>({
  name: "",
  kind: "temperature",
  unit: "°C",
  threshold: null,
  machine: null,
});
function openAddSensor(prefillMachineId?: number) {
  sensorForm.name = "";
  sensorForm.kind = "temperature";
  sensorForm.unit = "°C";
  sensorForm.threshold = null;
  sensorForm.machine = prefillMachineId ?? null; // null -> do puli
  showSensorModal.value = true;
}
function closeSensorModal() {
  showSensorModal.value = false;
}
async function saveSensor() {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const body: any = {
      kind: sensorForm.kind,
      unit: sensorForm.unit,
      threshold: sensorForm.threshold,
      machine: sensorForm.machine,
    };
    if (sensorForm.name) body.name = sensorForm.name; // backend zignoruje jeśli nie obsługuje
    await api(`/api/core/sensors/`, { method: "POST", body });
    showSensorModal.value = false;
    await loadTopology();
  } catch (e) {
    console.error(e);
  }
}

/** Delete machine */
async function deleteMachine(m: MachineFull) {
  if (!confirm(`Usunąć maszynę "${m.name}"?`)) return;
  try {
    await api(`/api/core/machines/${m.id}/`, { method: "DELETE" });
    await loadTopology();
  } catch (e) {
    console.error("Nie udało się usunąć maszyny.", e);
  }
}

/** Computed helpers */
const unassigned = computed(() =>
  (topo.value?.sensors || []).filter((s) => !s.machine)
);
function mStyle(m: MachineMini) {
  return { left: `${m.x}px`, top: `${m.y}px` };
}
const gridBgStyle = computed(() => {
  const s = gridStep.value;
  return {
    background: `linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px) 0 0 / ${s}px ${s}px,
       linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px) 0 0 / ${s}px ${s}px,
       #0b0f14`,
  };
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
