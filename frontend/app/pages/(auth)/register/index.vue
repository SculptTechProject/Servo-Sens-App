<script setup lang="ts">
import { useAuthStore } from "~/_stores/auth";

const auth = useAuthStore();
const name = ref("");
const email = ref("");
const password = ref("");
const password2 = ref("");
const err = ref("");
const pending = ref(false);

async function submit() {
  err.value = "";
  if (password.value !== password2.value) {
    err.value = "Hasła się różnią";
    return;
  }
  if (password.value.length < 5) {
    err.value = "Hasło musi mieć min. 5 znaków";
    return;
  }
  pending.value = true;
  try {
    await auth.register({
      name: name.value,
      email: email.value,
      password: password.value,
    });
    await navigateTo("/");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
    // spróbuj wyciągnąć komunikat z DRF
    const msg = e?.data
      ? Object.values(e.data).flat().join(" ")
      : "Błąd rejestracji";
    err.value = msg || "Błąd rejestracji";
  } finally {
    pending.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col text-gray-200 bg-gray-950">
    <!-- HEADER -->
    <AppHeader />

    <!-- MAIN -->
    <main class="flex-grow container mx-auto py-24">
      <div class="max-w-md mx-auto bg-gray-900 rounded-xl p-8 shadow">
        <h2
          class="text-3xl font-bold mb-6 text-center flex items-center justify-center gap-2"
        >
          <Icon name="i-heroicons-user-plus" class="w-7 h-7 text-emerald-500" />
          Rejestracja
        </h2>

        <form class="grid gap-4" @submit.prevent="submit">
          <input
            v-model="name"
            placeholder="Imię / nazwa"
            class="px-4 py-3 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
          <input
            v-model="email"
            type="email"
            placeholder="Email"
            class="px-4 py-3 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
          <input
            v-model="password"
            type="password"
            placeholder="Hasło (min. 5 znaków)"
            class="px-4 py-3 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >
          <input
            v-model="password2"
            type="password"
            placeholder="Powtórz hasło"
            class="px-4 py-3 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          >

          <button
            type="submit"
            :disabled="pending"
            class="px-4 py-3 rounded bg-emerald-600 hover:bg-emerald-500 shadow font-medium disabled:opacity-50"
          >
            {{ pending ? "Rejestruję…" : "Zarejestruj" }}
          </button>
          <p v-if="err" class="text-red-400 text-sm">{{ err }}</p>
        </form>

        <p class="text-sm text-gray-400 mt-4 text-center">
          Masz już konto?
          <NuxtLink to="/login" class="text-emerald-400 hover:underline"
            >Zaloguj się</NuxtLink
          >.
        </p>
      </div>
    </main>

    <!-- FOOTER -->
    <footer class="py-6 bg-gray-900 text-center text-gray-400">
      MIT License © {{ new Date().getFullYear() }} SculptTechProject
    </footer>
  </div>
</template>
