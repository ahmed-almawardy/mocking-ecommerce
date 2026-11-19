<script setup lang="ts">
import { buildCsv } from '../../utils/adminAnalyticsCore'
type PaymentRow = { order_number:string; customer_name:string; customer_email:string|null; provider:string; status:string; reference:string|null; amount:string; currency:string; created_at:string|null }
const api=useAdminApi(),items=ref<PaymentRow[]>([]),total=ref(0),query=ref(''),loading=ref(true),error=ref(''),page=ref(1)
const pageSize=25
const pageCount=computed(()=>Math.max(1,Math.ceil(total.value/pageSize)))
async function load(){loading.value=true;try{const result=await api.get<{items:PaymentRow[];total:number}>('payments',{q:query.value||undefined,page:page.value,page_size:pageSize});items.value=result.items;total.value=result.total}catch(e:any){error.value=e?.data?.detail||'Could not load payment records.'}finally{loading.value=false}}
function searchPayments(){page.value=1;load()}
function changePage(delta:number){page.value=Math.min(pageCount.value,Math.max(1,page.value+delta));load()}
const money=(v:string,c='EGP')=>new Intl.NumberFormat('en-EG',{style:'currency',currency:c,maximumFractionDigits:2}).format(Number(v))
function exportCsv(){const rows=[['Order','Customer','Email','Provider','Status','Reference','Amount','Currency','Created'],...items.value.map(p=>[p.order_number,p.customer_name,p.customer_email||'',p.provider,p.status,p.reference||'',p.amount,p.currency,p.created_at||''])];const csv=buildCsv(rows);const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='nova-home-payments.csv';a.click();URL.revokeObjectURL(url)}
onMounted(load)
</script>
<template>
  <AdminShell active="payments">
    <div class="admin-page-heading"><div><span class="admin-eyebrow">FINANCIAL OPERATIONS</span><h1>Payments</h1><p>Payment provider, transaction references, customer and collection status.</p></div><div class="admin-heading-count"><b>{{ total }}</b><small>payment records</small></div></div>
    <p v-if="error" class="admin-alert error">{{ error }}</p>
    <section class="admin-panel admin-list-panel"><div class="admin-panel-heading"><div><h2>Payment ledger</h2><p>Payment status is updated by verified provider webhooks.</p></div><div class="admin-search-control"><input v-model="query" type="search" placeholder="Order, customer or reference" @keyup.enter="searchPayments"><button @click="searchPayments">Search</button><button class="secondary" @click="exportCsv">↓ CSV</button></div></div>
      <div class="admin-table-scroll"><table class="admin-table"><thead><tr><th>Order</th><th>Customer</th><th>Provider</th><th>Status</th><th>Transaction reference</th><th>Amount</th><th>Date</th></tr></thead><tbody><tr v-for="payment in items" :key="payment.order_number"><td><b>{{ payment.order_number }}</b></td><td><b>{{ payment.customer_name }}</b><small>{{ payment.customer_email || '—' }}</small></td><td>{{ payment.provider }}</td><td><span class="admin-status" :class="`status-${payment.status}`">{{ payment.status }}</span></td><td>{{ payment.reference || '—' }}</td><td><b>{{ money(payment.amount,payment.currency) }}</b></td><td>{{ payment.created_at ? new Date(payment.created_at).toLocaleString('en-EG') : '—' }}</td></tr><tr v-if="!loading&&!items.length"><td colspan="7" class="admin-table-empty">No payment records found.</td></tr></tbody></table><div v-if="loading" class="admin-loading-inline">Loading payments…</div><div class="admin-pagination"><small>Showing {{ total ? (page-1)*pageSize+1 : 0 }}–{{ Math.min(page*pageSize,total) }} of {{ total }} payments</small><div><button :disabled="page<=1 || loading" @click="changePage(-1)">Previous</button><span>Page {{ page }} / {{ pageCount }}</span><button :disabled="page>=pageCount || loading" @click="changePage(1)">Next</button></div></div></div>
    </section>
  </AdminShell>
</template>
