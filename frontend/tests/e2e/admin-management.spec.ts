import { expect, test, type Page } from '@playwright/test'
import { Buffer } from 'node:buffer'

async function authenticateAsAdmin(page: Page) {
  await page.route('**/api/v1/auth/me', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      id: 'admin-1', name: 'Store Admin', email: 'admin@example.com',
      phone: null, whatsapp_opt_in: false, role: 'admin',
    }),
  }))
}

const emptyList = { items: [], total: 0, page: 1, page_size: 25 }

test.describe('NOVA HOME admin catalog and commerce management', () => {
  test('creates a product and uploads a real image asset', async ({ page }) => {
    await authenticateAsAdmin(page)
    const savedProducts: Array<Record<string, unknown>> = []

    await page.route('**/api/v1/admin/products**', async route => {
      if (route.request().method() === 'POST') {
        const payload = route.request().postDataJSON() as Record<string, unknown>
        savedProducts.push(payload)
        await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({
          id: 'product-1', ...payload, created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
        }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({
        ...emptyList, items: savedProducts, total: savedProducts.length,
      }) })
    })
    await page.route('**/api/v1/admin/media', route => route.fulfill({
      status: 201, contentType: 'application/json',
      body: JSON.stringify({ url: '/media/admin-test-product.webp', filename: 'admin-test-product.webp', content_type: 'image/webp', size: 1024 }),
    }))

    await page.goto('/admin/products')
    await page.getByLabel('Product name').fill('Admin Test Blender')
    await page.getByLabel('SKU').fill('NH-E2E-BL-01')
    await page.getByLabel('URL slug').fill('admin-test-blender')
    await page.getByLabel('Price (EGP)').fill('1499')
    await page.getByLabel('Stock quantity').fill('8')
    await page.locator('input[type="file"]').setInputFiles({
      name: 'blender.webp', mimeType: 'image/webp', buffer: Buffer.from('RIFF0000WEBPtest-image'),
    })
    await expect(page.locator('.admin-image-preview img')).toHaveAttribute('src', '/media/admin-test-product.webp')
    await page.getByRole('button', { name: 'Create product' }).click()
    await expect.poll(() => savedProducts.length).toBe(1)
    expect(savedProducts[0]?.image_url).toBe('/media/admin-test-product.webp')
    await expect(page.getByText('1 products registered')).toBeVisible()
  })

  test('creates a bilingual offer campaign', async ({ page }) => {
    await authenticateAsAdmin(page)
    const savedOffers: Array<Record<string, unknown>> = []
    await page.route('**/api/v1/admin/offers**', async route => {
      if (route.request().method() === 'POST') {
        const payload = route.request().postDataJSON() as Record<string, unknown>
        savedOffers.push(payload)
        await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ id: 'offer-1', ...payload }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: savedOffers }) })
    })

    await page.goto('/admin/offers')
    await page.getByLabel('Offer title', { exact: true }).fill('Winter appliance offers')
    await page.getByLabel('Subtitle (English)').fill('Save on selected home appliances')
    await page.getByLabel('Offer title (Arabic)').fill('عروض الأجهزة الشتوية')
    await page.getByLabel('Subtitle (Arabic)').fill('وفر على الأجهزة المنزلية المختارة')
    await page.getByRole('button', { name: 'Create offer' }).click()
    await expect.poll(() => savedOffers.length).toBe(1)
    expect(savedOffers[0]?.title_ar).toBe('عروض الأجهزة الشتوية')
    await expect(page.getByRole('heading', { name: 'Winter appliance offers' })).toBeVisible()
  })

  test('shows customers, orders and payments from their own admin data endpoints', async ({ page }) => {
    await authenticateAsAdmin(page)
    await page.route('**/api/v1/admin/customers**', route => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify({
        ...emptyList, total: 1, items: [{ id: 'customer-1', name: 'Test Customer', email: 'buyer@example.com', phone: '+201000000000', whatsapp_opt_in: true, is_active: true, created_at: new Date().toISOString() }],
      }),
    }))
    await page.route('**/api/v1/admin/orders**', route => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify({
        ...emptyList, total: 1, items: [{ id: 'order-1', order_number: 'NH-E2E-001', customer_name: 'Test Customer', customer_email: 'buyer@example.com', status: 'processing', payment_status: 'paid', subtotal: '1000', shipping_fee: '0', total: '1000', currency: 'EGP', payment_provider: 'kashier', payment_reference: 'KSH-001', created_at: new Date().toISOString() }],
      }),
    }))
    await page.route('**/api/v1/admin/payments**', route => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify({
        ...emptyList, total: 1, items: [{ order_number: 'NH-E2E-001', customer_name: 'Test Customer', customer_email: 'buyer@example.com', provider: 'kashier', status: 'paid', reference: 'KSH-001', amount: '1000', currency: 'EGP', created_at: new Date().toISOString() }],
      }),
    }))

    await page.goto('/admin/customers')
    await expect(page.getByText('buyer@example.com')).toBeVisible()
    await page.goto('/admin/orders')
    await expect(page.getByText('NH-E2E-001')).toBeVisible()
    await page.goto('/admin/payments')
    await expect(page.getByText('KSH-001')).toBeVisible()
  })
})
