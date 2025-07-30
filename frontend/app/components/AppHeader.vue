<template>
  <header class="py-4 bg-gray-900 text-gray-200">
    <div class="container mx-auto flex items-center justify-between">
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <Icon name="i-heroicons-cpu-chip" class="w-8 h-8 text-emerald-500" />
        <NuxtLink to="/" class="hover:text-emerald-400 transition-all">ServoSenseApp</NuxtLink>
      </h1>
      <nav class="flex items-center gap-6">
        <NuxtLink to="/dashboard" class="hover:text-emerald-400">Dashboard</NuxtLink>
        <NuxtLink to="/register" class="hover:text-emerald-400"
          >Rejestracja</NuxtLink
        >
        <NuxtLink to="/login" class="hover:text-emerald-400"
          >Logowanie</NuxtLink
        >
        <a
          href="https://github.com/SculptTechProject/Servo-Sens-App"
          target="_blank"
          class="inline-flex items-center px-4 py-2 rounded bg-emerald-600 shadow hover:bg-emerald-500"
          >GitHub</a
        >
      </nav>
    </div>
  </header>
</template>
