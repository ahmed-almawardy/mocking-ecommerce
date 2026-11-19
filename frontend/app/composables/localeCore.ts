export type LocaleMessages = Record<string, unknown>
export type TextDirection = 'ltr' | 'rtl'

export function resolveLocaleFromPath(path: string, supportedLocales: string[], fallback = 'en') {
  const firstSegment = path.split('/').filter(Boolean)[0]
  return firstSegment && supportedLocales.includes(firstSegment) ? firstSegment : fallback
}

export function localePath(path: string, targetLocale: string, supportedLocales: string[]) {
  const segments = path.split('/').filter(Boolean)
  if (segments.length && supportedLocales.includes(segments[0])) segments.shift()
  const rest = segments.join('/')
  return `/${targetLocale}${rest ? `/${rest}` : ''}`
}

export function readMessage(tree: LocaleMessages, key: string): unknown {
  return key.split('.').reduce<unknown>((value, part) => {
    if (value && typeof value === 'object' && part in (value as Record<string, unknown>)) {
      return (value as Record<string, unknown>)[part]
    }
    return undefined
  }, tree)
}

export function interpolateMessage(value: unknown, variables: Record<string, string | number> = {}) {
  let result = String(value ?? '')
  for (const [name, replacement] of Object.entries(variables)) {
    result = result.replaceAll(`{${name}}`, String(replacement))
  }
  return result
}

export function resolveTextDirection(value: unknown): TextDirection {
  return value === 'rtl' ? 'rtl' : 'ltr'
}

/** Returns dotted leaf paths, useful for checking that a locale is complete. */
export function collectMessagePaths(tree: LocaleMessages, prefix = ''): string[] {
  return Object.entries(tree).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return collectMessagePaths(value as LocaleMessages, path)
    }
    return [path]
  }).sort()
}
