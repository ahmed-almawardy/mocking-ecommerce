<script setup lang="ts">
const props = defineProps<{ active: 'dashboard' | 'products' | 'offers' | 'customers' | 'orders' | 'payments' }>()
const auth = useAuth()
const ready = ref(false)
const checking = ref(true)

const navigation = [
  { key: 'dashboard', label: 'Overview', to: '/admin', icon: 'dashboard' },
  { key: 'products', label: 'Products', to: '/admin/products', icon: 'products' },
  { key: 'offers', label: 'Offers', to: '/admin/offers', icon: 'offers' },
  { key: 'orders', label: 'Orders', to: '/admin/orders', icon: 'orders' },
  { key: 'customers', label: 'Customers', to: '/admin/customers', icon: 'customers' },
  { key: 'payments', label: 'Payments', to: '/admin/payments', icon: 'payments' },
]

onMounted(async () => {
  checking.value = true
  const current = await auth.refreshMe()
  if (!current || !['admin', 'super_admin'].includes(current.role || '')) {
    await navigateTo('/admin/login')
    return
  }
  ready.value = true
  checking.value = false
})

async function signOut() {
  await auth.logout()
  await navigateTo('/admin/login')
}
</script>

<template>
  <div v-if="checking" class="admin-loading-screen"><span class="admin-spinner" />Checking administrator session…</div>
  <div v-else-if="ready" class="admin-layout" dir="ltr">
    <aside class="admin-sidebar">
      <NuxtLink to="/admin" class="admin-brand"><span class="admin-brand-mark">N</span><span><b>NOVA HOME</b><small>STORE MANAGEMENT</small></span></NuxtLink>
      <div class="admin-sidebar-label">WORKSPACE</div>
      <nav class="admin-side-nav" aria-label="Administration">
        <NuxtLink v-for="item in navigation" :key="item.key" :to="item.to" :class="{ active: props.active === item.key }">
          <span class="admin-nav-icon"><AdminIcon :name="item.icon" :size="19" /></span><span>{{ item.label }}</span><span v-if="props.active === item.key" class="admin-nav-indicator" />
        </NuxtLink>
      </nav>
      <div class="admin-sidebar-bottom">
        <div class="admin-sidebar-promo"><span class="admin-promo-kicker">NOVA HOME</span><b>Better home.<br>Better business.</b><small>Commerce control center</small></div>
        <NuxtLink to="/en" class="admin-store-link">↗ <span>View storefront</span></NuxtLink>
        <button class="admin-signout" @click="signOut">⇥ <span>Sign out</span></button>
      </div>
    </aside>
    <section class="admin-main">
      <header class="admin-topbar">
        <div class="admin-topbar-search"><AdminIcon name="search" :size="19" /><input type="search" placeholder="Search products, orders, customers…" aria-label="Search admin records"></div>
        <div class="admin-topbar-user"><span class="admin-avatar">{{ (auth.user.value?.name || 'A').slice(0, 1).toUpperCase() }}</span><span><b>{{ auth.user.value?.name || 'Administrator' }}</b><small>Administrator</small></span></div>
      </header>
      <main class="admin-content"><slot /></main>
      <footer class="admin-footer">NOVA HOME · Store administration <span>Private workspace</span></footer>
    </section>
  </div>
</template>
