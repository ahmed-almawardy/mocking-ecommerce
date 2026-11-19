import { expect, test } from '@playwright/test'

test.describe('NOVA HOME shopping flows', () => {
  test('adds a featured product to the cart and persists it after navigation', async ({ page }) => {
    await page.goto('/')
    const addButton = page.getByRole('button', { name: /add to cart/i }).first()
    await expect(addButton).toBeVisible()
    await addButton.click()
    await page.goto('/cart')
    await expect(page.getByRole('heading', { name: 'Your shopping cart' })).toBeVisible()
    await expect(page.getByText('Inverter Air Conditioner 1.5 HP')).toBeVisible()
    await expect(page.getByRole('link', { name: /continue to checkout/i })).toBeVisible()
  })

  test('filters the fallback catalog using the product search', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('searchbox', { name: 'Search products' }).fill('air conditioner')
    await page.getByRole('searchbox', { name: 'Search products' }).press('Enter')
    await expect(page).toHaveURL(/\/products\?q=air/)
    await expect(page.getByRole('heading', { name: /search: air conditioner/i })).toBeVisible()
    await expect(page.getByText('Inverter Air Conditioner 1.5 HP')).toBeVisible()
  })
})
