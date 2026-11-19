export interface CartProduct {
  id: string
  slug: string
  name: string
  price: number | string
  image_url?: string
  category?: string
  stock_qty?: number
}

export interface CartLine {
  product: CartProduct
  quantity: number
}

const MAX_LINE_QUANTITY = 20

export function addCartProduct(
  lines: CartLine[],
  product: CartProduct,
  quantity = 1,
): CartLine[] {
  const requested = Number.isFinite(quantity) ? Math.floor(quantity) : 1
  const safeQuantity = Math.max(1, Math.min(requested, MAX_LINE_QUANTITY))
  const existing = lines.find((line) => line.product.id === product.id)
  if (existing) {
    return lines.map((line) => line.product.id === product.id
      ? { ...line, quantity: Math.min(line.quantity + safeQuantity, MAX_LINE_QUANTITY) }
      : line)
  }
  return [...lines, { product, quantity: safeQuantity }]
}

export function updateCartProduct(lines: CartLine[], productId: string, quantity: number): CartLine[] {
  if (!Number.isFinite(quantity)) return lines
  if (quantity <= 0) return lines.filter((line) => line.product.id !== productId)
  const safeQuantity = Math.min(Math.floor(quantity), MAX_LINE_QUANTITY)
  return lines.map((line) => line.product.id === productId
    ? { ...line, quantity: safeQuantity }
    : line)
}

export function removeCartProduct(lines: CartLine[], productId: string): CartLine[] {
  return lines.filter((line) => line.product.id !== productId)
}

export function cartCount(lines: CartLine[]): number {
  return lines.reduce((sum, line) => sum + line.quantity, 0)
}

export function cartSubtotal(lines: CartLine[]): number {
  return lines.reduce((sum, line) => sum + Number(line.product.price) * line.quantity, 0)
}
