<script setup lang="ts">
import { useApi } from "~/_composables/useApi";

const api = useApi();
const router = useRouter();

type Ws = { id: number; name: string; machines_count: number };
const items = ref<Ws[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    items.value = await api("/api/workspaces/"); // Authorization doda Twój useApi
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
    error.value = e?.data?.detail || "Błąd pobierania";
    if (e?.status === 401) router.push("/login");
  } finally {
    loading.value = false;
  }
});

function openWs(id: number) {
  // nazwa trasy z pliku pages/dashboard/workspaces/[id].vue
  router.push({ name: "dashboard-workspaces-id", params: { id } });
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-950 text-gray-200">
    <AppHeader />
    <main class="container mx-auto px-4 py-10">
      <h2 class="text-3xl font-bold mb-6">Twoje Workspaces</h2>

      <div v-if="loading" class="text-gray-400">Ładuję…</div>
      <div v-else-if="error" class="text-rose-400">{{ error }}</div>

      <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="w in items"
          :key="w.id"
          class="bg-gray-900 rounded-xl p-5 shadow"
        >
          <h3 class="text-xl font-semibold">{{ w.name }}</h3>
          <p class="text-gray-400 mt-1">Maszyny: {{ w.machines_count }}</p>
          <button
            class="mt-4 px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
            @click="openWs(w.id)"
          >
            Pracuj na tym workspace
          </button>
        </div>

        <!-- Pusta lista -->
        <div v-if="items.length === 0" class="col-span-full text-gray-400">
          Brak workspace’ów. Utwórz w backendzie/seedzie.
        </div>
      </div>
    </main>
  </div>
</template>
