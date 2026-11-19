<script setup lang="ts">
const { t, localePath } = useLocale()
definePageMeta({ layout: false })
const auth = useAuth()
const route = useRoute()
const form = reactive({ name:'', email:'', phone:'', password:'', whatsapp_opt_in:false })
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
    await auth.register(form)
    await navigateTo(localePath(String(route.query.next || '/account')))
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'We could not create your account. Please review your details.'
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
    <div class="auth-card register-card">
      <span class="eyebrow">{{ t('authPage.registerEyebrow') }}</span>
      <h1>{{ t('authPage.registerTitle') }}</h1>
      <p>{{ t('authPage.registerText') }}</p>
      <form @submit.prevent="submit">
        <label>{{ t('authPage.fullName') }}<input v-model="form.name" autocomplete="name" required minlength="2" :placeholder="t('authPage.namePlaceholder')"></label>
        <label>{{ t('authPage.email') }}<input v-model="form.email" type="email" autocomplete="email" required :placeholder="t('authPage.emailPlaceholder')"></label>
        <label>{{ t('authPage.mobile') }}<input v-model="form.phone" type="tel" autocomplete="tel" required :placeholder="t('authPage.phonePlaceholder')"></label>
        <label>{{ t('authPage.password') }}<input v-model="form.password" type="password" autocomplete="new-password" required minlength="10" :placeholder="t('authPage.passwordPlaceholder')"></label>
        <label class="check-label"><input v-model="form.whatsapp_opt_in" type="checkbox"><span>{{ t('authPage.whatsappOptin') }}</span></label>
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
        <button class="btn btn-primary auth-submit" :disabled="busy">{{ busy ? t('authPage.creating') : t('authPage.create') }} <span>→</span></button>
      </form>
      <div class="auth-separator"><span>{{ t('authPage.signUpWith') }}</span></div>
      <div class="social-buttons">
        <button :disabled="!providerStatus.google?.available" :title="providerStatus.google?.reason || 'Continue with Google'" @click="social('google')"><b>G</b> Google</button>
        <button :disabled="!providerStatus.facebook?.available" :title="providerStatus.facebook?.reason || 'Continue with Facebook'" @click="social('facebook')"><b>f</b> Facebook</button>
        <button :disabled="!providerStatus.apple?.available" :title="providerStatus.apple?.reason || 'Continue with Apple'" @click="social('apple')"><b>●</b> Apple</button>
      </div>
      <p class="auth-provider-note">{{ t('authPage.instagram') }}</p>
      <p v-if="providersLoaded && unavailableProviderMessages.length" class="auth-provider-note">{{ t('authPage.unavailable', { providers: unavailableProviderMessages.join(' · ') }) }}</p>
      <p class="auth-switch">{{ t('authPage.already') }} <NuxtLink :to="localePath('/auth/login')">{{ t('authPage.signIn') }}</NuxtLink></p>
      <NuxtLink :to="localePath('/')" class="back-home">{{ t('authPage.back') }}</NuxtLink>
    </div>
  </div>
</template>
