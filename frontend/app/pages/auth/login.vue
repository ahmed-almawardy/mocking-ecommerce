<script setup lang="ts">
definePageMeta({ layout: false })
const auth = useAuth()
const route = useRoute()
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const busy = ref(false)
async function submit() {
  errorMessage.value = ''
  busy.value = true
  try {
    await auth.login(email.value, password.value)
    await navigateTo(String(route.query.next || '/account'))
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'We could not sign you in. Please check your details.'
  } finally { busy.value = false }
}
function social(provider: string) { window.location.href = `/api/v1/auth/${provider}/login` }
</script>

<template>
  <div class="auth-page"><NuxtLink to="/" class="auth-brand"><span class="brand-mark">N</span><span class="brand-name">NOVA<span>HOME</span></span></NuxtLink><div class="auth-card"><span class="eyebrow">WELCOME BACK</span><h1>Good to see you.</h1><p>Sign in to manage your orders and continue shopping.</p><form @submit.prevent="submit"><label>Email address<input v-model="email" type="email" autocomplete="email" required placeholder="you@example.com"></label><label>Password<input v-model="password" type="password" autocomplete="current-password" required placeholder="Your password"></label><p v-if="errorMessage" class="form-error">{{ errorMessage }}</p><button class="btn btn-primary auth-submit" :disabled="busy">{{ busy ? 'Signing in…' : 'Sign in' }} <span>→</span></button></form><div class="auth-separator"><span>or continue with</span></div><div class="social-buttons"><button @click="social('google')"><b>G</b> Google</button><button @click="social('facebook')"><b>f</b> Facebook</button><button @click="social('apple')"><b>●</b> Apple</button></div><p class="auth-switch">New to NOVA HOME? <NuxtLink to="/auth/register">Create an account</NuxtLink></p><NuxtLink to="/" class="back-home">← Back to store</NuxtLink></div></div>
</template>
