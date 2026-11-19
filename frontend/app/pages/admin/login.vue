<script setup lang="ts">
definePageMeta({ layout: false })
const auth = useAuth()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
async function submit() {
  error.value = ''
  loading.value = true
  try {
    const user = await auth.login(email.value, password.value)
    if (!['admin', 'super_admin'].includes(user.role || '')) {
      await $fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => undefined)
      auth.user.value = null
      error.value = 'This account does not have administrator access.'
      return
    }
    await navigateTo('/admin')
  } catch (exception: any) {
    error.value = exception?.data?.detail || 'Unable to sign in. Check your email and password.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <NuxtLink to="/en" class="admin-brand"><span class="admin-brand-mark">N</span><span><b>NOVA HOME</b><small>STORE MANAGEMENT</small></span></NuxtLink>
      <span class="admin-login-eyebrow">SECURE ADMINISTRATION</span>
      <h1>Welcome back.</h1>
      <p>Sign in with your administrator account to manage the NOVA HOME store.</p>
      <form @submit.prevent="submit">
        <label>Email address<input v-model="email" type="email" autocomplete="username" required></label>
        <label>Password<input v-model="password" type="password" autocomplete="current-password" required></label>
        <p v-if="error" class="admin-alert error">{{ error }}</p>
        <button class="admin-primary-button" type="submit" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in to dashboard' }}</button>
      </form>
      <small class="admin-login-note">Administrator access is provisioned by the store owner. Customer accounts cannot access this area.</small>
    </div>
  </div>
</template>
