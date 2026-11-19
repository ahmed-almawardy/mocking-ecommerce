<script setup lang="ts">
const { t, localePath } = useLocale()
const auth = useAuth()
const orders = ref<any[]>([])
const orderError = ref('')
const retryingOrder = ref<string | null>(null)
const providerStatus = auth.oauthProviders
const socialLinkError = ref('')

function connect(provider: 'google' | 'facebook' | 'apple') {
  socialLinkError.value = ''
  const status = providerStatus.value[provider]
  if (!status?.available) {
    socialLinkError.value = status?.reason || 'This sign-in provider has not been configured by the store yet.'
    return
  }
  window.location.assign(`/api/v1/auth/${provider}/link`)
}

async function refreshOrders() {
  try {
    orders.value = await $fetch<any[]>('/api/v1/orders', { credentials: 'include' })
  } catch {
    orders.value = []
  }
}

async function retryPayment(order: any) {
  orderError.value = ''
  retryingOrder.value = order.order_number
  try {
    const result = await $fetch<{ payment_url: string }>(`/api/v1/orders/${order.order_number}/payment-session`, {
      method: 'POST',
      credentials: 'include',
    })
    window.location.assign(result.payment_url)
  } catch (error: any) {
    orderError.value = error?.data?.detail || 'Could not restart payment.'
  } finally {
    retryingOrder.value = null
  }
}

const money = (value: string | number) => new Intl.NumberFormat('en-EG', {
  style: 'currency', currency: 'EGP', maximumFractionDigits: 0,
}).format(Number(value))

onMounted(async () => {
  await auth.loadOAuthProviders()
  if (await auth.refreshMe()) await refreshOrders()
})
</script>

<template>
  <section class="page-hero compact">
    <div class="container">
      <div class="breadcrumbs"><NuxtLink :to="localePath('/')" >{{ t('accountPage.home') }}</NuxtLink><span>/</span><span>My account</span></div>
      <span class="eyebrow">{{ t('accountPage.eyebrow') }}</span>
      <h1>{{ t('accountPage.title') }}</h1>
      <p>{{ t('accountPage.intro') }}</p>
    </div>
  </section>

  <section class="section container account-section">
    <div v-if="auth.user.value" class="account-card">
      <div class="account-avatar">{{ auth.user.value.name.slice(0, 1).toUpperCase() }}</div>
      <div class="account-copy">
        <span class="eyebrow">{{ t('accountPage.signedIn') }}</span>
        <h2>{{ t('accountPage.hello', { name: auth.user.value.name }) }}</h2>
        <p>{{ auth.user.value.email }}</p>
        <p>{{ auth.user.value.phone }}</p>
        <span class="account-optin">{{ t('accountPage.optin', { status: auth.user.value.whatsapp_opt_in ? t('accountPage.enabled') : t('accountPage.disabled') }) }}</span>
        <div class="connected-methods">
          <small>{{ t('accountPage.connect') }}</small>
          <button :disabled="!providerStatus.google?.available" :title="providerStatus.google?.reason || 'Connect Google'" @click="connect('google')">＋ Google</button>
          <button :disabled="!providerStatus.facebook?.available" :title="providerStatus.facebook?.reason || 'Connect Facebook'" @click="connect('facebook')">＋ Facebook</button>
          <button :disabled="!providerStatus.apple?.available" :title="providerStatus.apple?.reason || 'Connect Apple'" @click="connect('apple')">＋ Apple</button>
        </div>
        <p v-if="socialLinkError" class="form-error">{{ socialLinkError }}</p>
      </div>
      <button class="btn btn-outline" @click="auth.logout">{{ t('accountPage.signOut') }}</button>
    </div>

    <div v-else class="account-guest">
      <h2>{{ t('accountPage.welcome') }}</h2>
      <p>{{ t('accountPage.guestText') }}</p>
      <div>
        <NuxtLink :to="localePath('/auth/login')" class="btn btn-primary">{{ t('accountPage.signIn') }} <span>→</span></NuxtLink>
        <NuxtLink :to="localePath('/auth/register')" class="btn btn-outline">{{ t('accountPage.create') }}</NuxtLink>
      </div>
    </div>

    <section v-if="auth.user.value" class="account-orders">
      <div class="account-orders-heading">
        <div><span class="eyebrow">{{ t('accountPage.purchases') }}</span><h2>{{ t('accountPage.history') }}</h2></div>
        <button class="btn btn-outline" @click="refreshOrders">{{ t('accountPage.refresh') }}</button>
      </div>
      <p v-if="orderError" class="form-error">{{ orderError }}</p>
      <div v-if="orders.length" class="account-order-list">
        <article v-for="order in orders" :key="order.order_number" class="account-order-card">
          <div class="account-order-main">
            <div><small>{{ t('accountPage.reference') }}</small><b>{{ order.order_number }}</b></div>
            <div><small>{{ t('accountPage.status') }}</small><b class="order-status">{{ order.status.replaceAll('_', ' ') }}</b></div>
            <div><small>{{ t('accountPage.payment') }}</small><b>{{ order.payment_status }}</b></div>
            <div><small>{{ t('accountPage.total') }}</small><b>{{ money(order.total) }}</b></div>
          </div>
          <div class="account-order-bottom">
            <span>{{ t('accountPage.lines', { count: order.items.length }) }}<template v-if="order.created_at"> · {{ new Date(order.created_at).toLocaleDateString('en-EG') }}</template></span>
            <div>
              <button
                v-if="order.payment_status === 'pending' && ['pending_payment', 'payment_setup_failed'].includes(order.status)"
                class="btn btn-primary"
                :disabled="retryingOrder === order.order_number"
                @click="retryPayment(order)"
              >{{ retryingOrder === order.order_number ? t('accountPage.opening') : t('accountPage.continuePayment') }}</button>
              <a v-if="order.receipt_available" class="receipt-link" :href="`/api/v1/orders/${order.order_number}/receipt.pdf`">{{ t('accountPage.download') }}</a>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="account-orders-empty">{{ t('accountPage.emptyOrders') }}</div>
    </section>

    <div class="account-shortcuts">
      <NuxtLink :to="localePath('/products')"><span>▦</span><b>{{ t('accountPage.browse') }}</b><small>{{ t('accountPage.browseText') }}</small></NuxtLink>
      <NuxtLink :to="localePath('/cart')"><span>▢</span><b>{{ t('accountPage.cart') }}</b><small>{{ t('accountPage.cartText') }}</small></NuxtLink>
      <a href="https://wa.me/" target="_blank" rel="noreferrer"><span>✆</span><b>{{ t('accountPage.support') }}</b><small>{{ t('accountPage.supportText') }}</small></a>
    </div>
  </section>
</template>
