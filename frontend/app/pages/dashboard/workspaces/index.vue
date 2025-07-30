<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { useApi } from "~/_composables/useApi";

const api = useApi();
const router = useRouter();

type Ws = { id: number; name: string; machines_count: number };
const items = ref<Ws[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// form
const name = ref("");
const creating = ref(false);
const createError = ref<string | null>(null);

// quickstart
const creatingDemo = ref(false);

onMounted(load);
async function load() {
  loading.value = true;
  try {
    items.value = await api("/api/workspaces/");
  } catch (e: any) {
    error.value = e?.data?.detail || "Błąd pobierania";
    if (e?.status === 401) router.push("/login");
  } finally {
    loading.value = false;
  }
}

async function createWs() {
  createError.value = null;
  if (name.value.trim().length < 2) {
    createError.value = "Podaj nazwę (min 2 znaki).";
    return;
  }
  creating.value = true;
  try {
    const ws = await api("/api/workspaces/", {
      method: "POST",
      body: { name: name.value.trim() },
    });
    items.value.unshift({ ...ws, machines_count: 0 });
    name.value = "";
  } catch (e: any) {
    createError.value = e?.data?.detail || "Nie udało się utworzyć.";
  } finally {
    creating.value = false;
  }
}

async function quickstart() {
  creatingDemo.value = true;
  try {
    const ws = await api("/api/workspaces/quickstart/", { method: "POST" });
    // od razu przejdź do detalu
    router.push({ name: "dashboard-workspaces-id", params: { id: ws.id } });
  } finally {
    creatingDemo.value = false;
  }
}

async function seedWs(id: number) {
  try {
    await api(`/api/workspaces/${id}/seed/`, { method: "POST" });
    router.push({ name: "dashboard-workspaces-id", params: { id } });
  } catch {
    // cicho – zostaniemy na liście
  }
}

function openWs(id: number) {
  router.push({ name: "dashboard-workspaces-id", params: { id } });
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-950 text-gray-200">
    <AppHeader />
    <main class="container mx-auto px-4 py-10">
      <h2 class="text-3xl font-bold mb-6">Twoje Workspaces</h2>

      <!-- Formularz -->
      <form
        class="bg-gray-900 rounded-xl p-4 mb-6 shadow"
        @submit.prevent="createWs"
      >
        <div class="flex flex-col sm:flex-row gap-3 items-stretch">
          <input
            v-model="name"
            type="text"
            placeholder="Nazwa workspace’u"
            class="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
          <button
            :disabled="creating"
            class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50"
          >
            {{ creating ? "Tworzę…" : "Utwórz" }}
          </button>
        </div>
        <p v-if="createError" class="text-rose-400 mt-2">{{ createError }}</p>
      </form>

      <!-- Lista / empty state -->
      <div v-if="loading" class="text-gray-400">Ładuję…</div>
      <div v-else-if="error" class="text-rose-400">{{ error }}</div>

      <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <!-- karty -->
        <div
          v-for="w in items"
          :key="w.id"
          class="bg-gray-900 rounded-xl p-5 shadow"
        >
          <h3 class="text-xl font-semibold">{{ w.name }}</h3>
          <p class="text-gray-400 mt-1">Maszyny: {{ w.machines_count }}</p>
          <div class="mt-4 flex gap-3">
            <button
              class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500"
              @click="openWs(w.id)"
            >
              Pracuj
            </button>
            <button
            class="px-4 py-2 rounded border border-emerald-500 text-emerald-400 hover:bg-emerald-600 hover:text-white"
            title="Dodaj przykładowe sensory i przejdź do widoku"
            @click="seedWs(w.id)"
            >
              Seed demo
            </button>
          </div>
        </div>

        <!-- empty -->
        <div
          v-if="items.length === 0"
          class="col-span-full bg-gray-900 rounded-xl p-6 shadow text-center"
        >
          <p class="text-gray-300 mb-3">
            Brak workspace’ów. Możesz utworzyć własny albo skorzystać z demo.
          </p>
          <button
            class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50"
            :disabled="creatingDemo"
            @click="quickstart"
          >
            {{ creatingDemo ? "Tworzę…" : "Utwórz demo workspace" }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
