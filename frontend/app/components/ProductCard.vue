<script setup lang="ts">
import type { CartProduct } from '~/composables/useCart'

const props = defineProps<{ product: CartProduct & { badge?: string | null; compare_at_price?: string | number | null } }>()
const cart = useCart()
const productAnalytics = useProductAnalytics()
const { t, locale, localePath } = useLocale()
const categoryLabels: Record<string, string> = { 'Cookers': 'nav.cookers', 'Cooling Appliances': 'nav.cooling', 'Small Home Appliances': 'nav.smallAppliances', 'Washing Machines': 'nav.washingMachines', 'Televisions': 'nav.televisions', 'Air Conditioners': 'nav.airConditioners' }
const money = (value: string | number) => new Intl.NumberFormat('en-EG', { style: 'currency', currency: 'EGP', maximumFractionDigits: 0 }).format(Number(value))
</script>

<template>
  <article class="product-card">
    <NuxtLink :to="localePath(`/products/${product.slug}`)" class="product-card-media">
      <span v-if="product.badge" class="product-badge">{{ product.badge }}</span>
      <ProductArtwork :category="product.category" :image-url="product.image_url" />
      <span class="quick-view">{{ t('common.viewDetails') }}</span>
    </NuxtLink>
    <div class="product-card-info">
      <small class="product-category">{{ categoryLabels[product.category] ? t(categoryLabels[product.category]) : product.category }}</small>
      <NuxtLink :to="localePath(`/products/${product.slug}`)" class="product-name">{{ product.name }}</NuxtLink>
      <div class="price-line"><b>{{ money(product.price) }}</b><del v-if="product.compare_at_price">{{ money(product.compare_at_price) }}</del></div>
      <button class="add-cart-btn" :disabled="product.stock_qty === 0" @click="cart.add(product); productAnalytics.track(product.id, 'add_to_cart')">{{ product.stock_qty === 0 ? (locale === 'ar' ? 'نفد المخزون' : 'Out of stock') : (locale === 'ar' ? 'أضف إلى السلة' : 'Add to cart') }} <span>＋</span></button>
    </div>
  </article>
</template>
