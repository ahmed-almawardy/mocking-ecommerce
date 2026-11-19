<script setup lang="ts">
const { t, localePath } = useLocale()
const cart = useCart()
const money = (value: number) => new Intl.NumberFormat('en-EG', { style:'currency', currency:'EGP', maximumFractionDigits:0 }).format(value)
const shipping = computed(() => cart.subtotal.value >= 2000 || cart.subtotal.value === 0 ? 0 : 75)
</script>

<template>
  <section class="page-hero compact"><div class="container"><div class="breadcrumbs"><NuxtLink :to="localePath('/')">{{ t('cartPage.home') }}</NuxtLink><span>/</span><span>{{ t('cartPage.title') }}</span></div><span class="eyebrow">{{ t('cartPage.eyebrow') }}</span><h1>{{ t('cartPage.title') }}</h1><p>{{ t('cartPage.intro') }}</p></div></section>
  <section class="section container cart-layout">
    <div class="cart-items-panel">
      <div v-if="cart.lines.value.length" class="cart-table">
        <div class="cart-table-head"><span>{{ t('cartPage.product') }}</span><span>{{ t('cartPage.quantity') }}</span><span>{{ t('cartPage.total') }}</span></div>
        <div v-for="line in cart.lines.value" :key="line.product.id" class="cart-line">
          <div class="cart-product"><ProductArtwork :category="line.product.category"/><div><NuxtLink :to="localePath(`/products/${line.product.slug}`)"><b>{{ line.product.name }}</b></NuxtLink><small>{{ line.product.category }}</small><button class="remove-link" @click="cart.remove(line.product.id)">{{ t('cartPage.remove') }}</button></div></div>
          <div class="quantity-control"><button :aria-label="`${t('cartPage.quantity')} -`" @click="cart.update(line.product.id, line.quantity - 1)">−</button><span>{{ line.quantity }}</span><button :aria-label="`${t('cartPage.quantity')} +`" @click="cart.update(line.product.id, line.quantity + 1)">＋</button></div>
          <b class="line-total">{{ money(Number(line.product.price) * line.quantity) }}</b>
        </div>
      </div>
      <div v-else class="empty-state"><span>▢</span><h2>{{ t('cartPage.emptyTitle') }}</h2><p>{{ t('cartPage.emptyText') }}</p><NuxtLink :to="localePath('/products')" class="btn btn-primary">{{ t('cartPage.explore') }} <span>→</span></NuxtLink></div>
    </div>
    <aside class="order-summary"><h2>{{ t('cartPage.summary') }}</h2><div><span>{{ t('cartPage.subtotal') }}</span><b>{{ money(cart.subtotal.value) }}</b></div><div><span>{{ t('cartPage.delivery') }}</span><b>{{ shipping === 0 ? t('cartPage.free') : money(shipping) }}</b></div><div class="summary-total"><span>{{ t('cartPage.estimated') }}</span><b>{{ money(cart.subtotal.value + shipping) }}</b></div><p v-if="cart.subtotal.value > 0 && cart.subtotal.value < 2000" class="shipping-hint">{{ t('cartPage.addMore', { amount: money(2000 - cart.subtotal.value) }) }}</p><NuxtLink v-if="cart.lines.value.length" :to="localePath('/checkout')" class="btn btn-primary checkout-link">{{ t('cartPage.continue') }} <span>→</span></NuxtLink><NuxtLink v-else :to="localePath('/products')" class="btn btn-primary checkout-link">{{ t('cartPage.start') }}</NuxtLink><div class="secure-note">▣ {{ t('cartPage.secure') }}</div></aside>
  </section>
</template>
