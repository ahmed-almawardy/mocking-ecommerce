<script setup lang="ts">
const { t, locale, localePath } = useLocale()
const route = useRoute()
const storeApi = useStoreApi()
const search = ref(String(route.query.q || ''))
const selectedCategory = computed(() => String(route.query.category || ''))
const queryKey = computed(() => `products-${locale.value}-${route.query.q || ''}-${route.query.category || ''}-${route.query.page || 1}`)
const { data } = await useAsyncData(queryKey, () => storeApi<{ items: any[]; total: number }>('/products', {
  query: { q: route.query.q, category: route.query.category, featured: route.query.offer ? true : undefined, page: route.query.page || 1, page_size: 24 },
}).catch(() => ({ items: [], total: 0 })), { watch: [() => route.query] })
const fallback = [
  { id: 'demo-1', slug: 'nova-inverter-air-conditioner-1-5hp', name: 'Inverter Air Conditioner 1.5 HP', category: 'Air Conditioners', price: '24999', compare_at_price: '27999', stock_qty: 18, badge: 'Best seller' },
  { id: 'demo-2', slug: 'nova-front-load-washing-machine-8kg', name: 'Front Load Washing Machine 8 KG', category: 'Washing Machines', price: '18499', compare_at_price: '20999', stock_qty: 12, badge: 'Save 12%' },
  { id: 'demo-3', slug: 'nova-stainless-gas-cooker-5-burner', name: 'Stainless Gas Cooker 5 Burners', category: 'Cookers', price: '13999', compare_at_price: null, stock_qty: 9, badge: 'New' },
  { id: 'demo-4', slug: 'nova-no-frost-refrigerator-420l', name: 'No Frost Refrigerator 420 L', category: 'Cooling Appliances', price: '29999', compare_at_price: '32999', stock_qty: 7, badge: 'Special offer' },
  { id: 'demo-5', slug: 'nova-smart-tv-55-inch-4k', name: 'Smart TV 55 inch 4K UHD', category: 'Televisions', price: '21999', compare_at_price: null, stock_qty: 15, badge: 'Popular' },
  { id: 'demo-6', slug: 'nova-digital-air-fryer-6l', name: 'Digital Air Fryer 6 L', category: 'Small Home Appliances', price: '3499', compare_at_price: '3999', stock_qty: 35, badge: 'Save 500 EGP' },
]
const products = computed(() => data.value?.items?.length ? data.value.items : fallback.filter(p => !selectedCategory.value || p.category === selectedCategory.value).filter(p => !route.query.q || p.name.toLowerCase().includes(String(route.query.q).toLowerCase())))
const categoryKeys: Record<string, string> = {
  Cookers: 'nav.cookers',
  'Cooling Appliances': 'nav.cooling',
  'Small Home Appliances': 'nav.smallAppliances',
  'Washing Machines': 'nav.washingMachines',
  Televisions: 'nav.televisions',
  'Air Conditioners': 'nav.airConditioners',
}
const title = computed(() => selectedCategory.value
  ? t(categoryKeys[selectedCategory.value] || 'productsPage.shop')
  : route.query.q
    ? `${locale.value === 'ar' ? 'بحث عن' : 'Search'}: ${route.query.q}`
    : route.query.offer ? t('productsPage.special') : t('productsPage.allTitle'))
const categories = [
  ['Cookers', 'nav.cookers'], ['Cooling Appliances', 'nav.cooling'], ['Small Home Appliances', 'nav.smallAppliances'],
  ['Washing Machines', 'nav.washingMachines'], ['Televisions', 'nav.televisions'], ['Air Conditioners', 'nav.airConditioners'], ['Water Heaters', 'menu.waterHeaters'],
] as const
function applySearch() {
  navigateTo({ path: localePath('/products'), query: { ...(search.value ? { q: search.value } : {}), ...(selectedCategory.value ? { category: selectedCategory.value } : {}) } })
}
</script>

<template>
  <section class="page-hero"><div class="container"><div class="breadcrumbs"><NuxtLink :to="localePath('/')">{{ t('productsPage.home') }}</NuxtLink><span>/</span><span>{{ t('productsPage.shop') }}</span></div><span class="eyebrow">{{ t('productsPage.eyebrow') }}</span><h1>{{ title }}</h1><p>{{ t('productsPage.intro') }}</p></div></section>
  <section class="section container listing-layout">
    <aside class="filter-panel"><h3>{{ t('productsPage.browse') }}</h3><NuxtLink :to="localePath('/products')">{{ t('productsPage.all') }}</NuxtLink><NuxtLink v-for="[category, key] in categories" :key="category" :to="{ path: localePath('/products'), query: { category } }" :class="{ active: category === selectedCategory }">{{ t(key) }}</NuxtLink><div class="filter-help"><b>{{ t('productsPage.help') }}</b><small>{{ t('productsPage.helpText') }}</small><a href="https://wa.me/" target="_blank" rel="noreferrer">{{ t('productsPage.chat') }} ↗</a></div></aside>
    <div class="listing-main"><div class="listing-toolbar"><span>{{ data?.total || products.length }} {{ locale === 'ar' ? 'منتج' : 'products' }}</span><form class="listing-search" @submit.prevent="applySearch"><input v-model="search" :placeholder="t('productsPage.search')"><button>{{ t('productsPage.searchButton') }}</button></form></div><div v-if="products.length" class="product-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div><div v-else class="empty-state"><span>⌕</span><h2>{{ t('productsPage.none') }}</h2><p>{{ t('productsPage.noneText') }}</p><NuxtLink :to="localePath('/products')" class="btn btn-primary">{{ t('productsPage.clear') }}</NuxtLink></div></div>
  </section>
</template>
