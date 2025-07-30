<script setup lang="ts">
import { useAuthStore } from "~/_stores/auth";
const auth = useAuthStore();
const router = useRouter(); 

const loading = ref(true);
const isAuthed = computed(() => {
  if (!import.meta.client) return false;
  return !!localStorage.getItem("token") && !!auth.user;
});

onMounted(async () => {
  if (import.meta.client) {
    const t = localStorage.getItem("token");
    if (t && !auth.user) {
      try {
        await auth.fetchMe();
      } catch {
        localStorage.removeItem("token");
      }
    }
  }
  loading.value = false;
});

function goLogin() {
  navigateTo("/login");
}
function goRegister() {
  navigateTo("/register");
}

function goWorkspaces() {
  router.push('/dashboard/workspaces');
}
</script>

<template>
  <div class="min-h-screen flex flex-col text-gray-200 bg-gray-950">
    <AppHeader />

    <main class="flex-grow container mx-auto py-12">
      <!-- Ładowanie (krótko, gdy sprawdzamy /me) -->
      <div v-if="loading" class="text-center text-gray-400">Ładuję dane…</div>

      <!-- Niezalogowany: prosimy o logowanie -->
      <section v-else-if="!isAuthed" class="text-center">
        <h2 class="text-3xl md:text-4xl font-bold mb-3">
          Proszę się zalogować
        </h2>
        <p class="text-gray-300 mb-6">
          Ten widok jest dostępny tylko dla zalogowanych użytkowników.
        </p>
        <div class="flex justify-center gap-3">
          <button
            class="px-5 py-2 rounded bg-emerald-600 hover:bg-emerald-500 shadow"
            @click="goLogin"
          >
            Przejdź do logowania
          </button>
          <button
            class="px-5 py-2 rounded border border-emerald-500 text-emerald-400 hover:bg-emerald-600 hover:text-white"
            @click="goRegister"
          >
            Zarejestruj się
          </button>
        </div>
      </section>

      <!-- Zalogowany: normalny dashboard -->
      <section v-else class="text-center mb-10">
        <h2 class="text-4xl md:text-5xl font-bold">
          Witaj, <em class="text-emerald-500">{{ auth.user?.name }}</em>
        </h2>
        <p class="text-gray-300 mt-3">Masz dostęp do panelu i API.</p>

        <div class="mt-6 flex flex-wrap justify-center gap-3">
          <!-- NEW: przejście do /workspaces -->
          <button
            class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 shadow inline-flex items-center gap-2"
            @click="goWorkspaces"
          >
            <Icon name="i-heroicons-folder" class="w-5 h-5" />
            Workspaces
          </button>

          <button
            class="px-4 py-2 rounded border border-emerald-500 text-emerald-400 hover:bg-emerald-600 hover:text-white"
            @click="auth.logout()"
          >
            Wyloguj
          </button>
        </div>
      </section>

      <section v-if="isAuthed" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div class="bg-gray-900 rounded-xl p-6 shadow">
          <h3 class="text-xl font-semibold mb-2 flex items-center gap-2">
            <Icon name="i-heroicons-chart-bar" class="text-emerald-500" />
            Odczyty na żywo
          </h3>
          <p class="text-gray-400">Podłączę wykres po API.</p>
        </div>
        <div class="bg-gray-900 rounded-xl p-6 shadow">
          <h3 class="text-xl font-semibold mb-2 flex items-center gap-2">
            <Icon name="i-heroicons-bell-alert" class="text-emerald-500" />
            Alerty
          </h3>
          <p class="text-gray-400">Konfiguracja progów i powiadomień.</p>
        </div>
        <div class="bg-gray-900 rounded-xl p-6 shadow">
          <h3 class="text-xl font-semibold mb-2 flex items-center gap-2">
            <Icon name="i-heroicons-circle-stack" class="text-emerald-500" />
            Twoje konto
          </h3>
          <p class="text-gray-400"><b>Email:</b> {{ auth.user?.email }}</p>
        </div>
      </section>
    </main>

    <footer class="py-6 bg-gray-900 text-center text-gray-400">
      MIT License © {{ new Date().getFullYear() }} SculptTechProject
    </footer>
  </div>
</template>
