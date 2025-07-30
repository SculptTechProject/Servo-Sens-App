<script setup lang="ts">
import { useRoute } from "vue-router";

const route = useRoute();
const open = ref(false);

function linkClass(path: string) {
  const active = route.path === path;
  return [
    "inline-flex items-center leading-none transition-colors",
    active ? "text-emerald-400" : "hover:text-emerald-400",
  ];
}
watch(
  () => route.fullPath,
  () => (open.value = false)
);
function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") open.value = false;
}
onMounted(() => window.addEventListener("keydown", onKeydown));
onBeforeUnmount(() => window.removeEventListener("keydown", onKeydown));
</script>

<template>
  <header
    class="sticky top-0 z-40 py-4 bg-gray-900 text-gray-200 border-b border-gray-800"
  >
    <div class="container mx-auto px-4 flex items-center justify-between">
      <!-- Logo -->
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <Icon name="i-heroicons-cpu-chip" class="w-8 h-8 text-emerald-500" />
        <NuxtLink to="/" class="hover:text-emerald-400 transition-colors"
          >ServoSenseApp</NuxtLink
        >
      </h1>

      <!-- Desktop nav -->
      <nav class="hidden md:flex items-center gap-6">
        <NuxtLink :class="linkClass('/dashboard')" to="/dashboard"
          >Dashboard</NuxtLink
        >
        <NuxtLink :class="linkClass('/register')" to="/register"
          >Rejestracja</NuxtLink
        >
        <NuxtLink :class="linkClass('/login')" to="/login">Logowanie</NuxtLink>
        <a
          href="https://github.com/SculptTechProject/Servo-Sens-App"
          target="_blank"
          class="inline-flex items-center px-4 py-2 rounded bg-emerald-600 shadow hover:bg-emerald-500"
        >
          GitHub
        </a>
      </nav>

      <!-- Burger -->
      <button
        type="button"
        class="md:hidden inline-flex items-center justify-center rounded-lg p-2 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        aria-label="Przełącz menu"
        aria-controls="mobile-menu"
        :aria-expanded="open ? 'true' : 'false'"
        @click="open = !open"
      >
        <Icon v-if="!open" name="i-heroicons-bars-3" class="w-7 h-7" />
        <Icon v-else name="i-heroicons-x-mark" class="w-7 h-7" />
      </button>
    </div>

    <!-- Mobile off-canvas -->
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-40 md:hidden"
        aria-modal="true"
        role="dialog"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/60 transition-all"
          @click="open = false"
        />

        <!-- Panel -->
        <Transition name="slide">
          <div
            v-if="open"
            id="mobile-menu"
            class="absolute right-0 top-0 h-full w-72 max-w-[85%] bg-gray-900 border-l border-gray-800 shadow-xl p-6 flex flex-col gap-4"
            @click.self="open = false"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-xl font-semibold flex items-center gap-2">
                <Icon
                  name="i-heroicons-cpu-chip"
                  class="w-6 h-6 text-emerald-500"
                />
                ServoSenseApp
              </span>
              <button
                class="rounded-lg p-2 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-600"
                aria-label="Zamknij menu"
                @click="open = false"
              >
                <Icon name="i-heroicons-x-mark" class="w-6 h-6" />
              </button>
            </div>

            <NuxtLink
              :class="linkClass('/dashboard')"
              to="/dashboard"
              @click="open = false"
            >
              Dashboard
            </NuxtLink>
            <NuxtLink
              :class="linkClass('/register')"
              to="/register"
              @click="open = false"
            >
              Rejestracja
            </NuxtLink>
            <NuxtLink
              :class="linkClass('/login')"
              to="/login"
              @click="open = false"
            >
              Logowanie
            </NuxtLink>

            <a
              href="https://github.com/SculptTechProject/Servo-Sens-App"
              target="_blank"
              class="mt-2 inline-flex items-center justify-center px-4 py-2 rounded bg-emerald-600 shadow hover:bg-emerald-500"
              @click="open = false"
            >
              GitHub
            </a>

            <div
              class="mt-auto pt-4 text-xs text-gray-400 border-t border-gray-800"
            >
              MIT License © {{ new Date().getFullYear() }} SculptTechProject
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
