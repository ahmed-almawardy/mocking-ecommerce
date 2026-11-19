export interface StoreUser {
  id: string
  name: string
  email: string | null
  phone: string | null
  whatsapp_opt_in: boolean
  role: string
}

export function useAuth() {
  const user = useState<StoreUser | null>('nova-user', () => null)
  const loading = useState<boolean>('nova-auth-loading', () => false)
  const oauthProviders = useState<Record<string, { configured: boolean; available: boolean; reason: string | null; callback_url: string }>>('nova-oauth-providers', () => ({}))
  const oauthProvidersLoaded = useState<boolean>('nova-oauth-providers-loaded', () => false)
  const { localePath } = useLocale()

  async function loadOAuthProviders() {
    try {
      const response = await $fetch<{ providers: typeof oauthProviders.value }>('/api/v1/auth/providers', { credentials: 'include' })
      oauthProviders.value = response.providers
    } catch {
      oauthProviders.value = {}
    } finally {
      oauthProvidersLoaded.value = true
    }
    return oauthProviders.value
  }

  async function refreshMe() {
    loading.value = true
    try {
      try {
        user.value = await $fetch<StoreUser>('/api/v1/auth/me', { credentials: 'include' })
      } catch {
        await $fetch('/api/v1/auth/refresh', { method: 'POST', credentials: 'include' })
        user.value = await $fetch<StoreUser>('/api/v1/auth/me', { credentials: 'include' })
      }
      return user.value
    } catch {
      user.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  async function login(email: string, password: string) {
    const response = await $fetch<{ user: StoreUser }>('/api/v1/auth/login', {
      method: 'POST', credentials: 'include', body: { email, password },
    })
    user.value = response.user
    return response.user
  }

  async function register(payload: { name: string; email: string; phone: string; password: string; whatsapp_opt_in: boolean }) {
    const response = await $fetch<{ user: StoreUser }>('/api/v1/auth/register', {
      method: 'POST', credentials: 'include', body: payload,
    })
    user.value = response.user
    return response.user
  }

  async function logout() {
    await $fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => undefined)
    user.value = null
    await navigateTo(localePath('/'))
  }

  return { user, loading, oauthProviders, oauthProvidersLoaded, loadOAuthProviders, refreshMe, login, register, logout }
}
