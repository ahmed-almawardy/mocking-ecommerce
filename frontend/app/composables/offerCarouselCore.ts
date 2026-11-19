export interface OfferSlide {
  id: string
  image: string
  title: string
  description: string
  position: string
}

/** The home-page offer carousel intentionally contains exactly four slots. */
export const offerSlides: readonly OfferSlide[] = [
  {
    id: 'home-appliance-collection',
    image: '/images/offers/offer-1.webp',
    title: 'offers.slide1Title',
    description: 'offers.slide1Text',
    position: 'center 54%',
  },
  {
    id: 'cooling-and-kitchen',
    image: '/images/offers/offer-2.webp',
    title: 'offers.slide2Title',
    description: 'offers.slide2Text',
    position: 'center 47%',
  },
  {
    id: 'kitchen-essentials',
    image: '/images/offers/offer-3.webp',
    title: 'offers.slide3Title',
    description: 'offers.slide3Text',
    position: 'center 52%',
  },
  {
    id: 'everyday-home',
    image: '/images/offers/offer-4.webp',
    title: 'offers.slide4Title',
    description: 'offers.slide4Text',
    position: 'center 52%',
  },
] as const

export function wrapOfferIndex(index: number, slideCount = offerSlides.length): number {
  if (!Number.isInteger(slideCount) || slideCount < 1) {
    throw new RangeError('slideCount must be a positive integer')
  }
  return ((index % slideCount) + slideCount) % slideCount
}

export function offerTrackOffset(index: number, slideCount = offerSlides.length): string {
  return `translate3d(-${wrapOfferIndex(index, slideCount) * 100}%, 0, 0)`
}
