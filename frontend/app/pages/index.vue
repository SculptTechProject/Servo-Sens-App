<template>
  <div class="min-h-screen flex flex-col text-gray-200 bg-gray-950">
    <!-- ===== HEADER ===== -->
    <header class="py-4 bg-gray-900">
  <div class="container mx-auto flex items-center justify-between">
    <h1 class="text-2xl font-semibold flex items-center gap-2">
      <Icon name="i-heroicons-cpu-chip" class="w-8 h-8 text-emerald-500" />
      ServoSenseApp
    </h1>

    <nav class="flex items-center gap-6">
      <NuxtLink
        to="#features"
        class="inline-flex items-center leading-none hover:text-emerald-400"
      >
        Funkcje
      </NuxtLink>

      <NuxtLink
        to="#stack"
        class="inline-flex items-center leading-none hover:text-emerald-400"
      >
        Tech Stack
      </NuxtLink>
      <a
        href="https://github.com/SculptTechProject/Servo-Sens-App"
        target="_blank"
        class="inline-flex items-center px-4 py-2 rounded bg-emerald-600 shadow hover:bg-emerald-500"
      >
        GitHub
      </a>
    </nav>
  </div>
</header>


    <!-- ===== HERO ===== -->
    <main class="flex-grow">
      <section class="container mx-auto py-24 text-center">
        <h2 class="text-4xl md:text-5xl font-bold mb-4">
          Monitoruj swoje dane <em class="text-emerald-500"
            >w czasie rzeczywistym</em
          >
        </h2>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          ServoSenseApp to platforma klasy przemysłowej do procesowania,
          wizualizacji i alertowania danych z sensorów.
        </p>

        <div class="mt-10 flex flex-wrap justify-center gap-4">
          <a
            href="#features"
            class="px-6 py-3 rounded bg-emerald-600 shadow hover:bg-emerald-500"
            >Zobacz funkcje</a
          >
          <a
            href="https://github.com/SculptTechProject/Servo-Sens-App"
            target="_blank"
            class="px-6 py-3 rounded border border-emerald-500 text-emerald-400 hover:bg-emerald-600 hover:text-white"
            >Repozytorium</a
          >
        </div>
      </section>

      <!-- ===== FEATURES ===== -->
      <section id="features" class="bg-gray-900 py-20">
        <div class="container mx-auto">
          <h3 class="text-3xl font-semibold text-center mb-12">Funkcje</h3>

          <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              v-for="f in features"
              :key="f.title"
              :icon="f.icon"
              :title="f.title"
              :desc="f.desc"
            />
          </div>
        </div>
      </section>

      <!-- ===== TECH STACK ===== -->
      <section id="stack" class="container mx-auto py-20">
        <h3 class="text-3xl font-semibold text-center mb-12">Tech Stack</h3>

        <div class="flex flex-wrap justify-center gap-4 text-lg">
          <Tag v-for="t in stack" :key="t">{{ t }}</Tag>
        </div>
      </section>
    </main>

    <!-- ===== FOOTER ===== -->
    <footer class="py-6 bg-gray-900 text-center text-gray-400">
      MIT License © {{ new Date().getFullYear() }} SculptTechProject
    </footer>
  </div>
</template>

<script setup lang="ts">
const features = [
  {
    icon: "i-heroicons-chart-bar",
    title: "Dashboardy live",
    desc: "Wykresy i widżety aktualizują się co sekundę.",
  },
  {
    icon: "i-heroicons-bell-alert",
    title: "Alerty progowe",
    desc: "Ustaw temperaturę/drgania i dostajesz powiadomienie.",
  },
  {
    icon: "i-heroicons-database",
    title: "API sensorów",
    desc: "REST CRUD dla sensorów i odczytów.",
  },
  {
    icon: "i-heroicons-shield-check",
    title: "Auth backend",
    desc: "Gotowe JWT i uprawnienia rolowe.",
  },
  {
    icon: "i-heroicons-cloud",
    title: "Docker deploy",
    desc: "Jedno `docker compose up` i lecisz.",
  },
  {
    icon: "i-heroicons-presentation-chart-line",
    title: "Analityka",
    desc: "Spark & Pandas do batch + streaming.",
  },
];

const stack = [
  "Django",
  "DRF",
  "Nuxt 3",
  "Vue 3",
  "PostgreSQL",
  "Docker Compose",
];

definePageMeta({
  title: "ServoSenseApp – Landing",
  description:
    "Landing page projektu Servo‑Sens‑App – platforma do monitoringu danych sensorowych w czasie rzeczywistym",
});
</script>
