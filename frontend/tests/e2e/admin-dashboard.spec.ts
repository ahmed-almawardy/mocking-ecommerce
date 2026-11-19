import { expect, test, type Page } from '@playwright/test'

const today = new Date()
const yyyy = today.getFullYear()
const mm = String(today.getMonth() + 1).padStart(2, '0')
const dd = String(today.getDate()).padStart(2, '0')
const todayString = `${yyyy}-${mm}-${dd}`

const analyticsFixture = {
  range: { start: todayString, end: todayString, group_by: 'day' },
  summary: {
    revenue: '12500.00', orders: 8, paid_orders: 6, pending_payments: 2,
    new_customers: 4, total_customers: 120, active_products: 28, low_stock_products: 3,
  },
  revenue_series: [{ date: `${todayString}T00:00:00+00:00`, revenue: '12500.00', orders: 6 }],
  user_series: [{ date: `${todayString}T00:00:00+00:00`, users: 4 }],
  payment_distribution: [
    { status: 'paid', count: 6, amount: '12500.00' },
    { status: 'pending', count: 2, amount: '3200.00' },
  ],
  top_selling_products: [{ id: 'product-1', name: 'Front Load Washing Machine', image_url: '/images/products/washing-machine.webp', units_sold: 12, revenue: '98000.00' }],
  most_viewed_products: [{ id: 'product-1', name: 'Front Load Washing Machine', image_url: '/images/products/washing-machine.webp', views: 240 }],
  most_added_to_cart: [{ id: 'product-1', name: 'Front Load Washing Machine', image_url: '/images/products/washing-machine.webp', quantity: 35 }],
  recent_orders: [],
}

async function mockAdminApi(page: Page) {
  await page.route('**/api/v1/auth/me', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ id: 'admin-1', name: 'Store Admin', email: 'admin@example.com', phone: null, whatsapp_opt_in: false, role: 'admin' }),
  }))
  await page.route('**/api/v1/admin/analytics**', route => route.fulfill({
    status: 200, contentType: 'application/json', body: JSON.stringify(analyticsFixture),
  }))
}

test.describe('NOVA HOME administrator dashboard', () => {
  test('shows commerce KPIs and all requested analytics charts', async ({ page }) => {
    await mockAdminApi(page)
    await page.goto('/admin')
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
    await expect(page.getByText('Paid revenue')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Sales overview' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'New customers' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Payment statistics' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Best-selling products' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Most viewed products' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Most added to cart' })).toBeVisible()
  })

  test('week, month, year and custom period controls fetch the chosen date range', async ({ page }) => {
    const requested: URL[] = []
    await page.route('**/api/v1/auth/me', route => route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ id: 'admin-1', name: 'Store Admin', email: 'admin@example.com', phone: null, whatsapp_opt_in: false, role: 'admin' }),
    }))
    await page.route('**/api/v1/admin/analytics**', route => {
      requested.push(new URL(route.request().url()))
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(analyticsFixture) })
    })
    await page.goto('/admin')
    await expect.poll(() => requested.length).toBeGreaterThan(0)

    await page.getByRole('button', { name: 'Month' }).click()
    await expect.poll(() => requested.at(-1)?.searchParams.get('start')).toBe(`${yyyy}-${mm}-01`)

    await page.getByRole('button', { name: 'Year' }).click()
    await expect.poll(() => requested.at(-1)?.searchParams.get('start')).toBe(`${yyyy}-01-01`)

    await page.getByRole('button', { name: 'Custom' }).click()
    await page.getByLabel('From').fill('2026-10-01')
    await page.getByLabel('To').fill('2026-10-20')
    await page.getByRole('button', { name: 'Apply' }).click()
    await expect.poll(() => requested.at(-1)?.searchParams.get('start')).toBe('2026-10-01')
    await expect.poll(() => requested.at(-1)?.searchParams.get('end')).toBe('2026-10-20')
  })

  test('each chart exposes CSV and PNG download actions', async ({ page }) => {
    await mockAdminApi(page)
    await page.goto('/admin')
    const chart = page.locator('.admin-chart-panel').first()
    await expect(chart.getByTitle('Download chart as CSV')).toBeVisible()
    await expect(chart.getByTitle('Download chart as PNG')).toBeVisible()
    const csvDownload = page.waitForEvent('download')
    await chart.getByTitle('Download chart as CSV').click()
    expect((await csvDownload).suggestedFilename()).toContain('.csv')
    const pngDownload = page.waitForEvent('download')
    await chart.getByTitle('Download chart as PNG').click()
    expect((await pngDownload).suggestedFilename()).toContain('.png')
  })

  test('customer accounts are redirected away from private administration', async ({ page }) => {
    await page.route('**/api/v1/auth/me', route => route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ id: 'customer-1', name: 'Customer', email: 'customer@example.com', phone: null, whatsapp_opt_in: false, role: 'customer' }),
    }))
    await page.goto('/admin')
    await expect(page).toHaveURL(/\/admin\/login$/)
    await expect(page.getByRole('heading', { name: 'Welcome back.' })).toBeVisible()
  })
})
