export function useProductAnalytics() {
  const storeApi = useStoreApi()
  const isProductId = (value: string) => /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value)

  function sessionKey() {
    if (!import.meta.client) return undefined
    const key = 'nova-home-analytics-session'
    let value = localStorage.getItem(key)
    if (!value) {
      value = crypto.randomUUID()
      localStorage.setItem(key, value)
    }
    return value
  }

  async function track(productId: string, eventType: 'view' | 'add_to_cart', quantity = 1) {
    if (!import.meta.client || !isProductId(productId)) return
    try {
      await storeApi('/analytics/events', {
        method: 'POST',
        body: { product_id: productId, event_type: eventType, quantity, session_key: sessionKey() },
      })
    } catch {
      // Analytics must never interrupt shopping when tracking is unavailable.
    }
  }

  return { track }
}
