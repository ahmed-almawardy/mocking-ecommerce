<script setup lang="ts">
const { t, localePath } = useLocale()
</script>

<template>
  <footer class="store-footer">
    <div class="container footer-benefits">
      <div><span>⌁</span><section><b>{{ t('footer.delivery') }}</b><small>{{ t('footer.deliveryText') }}</small></section></div>
      <div><span>◷</span><section><b>{{ t('footer.payment') }}</b><small>{{ t('footer.paymentText') }}</small></section></div>
      <div><span>✓</span><section><b>{{ t('footer.support') }}</b><small>{{ t('footer.supportText') }}</small></section></div>
      <div><span>↺</span><section><b>{{ t('footer.assistance') }}</b><small>{{ t('footer.assistanceText') }}</small></section></div>
    </div>
    <div class="footer-main">
      <div class="container footer-grid">
        <div class="footer-about"><div class="brand-lockup footer-brand"><span class="brand-mark">N</span><span class="brand-name">NOVA<span>HOME</span></span></div><p>{{ t('footer.aboutText') }}</p><p class="footer-contact">{{ t('footer.customerCare') }} <b>19000</b></p></div>
        <div><h3>{{ t('footer.shop') }}</h3><NuxtLink :to="localePath('/products')">{{ t('footer.allProducts') }}</NuxtLink><NuxtLink :to="{ path: localePath('/products'), query: { category: 'Cookers' } }">{{ t('nav.cookers') }}</NuxtLink><NuxtLink :to="{ path: localePath('/products'), query: { category: 'Cooling Appliances' } }">{{ t('nav.cooling') }}</NuxtLink><NuxtLink :to="{ path: localePath('/products'), query: { category: 'Small Home Appliances' } }">{{ t('nav.smallAppliances') }}</NuxtLink></div>
        <div><h3>{{ t('footer.customerService') }}</h3><a href="mailto:support@novahome.example">{{ t('footer.contact') }}</a><NuxtLink :to="localePath('/account')">{{ t('nav.account') }}</NuxtLink><NuxtLink :to="localePath('/cart')">{{ t('nav.cart') }}</NuxtLink><a href="https://wa.me/" target="_blank" rel="noreferrer">WhatsApp</a></div>
        <div><h3>{{ t('footer.newsletter') }}</h3><p>{{ t('footer.newsletterText') }}</p><form class="newsletter" @submit.prevent="($event.target as HTMLFormElement).reset()"><input type="email" required :placeholder="t('home.emailPlaceholder')"><button type="submit">{{ t('footer.join') }}</button></form><small class="footer-note">{{ t('footer.footerNote') }}</small></div>
      </div>
    </div>
    <div class="footer-bottom"><div class="container footer-bottom-inner"><span>© {{ new Date().getFullYear() }} NOVA HOME. {{ t('footer.rights') }}</span><span>Secure checkout · EGP</span></div></div>
  </footer>
</template>
