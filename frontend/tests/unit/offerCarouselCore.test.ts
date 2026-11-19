import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { offerSlides, offerTrackOffset, wrapOfferIndex } from '../../app/composables/offerCarouselCore'

const publicDirectory = fileURLToPath(new URL('../../public/', import.meta.url))

describe('featured offers carousel model', () => {
  it('contains exactly four unique local offer images', () => {
    expect(offerSlides).toHaveLength(4)
    expect(new Set(offerSlides.map(slide => slide.image)).size).toBe(4)
    expect(offerSlides.every(slide => slide.image.startsWith('/images/offers/'))).toBe(true)
    for (const slide of offerSlides) {
      expect(existsSync(join(publicDirectory, slide.image.replace(/^\//, '')))).toBe(true)
    }
  })

  it('wraps previous and next navigation at both ends', () => {
    expect(wrapOfferIndex(0 - 1)).toBe(3)
    expect(wrapOfferIndex(3 + 1)).toBe(0)
    expect(wrapOfferIndex(7)).toBe(3)
  })

  it('uses a leftward track offset for each subsequent slide', () => {
    expect(offerTrackOffset(0)).toBe('translate3d(-0%, 0, 0)')
    expect(offerTrackOffset(1)).toBe('translate3d(-100%, 0, 0)')
    expect(offerTrackOffset(2)).toBe('translate3d(-200%, 0, 0)')
    expect(offerTrackOffset(3)).toBe('translate3d(-300%, 0, 0)')
  })

  it('rejects a zero-slide carousel instead of dividing by zero', () => {
    expect(() => wrapOfferIndex(0, 0)).toThrow(RangeError)
  })
})
