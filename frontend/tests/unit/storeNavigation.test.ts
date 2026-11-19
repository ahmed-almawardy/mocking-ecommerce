import { describe, expect, it } from 'vitest'
import { storeNavigation } from '../../app/composables/storeNavigation'
import { readMessage } from '../../app/composables/localeCore'
import en from '../../app/locales/en.json'
import ar from '../../app/locales/ar.json'

describe('store category navigation', () => {
  it('exposes the six top-level shopping categories shown in the reference menu', () => {
    expect(storeNavigation.map(item => item.key)).toEqual([
      'cookers',
      'smallAppliances',
      'televisions',
      'cooling',
      'airConditioners',
      'washingMachines',
    ])
  })

  it('uses the five-column, two-row small-appliance group structure', () => {
    const smallAppliances = storeNavigation.find(item => item.key === 'smallAppliances')
    expect(smallAppliances?.groups.map(group => group.title)).toEqual([
      'menu.microwave',
      'menu.electricOven',
      'menu.vacuumCleaner',
      'menu.clothesIron',
      'menu.heater',
      'menu.waterAppliances',
      'menu.kitchenAppliances',
      'menu.waterHeaters',
      'menu.fans',
      'menu.airCooler',
    ])
    expect(smallAppliances?.groups).toHaveLength(10)
  })

  it('has a translated heading and link label for every group in English and Arabic', () => {
    for (const locale of [en, ar]) {
      for (const category of storeNavigation) {
        expect(readMessage(locale, `nav.${category.key}`)).toBeTruthy()
        for (const group of category.groups) {
          expect(readMessage(locale, group.title)).toBeTruthy()
          expect(group.items.length).toBeGreaterThan(0)
          for (const item of group.items) expect(readMessage(locale, item.key)).toBeTruthy()
        }
      }
    }
  })
})
