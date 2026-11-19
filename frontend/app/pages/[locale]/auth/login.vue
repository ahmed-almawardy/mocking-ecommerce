<script setup lang="ts">
const { t, localePath } = useLocale()
definePageMeta({ layout: false })
const auth = useAuth()
const route = useRoute()
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const busy = ref(false)
const providerStatus = auth.oauthProviders
const providersLoaded = auth.oauthProvidersLoaded
const unavailableProviderMessages = computed(() => Object.entries(providerStatus.value).filter(([, provider]) => !provider.available).map(([name, provider]) => `${name}: ${provider.reason || 'not configured'}`))
onMounted(() => { void auth.loadOAuthProviders() })
async function submit() {
  errorMessage.value = ''
  busy.value = true
  try {
    await auth.login(email.value, password.value)
    await navigateTo(localePath(String(route.query.next || '/account')))
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'We could not sign you in. Please check your details.'
  } finally { busy.value = false }
}
function social(provider: 'google' | 'facebook' | 'apple') {
  const status = providerStatus.value[provider]
  if (!status?.available) {
    errorMessage.value = status?.reason || 'This sign-in provider has not been configured by the store yet.'
    return
  }
  window.location.assign(`/api/v1/auth/${provider}/login`)
}
const oauthErrorMessages: Record<string, string> = {
  account_link_required: 'An account already uses this email. Sign in with that account first, then link this social provider from your account settings.',
  provider_callback_failed: 'The social provider could not complete sign-in. Check the provider configuration and callback URL, then try again.',
  provider_email_missing: 'The provider did not share an email address. Register with your email and password instead.',
}
onMounted(() => {
  const code = String(route.query.oauth_error || '')
  if (code && oauthErrorMessages[code]) errorMessage.value = oauthErrorMessages[code]
})
</script>

<template>
  <div class="auth-page">
    <NuxtLink :to="localePath('/')" class="auth-brand"><span class="brand-mark">N</span><span class="brand-name">NOVA<span>HOME</span></span></NuxtLink>
    <div class="auth-card">
      <span class="eyebrow">{{ t('authPage.loginEyebrow') }}</span>
      <h1>{{ t('authPage.loginTitle') }}</h1>
      <p>{{ t('authPage.loginText') }}</p>
      <form @submit.prevent="submit">
        <label>{{ t('authPage.email') }}<input v-model="email" type="email" autocomplete="email" required :placeholder="t('authPage.emailPlaceholder')"></label>
        <label>{{ t('authPage.password') }}<input v-model="password" type="password" autocomplete="current-password" required :placeholder="t('authPage.currentPassword')"></label>
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
        <button class="btn btn-primary auth-submit" :disabled="busy">{{ busy ? t('authPage.signingIn') : t('authPage.signIn') }} <span>→</span></button>
      </form>
      <div class="auth-separator"><span>{{ t('authPage.continueWith') }}</span></div>
      <div class="social-buttons">
        <button :disabled="!providerStatus.google?.available" :title="providerStatus.google?.reason || 'Continue with Google'" @click="social('google')"><b>G</b> Google</button>
        <button :disabled="!providerStatus.facebook?.available" :title="providerStatus.facebook?.reason || 'Continue with Facebook'" @click="social('facebook')"><b>f</b> Facebook</button>
        <button :disabled="!providerStatus.apple?.available" :title="providerStatus.apple?.reason || 'Continue with Apple'" @click="social('apple')"><b>●</b> Apple</button>
      </div>
      <p class="auth-provider-note">{{ t('authPage.instagram') }}</p>
      <p v-if="providersLoaded && unavailableProviderMessages.length" class="auth-provider-note">{{ t('authPage.unavailable', { providers: unavailableProviderMessages.join(' · ') }) }}</p>
      <p class="auth-switch">{{ t('authPage.new') }} <NuxtLink :to="localePath('/auth/register')">{{ t('authPage.create') }}</NuxtLink></p>
      <NuxtLink :to="localePath('/')" class="back-home">{{ t('authPage.back') }}</NuxtLink>
    </div>
  </div>
</template>
