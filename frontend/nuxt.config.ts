const apiTarget = process.env.API_INTERNAL_URL || 'http://localhost:8000'

export default defineNuxtConfig({
  compatibilityDate: '2026-11-01',
  devtools: { enabled: process.env.NODE_ENV !== 'production' },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    apiInternalBase: process.env.NUXT_API_INTERNAL_BASE || 'http://localhost:8000',
    public: {
      brandName: process.env.NUXT_PUBLIC_BRAND_NAME || 'NOVA HOME',
    },
  },
  routeRules: {
    '/api/**': { proxy: `${apiTarget}/api/**` },
    '/media/**': { proxy: `${apiTarget}/media/**` },
  },
  app: {
    head: {
      title: 'NOVA HOME | Appliances for everyday living',
      meta: [
        { name: 'description', content: 'Discover thoughtful home appliances, helpful service and convenient shopping at NOVA HOME.' },
        { name: 'theme-color', content: '#ed1c24' },
      ],
    },
  },
})
