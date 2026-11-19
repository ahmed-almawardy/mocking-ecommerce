<script setup lang="ts">
definePageMeta({ layout: false })
const auth = useAuth()
const route = useRoute()
const form = reactive({ name:'', email:'', phone:'', password:'', whatsapp_opt_in:false })
const errorMessage = ref('')
const busy = ref(false)
async function submit() {
  errorMessage.value = ''
  busy.value = true
  try {
    await auth.register(form)
    await navigateTo(String(route.query.next || '/account'))
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'We could not create your account. Please review your details.'
  } finally { busy.value = false }
}
function social(provider: string) { window.location.href = `/api/v1/auth/${provider}/login` }
</script>

<template>
  <div class="auth-page"><NuxtLink to="/" class="auth-brand"><span class="brand-mark">N</span><span class="brand-name">NOVA<span>HOME</span></span></NuxtLink><div class="auth-card register-card"><span class="eyebrow">MAKE YOURSELF AT HOME</span><h1>Create your account.</h1><p>One account for orders, updates and a smoother checkout.</p><form @submit.prevent="submit"><label>Full name<input v-model="form.name" autocomplete="name" required minlength="2" placeholder="Your name"></label><label>Email address<input v-model="form.email" type="email" autocomplete="email" required placeholder="you@example.com"></label><label>Mobile number<input v-model="form.phone" type="tel" autocomplete="tel" required placeholder="+20 10 1234 5678"></label><label>Password<input v-model="form.password" type="password" autocomplete="new-password" required minlength="10" placeholder="At least 10 characters"></label><label class="check-label"><input v-model="form.whatsapp_opt_in" type="checkbox"><span>I agree to receive order and account messages on WhatsApp at this number.</span></label><p v-if="errorMessage" class="form-error">{{ errorMessage }}</p><button class="btn btn-primary auth-submit" :disabled="busy">{{ busy ? 'Creating account…' : 'Create account' }} <span>→</span></button></form><div class="auth-separator"><span>or sign up with</span></div><div class="social-buttons"><button @click="social('google')"><b>G</b> Google</button><button @click="social('facebook')"><b>f</b> Facebook</button><button @click="social('apple')"><b>●</b> Apple</button></div><p class="auth-switch">Already have an account? <NuxtLink to="/auth/login">Sign in</NuxtLink></p><NuxtLink to="/" class="back-home">← Back to store</NuxtLink></div></div>
</template>
