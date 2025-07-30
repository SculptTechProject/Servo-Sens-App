<template>
  <article
    class="group relative rounded-xl border border-gray-800 bg-gray-950/40 p-6 transition hover:-translate-y-0.5 hover:border-emerald-500/60 hover:bg-gray-900/60"
  >
    <div
      class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20 group-hover:text-emerald-300 group-hover:ring-emerald-500/40 transition"
    >
      <Icon :name="icon" class="h-6 w-6" aria-hidden="true" />
    </div>

    <h4 class="text-xl font-semibold tracking-tight">
      {{ title }}
    </h4>

    <p class="mt-2 text-gray-300 leading-relaxed">
      {{ desc }}
    </p>

    <!-- ozdobny akcent na dole karty -->
    <span
      class="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-600/40 to-transparent"
      aria-hidden="true"
    />
  </article>
</template>

<script setup lang="ts">
defineProps<{
  icon: string;
  title: string;
  desc: string;
}>();
</script>
