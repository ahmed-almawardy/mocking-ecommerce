<script setup lang="ts">
import { offerSlides, offerTrackOffset, wrapOfferIndex } from '../composables/offerCarouselCore'

const { t, isRtl, locale, localePath } = useLocale()
const storeApi = useStoreApi()
const { data: offerResponse } = await useAsyncData('storefront-active-offers', () => storeApi<{ items: Array<{ id:string; title:string; subtitle:string; title_ar:string|null; subtitle_ar:string|null; image_url:string; link_url:string; badge:string|null }> }>('/offers/active').catch(() => ({ items: [] })))
type CarouselSlide = { id:string; image:string; title:string; description:string; position:string; link?:string; dynamic:boolean }
const slides = computed<CarouselSlide[]>(() => {
  const active = (offerResponse.value?.items || []).slice(0, 4)
  const dynamicSlides = active.map(offer => ({
    id:offer.id,
    image:offer.image_url,
    title:locale.value === 'ar' && offer.title_ar ? offer.title_ar : offer.title,
    description:locale.value === 'ar' && offer.subtitle_ar ? offer.subtitle_ar : offer.subtitle,
    position:'center',
    link:offer.link_url,
    dynamic:true,
  }))
  const fallbackSlides = offerSlides.slice(dynamicSlides.length).map(slide => ({ ...slide, dynamic:false }))
  return [...dynamicSlides, ...fallbackSlides].slice(0, 4)
})
function slideHref(slide: CarouselSlide) {
  if (!slide.dynamic || !slide.link) return { path:localePath('/products'), query:{ offer:'1' } }
  const localPath = slide.link.replace(/^\/(en|ar)(?=\/|$)/, '') || '/'
  return localPath.startsWith('/') ? localePath(localPath) : localePath('/products')
}
const activeIndex = ref(0)
const paused = ref(false)
const skipTransition = ref(false)
let autoplayTimer: ReturnType<typeof setInterval> | undefined
let reducedMotion = false

function goTo(index: number, withoutAnimation = false) {
  const nextIndex = wrapOfferIndex(index, slides.value.length)
  if (withoutAnimation) {
    skipTransition.value = true
    activeIndex.value = nextIndex
    void nextTick(() => {
      requestAnimationFrame(() => { skipTransition.value = false })
    })
    return
  }
  activeIndex.value = nextIndex
}
function previous() {
  if (activeIndex.value === 0) goTo(slides.value.length - 1, true)
  else goTo(activeIndex.value - 1)
}
function next() {
  // Reset instantly at the loop boundary; otherwise the track would animate
  // backwards across three slides instead of continuing its leftward movement.
  if (activeIndex.value === slides.value.length - 1) goTo(0, true)
  else goTo(activeIndex.value + 1)
}
function resumeOnFocusOut(event: FocusEvent) {
  const root = event.currentTarget as HTMLElement | null
  if (root && event.relatedTarget instanceof Node && root.contains(event.relatedTarget)) return
  paused.value = false
}

onMounted(() => {
  reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reducedMotion) return
  autoplayTimer = setInterval(() => {
    if (!paused.value && !document.hidden) next()
  }, 5000)
})
onBeforeUnmount(() => {
  if (autoplayTimer) clearInterval(autoplayTimer)
})
</script>

<template>
  <section
    class="featured-offers"
    role="region"
    aria-roledescription="carousel"
    :aria-label="t('offers.eyebrow')"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
    @focusin="paused = true"
    @focusout="resumeOnFocusOut"
  >
    <div class="featured-offers-frame">
      <div class="featured-offers-track" :class="{ 'no-transition': skipTransition }" :style="{ transform: offerTrackOffset(activeIndex, slides.length) }">
        <article
          v-for="(slide, index) in slides"
          :key="slide.id"
          class="featured-offer-slide"
          role="group"
          aria-roledescription="slide"
          :aria-hidden="activeIndex !== index"
          :aria-label="`${index + 1} / ${slides.length}: ${slide.dynamic ? slide.title : t(slide.title)}`"
          :inert="activeIndex !== index"
        >
          <img
            :src="slide.image"
            :alt="slide.dynamic ? slide.title : t(slide.title)"
            :style="{ objectPosition: slide.position }"
            :loading="index === 0 ? 'eager' : 'lazy'"
            :fetchpriority="index === 0 ? 'high' : 'auto'"
          >
          <div class="featured-offer-scrim" />
          <div class="featured-offer-copy" :class="{ 'copy-rtl': isRtl }">
            <span class="offer-eyebrow">{{ t('offers.eyebrow') }}</span>
            <h2>{{ slide.dynamic ? slide.title : t(slide.title) }}</h2>
            <p>{{ slide.dynamic ? slide.description : t(slide.description) }}</p>
            <NuxtLink :to="slideHref(slide)" class="offer-cta">
              {{ t('offers.cta') }} <span aria-hidden="true">↗</span>
            </NuxtLink>
          </div>
        </article>
      </div>
      <button class="offer-arrow offer-arrow-left" type="button" :aria-label="t('offers.previous')" @click="previous">‹</button>
      <button class="offer-arrow offer-arrow-right" type="button" :aria-label="t('offers.next')" @click="next">›</button>
    </div>
    <div class="featured-offers-pagination" :aria-label="t('offers.paginationLabel')">
      <button
        v-for="(_, index) in slides"
        :key="index"
        type="button"
        class="offer-dot"
        :class="{ active: activeIndex === index }"
        :aria-label="t('offers.goTo', { number: index + 1 })"
        :aria-current="activeIndex === index ? 'true' : undefined"
        @click="goTo(index)"
      />
    </div>
  </section>
</template>
