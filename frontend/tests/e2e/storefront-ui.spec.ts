import { expect, test } from '@playwright/test'

test.describe('NOVA HOME storefront UI', () => {
  test('renders the English home page and primary shopping navigation', async ({ page }) => {
    await page.goto('/en')
    await expect(page.locator('html')).toHaveAttribute('lang', 'en')
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr')
    await expect(page.getByRole('heading', { name: /make room for\s*better living/i })).toBeVisible()
    await expect(page.getByRole('navigation').getByRole('link', { name: 'Cookers' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Shop by category' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Featured products' })).toBeVisible()
    const navBottom = await page.locator('.category-nav').evaluate(element => element.getBoundingClientRect().bottom)
    const offerTop = await page.locator('.featured-offers').evaluate(element => element.getBoundingClientRect().top)
    expect(offerTop).toBeGreaterThanOrEqual(navBottom)
  })

  test('opens the category mega menu on hover and presents grouped links', async ({ page }) => {
    await page.goto('/en')
    await page.getByRole('navigation').getByRole('link', { name: 'Small Home Appliances' }).hover()
    await expect(page.getByRole('heading', { name: 'Microwave' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Convection Microwave' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Kitchen Appliances' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Coffee Machine' })).toBeVisible()
    const gridColumnCount = await page.locator('.mega-menu-grid').evaluate(element => getComputedStyle(element).gridTemplateColumns.split(' ').length)
    expect(gridColumnCount).toBe(5)
  })

  test('opens the mega menu on mobile using its explicit toggle control', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/en')
    await page.getByRole('button', { name: 'Open Small Home Appliances menu' }).click()
    await expect(page.getByRole('heading', { name: 'Microwave' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Open Small Home Appliances menu' })).toHaveAttribute('aria-expanded', 'true')
  })

  test('shows four offer slides with arrow and dot navigation', async ({ page }) => {
    await page.goto('/en')
    const slides = page.locator('.featured-offer-slide')
    await expect(slides).toHaveCount(4)
    await expect(page.getByRole('button', { name: 'Next offer' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Previous offer' })).toBeVisible()
    const dots = page.locator('.offer-dot')
    await expect(dots).toHaveCount(4)
    await page.getByRole('button', { name: 'Go to offer 3' }).click()
    await expect(slides.nth(2)).toHaveAttribute('aria-hidden', 'false')
    await page.getByRole('button', { name: 'Next offer' }).click()
    await expect(slides.nth(3)).toHaveAttribute('aria-hidden', 'false')
    await page.getByRole('button', { name: 'Previous offer' }).click()
    await expect(slides.nth(2)).toHaveAttribute('aria-hidden', 'false')
    await expect(slides.nth(0)).toHaveAttribute('inert', '')
    await page.getByRole('button', { name: 'Go to offer 4' }).click()
    await page.getByRole('button', { name: 'Next offer' }).click()
    await expect(slides.nth(0)).toHaveAttribute('aria-hidden', 'false')
    await page.getByRole('button', { name: 'Previous offer' }).click()
    await expect(slides.nth(3)).toHaveAttribute('aria-hidden', 'false')
  })

  test('automatically advances the offer carousel every five seconds', async ({ page }) => {
    await page.clock.install()
    await page.goto('/en')
    const slides = page.locator('.featured-offer-slide')
    await expect(slides.nth(0)).toHaveAttribute('aria-hidden', 'false')
    await page.clock.fastForward(5100)
    await expect(slides.nth(1)).toHaveAttribute('aria-hidden', 'false')
  })

  test('switches to Arabic and applies RTL layout', async ({ page }) => {
    await page.goto('/en')
    await page.getByRole('link', { name: 'العربية' }).click()
    await expect(page).toHaveURL(/\/ar$/)
    await expect(page.locator('html')).toHaveAttribute('lang', 'ar')
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
    await expect(page.getByRole('navigation').getByRole('link', { name: 'الأجهزة المنزلية الصغيرة' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'تسوق حسب القسم' })).toBeVisible()
  })

  test('shows registration form and browser-level required-field validation', async ({ page }) => {
    await page.route('**/api/v1/auth/providers', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ providers: {
        google: { configured: false, available: false, reason: 'Provider credentials are not configured on the server.', callback_url: 'http://localhost:8000/api/v1/auth/google/callback' },
        facebook: { configured: false, available: false, reason: 'Provider credentials are not configured on the server.', callback_url: 'http://localhost:8000/api/v1/auth/facebook/callback' },
        apple: { configured: false, available: false, reason: 'Provider credentials are not configured on the server.', callback_url: 'http://localhost:8000/api/v1/auth/apple/callback' },
      } }),
    }))
    await page.goto('/en/auth/register')
    await expect(page.getByRole('heading', { name: 'Create your account.' })).toBeVisible()
    await expect(page.getByLabel('Full name')).toBeVisible()
    await expect(page.getByLabel('Email address')).toBeVisible()
    await expect(page.getByLabel('Mobile number')).toBeVisible()
    await expect(page.getByLabel('Password')).toBeVisible()
    await expect(page.getByRole('button', { name: /create account/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /google/i })).toBeDisabled()
    await expect(page.getByText(/Instagram personal accounts cannot be used/i)).toBeVisible()
  })
})
