<script setup lang="ts">
const { t, localePath, locale } = useLocale()
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
    errorMessage.value = error?.data?.detail || t('confirmationPage.signInError')
  } finally { loading.value = false }
}
onMounted(refreshStatus)
</script>

<template>
  <section class="section container confirmation-page"><div class="confirmation-icon">✓</div><span class="eyebrow">{{ t('confirmationPage.thanks') }}</span><h1>{{ t('confirmationPage.title') }}</h1><p class="confirmation-lead">{{ t('confirmationPage.lead') }}</p><div v-if="orderNumber" class="confirmation-order"><small>{{ t('confirmationPage.reference') }}</small><b>{{ orderNumber }}</b><div v-if="order"><span>{{ t('confirmationPage.status') }}</span><strong>{{ order.status.replaceAll('_', ' ') }}</strong><span>{{ t('confirmationPage.payment') }}</span><strong>{{ order.payment_status }}</strong><span>{{ t('confirmationPage.total') }}</span><strong>EGP {{ Number(order.total).toLocaleString(locale === 'ar' ? 'ar-EG' : 'en-EG') }}</strong></div><p v-if="errorMessage" class="form-error">{{ errorMessage }}</p><button class="btn btn-outline" :disabled="loading" @click="refreshStatus">{{ loading ? t('confirmationPage.checking') : t('confirmationPage.refresh') }}</button></div><div class="confirmation-actions"><NuxtLink :to="localePath('/products')" class="btn btn-primary">{{ t('confirmationPage.continue') }} <span>→</span></NuxtLink><NuxtLink :to="localePath('/account')" class="text-link">{{ t('confirmationPage.account') }}</NuxtLink></div></section>
</template>
