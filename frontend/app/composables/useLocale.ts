import { computed } from 'vue'
import { useRoute } from '#imports'
import {
  collectMessagePaths,
  interpolateMessage,
  localePath as buildLocalePath,
  readMessage,
  resolveLocaleFromPath,
  resolveTextDirection,
} from './localeCore'

type MessageTree = Record<string, unknown>

// Add a locale by creating app/locales/<locale>.json and rebuilding the Nuxt app.
// The locale code becomes its route prefix automatically (for example fr.json -> /fr).
const localeModules = import.meta.glob('../locales/*.json', {
  eager: true,
  import: 'default',
}) as Record<string, MessageTree>

const messages: Record<string, MessageTree> = Object.fromEntries(
  Object.entries(localeModules).map(([filePath, value]) => {
    const locale = filePath.split('/').pop()?.replace(/\.json$/, '') || 'en'
    return [locale, value]
  }),
)

export function availableLocales() {
  return Object.keys(messages).sort()
}

export function useLocale() {
  const route = useRoute()
  const locales = availableLocales()
  const fallbackLocale = locales.includes('en') ? 'en' : locales[0]
  const locale = computed(() => resolveLocaleFromPath(route.path, locales, fallbackLocale))
  const direction = computed(() => resolveTextDirection(messages[locale.value]?.direction))
  const isRtl = computed(() => direction.value === 'rtl')

  function t(key: string, values: Record<string, string | number> = {}) {
    const selected = readMessage(messages[locale.value] || {}, key)
    const fallback = readMessage(messages[fallbackLocale] || {}, key)
    return interpolateMessage(selected ?? fallback ?? key, values)
  }

  function localePath(path: string, targetLocale = locale.value) {
    return buildLocalePath(path, targetLocale, locales)
  }

  function switchLocalePath(targetLocale: string) {
    return localePath(route.path, targetLocale)
  }

  function localeLabel(code: string) {
    const configuredName = messages[code]?.languageName
    return typeof configuredName === 'string' && configuredName.trim() ? configuredName : code.toUpperCase()
  }

  function missingMessagePaths(code: string) {
    const base = collectMessagePaths(messages[fallbackLocale] || {})
    const target = new Set(collectMessagePaths(messages[code] || {}))
    return base.filter(path => !target.has(path))
  }

  return {
    locale,
    direction,
    isRtl,
    t,
    localePath,
    switchLocalePath,
    localeLabel,
    availableLocales: locales,
    missingMessagePaths,
  }
}
