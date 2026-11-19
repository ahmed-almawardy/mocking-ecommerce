import { addCartProduct, cartCount, cartSubtotal, removeCartProduct, updateCartProduct } from './cartCore'
import type { CartLine, CartProduct } from './cartCore'

export type { CartLine, CartProduct } from './cartCore'

export function useCart() {
  const lines = useState<CartLine[]>('nova-cart-lines', () => [])
  const ready = useState<boolean>('nova-cart-ready', () => false)

  onMounted(() => {
    if (ready.value) return
    try {
      const stored = localStorage.getItem('nova-home-cart')
      if (stored) lines.value = JSON.parse(stored) as CartLine[]
    } catch {
      lines.value = []
    }
    ready.value = true
  })

  const persist = () => {
    if (import.meta.client) localStorage.setItem('nova-home-cart', JSON.stringify(lines.value))
  }

  const count = computed(() => cartCount(lines.value))
  const subtotal = computed(() => cartSubtotal(lines.value))

  function add(product: CartProduct, quantity = 1) {
    lines.value = addCartProduct(lines.value, product, quantity)
    persist()
  }

  function update(productId: string, quantity: number) {
    lines.value = updateCartProduct(lines.value, productId, quantity)
    persist()
  }

  function remove(productId: string) {
    lines.value = removeCartProduct(lines.value, productId)
    persist()
  }

  function clear() {
    lines.value = []
    persist()
  }

  return { lines, count, subtotal, add, update, remove, clear }
}
