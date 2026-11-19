<script setup lang="ts">
const route = useRoute()
const storeApi = useStoreApi()
const slug = computed(() => String(route.params.slug))
const { data: product } = await useAsyncData(() => `product-${slug.value}`, () => storeApi<any>(`/products/${slug.value}`).catch(() => null), { watch: [slug] })
const fallbackProducts: Record<string, any> = {
  'nova-inverter-air-conditioner-1-5hp': { id:'demo-1', slug:'nova-inverter-air-conditioner-1-5hp', name:'Inverter Air Conditioner 1.5 HP', category:'Air Conditioners', price:'24999', compare_at_price:'27999', stock_qty:18, sku:'NH-AC-18K', badge:'Best seller', description:'Efficient cooling with quiet operation, multiple fan modes and a clean modern finish.' },
  'nova-front-load-washing-machine-8kg': { id:'demo-2', slug:'nova-front-load-washing-machine-8kg', name:'Front Load Washing Machine 8 KG', category:'Washing Machines', price:'18499', compare_at_price:'20999', stock_qty:12, sku:'NH-WM-8KG', badge:'Save 12%', description:'A generous 8 KG capacity, everyday wash programs and a compact contemporary design.' },
  'nova-stainless-gas-cooker-5-burner': { id:'demo-3', slug:'nova-stainless-gas-cooker-5-burner', name:'Stainless Gas Cooker 5 Burners', category:'Cookers', price:'13999', compare_at_price:null, stock_qty:9, sku:'NH-CK-5B', badge:'New', description:'Five burners, a spacious oven and easy-clean stainless steel styling for family kitchens.' },
  'nova-no-frost-refrigerator-420l': { id:'demo-4', slug:'nova-no-frost-refrigerator-420l', name:'No Frost Refrigerator 420 L', category:'Cooling Appliances', price:'29999', compare_at_price:'32999', stock_qty:7, sku:'NH-FR-420', badge:'Special offer', description:'Spacious storage, balanced cooling and a modern finish designed for busy households.' },
}
const item = computed(() => product.value || fallbackProducts[slug.value])
const quantity = ref(1)
const cart = useCart()
const money = (value: string | number) => new Intl.NumberFormat('en-EG', { style:'currency', currency:'EGP', maximumFractionDigits:0 }).format(Number(value))
if (!item.value) throw createError({ statusCode: 404, statusMessage: 'Product not found' })
</script>

<template>
  <section v-if="item" class="container product-detail-page">
    <div class="breadcrumbs"><NuxtLink to="/">Home</NuxtLink><span>/</span><NuxtLink to="/products">Shop</NuxtLink><span>/</span><span>{{ item.name }}</span></div>
    <div class="product-detail-grid"><div class="detail-image-panel"><span v-if="item.badge" class="product-badge">{{ item.badge }}</span><ProductArtwork :category="item.category" variant="large"/><div class="image-caption">NOVA HOME · {{ item.sku }}</div></div><div class="detail-copy"><span class="eyebrow">{{ item.category }}</span><h1>{{ item.name }}</h1><div class="rating-line"><span>★★★★★</span><small>Quality chosen for everyday living</small></div><div class="detail-price"><b>{{ money(item.price) }}</b><del v-if="item.compare_at_price">{{ money(item.compare_at_price) }}</del></div><p class="detail-description">{{ item.description }}</p><div class="stock-line"><span :class="item.stock_qty > 0 ? 'stock-dot' : 'stock-dot out'" />{{ item.stock_qty > 0 ? `${item.stock_qty} available` : 'Currently unavailable' }}</div><div class="purchase-row"><div class="quantity-control"><button @click="quantity = Math.max(1, quantity - 1)">−</button><span>{{ quantity }}</span><button @click="quantity = Math.min(20, quantity + 1)">＋</button></div><button class="btn btn-primary add-detail" :disabled="item.stock_qty === 0" @click="cart.add(item, quantity)">Add to cart <span>→</span></button></div><div class="detail-promises"><div><b>✓</b><span>Secure online payment</span></div><div><b>✓</b><span>Delivery support across Egypt</span></div><div><b>✓</b><span>Customer care when you need it</span></div></div><div class="detail-help">Questions about this product? <a href="https://wa.me/" target="_blank" rel="noreferrer">Talk to our team ↗</a></div></div></div>
    <div class="product-tabs"><div class="tab-title">Product overview</div><p>{{ item.description }} Contact our team for availability, delivery and product-support information.</p></div>
  </section>
</template>
