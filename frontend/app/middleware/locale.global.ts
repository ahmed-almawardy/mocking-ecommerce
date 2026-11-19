import { availableLocales } from '../composables/useLocale'

export default defineNuxtRouteMiddleware((to) => {
  if (to.path === '/admin' || to.path.startsWith('/admin/')) return
  const supported = availableLocales()
  const firstSegment = to.path.split('/').filter(Boolean)[0]

  if (!firstSegment || !supported.includes(firstSegment)) {
    const targetPath = `/${supported.includes('en') ? 'en' : (supported[0] || 'en')}${to.path === '/' ? '' : to.path}`
    return navigateTo({ path: targetPath, query: to.query, hash: to.hash }, { redirectCode: 302 })
  }
})
