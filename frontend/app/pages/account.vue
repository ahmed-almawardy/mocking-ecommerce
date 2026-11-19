<script setup lang="ts">
const auth = useAuth()
const orders = ref<any[]>([])
const orderError = ref('')
const retryingOrder = ref<string | null>(null)

function connect(provider: string) {
  window.location.href = `/api/v1/auth/${provider}/link`
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
  if (await auth.refreshMe()) await refreshOrders()
})
</script>

<template>
  <section class="page-hero compact">
    <div class="container">
      <div class="breadcrumbs"><NuxtLink to="/">Home</NuxtLink><span>/</span><span>My account</span></div>
      <span class="eyebrow">YOUR NOVA HOME</span>
      <h1>My account</h1>
      <p>Your details and a place to keep your shopping organised.</p>
    </div>
  </section>

  <section class="section container account-section">
    <div v-if="auth.user.value" class="account-card">
      <div class="account-avatar">{{ auth.user.value.name.slice(0, 1).toUpperCase() }}</div>
      <div class="account-copy">
        <span class="eyebrow">SIGNED IN</span>
        <h2>Hello, {{ auth.user.value.name }}</h2>
        <p>{{ auth.user.value.email }}</p>
        <p>{{ auth.user.value.phone }}</p>
        <span class="account-optin">WhatsApp order updates: {{ auth.user.value.whatsapp_opt_in ? 'Opted in' : 'Not enabled' }}</span>
        <div class="connected-methods">
          <small>Connect sign-in methods</small>
          <button @click="connect('google')">＋ Google</button>
          <button @click="connect('facebook')">＋ Facebook</button>
          <button @click="connect('apple')">＋ Apple</button>
        </div>
      </div>
      <button class="btn btn-outline" @click="auth.logout">Sign out</button>
    </div>

    <div v-else class="account-guest">
      <h2>Welcome to NOVA HOME</h2>
      <p>Sign in to view your account, or create an account to make checkout easier.</p>
      <div>
        <NuxtLink to="/auth/login" class="btn btn-primary">Sign in <span>→</span></NuxtLink>
        <NuxtLink to="/auth/register" class="btn btn-outline">Create account</NuxtLink>
      </div>
    </div>

    <section v-if="auth.user.value" class="account-orders">
      <div class="account-orders-heading">
        <div><span class="eyebrow">YOUR PURCHASES</span><h2>Order history</h2></div>
        <button class="btn btn-outline" @click="refreshOrders">Refresh</button>
      </div>
      <p v-if="orderError" class="form-error">{{ orderError }}</p>
      <div v-if="orders.length" class="account-order-list">
        <article v-for="order in orders" :key="order.order_number" class="account-order-card">
          <div class="account-order-main">
            <div><small>ORDER REFERENCE</small><b>{{ order.order_number }}</b></div>
            <div><small>STATUS</small><b class="order-status">{{ order.status.replaceAll('_', ' ') }}</b></div>
            <div><small>PAYMENT</small><b>{{ order.payment_status }}</b></div>
            <div><small>TOTAL</small><b>{{ money(order.total) }}</b></div>
          </div>
          <div class="account-order-bottom">
            <span>{{ order.items.length }} item line(s)<template v-if="order.created_at"> · {{ new Date(order.created_at).toLocaleDateString('en-EG') }}</template></span>
            <div>
              <button
                v-if="order.payment_status === 'pending' && ['pending_payment', 'payment_setup_failed'].includes(order.status)"
                class="btn btn-primary"
                :disabled="retryingOrder === order.order_number"
                @click="retryPayment(order)"
              >{{ retryingOrder === order.order_number ? 'Opening…' : 'Continue payment' }}</button>
              <a v-if="order.receipt_available" class="receipt-link" :href="`/api/v1/orders/${order.order_number}/receipt.pdf`">Download receipt ↓</a>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="account-orders-empty">Your orders will appear here after your first checkout.</div>
    </section>

    <div class="account-shortcuts">
      <NuxtLink to="/products"><span>▦</span><b>Browse products</b><small>Explore our appliance collection</small></NuxtLink>
      <NuxtLink to="/cart"><span>▢</span><b>Shopping cart</b><small>Review items before checkout</small></NuxtLink>
      <a href="https://wa.me/" target="_blank" rel="noreferrer"><span>✆</span><b>Customer support</b><small>Talk to our team on WhatsApp</small></a>
    </div>
  </section>
</template>
