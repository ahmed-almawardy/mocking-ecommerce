<script setup lang="ts">
const { t, localePath } = useLocale()
const categories = [
  { name: 'home.categories.cookers', detail: 'home.categoryDetails.cookers', icon: '♨', key: 'Cookers' },
  { name: 'home.categories.cooling', detail: 'home.categoryDetails.cooling', icon: '▥', key: 'Cooling Appliances' },
  { name: 'home.categories.small', detail: 'home.categoryDetails.small', icon: '◉', key: 'Small Home Appliances' },
  { name: 'home.categories.washing', detail: 'home.categoryDetails.washing', icon: '◌', key: 'Washing Machines' },
  { name: 'home.categories.televisions', detail: 'home.categoryDetails.televisions', icon: '▣', key: 'Televisions' },
  { name: 'home.categories.air', detail: 'home.categoryDetails.air', icon: '❋', key: 'Air Conditioners' },
]
const storeApi = useStoreApi()
const { data } = await useAsyncData('home-featured-products', () => storeApi<{ items: any[] }>('/products?page=1&page_size=8&featured=true').catch(() => ({ items: [] })))
const sampleProducts = [
  { id: 'demo-1', slug: 'nova-inverter-air-conditioner-1-5hp', name: 'Inverter Air Conditioner 1.5 HP', category: 'Air Conditioners', price: '24999', compare_at_price: '27999', stock_qty: 18, badge: 'Best seller' },
  { id: 'demo-2', slug: 'nova-front-load-washing-machine-8kg', name: 'Front Load Washing Machine 8 KG', category: 'Washing Machines', price: '18499', compare_at_price: '20999', stock_qty: 12, badge: 'Save 12%' },
  { id: 'demo-3', slug: 'nova-stainless-gas-cooker-5-burner', name: 'Stainless Gas Cooker 5 Burners', category: 'Cookers', price: '13999', compare_at_price: null, stock_qty: 9, badge: 'New' },
  { id: 'demo-4', slug: 'nova-no-frost-refrigerator-420l', name: 'No Frost Refrigerator 420 L', category: 'Cooling Appliances', price: '29999', compare_at_price: '32999', stock_qty: 7, badge: 'Special offer' },
]
const products = computed(() => data.value?.items?.length ? data.value.items : sampleProducts)
</script>

<template>
  <div>
    <FeaturedOffersCarousel />

    <section class="hero-wrap">
      <div class="container hero-grid">
        <div class="hero-copy">
          <span class="eyebrow"><i /> {{ t('home.heroEyebrow') }}</span>
          <h1>{{ t('home.heroTitle') }}<br><em>{{ t('home.heroTitleAccent') }}</em></h1>
          <p>{{ t('home.heroDescription') }}</p>
          <div class="hero-buttons"><NuxtLink :to="localePath('/products')" class="btn btn-primary">{{ t('home.explore') }} <span>→</span></NuxtLink><a href="#categories" class="text-link">{{ t('home.browseCategories') }}</a></div>
          <div class="hero-proof"><span><b>✓</b> {{ t('home.secureCheckout') }}</span><span><b>✓</b> {{ t('home.helpfulSupport') }}</span></div>
        </div>
        <div class="hero-visual">
          <div class="hero-orbit orbit-one" /><div class="hero-orbit orbit-two" />
          <div class="hero-glass-card"><span class="hero-mini-label">NOVA HOME</span><div class="hero-appliances"><ProductArtwork category="Cooling Appliances" variant="large"/><ProductArtwork category="Washing Machines" variant="large"/></div><div class="hero-visual-caption"><b>{{ t('home.featuredTitle') }}</b><small>{{ t('home.featuredText') }}</small></div></div>
          <div class="hero-stamp"><b>HOME</b><span>made better</span></div>
        </div>
      </div>
      <div class="hero-bottom-line" />
    </section>

    <section class="service-strip"><div class="container service-strip-grid"><div><span>↗</span><section><b>{{ t('home.deliveryTitle') }}</b><small>{{ t('home.deliveryDetail') }}</small></section></div><div><span>▤</span><section><b>{{ t('home.paymentTitle') }}</b><small>{{ t('home.paymentDetail') }}</small></section></div><div><span>♡</span><section><b>{{ t('home.supportTitle') }}</b><small>{{ t('home.supportDetail') }}</small></section></div><div><span>✓</span><section><b>{{ t('home.confidenceTitle') }}</b><small>{{ t('home.confidenceDetail') }}</small></section></div></div></section>

    <section id="categories" class="section container category-section">
      <div class="section-heading"><div><span class="eyebrow">{{ t('home.categoryEyebrow') }}</span><h2>{{ t('home.categoryTitle') }}</h2><p>{{ t('home.categoryText') }}</p></div><NuxtLink :to="localePath('/products')" class="section-link">{{ t('home.viewAll') }} <span>→</span></NuxtLink></div>
      <div class="category-grid"><NuxtLink v-for="(category, index) in categories" :key="category.key" :to="{ path: localePath('/products'), query: { category: category.key } }" class="category-tile"><span class="category-number">0{{ index + 1 }}</span><span class="category-icon">{{ category.icon }}</span><b>{{ t(category.name) }}</b><small>{{ t(category.detail) }}</small><span class="category-arrow">↗</span></NuxtLink></div>
    </section>

    <section class="featured-band"><div class="container featured-band-inner"><div><span class="eyebrow">{{ t('home.featuredEyebrow') }}</span><h2>{{ t('home.featuredTitle') }}<br><em>{{ t('home.featuredAccent') }}</em></h2><p>{{ t('home.featuredText') }}</p><NuxtLink :to="localePath('/products')" class="btn btn-light">{{ t('home.shopCollection') }} <span>→</span></NuxtLink></div><div class="featured-band-art"><div class="floating-ring"/><ProductArtwork category="Cookers" variant="large"/><ProductArtwork category="Air Conditioners" variant="large"/></div></div></section>

    <section class="section container products-section"><div class="section-heading"><div><span class="eyebrow">{{ t('home.handpicked') }}</span><h2>{{ t('home.featuredProducts') }}</h2><p>{{ t('home.featuredProductsText') }}</p></div><NuxtLink :to="localePath('/products')" class="section-link">{{ t('home.viewAll') }} <span>→</span></NuxtLink></div><div class="product-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div></section>

    <section class="newsletter-band"><div class="container newsletter-inner"><div><span class="eyebrow">{{ t('home.newsletterEyebrow') }}</span><h2>{{ t('home.newsletterTitle') }}</h2><p>{{ t('home.newsletterText') }}</p></div><form class="newsletter" @submit.prevent="($event.target as HTMLFormElement).reset()"><input type="email" :placeholder="t('home.emailPlaceholder')" required><button type="submit">{{ t('home.subscribe') }} <span>→</span></button></form></div></section>
  </div>
</template>
