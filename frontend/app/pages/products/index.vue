<script setup lang="ts">
const route = useRoute()
const storeApi = useStoreApi()
const search = ref(String(route.query.q || ''))
const selectedCategory = computed(() => String(route.query.category || ''))
const queryKey = computed(() => `products-${route.query.q || ''}-${route.query.category || ''}-${route.query.page || 1}`)
const { data, pending, error } = await useAsyncData(queryKey, () => storeApi<{ items: any[]; total: number }>('/products', {
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
const title = computed(() => selectedCategory.value || (route.query.q ? `Search: ${route.query.q}` : route.query.offer ? 'Special offers' : 'Shop all products'))
function applySearch() { navigateTo({ path: '/products', query: { ...(search.value ? { q: search.value } : {}), ...(selectedCategory.value ? { category: selectedCategory.value } : {}) } }) }
</script>

<template>
  <section class="page-hero"><div class="container"><div class="breadcrumbs"><NuxtLink to="/">Home</NuxtLink><span>/</span><span>Shop</span></div><span class="eyebrow">THE NOVA HOME COLLECTION</span><h1>{{ title }}</h1><p>Find dependable home essentials and thoughtful appliances for every room.</p></div></section>
  <section class="section container listing-layout">
    <aside class="filter-panel"><h3>Browse categories</h3><NuxtLink to="/products">All products</NuxtLink><NuxtLink v-for="category in ['Cookers','Cooling Appliances','Small Home Appliances','Washing Machines','Televisions','Air Conditioners','Water Heaters']" :key="category" :to="{ path: '/products', query: { category } }" :class="{ active: category === selectedCategory }">{{ category }}</NuxtLink><div class="filter-help"><b>Need help choosing?</b><small>Our customer team is happy to help.</small><a href="https://wa.me/" target="_blank" rel="noreferrer">Chat with us ↗</a></div></aside>
    <div class="listing-main"><div class="listing-toolbar"><span>{{ data?.total || products.length }} products</span><form class="listing-search" @submit.prevent="applySearch"><input v-model="search" placeholder="Search products"><button>Search</button></form></div><div v-if="products.length" class="product-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div><div v-else class="empty-state"><span>⌕</span><h2>No products found</h2><p>Try another search or browse all products.</p><NuxtLink to="/products" class="btn btn-primary">Clear filters</NuxtLink></div></div>
  </section>
</template>
