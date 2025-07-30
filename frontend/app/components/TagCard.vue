<template>
  <span
    class="inline-flex items-center rounded-full border border-emerald-700/60 bg-emerald-900/20 px-3 py-1 text-sm font-medium text-emerald-300 hover:border-emerald-500/70 hover:text-emerald-200 transition select-none"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
// Bez propsów – prosta „pigułka” na tekst ze slota.
// Jak będziesz chciał warianty/rozmiary, dorzucimy propsy `variant` i `size`.
</script>
