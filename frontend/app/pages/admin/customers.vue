<script setup lang="ts">
import { buildCsv } from '../../utils/adminAnalyticsCore'
type Customer = { id:string; name:string; email:string|null; phone:string|null; whatsapp_opt_in:boolean; is_active:boolean; created_at:string|null }
const api = useAdminApi()
const items = ref<Customer[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 25
const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const query = ref('')
const loading = ref(true)
const error = ref('')
async function load() {
  loading.value = true
  try { const result = await api.get<{items:Customer[];total:number}>('customers', { q:query.value || undefined, page:page.value, page_size:pageSize }); items.value=result.items; total.value=result.total }
  catch (e:any) { error.value=e?.data?.detail || 'Could not load customers.' }
  finally { loading.value=false }
}
function searchCustomers() { page.value=1; load() }
function changePage(delta:number) { page.value=Math.min(pageCount.value,Math.max(1,page.value+delta)); load() }
function exportCsv() {
  const rows = [['Name','Email','Phone','WhatsApp opt-in','Status','Joined'], ...items.value.map(x=>[x.name,x.email||'',x.phone||'',x.whatsapp_opt_in?'Yes':'No',x.is_active?'Active':'Disabled',x.created_at||''])]
  const csv = buildCsv(rows)
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})); const a=document.createElement('a');a.href=url;a.download='nova-home-customers.csv';a.click();URL.revokeObjectURL(url)
}
onMounted(load)
</script>
<template>
  <AdminShell active="customers">
    <div class="admin-page-heading"><div><span class="admin-eyebrow">CUSTOMER DIRECTORY</span><h1>Customers</h1><p>Customer profiles, contact details and communication preferences.</p></div><div class="admin-heading-count"><b>{{ total }}</b><small>customers</small></div></div>
    <p v-if="error" class="admin-alert error">{{ error }}</p>
    <section class="admin-panel admin-list-panel"><div class="admin-panel-heading"><div><h2>Registered customers</h2><p>Personal information is visible only to authorized administrators.</p></div><div class="admin-search-control"><input v-model="query" type="search" placeholder="Name, email or phone" @keyup.enter="searchCustomers"><button @click="searchCustomers">Search</button><button class="secondary" @click="exportCsv">↓ CSV</button></div></div>
      <div class="admin-table-scroll"><table class="admin-table"><thead><tr><th>Customer</th><th>Phone</th><th>WhatsApp</th><th>Account</th><th>Joined</th></tr></thead><tbody><tr v-for="customer in items" :key="customer.id"><td><b>{{ customer.name }}</b><small>{{ customer.email || 'No email' }}</small></td><td>{{ customer.phone || '—' }}</td><td><span class="admin-status" :class="customer.whatsapp_opt_in ? 'status-paid' : 'status-muted'">{{ customer.whatsapp_opt_in ? 'Opted in' : 'Not opted in' }}</span></td><td><span class="admin-status" :class="customer.is_active ? 'status-paid' : 'status-failed'">{{ customer.is_active ? 'Active' : 'Disabled' }}</span></td><td>{{ customer.created_at ? new Date(customer.created_at).toLocaleDateString('en-EG') : '—' }}</td></tr><tr v-if="!loading && !items.length"><td colspan="5" class="admin-table-empty">No customers found.</td></tr></tbody></table><div v-if="loading" class="admin-loading-inline">Loading customers…</div><div class="admin-pagination"><small>Showing {{ total ? (page-1)*pageSize+1 : 0 }}–{{ Math.min(page*pageSize,total) }} of {{ total }} customers</small><div><button :disabled="page<=1 || loading" @click="changePage(-1)">Previous</button><span>Page {{ page }} / {{ pageCount }}</span><button :disabled="page>=pageCount || loading" @click="changePage(1)">Next</button></div></div></div>
    </section>
  </AdminShell>
</template>
