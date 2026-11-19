<script setup lang="ts">
type AdminProduct = { id:string; sku:string; slug:string; name:string; category:string; description:string; price:string; compare_at_price:string|null; stock_qty:number; image_url:string; badge:string|null; featured:boolean; is_active:boolean }
const api = useAdminApi()
const loading = ref(true)
const saving = ref(false)
const uploadingImage = ref(false)
const error = ref('')
const search = ref('')
const products = ref<AdminProduct[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 25
const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const editingId = ref<string|null>(null)
const form = reactive({ sku:'', slug:'', name:'', category:'Small Home Appliances', description:'', price:'', compare_at_price:'', stock_qty:0, image_url:'/images/products/refrigerator.webp', badge:'', featured:false, is_active:true })
async function load() {
  loading.value = true
  error.value = ''
  try {
    const result = await api.get<{items:AdminProduct[];total:number}>('products', { q: search.value || undefined, page:page.value, page_size:pageSize })
    products.value = result.items
    total.value = result.total
  } catch (e:any) { error.value = e?.data?.detail || 'Could not load products.' }
  finally { loading.value = false }
}

async function uploadProductImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  error.value = ''
  if (file.size > 10 * 1024 * 1024) { error.value = 'Choose an image no larger than 10 MB.'; input.value = ''; return }
  uploadingImage.value = true
  try {
    const result = await api.upload(file)
    form.image_url = result.url
  } catch (exception: any) {
    error.value = exception?.data?.detail || 'The product image could not be uploaded.'
  } finally {
    uploadingImage.value = false
    input.value = ''
  }
}

function searchProducts() { page.value = 1; load() }
function changePage(delta: number) { page.value = Math.min(pageCount.value, Math.max(1, page.value + delta)); load() }
function resetForm() {
  editingId.value = null
  Object.assign(form, { sku:'', slug:'', name:'', category:'Small Home Appliances', description:'', price:'', compare_at_price:'', stock_qty:0, image_url:'/images/products/refrigerator.webp', badge:'', featured:false, is_active:true })
}
function editProduct(product: AdminProduct) {
  editingId.value = product.id
  Object.assign(form, { ...product, compare_at_price: product.compare_at_price || '', badge: product.badge || '' })
  window.scrollTo({ top:0, behavior:'smooth' })
}
async function save() {
  error.value = ''
  saving.value = true
  try {
    const payload = { ...form, price:Number(form.price), compare_at_price:form.compare_at_price ? Number(form.compare_at_price) : null, stock_qty:Number(form.stock_qty), badge:form.badge || null }
    if (editingId.value) await api.patch(`products/${editingId.value}`, payload)
    else await api.post('products', payload)
    resetForm()
    await load()
  } catch (e:any) { error.value = e?.data?.detail || 'The product could not be saved.' }
  finally { saving.value = false }
}
async function archive(product: AdminProduct) {
  if (!window.confirm(`Archive ${product.name}? It will be hidden from the storefront but retained in orders.`)) return
  try { await api.remove(`products/${product.id}`); await load() }
  catch (e:any) { error.value = e?.data?.detail || 'Could not archive product.' }
}
onMounted(load)
</script>

<template>
  <AdminShell active="products">
    <div class="admin-page-heading"><div><span class="admin-eyebrow">CATALOG MANAGEMENT</span><h1>Products</h1><p>Create, update, price and manage stock for your catalog.</p></div><div class="admin-heading-count"><b>{{ total }}</b><small>catalog items</small></div></div>
    <p v-if="error" class="admin-alert error">{{ error }}</p>
    <section class="admin-panel admin-form-panel">
      <div class="admin-panel-heading"><div><h2>{{ editingId ? 'Edit product' : 'Add a product' }}</h2><p>{{ editingId ? 'Update product details and stock.' : 'Add a product to the NOVA HOME catalog.' }}</p></div><button v-if="editingId" class="admin-secondary-button" @click="resetForm">Cancel edit</button></div>
      <form class="admin-form-grid" @submit.prevent="save">
        <label>Product name<input v-model="form.name" required minlength="2" maxlength="220" placeholder="e.g. No Frost Refrigerator 420 L"></label>
        <label>SKU<input v-model="form.sku" required placeholder="NH-FR-420"></label>
        <label>URL slug<input v-model="form.slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="nova-refrigerator-420l"></label>
        <label>Category<select v-model="form.category"><option>Cookers</option><option>Cooling Appliances</option><option>Small Home Appliances</option><option>Washing Machines</option><option>Televisions</option><option>Air Conditioners</option><option>Water Heaters</option></select></label>
        <label>Price (EGP)<input v-model="form.price" type="number" min="0.01" step="0.01" required></label>
        <label>Compare-at price (EGP)<input v-model="form.compare_at_price" type="number" min="0.01" step="0.01"></label>
        <label>Stock quantity<input v-model.number="form.stock_qty" type="number" min="0" step="1" required></label>
        <label>Badge<input v-model="form.badge" maxlength="50" placeholder="Best seller / New / Offer"></label>
        <label class="span-2">Product image URL<input v-model="form.image_url" required placeholder="/media/your-uploaded-image.webp"></label>
        <label class="span-2">Upload product photo<input type="file" accept="image/jpeg,image/png,image/webp" :disabled="uploadingImage" @change="uploadProductImage"><small>{{ uploadingImage ? 'Uploading image…' : 'JPEG, PNG or WebP · maximum 10 MB' }}</small></label>
        <div v-if="form.image_url" class="admin-image-preview span-2"><img :src="form.image_url" alt="Product preview"><span>Current product image</span></div>
        <label class="span-2">Description<textarea v-model="form.description" rows="3" maxlength="10000" /></label>
        <div class="admin-form-options"><label class="admin-check"><input v-model="form.featured" type="checkbox"> Featured product</label><label class="admin-check"><input v-model="form.is_active" type="checkbox"> Visible on storefront</label></div>
        <div class="admin-form-submit"><button class="admin-primary-button" type="submit" :disabled="saving">{{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Create product' }}</button></div>
      </form>
    </section>
    <section class="admin-panel admin-list-panel">
      <div class="admin-panel-heading"><div><h2>Product catalog</h2><p>{{ total }} products registered</p></div><div class="admin-search-control"><input v-model="search" type="search" placeholder="Search name, SKU or category" @keyup.enter="searchProducts"><button @click="searchProducts">Search</button></div></div>
      <div class="admin-table-scroll"><table class="admin-table"><thead><tr><th>Product</th><th>SKU / Category</th><th>Price</th><th>Stock</th><th>Status</th><th>Actions</th></tr></thead><tbody><tr v-for="product in products" :key="product.id"><td><div class="admin-product-cell"><img :src="product.image_url" :alt="product.name"><b>{{ product.name }}</b></div></td><td><b>{{ product.sku }}</b><small>{{ product.category }}</small></td><td><b>{{ Number(product.price).toLocaleString('en-EG') }} EGP</b><small v-if="product.compare_at_price">Was {{ Number(product.compare_at_price).toLocaleString('en-EG') }}</small></td><td><span :class="product.stock_qty <= 5 ? 'admin-stock-low' : ''">{{ product.stock_qty }}</span></td><td><span class="admin-status" :class="product.is_active ? 'status-paid' : 'status-failed'">{{ product.is_active ? 'Active' : 'Archived' }}</span></td><td><div class="admin-row-actions"><button @click="editProduct(product)">Edit</button><button v-if="product.is_active" class="danger" @click="archive(product)">Archive</button></div></td></tr><tr v-if="!loading && !products.length"><td colspan="6" class="admin-table-empty">No products found.</td></tr></tbody></table><div v-if="loading" class="admin-loading-inline">Loading products…</div><div class="admin-pagination"><small>Showing {{ total ? (page-1)*pageSize+1 : 0 }}–{{ Math.min(page*pageSize,total) }} of {{ total }} products</small><div><button :disabled="page<=1 || loading" @click="changePage(-1)">Previous</button><span>Page {{ page }} / {{ pageCount }}</span><button :disabled="page>=pageCount || loading" @click="changePage(1)">Next</button></div></div></div>
    </section>
  </AdminShell>
</template>
