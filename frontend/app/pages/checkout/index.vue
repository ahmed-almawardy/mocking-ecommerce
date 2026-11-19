<script setup lang="ts">
const cart = useCart()
const auth = useAuth()
const form = reactive({ shipping_name: '', shipping_phone: '', shipping_address: '', shipping_city: 'Cairo' })
const busy = ref(false)
const errorMessage = ref('')
const shipping = computed(() => cart.subtotal.value >= 2000 ? 0 : 75)
const money = (value: number) => new Intl.NumberFormat('en-EG', { style:'currency', currency:'EGP', maximumFractionDigits:0 }).format(value)
onMounted(async () => {
  const user = await auth.refreshMe()
  if (!user) await navigateTo('/auth/login?next=/checkout')
  else {
    form.shipping_name = user.name
    form.shipping_phone = user.phone || ''
  }
})
async function placeOrder() {
  errorMessage.value = ''
  if (!cart.lines.value.length) { errorMessage.value = 'Your cart is empty.'; return }
  busy.value = true
  try {
    const result = await $fetch<{ payment_url: string }>('/api/v1/orders', {
      method: 'POST', credentials: 'include', body: {
        ...form,
        items: cart.lines.value.map(line => ({ product_id: line.product.id, quantity: line.quantity })),
      },
    })
    cart.clear()
    window.location.assign(result.payment_url)
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'We could not start checkout. Please try again.'
  } finally { busy.value = false }
}
</script>

<template>
  <section class="page-hero compact"><div class="container"><div class="breadcrumbs"><NuxtLink to="/">Home</NuxtLink><span>/</span><NuxtLink to="/cart">Cart</NuxtLink><span>/</span><span>Checkout</span></div><span class="eyebrow">SECURE CHECKOUT</span><h1>Where should we deliver?</h1><p>Enter your delivery details and continue to Kashier's secure payment page.</p></div></section>
  <section class="section container checkout-layout"><div class="checkout-form-panel"><div class="checkout-step"><span>01</span><div><h2>Delivery information</h2><p>We'll use these details to coordinate your delivery.</p></div></div><form @submit.prevent="placeOrder"><div class="form-two-col"><label>Recipient name<input v-model="form.shipping_name" required minlength="2" autocomplete="name"></label><label>Mobile number<input v-model="form.shipping_phone" required minlength="8" autocomplete="tel"></label></div><label>Street address and building details<textarea v-model="form.shipping_address" rows="3" required minlength="8" placeholder="Street, building, floor and apartment"></textarea></label><label>City / governorate<select v-model="form.shipping_city"><option>Cairo</option><option>Giza</option><option>Alexandria</option><option>Qalyubia</option><option>Other</option></select></label><p v-if="errorMessage" class="form-error">{{ errorMessage }}</p><button class="btn btn-primary place-order-btn" :disabled="busy || !cart.lines.value.length">{{ busy ? 'Preparing secure payment…' : 'Continue to payment' }} <span>→</span></button><p class="checkout-disclaimer">Your payment details are entered on Kashier's secure checkout. NOVA HOME does not store your card number.</p></form></div><aside class="order-summary checkout-summary"><h2>Your order</h2><div v-for="line in cart.lines.value" :key="line.product.id" class="checkout-item"><ProductArtwork :category="line.product.category"/><div><b>{{ line.product.name }}</b><small>Qty {{ line.quantity }}</small></div><strong>{{ money(Number(line.product.price) * line.quantity) }}</strong></div><div class="summary-divider"/><div><span>Subtotal</span><b>{{ money(cart.subtotal.value) }}</b></div><div><span>Delivery</span><b>{{ shipping ? money(shipping) : 'Free' }}</b></div><div class="summary-total"><span>Total</span><b>{{ money(cart.subtotal.value + shipping) }}</b></div><div class="secure-note">▣ Powered by secure Kashier checkout</div></aside></section>
</template>
