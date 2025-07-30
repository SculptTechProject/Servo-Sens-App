<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { useApi } from "~/_composables/useApi";
import { useWs } from "~/_composables/_useWs";
const route = useRoute();
const id = Number(route.params.id);
const api = useApi();
const readings = ref<any[]>([]);
const events = ref<any[]>([]);
useWs(id, (m) => {
  if (m.type === "reading") readings.value.unshift(m);
  if (m.type === "event") events.value.unshift(m);
  readings.value.splice(0, 100);
});
const start = () => api(`/api/sim/start/${id}/`, { method: "POST" });
const stop = () => api(`/api/sim/stop/${id}/`, { method: "POST" });
</script>

<template>
  <div class="container mx-auto py-8 text-gray-200">
    <div class="flex gap-3 mb-6">
      <button
        class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
        @click="start"
      >
        Start
      </button>
      <button
        class="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700"
        @click="stop"
      >
        Stop
      </button>
    </div>
    <div class="grid gap-6 md:grid-cols-2">
      <div class="bg-gray-900 rounded-xl p-4">
        <h3 class="font-semibold mb-2">Odczyty</h3>
        <div class="h-64 overflow-auto text-sm">
          <div
            v-for="(r, i) in readings"
            :key="i"
            class="flex justify-between border-b border-gray-800 py-1"
          >
            <span>#{{ r.sensor_id }}</span
            ><span>{{ r.value }} {{ r.unit }}</span>
          </div>
        </div>
      </div>
      <div class="bg-gray-900 rounded-xl p-4">
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
        </div>
      </div>
    </div>
  </div>
</template>
