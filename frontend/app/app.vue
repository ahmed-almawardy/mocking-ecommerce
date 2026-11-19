<script setup lang="ts">
const route = useRoute()
const isAdminRoute = computed(() => route.path === '/admin' || route.path.startsWith('/admin/'))
const { locale, isRtl } = useLocale()
useHead(() => ({
  htmlAttrs: {
    lang: isAdminRoute.value ? 'en' : locale.value,
    dir: isAdminRoute.value ? 'ltr' : isRtl.value ? 'rtl' : 'ltr',
  },
}))
</script>

<template>
  <div v-if="isAdminRoute" class="admin-app-root"><NuxtPage /></div>
  <div v-else class="site-shell" :dir="isRtl ? 'rtl' : 'ltr'">
    <StoreHeader />
    <main><NuxtPage /></main>
    <StoreFooter />
    <a class="whatsapp-fab" href="https://wa.me/" target="_blank" rel="noreferrer" aria-label="WhatsApp support"><span>✆</span></a>
  </div>
</template>
