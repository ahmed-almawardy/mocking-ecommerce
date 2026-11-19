import { describe, expect, it } from 'vitest'
import {
  collectMessagePaths,
  interpolateMessage,
  localePath,
  readMessage,
  resolveLocaleFromPath,
  resolveTextDirection,
} from '../../app/composables/localeCore'
import en from '../../app/locales/en.json'
import ar from '../../app/locales/ar.json'

describe('locale routing and message resolution', () => {
  const locales = ['ar', 'en']

  it('resolves supported locale prefixes', () => {
    expect(resolveLocaleFromPath('/en/products', locales)).toBe('en')
    expect(resolveLocaleFromPath('/ar/cart', locales)).toBe('ar')
    expect(resolveLocaleFromPath('/products', locales)).toBe('en')
  })

  it('adds and replaces locale prefixes without duplicating them', () => {
    expect(localePath('/products', 'en', locales)).toBe('/en/products')
    expect(localePath('/en/products', 'ar', locales)).toBe('/ar/products')
    expect(localePath('/ar', 'en', locales)).toBe('/en')
  })

  it('returns localized menu and carousel messages', () => {
    expect(readMessage(en, 'nav.smallAppliances')).toBe('Small Home Appliances')
    expect(readMessage(ar, 'nav.smallAppliances')).toBe('الأجهزة المنزلية الصغيرة')
    expect(readMessage(ar, 'offers.slide1Title')).toBe('بداية الانتعاش في بيتك')
    expect(readMessage(ar, 'offers.paginationLabel')).toBe('اختر عرضاً')
  })

  it('interpolates message placeholders', () => {
    expect(interpolateMessage('Go to offer {number}', { number: 4 })).toBe('Go to offer 4')
    expect(interpolateMessage('تسوق {category}', { category: 'التكييفات' })).toBe('تسوق التكييفات')
  })

  it('reads direction from locale metadata instead of hard-coding language codes', () => {
    expect(resolveTextDirection(en.direction)).toBe('ltr')
    expect(resolveTextDirection(ar.direction)).toBe('rtl')
    expect(resolveTextDirection('anything-else')).toBe('ltr')
  })

  it('keeps English and Arabic translation keys in sync', () => {
    expect(collectMessagePaths(ar)).toEqual(collectMessagePaths(en))
  })
})
