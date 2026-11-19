<script setup lang="ts">
const { t, locale, localePath } = useLocale()
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
const productAnalytics = useProductAnalytics()
watch(item, (value, previous) => { if (value?.id && value.id !== previous?.id) productAnalytics.track(value.id, 'view') }, { immediate: true })
const money = (value: string | number) => new Intl.NumberFormat(locale.value === 'ar' ? 'ar-EG' : 'en-EG', { style:'currency', currency:'EGP', maximumFractionDigits:0 }).format(Number(value))
const categoryLabels: Record<string, string> = { 'Cookers': 'nav.cookers', 'Cooling Appliances': 'nav.cooling', 'Small Home Appliances': 'nav.smallAppliances', 'Washing Machines': 'nav.washingMachines', 'Televisions': 'nav.televisions', 'Air Conditioners': 'nav.airConditioners' }
if (!item.value) throw createError({ statusCode: 404, statusMessage: 'Product not found' })
</script>

<template>
  <section v-if="item" class="container product-detail-page">
    <div class="breadcrumbs"><NuxtLink :to="localePath('/')">{{ t('productDetail.home') }}</NuxtLink><span>/</span><NuxtLink :to="localePath('/products')">{{ t('productDetail.shop') }}</NuxtLink><span>/</span><span>{{ item.name }}</span></div>
    <div class="product-detail-grid">
      <div class="detail-image-panel"><span v-if="item.badge" class="product-badge">{{ item.badge }}</span><ProductArtwork :category="item.category" :image-url="item.image_url" variant="large"/><div class="image-caption">NOVA HOME · {{ item.sku }}</div></div>
      <div class="detail-copy"><span class="eyebrow">{{ categoryLabels[item.category] ? t(categoryLabels[item.category]) : item.category }}</span><h1>{{ item.name }}</h1><div class="rating-line"><span>★★★★★</span><small>{{ t('productDetail.rating') }}</small></div><div class="detail-price"><b>{{ money(item.price) }}</b><del v-if="item.compare_at_price">{{ money(item.compare_at_price) }}</del></div><p class="detail-description">{{ item.description }}</p><div class="stock-line"><span :class="item.stock_qty > 0 ? 'stock-dot' : 'stock-dot out'" />{{ item.stock_qty > 0 ? t('productDetail.available', { count: item.stock_qty }) : t('productDetail.unavailable') }}</div><div class="purchase-row"><div class="quantity-control"><button @click="quantity = Math.max(1, quantity - 1)">−</button><span>{{ quantity }}</span><button @click="quantity = Math.min(20, quantity + 1)">＋</button></div><button class="btn btn-primary add-detail" :disabled="item.stock_qty === 0" @click="cart.add(item, quantity); productAnalytics.track(item.id, 'add_to_cart', quantity)">{{ t('productDetail.add') }} <span>→</span></button></div><div class="detail-promises"><div><b>✓</b><span>{{ t('productDetail.secure') }}</span></div><div><b>✓</b><span>{{ t('productDetail.delivery') }}</span></div><div><b>✓</b><span>{{ t('productDetail.customerCare') }}</span></div></div><div class="detail-help">{{ t('productDetail.questions') }} <a href="https://wa.me/" target="_blank" rel="noreferrer">{{ t('productDetail.talk') }} ↗</a></div></div>
    </div>
    <div class="product-tabs"><div class="tab-title">{{ t('productDetail.overview') }}</div><p>{{ item.description }} {{ t('productDetail.overviewText') }}</p></div>
  </section>
</template>
