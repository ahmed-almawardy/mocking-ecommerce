<script setup lang="ts">
const props = withDefaults(defineProps<{ name: string; size?: number }>(), { size: 20 })

const iconPaths: Record<string, string[]> = {
  dashboard: [
    'M3 3h7v7H3z', 'M14 3h7v4h-7z', 'M14 10h7v11h-7z', 'M3 13h7v8H3z',
  ],
  products: [
    'm12 3 9 5-9 5-9-5 9-5Z', 'm3 8 9 5 9-5', 'M12 13v8', 'm7.5 5.5 9 5',
  ],
  offers: [
    'm20.5 13.5-7 7a2 2 0 0 1-2.8 0l-8.2-8.2V3h9.3l8.7 8.7a1.3 1.3 0 0 1 0 1.8Z',
    'M7.5 7.5h.01',
  ],
  orders: [
    'M6 3h12l2 3v15H4V6l2-3Z', 'M8 3v5h8V3', 'M8 12h8', 'M8 16h6',
  ],
  customers: [
    'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2',
    'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z',
    'M22 21v-2a4 4 0 0 0-3-3.87', 'M16 3.13a4 4 0 0 1 0 7.75',
  ],
  payments: [
    'M3 6h18v13H3z', 'M3 10h18', 'M7 15h4', 'M17 15h.01',
  ],
  revenue: [
    'M3 17 9 11l4 4 8-9', 'M15 6h6v6', 'M3 21h18',
  ],
  search: [
    'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z', 'm21 21-4.3-4.3',
  ],
}

const paths = computed(() => iconPaths[props.name] || iconPaths.dashboard)
</script>

<template>
  <svg class="admin-icon" :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
    <path v-for="(path, index) in paths" :key="index" :d="path" />
  </svg>
</template>
