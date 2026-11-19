<script setup lang="ts">
import { buildCsv, formatDashboardDate, getDashboardDateRange, getDashboardGroupBy, type DashboardPeriod } from '../../utils/adminAnalyticsCore'

type Analytics = {
  range: { start: string; end: string; group_by: string }
  summary: { revenue: string; orders: number; paid_orders: number; pending_payments: number; new_customers: number; total_customers: number; active_products: number; low_stock_products: number }
  revenue_series: Array<{ date: string; revenue: string; orders: number }>
  user_series: Array<{ date: string; users: number }>
  payment_distribution: Array<{ status: string; count: number; amount: string }>
  top_selling_products: Array<{ id: string; name: string; image_url: string; units_sold: number; revenue: string }>
  most_viewed_products: Array<{ id: string; name: string; image_url: string; views: number }>
  most_added_to_cart: Array<{ id: string; name: string; image_url: string; quantity: number }>
  recent_orders: Array<{ order_number: string; customer_name: string; customer_email: string; total: string; currency: string; status: string; payment_status: string; created_at: string | null }>
}
const api = useAdminApi()
const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const period = ref<DashboardPeriod>('week')
const initialRange = getDashboardDateRange('week')
const startDate = ref(initialRange.start)
const endDate = ref(initialRange.end)
const analytics = ref<Analytics | null>(null)
const groupBy = computed(() => getDashboardGroupBy(startDate.value, endDate.value))
function setPeriod(value: DashboardPeriod) {
  period.value = value
  if (value === 'custom') return
  const range = getDashboardDateRange(value)
  startDate.value = range.start
  endDate.value = range.end
  // The week/month/year controls must fetch the newly selected range immediately.
  nextTick(() => loadAnalytics())
}
async function loadAnalytics(showSpinner = true) {
  if (startDate.value > endDate.value) {
    error.value = 'The start date must be on or before the end date.'
    return
  }
  if (showSpinner) loading.value = true
  else refreshing.value = true
  error.value = ''
  try {
    analytics.value = await api.get<Analytics>('analytics', {
      start: startDate.value, end: endDate.value, group_by: groupBy.value,
    })
  } catch (exception: any) {
    error.value = exception?.data?.detail || 'Analytics could not be loaded. Check your administrator session and API.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}
watch([startDate, endDate], () => {
  if (period.value === 'custom') loadAnalytics(false)
})
onMounted(() => loadAnalytics())
const summary = computed(() => analytics.value?.summary || {
  revenue: '0', orders: 0, paid_orders: 0, pending_payments: 0,
  new_customers: 0, total_customers: 0, active_products: 0, low_stock_products: 0,
})
const money = (value: string | number) => new Intl.NumberFormat('en-EG', { style: 'currency', currency: 'EGP', maximumFractionDigits: 0 }).format(Number(value || 0))
const formatDay = formatDashboardDate
const revenueRows = computed(() => (analytics.value?.revenue_series || []).map(row => ({
  label: formatDay(row.date), value: Number(row.revenue), detail: `${row.orders} paid orders`,
})))
const userRows = computed(() => (analytics.value?.user_series || []).map(row => ({ label: formatDay(row.date), value: row.users, detail: `${row.users} new customer registrations` })))
const paymentRows = computed(() => (analytics.value?.payment_distribution || []).map(row => ({
  label: row.status.replaceAll('_', ' '), value: row.count, detail: `${money(row.amount)} transaction value`,
})))
const bestSellerRows = computed(() => (analytics.value?.top_selling_products || []).map(row => ({
  label: row.name, value: row.units_sold, detail: `${money(row.revenue)} sales revenue`,
})))
const mostViewedRows = computed(() => (analytics.value?.most_viewed_products || []).map(row => ({
  label: row.name, value: row.views, detail: 'Product detail page views',
})))
const mostCartedRows = computed(() => (analytics.value?.most_added_to_cart || []).map(row => ({
  label: row.name, value: row.quantity, detail: 'Units added to carts',
})))
function exportReport() {
  if (!analytics.value) return
  const reportRows: Array<Array<string | number>> = [
    ['NOVA HOME analytics', `${startDate.value} to ${endDate.value}`], [],
    ['Metric', 'Value'], ['Revenue (EGP)', summary.value.revenue], ['Orders', summary.value.orders],
    ['Paid orders', summary.value.paid_orders], ['Pending payments', summary.value.pending_payments],
    ['New customers', summary.value.new_customers], ['Total customers', summary.value.total_customers],
    ['Active products', summary.value.active_products], ['Low stock products', summary.value.low_stock_products], [],
    ['Revenue date', 'Revenue EGP', 'Paid orders'],
    ...analytics.value.revenue_series.map(row => [row.date, row.revenue, row.orders]), [],
    ['Payment status', 'Count', 'Amount EGP'],
    ...analytics.value.payment_distribution.map(row => [row.status, row.count, row.amount]),
  ]
  const blob = new Blob([buildCsv(reportRows)], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `nova-home-analytics-${startDate.value}-${endDate.value}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <AdminShell active="dashboard">
    <div class="admin-page-heading">
      <div><span class="admin-eyebrow">STORE PERFORMANCE</span><h1>Dashboard</h1><p>Welcome back. Here's what is happening with your store.</p></div>
      <div class="admin-page-actions"><button class="admin-secondary-button" :disabled="refreshing" @click="loadAnalytics(false)">{{ refreshing ? 'Refreshing…' : '↻ Refresh' }}</button><button class="admin-primary-button compact" :disabled="!analytics" @click="exportReport">↓ Export report</button></div>
    </div>

    <section class="admin-filter-bar">
      <div class="admin-period-tabs" role="group" aria-label="Analytics period">
        <button v-for="item in (['week','month','year','custom'] as const)" :key="item" :class="{ active: period === item }" @click="setPeriod(item)">{{ item === 'week' ? 'Week' : item === 'month' ? 'Month' : item === 'year' ? 'Year' : 'Custom' }}</button>
      </div>
      <div class="admin-date-controls"><label>From<input v-model="startDate" type="date" @focus="period = 'custom'"></label><label>To<input v-model="endDate" type="date" @focus="period = 'custom'"></label><button class="admin-secondary-button" @click="loadAnalytics()">Apply</button></div>
    </section>

    <p v-if="error" class="admin-alert error">{{ error }}</p>
    <div v-if="loading" class="admin-loading-inline"><span class="admin-spinner" /> Loading store analytics…</div>
    <template v-else>
      <section class="admin-kpi-grid">
        <article class="admin-kpi-card"><span class="admin-kpi-icon"><AdminIcon name="revenue" :size="22" /></span><div><small>Paid revenue</small><strong>{{ money(summary.revenue) }}</strong><em>{{ summary.paid_orders }} paid orders in range</em></div><span class="admin-kpi-trend">EGP</span></article>
        <article class="admin-kpi-card"><span class="admin-kpi-icon"><AdminIcon name="orders" :size="22" /></span><div><small>Total orders</small><strong>{{ summary.orders.toLocaleString() }}</strong><em>{{ summary.pending_payments }} pending payments</em></div><span class="admin-kpi-trend">#</span></article>
        <article class="admin-kpi-card"><span class="admin-kpi-icon"><AdminIcon name="customers" :size="22" /></span><div><small>New customers</small><strong>{{ summary.new_customers.toLocaleString() }}</strong><em>{{ summary.total_customers.toLocaleString() }} registered customers total</em></div><span class="admin-kpi-trend">+</span></article>
        <article class="admin-kpi-card"><span class="admin-kpi-icon"><AdminIcon name="products" :size="22" /></span><div><small>Active products</small><strong>{{ summary.active_products.toLocaleString() }}</strong><em>{{ summary.low_stock_products }} products low in stock</em></div><span class="admin-kpi-trend">◎</span></article>
      </section>

      <section class="admin-dashboard-grid main-charts">
        <AdminChartCard title="Sales overview" subtitle="Paid revenue over the selected period · EGP" :rows="revenueRows" value-prefix="EGP " filename="nova-home-sales" />
        <AdminChartCard title="New customers" subtitle="Customer registrations over time" :rows="userRows" mode="bar" filename="nova-home-customer-signups" />
      </section>

      <section class="admin-dashboard-grid analytics-lower-grid">
        <AdminChartCard title="Payment statistics" subtitle="Payment ledger states · transaction count" :rows="paymentRows" mode="donut" filename="nova-home-payment-statistics" />
        <AdminChartCard title="Best-selling products" subtitle="Paid order units sold in this period" :rows="bestSellerRows" mode="bar" filename="nova-home-best-selling-products" />
      </section>

      <section class="admin-dashboard-grid product-rank-grid">
        <AdminChartCard title="Most viewed products" subtitle="Product detail page views in this period" :rows="mostViewedRows" mode="bar" filename="nova-home-most-viewed-products" />
        <AdminChartCard title="Most added to cart" subtitle="Units added to customer carts in this period" :rows="mostCartedRows" mode="bar" filename="nova-home-most-added-to-cart" />
      </section>

      <section class="admin-panel admin-recent-panel">
        <div class="admin-panel-heading"><div><h2>Recent orders</h2><p>Latest customer orders in the selected period</p></div><button class="admin-text-link" @click="navigateTo('/admin/orders')">View all orders →</button></div>
        <div class="admin-table-scroll"><table class="admin-table"><thead><tr><th>Order</th><th>Customer</th><th>Amount</th><th>Order status</th><th>Payment</th><th>Date</th></tr></thead><tbody><tr v-for="order in analytics?.recent_orders || []" :key="order.order_number"><td><b>{{ order.order_number }}</b></td><td><span>{{ order.customer_name }}</span><small>{{ order.customer_email }}</small></td><td><b>{{ money(order.total) }}</b></td><td><span class="admin-status" :class="`status-${order.status}`">{{ order.status.replaceAll('_',' ') }}</span></td><td><span class="admin-status" :class="`status-${order.payment_status}`">{{ order.payment_status }}</span></td><td>{{ order.created_at ? new Date(order.created_at).toLocaleString('en-EG') : '—' }}</td></tr><tr v-if="!analytics?.recent_orders.length"><td colspan="6" class="admin-table-empty">No orders found for this period.</td></tr></tbody></table></div>
      </section>
      <p class="admin-data-note">Analytics are calculated from persisted orders, customer registrations, payment states and tracked product events. Product views and cart activity start accumulating after the analytics tracking update is deployed.</p>
    </template>
  </AdminShell>
</template>
