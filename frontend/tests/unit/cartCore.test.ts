import { describe, expect, it } from 'vitest'
import { addCartProduct, cartCount, cartSubtotal, removeCartProduct, updateCartProduct } from '../../app/composables/cartCore'
import type { CartProduct } from '../../app/composables/cartCore'

const kettle: CartProduct = {
  id: 'p-1', slug: 'test-kettle', name: 'Test Kettle', price: '1250.50', stock_qty: 5,
}
const fan: CartProduct = {
  id: 'p-2', slug: 'test-fan', name: 'Test Fan', price: 2000, stock_qty: 3,
}

describe('cartCore', () => {
  it('adds a product and calculates count and subtotal', () => {
    const lines = addCartProduct([], kettle, 2)
    expect(cartCount(lines)).toBe(2)
    expect(cartSubtotal(lines)).toBe(2501)
  })

  it('merges duplicate products and caps quantity at 20', () => {
    const once = addCartProduct([], kettle, 12)
    const twice = addCartProduct(once, kettle, 12)
    expect(twice).toHaveLength(1)
    expect(twice[0]?.quantity).toBe(20)
  })

  it('updates or removes a line when its quantity reaches zero', () => {
    const lines = addCartProduct([], kettle)
    expect(updateCartProduct(lines, kettle.id, 4)[0]?.quantity).toBe(4)
    expect(updateCartProduct(lines, kettle.id, 0)).toEqual([])
    expect(updateCartProduct(lines, kettle.id, Number.NaN)).toEqual(lines)
  })

  it('removes only the selected product and retains other lines', () => {
    const lines = addCartProduct(addCartProduct([], kettle), fan)
    const next = removeCartProduct(lines, kettle.id)
    expect(next).toHaveLength(1)
    expect(next[0]?.product.id).toBe(fan.id)
  })
})
