<script setup lang="ts">
import { storeNavigation as navItems } from '../composables/storeNavigation'
const route = useRoute()
const cart = useCart()
const { t, locale, localePath, switchLocalePath, availableLocales, localeLabel } = useLocale()
const searchText = ref(String(route.query.q || ''))
const openMenu = ref<string | null>(null)
watch(() => route.fullPath, close)

function open(item: string) { openMenu.value = item }
function onNavItemMouseEnter(item: string) {
  if (typeof window !== 'undefined' && window.innerWidth > 760 && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    open(item)
  }
}
function close() { openMenu.value = null }
function toggleMenu(item: string) { openMenu.value = openMenu.value === item ? null : item }
function onNavFocusOut(event: FocusEvent) {
  const root = event.currentTarget as HTMLElement | null
  const next = event.relatedTarget
  if (root && next instanceof Node && root.contains(next)) return
  close()
}
function categoryHref(category: string, search?: string) {
  return { path: localePath('/products'), query: { category, ...(search ? { q: search } : {}) } }
}
function search() {
  navigateTo({ path: localePath('/products'), query: searchText.value.trim() ? { q: searchText.value.trim() } : {} })
}
</script>

<template>
  <header class="store-header">
    <div class="topline">
      <div class="container topline-inner">
        <span>{{ t('home.heroDescription') }}</span>
        <div class="topline-links">
          <a href="tel:19000">19000</a>
          <a href="https://wa.me/" target="_blank" rel="noreferrer">WhatsApp</a>
          <NuxtLink :to="localePath('/account')">{{ t('nav.account') }}</NuxtLink>
          <NuxtLink v-for="code in availableLocales.filter(code => code !== locale)" :key="code" :to="switchLocalePath(code)" class="locale-switch">{{ localeLabel(code) }}</NuxtLink>
        </div>
      </div>
    </div>
    <div class="container masthead">
      <NuxtLink :to="localePath('/')" class="brand-lockup" aria-label="NOVA HOME home">
        <span class="brand-mark">N</span><span class="brand-name">NOVA<span>HOME</span></span>
      </NuxtLink>
      <form class="header-search" role="search" @submit.prevent="search">
        <input v-model="searchText" type="search" :placeholder="t('nav.search')" :aria-label="t('nav.search')">
        <button type="submit" :aria-label="t('nav.search')">⌕</button>
      </form>
      <div class="header-actions">
        <NuxtLink :to="localePath('/account')" class="header-action"><span class="action-icon">♙</span><span><small>{{ t('common.home') }}</small><b>{{ t('nav.signIn') }}</b></span></NuxtLink>
        <NuxtLink :to="localePath('/cart')" class="header-action cart-action"><span class="action-icon">▢</span><span><small>{{ t('nav.cart') }}</small><b>EGP {{ cart.subtotal.value.toLocaleString('en-EG', { maximumFractionDigits: 0 }) }}</b></span><i>{{ cart.count.value }}</i></NuxtLink>
      </div>
    </div>
    <nav class="category-nav" :aria-label="t('nav.shopAll')">
      <div class="nav-shell" @mouseleave="close" @focusout="onNavFocusOut" @keydown.esc.prevent="close">
        <div class="container nav-inner">
          <div v-for="item in navItems" :key="item.key" class="nav-item-wrap" @mouseenter="onNavItemMouseEnter(item.key)">
            <NuxtLink
              :to="categoryHref(item.category)"
              :id="`nav-${item.key}`"
              :aria-expanded="openMenu === item.key"
              :aria-controls="openMenu === item.key ? `mega-menu-${item.key}` : undefined"
              aria-haspopup="true"
              @focus="open(item.key)"
            >{{ t(`nav.${item.key}`) }}</NuxtLink>
            <button
              class="nav-expand"
              type="button"
              :aria-label="t(openMenu === item.key ? 'nav.collapseCategory' : 'nav.expandCategory', { category: t(`nav.${item.key}`) })"
              :aria-expanded="openMenu === item.key"
              :aria-controls="`mega-menu-${item.key}`"
              @click.stop="toggleMenu(item.key)"
            ><span aria-hidden="true">⌄</span></button>
          </div>
          <NuxtLink :to="{ path: localePath('/products'), query: { offer: '1' } }" class="nav-offers">{{ t('nav.offers') }}</NuxtLink>
          <NuxtLink :to="localePath('/account')" class="nav-opinion">{{ t('nav.opinion') }}</NuxtLink>
        </div>

        <section
          v-if="openMenu"
          :id="`mega-menu-${openMenu}`"
          class="mega-menu"
          :class="{ 'mega-menu-small': openMenu === 'smallAppliances' }"
          :aria-labelledby="`nav-${openMenu}`"
        >
          <div class="mega-menu-grid">
            <div v-for="group in navItems.find(item => item.key === openMenu)?.groups" :key="group.title" class="mega-menu-group">
              <h3><NuxtLink :to="categoryHref(navItems.find(item => item.key === openMenu)!.category)">{{ t(group.title) }}</NuxtLink></h3>
              <NuxtLink v-for="entry in group.items" :key="entry.key" :to="categoryHref(entry.category, entry.search || t(entry.key))" @click="close">{{ t(entry.key) }}</NuxtLink>
            </div>
          </div>
        </section>
      </div>
    </nav>
  </header>
</template>
