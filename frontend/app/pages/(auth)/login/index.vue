<script setup lang="ts">
import { useAuthStore } from "~/_stores/auth";
const auth = useAuthStore();
const email = ref("");
const password = ref("");
const err = ref("");
async function submit() {
  err.value = "";
  try {
    await auth.login(email.value, password.value);
    await navigateTo("/dashboard");
  } catch {
    err.value = "Błędny email lub hasło";
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col text-gray-200 bg-gray-950">
    <AppHeader />
    <main class="flex-grow container mx-auto py-24">
      <div class="max-w-md mx-auto bg-gray-900 rounded-xl p-8 shadow">
        <h2 class="text-3xl font-bold mb-6 text-center">Zaloguj się</h2>
        <form class="grid gap-4" @submit.prevent="submit">
          <input
            v-model="email"
            type="email"
            placeholder="Email"
            class="px-4 py-3 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
          <input
            v-model="password"
            type="password"
            placeholder="Hasło"
            class="px-4 py-3 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
          <button
            type="submit"
            class="px-4 py-3 rounded bg-emerald-600 hover:bg-emerald-500 shadow font-medium"
          >
            Zaloguj
          </button>
          <p v-if="err" class="text-red-400 text-sm">{{ err }}</p>
        </form>
      </div>
    </main>
    <footer class="py-6 bg-gray-900 text-center text-gray-400">
      MIT License © {{ new Date().getFullYear() }} SculptTechProject
    </footer>
  </div>
</template>
