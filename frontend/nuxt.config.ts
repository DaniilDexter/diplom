// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css'],
  modules: ['@nuxt/icon', 'shadcn-nuxt', '@pinia/nuxt', 'pinia-plugin-persistedstate/nuxt'],
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
  shadcn: {
    prefix: '',
    /**
     * Directory that the component lives in.
     * @default "./components/ui"
     */
    componentDir: './components/ui'
  },
  runtimeConfig: {
    public: {
      baseURL: 'http://127.0.0.1:8000/api/v1/',
    }
  },
  piniaPluginPersistedstate: {
    storage: 'cookies',
    cookieOptions: {
      maxAge: 365 * 24 * 60 * 60
    }
  }
})