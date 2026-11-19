<script setup lang="ts">
const props = defineProps<{ category?: string; variant?: 'card' | 'large'; imageUrl?: string }>()
const failed = ref(false)
const fallbackImage = computed(() => {
  const value = (props.category || '').toLowerCase()
  if (value.includes('wash')) return '/images/products/washing-machine.webp'
  if (value.includes('cool') || value.includes('fridge') || value.includes('refrigerator')) return '/images/products/refrigerator.webp'
  if (value.includes('cooker') || value.includes('oven')) return '/images/products/gas-cooker.webp'
  if (value.includes('air condition') || value.includes('cooling')) return '/images/products/air-conditioner.webp'
  if (value.includes('tv') || value.includes('television')) return '/images/products/television.webp'
  if (value.includes('coffee')) return '/images/products/espresso-machine.webp'
  if (value.includes('vacuum')) return '/images/products/vacuum-cleaner.webp'
  if (value.includes('microwave')) return '/images/products/microwave.webp'
  return '/images/products/blender.webp'
})
const image = computed(() => failed.value ? fallbackImage.value : props.imageUrl || fallbackImage.value)
watch(() => props.imageUrl, () => { failed.value = false })
function useFallback() {
  if (image.value !== fallbackImage.value) failed.value = true
}
</script>

<template>
  <div class="product-art product-art-photo" :class="`art-${variant || 'card'}`" aria-hidden="true">
    <img :src="image" alt="" loading="lazy" decoding="async" @error="useFallback">
    <span class="art-glow" />
  </div>
</template>
