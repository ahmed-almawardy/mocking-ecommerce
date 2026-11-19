<script setup lang="ts">
type OrderRow = { id:string; order_number:string; customer_name:string; customer_email:string|null; status:string; payment_status:string; subtotal:string; shipping_fee:string; total:string; currency:string; payment_provider:string; payment_reference:string|null; created_at:string|null }
const api = useAdminApi()
const items=ref<OrderRow[]>([]),total=ref(0),query=ref(''),loading=ref(true),error=ref(''),page=ref(1)
const pageSize=25
const pageCount=computed(()=>Math.max(1,Math.ceil(total.value/pageSize)))
async function load(){loading.value=true;try{const result=await api.get<{items:OrderRow[];total:number}>('orders',{q:query.value||undefined,page:page.value,page_size:pageSize});items.value=result.items;total.value=result.total}catch(e:any){error.value=e?.data?.detail||'Could not load orders.'}finally{loading.value=false}}
function searchOrders(){page.value=1;load()}
function changePage(delta:number){page.value=Math.min(pageCount.value,Math.max(1,page.value+delta));load()}
const money=(v:string,c='EGP')=>new Intl.NumberFormat('en-EG',{style:'currency',currency:c,maximumFractionDigits:0}).format(Number(v))
onMounted(load)
</script>
<template>
  <AdminShell active="orders">
    <div class="admin-page-heading"><div><span class="admin-eyebrow">FULFILLMENT</span><h1>Orders</h1><p>Review customer purchases, order status and payment progress.</p></div><div class="admin-heading-count"><b>{{ total }}</b><small>orders</small></div></div>
    <p v-if="error" class="admin-alert error">{{ error }}</p>
    <section class="admin-panel admin-list-panel"><div class="admin-panel-heading"><div><h2>All orders</h2><p>Search by order number or customer name.</p></div><div class="admin-search-control"><input v-model="query" placeholder="Order or customer" @keyup.enter="searchOrders"><button @click="searchOrders">Search</button></div></div>
      <div class="admin-table-scroll"><table class="admin-table"><thead><tr><th>Order</th><th>Customer</th><th>Order status</th><th>Payment</th><th>Provider / reference</th><th>Total</th><th>Placed</th></tr></thead><tbody><tr v-for="order in items" :key="order.id"><td><b>{{ order.order_number }}</b></td><td><b>{{ order.customer_name }}</b><small>{{ order.customer_email || '—' }}</small></td><td><span class="admin-status" :class="`status-${order.status}`">{{ order.status.replaceAll('_',' ') }}</span></td><td><span class="admin-status" :class="`status-${order.payment_status}`">{{ order.payment_status }}</span></td><td><b>{{ order.payment_provider }}</b><small>{{ order.payment_reference || 'Awaiting provider reference' }}</small></td><td><b>{{ money(order.total,order.currency) }}</b></td><td>{{ order.created_at ? new Date(order.created_at).toLocaleString('en-EG') : '—' }}</td></tr><tr v-if="!loading&&!items.length"><td colspan="7" class="admin-table-empty">No orders found.</td></tr></tbody></table><div v-if="loading" class="admin-loading-inline">Loading orders…</div><div class="admin-pagination"><small>Showing {{ total ? (page-1)*pageSize+1 : 0 }}–{{ Math.min(page*pageSize,total) }} of {{ total }} orders</small><div><button :disabled="page<=1 || loading" @click="changePage(-1)">Previous</button><span>Page {{ page }} / {{ pageCount }}</span><button :disabled="page>=pageCount || loading" @click="changePage(1)">Next</button></div></div></div>
    </section>
  </AdminShell>
</template>
