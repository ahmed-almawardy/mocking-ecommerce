<script setup lang="ts">
const route = useRoute()
const auth = useAuth()
const orderNumber = computed(() => String(route.query.order || ''))
const order = ref<any>(null)
const loading = ref(false)
const errorMessage = ref('')
async function refreshStatus() {
  if (!orderNumber.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    if (!auth.user.value) await auth.refreshMe()
    order.value = await $fetch(`/api/v1/orders/${orderNumber.value}`, { credentials: 'include' })
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Sign in with the account used for this order to view its status.'
  } finally { loading.value = false }
}
onMounted(refreshStatus)
</script>

<template>
  <section class="section container confirmation-page"><div class="confirmation-icon">✓</div><span class="eyebrow">THANK YOU FOR SHOPPING WITH NOVA HOME</span><h1>Your payment return was received.</h1><p class="confirmation-lead">We are checking the server-confirmed payment status. Your order is only marked paid after Kashier's verified webhook reaches our backend.</p><div v-if="orderNumber" class="confirmation-order"><small>Order reference</small><b>{{ orderNumber }}</b><div v-if="order"><span>Order status</span><strong>{{ order.status.replaceAll('_', ' ') }}</strong><span>Payment status</span><strong>{{ order.payment_status }}</strong><span>Total</span><strong>EGP {{ Number(order.total).toLocaleString('en-EG') }}</strong></div><p v-if="errorMessage" class="form-error">{{ errorMessage }}</p><button class="btn btn-outline" :disabled="loading" @click="refreshStatus">{{ loading ? 'Checking…' : 'Refresh order status' }}</button></div><div class="confirmation-actions"><NuxtLink to="/products" class="btn btn-primary">Continue shopping <span>→</span></NuxtLink><NuxtLink to="/account" class="text-link">Go to my account</NuxtLink></div></section>
</template>
