<script setup lang="ts">
type Offer = { id:string; title:string; subtitle:string; image_url:string; link_url:string; badge:string|null; is_active:boolean; sort_order:number; starts_at:string|null; ends_at:string|null }
const api = useAdminApi()
const offers = ref<Offer[]>([])
const loading = ref(true)
const saving = ref(false)
const uploadingImage = ref(false)
const error = ref('')
const editingId = ref<string|null>(null)
const form = reactive({ title:'', subtitle:'', title_ar:'', subtitle_ar:'', image_url:'/images/offers/offer-1.webp', link_url:'/en/products', badge:'', is_active:true, sort_order:0, starts_at:'', ends_at:'' })

async function uploadOfferImage(event: Event) {
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
    error.value = exception?.data?.detail || 'The offer banner could not be uploaded.'
  } finally {
    uploadingImage.value = false
    input.value = ''
  }
}

async function load() {
  loading.value = true
  try { offers.value = (await api.get<{items:Offer[]}>('offers')).items }
  catch (e:any) { error.value = e?.data?.detail || 'Could not load offers.' }
  finally { loading.value = false }
}
function reset() {
  editingId.value = null
  Object.assign(form, { title:'', subtitle:'', title_ar:'', subtitle_ar:'', image_url:'/images/offers/offer-1.webp', link_url:'/en/products', badge:'', is_active:true, sort_order:offers.value.length, starts_at:'', ends_at:'' })
}
function edit(item: Offer) {
  editingId.value = item.id
  Object.assign(form, { ...item, starts_at:item.starts_at?.slice(0,16) || '', ends_at:item.ends_at?.slice(0,16) || '', badge:item.badge || '' })
  window.scrollTo({ top:0, behavior:'smooth' })
}
async function save() {
  saving.value = true
  error.value = ''
  const payload = { ...form, sort_order:Number(form.sort_order), badge:form.badge || null, starts_at:form.starts_at ? new Date(form.starts_at).toISOString() : null, ends_at:form.ends_at ? new Date(form.ends_at).toISOString() : null }
  try {
    if (editingId.value) await api.patch(`offers/${editingId.value}`, payload)
    else await api.post('offers', payload)
    reset()
    await load()
  } catch (e:any) { error.value = e?.data?.detail || 'The offer could not be saved.' }
  finally { saving.value = false }
}
async function toggle(item: Offer) {
  try { await api.patch(`offers/${item.id}`, { is_active:!item.is_active }); await load() }
  catch (e:any) { error.value = e?.data?.detail || 'Could not update offer.' }
}
async function remove(item: Offer) {
  if (!window.confirm(`Delete offer “${item.title}”?`)) return
  try { await api.remove(`offers/${item.id}`); await load() }
  catch (e:any) { error.value = e?.data?.detail || 'Could not delete offer.' }
}
onMounted(load)
</script>

<template>
  <AdminShell active="offers">
    <div class="admin-page-heading"><div><span class="admin-eyebrow">PROMOTIONS</span><h1>Offers</h1><p>Create and schedule the campaigns shown in the storefront offer carousel.</p></div><div class="admin-heading-count"><b>{{ offers.length }}</b><small>offers</small></div></div>
    <p v-if="error" class="admin-alert error">{{ error }}</p>
    <section class="admin-panel admin-form-panel"><div class="admin-panel-heading"><div><h2>{{ editingId ? 'Edit offer' : 'Create an offer' }}</h2><p>Use a banner image, a destination and optional scheduling dates.</p></div><button v-if="editingId" class="admin-secondary-button" @click="reset">Cancel edit</button></div>
      <form class="admin-form-grid" @submit.prevent="save">
        <label>Offer title<input v-model="form.title" required maxlength="180" placeholder="Winter home refresh"></label>
        <label>Badge<input v-model="form.badge" maxlength="60" placeholder="LIMITED TIME"></label>
        <label class="span-2">Subtitle (English)<input v-model="form.subtitle" maxlength="300" placeholder="Special prices on selected appliances"></label>
        <label>Offer title (Arabic)<input v-model="form.title_ar" dir="rtl" maxlength="180" placeholder="عروض خاصة"></label>
        <label>Subtitle (Arabic)<input v-model="form.subtitle_ar" dir="rtl" maxlength="300" placeholder="عروض على أجهزة مختارة"></label>
        <label class="span-2">Banner image URL<input v-model="form.image_url" required maxlength="700" placeholder="/media/your-offer-banner.webp"></label>
        <label class="span-2">Upload banner image<input type="file" accept="image/jpeg,image/png,image/webp" :disabled="uploadingImage" @change="uploadOfferImage"><small>{{ uploadingImage ? 'Uploading image…' : 'JPEG, PNG or WebP · maximum 10 MB' }}</small></label>
        <div v-if="form.image_url" class="admin-image-preview span-2"><img :src="form.image_url" alt="Offer banner preview"><span>Current offer banner</span></div>
        <label class="span-2">Destination URL<input v-model="form.link_url" required maxlength="700" placeholder="/en/products"></label>
        <label>Display order<input v-model.number="form.sort_order" type="number" min="0" max="10000"></label>
        <label>Starts at<input v-model="form.starts_at" type="datetime-local"></label>
        <label>Ends at<input v-model="form.ends_at" type="datetime-local"></label>
        <label class="admin-check align-check"><input v-model="form.is_active" type="checkbox"> Active and eligible to display</label>
        <div class="admin-form-submit"><button class="admin-primary-button" type="submit" :disabled="saving">{{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Create offer' }}</button></div>
      </form>
    </section>
    <section class="admin-panel admin-list-panel"><div class="admin-panel-heading"><div><h2>Offer library</h2><p>Manage every homepage banner campaign.</p></div></div>
      <div v-if="loading" class="admin-loading-inline">Loading offers…</div>
      <div v-else-if="offers.length" class="admin-offer-grid"><article v-for="offer in offers" :key="offer.id" class="admin-offer-card"><img :src="offer.image_url" :alt="offer.title"><div class="admin-offer-copy"><div><span class="admin-status" :class="offer.is_active ? 'status-paid' : 'status-failed'">{{ offer.is_active ? 'Active' : 'Inactive' }}</span><small>Priority {{ offer.sort_order }}</small></div><h3>{{ offer.title }}</h3><p>{{ offer.subtitle }}</p><small class="admin-muted">{{ offer.image_url }}</small><div class="admin-row-actions"><button @click="edit(offer)">Edit</button><button @click="toggle(offer)">{{ offer.is_active ? 'Deactivate' : 'Activate' }}</button><button class="danger" @click="remove(offer)">Delete</button></div></div></article></div>
      <div v-else class="admin-empty-chart compact-empty">No offers yet. Create the first banner above.</div>
    </section>
  </AdminShell>
</template>
