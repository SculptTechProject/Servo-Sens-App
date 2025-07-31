<script setup lang="ts">
import { useAuthStore } from "~/_stores/auth";
import { useApi } from "~/_composables/useApi";

const auth = useAuthStore();
const api = useApi();
const router = useRouter();

const loadingAuth = ref(true);
const loadingWs = ref(true);
type Ws = { id:number; name:string; machines_count:number; sensors_count:number };
const workspaces = ref<Ws[]>([]);
const showCreateModal = ref(false);
const newWsName = ref("Nowy Workspace");
const lastWsId = ref<number | null>(null);

// prosty filtr + ref do inputa (dla skrótu '/')
const q = ref("");
const searchRef = ref<HTMLInputElement|null>(null);
const filtered = computed(() => {
  const s = q.value.trim().toLowerCase();
  if (!s) return workspaces.value;
  return workspaces.value.filter(w => w.name.toLowerCase().includes(s));
});

const isAuthed = computed(() => {
  if (!import.meta.client) return false;
  return !!localStorage.getItem("token") && !!auth.user;
});

onMounted(async () => {
  // auth bootstrap
  if (import.meta.client) {
    const t = localStorage.getItem("token");
    if (t && !auth.user) {
      try { await auth.fetchMe(); } catch { localStorage.removeItem("token"); }
    }
    lastWsId.value = Number(localStorage.getItem("last_ws_id") || "") || null;
  }
  loadingAuth.value = false;

  if (isAuthed.value) await loadWorkspaces();

  window.addEventListener("keydown", handleShortcut);
});
onBeforeUnmount(() => window.removeEventListener("keydown", handleShortcut));

async function loadWorkspaces() {
  loadingWs.value = true;
  try {
    workspaces.value = await api("/api/workspaces/");
  } finally {
    loadingWs.value = false;
  }
}

async function quickstart() {
  const res = await api<{ ok:boolean } & Ws>("/api/workspaces/quickstart/", { method: "POST" });
  const wsId = res.id;
  if (import.meta.client) localStorage.setItem("last_ws_id", String(wsId));
  router.push(`/dashboard/workspaces/${wsId}`); // ✅ poprawiona ścieżka
}

async function createWs() {
  const ws = await api<Ws>("/api/workspaces/", { method:"POST", body:{ name: newWsName.value || "Nowy Workspace" }});
  showCreateModal.value = false;
  await loadWorkspaces();
}

function goLogin(){ navigateTo("/login"); }
function goRegister(){ navigateTo("/register"); }
function goWorkspaces(){ router.push("/dashboard/workspaces"); }
function goContinue(){
  if (lastWsId.value) router.push(`/dashboard/workspaces/${lastWsId.value}`);
}
function openWs(id:number){
  if (import.meta.client) localStorage.setItem("last_ws_id", String(id));
  router.push(`/dashboard/workspaces/${id}`); // ✅
}

/* ---------- Skróty klawiszowe ---------- */
function isTyping(el: EventTarget | null) {
  const t = el as HTMLElement | null;
  return !!t?.closest("input, textarea, select, [contenteditable='true']");
}

// prosty stan do 'g + litera'
const chord = reactive({ g:false, ts:0 });

function handleShortcut(e: KeyboardEvent) {
  const key = e.key.toLowerCase();
  if (isTyping(e.target)) return;        // nie działaj w inputach
  if (e.metaKey || e.ctrlKey || e.altKey) return;

  const now = Date.now();
  if (now - chord.ts > 900) chord.g = false; // timeout 0.9s

  // '?' – pokaż/ukryj okno pomocy
  if (key === "?") { e.preventDefault(); showHelp.value = !showHelp.value; return; }

  // '/' – fokus do wyszukiwarki
  if (key === "/") {
    e.preventDefault();
    searchRef.value?.focus();
    return;
  }

  // cyfry 1..9 – otwórz n-ty workspace z listy
  if (/^[1-9]$/.test(key)) {
    const idx = Number(key) - 1;
    const list = filtered.value;
    if (idx < list.length) {
      openWs(list[idx].id);
      return;
    }
  }

  // sekwencja 'g' + 'x'
  if (key === "g") {
    chord.g = true; chord.ts = now; return;
  }
  if (chord.g) {
    chord.g = false; chord.ts = now;
    if (key === "w") return goWorkspaces();
    if (key === "n") { showCreateModal.value = true; return; }   // nowy WS
    if (key === "q") return quickstart();                        // quickstart
    if (key === "l") return goContinue();                        // last
  }
}

// pomoc (lista skrótów)
const showHelp = ref(false);
</script>

<template>
  <div class="min-h-screen flex flex-col text-gray-200 bg-gray-950">
    <AppHeader />

    <main class="flex-grow">
      <!-- ===== HERO / CTA ===== -->
      <section class="container mx-auto pt-14 pb-4 text-center">
        <h2 class="text-4xl md:text-5xl font-bold mb-2">
          Twój <span class="text-emerald-500">Dashboard</span>
        </h2>
        <p class="text-gray-300">
          Szybki start, ostatnie projekty i skróty
          <kbd class="px-1 rounded bg-gray-800">g</kbd>
          <kbd class="px-1 rounded bg-gray-800">w</kbd>,
          <kbd class="px-1 rounded bg-gray-800">g</kbd>
          <kbd class="px-1 rounded bg-gray-800">q</kbd>,
          <kbd class="px-1 rounded bg-gray-800">?</kbd>.
        </p>

        <!-- search -->
        <div class="mt-5 flex justify-center">
          <input
            ref="searchRef"
            v-model="q"
            type="text"
            placeholder="Szukaj workspace’u… ( / )"
            class="w-full max-w-xl px-3 py-2 rounded bg-gray-900 border border-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
        </div>
      </section>

      <section class="container mx-auto pb-12">
        <!-- Ładowanie auth -->
        <div v-if="loadingAuth" class="text-center text-gray-400">Ładuję dane…</div>

        <!-- Niezalogowany -->
        <div v-else-if="!isAuthed" class="text-center">
          <h3 class="text-3xl font-semibold mb-3">Proszę się zalogować</h3>
          <p class="text-gray-300 mb-6">Ten widok jest dostępny tylko dla zalogowanych.</p>
          <div class="flex justify-center gap-3">
            <button class="px-5 py-2 rounded bg-emerald-600 hover:bg-emerald-500 shadow" @click="goLogin">Logowanie</button>
            <button class="px-5 py-2 rounded border border-emerald-500 text-emerald-400 hover:bg-emerald-600 hover:text-white" @click="goRegister">Rejestracja</button>
          </div>
        </div>

        <!-- Zalogowany -->
        <div v-else class="space-y-8">
          <!-- Quick actions -->
          <div class="flex flex-wrap justify-center gap-3">
            <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 shadow inline-flex items-center gap-2" @click="goWorkspaces">
              <Icon name="i-heroicons-folder" class="w-5 h-5" /> Workspaces
            </button>

            <button v-if="lastWsId" class="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700 inline-flex items-center gap-2" @click="goContinue">
              <Icon name="i-heroicons-play" class="w-5 h-5" /> Kontynuuj ostatni
            </button>

            <button class="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700 inline-flex items-center gap-2" @click="showCreateModal = true">
              <Icon name="i-heroicons-plus" class="w-5 h-5" /> Utwórz workspace
            </button>

            <button
              v-if="!loadingWs && workspaces.length === 0"
              class="px-4 py-2 rounded border border-emerald-500 text-emerald-400 hover:bg-emerald-600 hover:text-white inline-flex items-center gap-2"
              @click="quickstart"
            >
              <Icon name="i-heroicons-bolt" class="w-5 h-5" /> Szybki start (demo)
            </button>
          </div>

          <!-- Lista WS -->
          <div class="mt-6">
            <h3 class="text-xl font-semibold mb-3">Twoje workspaces</h3>

            <!-- Skeleton -->
            <div v-if="loadingWs" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div v-for="i in 6" :key="i" class="rounded-xl bg-gray-900 border border-gray-800 p-5">
                <div class="h-5 w-40 bg-gray-800 rounded mb-3"/>
                <div class="h-4 w-24 bg-gray-800 rounded"/>
              </div>
            </div>

            <div v-else-if="filtered.length === 0" class="text-gray-400">
              Brak wyników. Spróbuj innej frazy lub utwórz workspace.
            </div>

            <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div v-for="(ws, idx) in filtered" :key="ws.id" class="rounded-xl bg-gray-900 border border-gray-800 p-5 shadow">
                <div class="flex items-center justify-between">
                  <h4 class="font-semibold truncate">
                    <span class="text-gray-500 mr-1">{{ idx+1 }}.</span> {{ ws.name }}
                  </h4>
                  <!-- ✅ poprawiona ścieżka -->
                  <NuxtLink :to="`/dashboard/workspaces/${ws.id}`" class="text-emerald-400 hover:underline">Otwórz</NuxtLink>
                </div>
                <div class="mt-2 text-sm text-gray-400">
                  {{ ws.machines_count }} maszyn • {{ ws.sensors_count }} sensorów
                </div>
                <div class="mt-3">
                  <button class="text-xs text-emerald-400 hover:underline" @click="openWs(ws.id)">
                    Skrót: {{ idx < 9 ? idx+1 : '-' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="py-6 bg-gray-900 text-center text-gray-400">
      MIT License © {{ new Date().getFullYear() }} SculptTechProject
    </footer>

    <!-- Create WS modal -->
    <transition name="fade">
      <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 grid place-items-center z-50">
        <div class="w-full max-w-md rounded-2xl bg-gray-900 border border-gray-800 p-4">
          <h3 class="font-semibold mb-3">Utwórz workspace</h3>
          <input v-model="newWsName" class="w-full rounded bg-gray-800 p-2 outline-none" placeholder="Nazwa" >
          <div class="mt-4 flex justify-end gap-2">
            <button class="px-3 py-2 rounded bg-gray-800 hover:bg-gray-700" @click="showCreateModal=false">Anuluj</button>
            <button class="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500" @click="createWs">Utwórz</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Modal: skróty -->
    <transition name="fade">
      <div v-if="showHelp" class="fixed inset-0 bg-black/50 grid place-items-center z-50">
        <div class="w-full max-w-lg rounded-2xl bg-gray-900 border border-gray-800 p-5">
          <h3 class="font-semibold mb-3">Skróty klawiszowe</h3>
          <ul class="text-sm space-y-1 text-gray-300">
            <li><kbd class="px-1 rounded bg-gray-800">g</kbd> <kbd class="px-1 rounded bg-gray-800">w</kbd> — Workspaces</li>
            <li><kbd class="px-1 rounded bg-gray-800">g</kbd> <kbd class="px-1 rounded bg-gray-800">n</kbd> — Nowy workspace</li>
            <li><kbd class="px-1 rounded bg-gray-800">g</kbd> <kbd class="px-1 rounded bg-gray-800">q</kbd> — Szybki start</li>
            <li><kbd class="px-1 rounded bg-gray-800">g</kbd> <kbd class="px-1 rounded bg-gray-800">l</kbd> — Kontynuuj ostatni</li>
            <li><kbd class="px-1 rounded bg-gray-800">/</kbd> — Szukaj</li>
            <li><kbd class="px-1 rounded bg-gray-800">1..9</kbd> — Otwórz n-ty workspace z listy</li>
            <li><kbd class="px-1 rounded bg-gray-800">?</kbd> — Pokaż/ukryj tę pomoc</li>
          </ul>
          <div class="mt-4 text-right">
            <button class="px-3 py-2 rounded bg-gray-800 hover:bg-gray-700" @click="showHelp=false">Zamknij</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,.fade-leave-active{transition:opacity .15s;}
.fade-enter-from,.fade-leave-to{opacity:0;}
</style>
