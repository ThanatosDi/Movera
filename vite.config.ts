import vueI18n from '@intlify/unplugin-vue-i18n/vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'node:path'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import vueDevTools from 'vite-plugin-vue-devtools'

const packageJson = fs.readFileSync(path.resolve(__dirname, './package.json'), 'utf-8')
const { version } = JSON.parse(packageJson)

export default defineConfig({
  server: {
    watch: {
      ignored: ['backend/**'],
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify(version),
  },
  plugins: [
    vue(),
    tailwindcss(),
    vueDevTools(),
    vueI18n({
      compositionOnly: false,
      runtimeOnly: false,
      include: path.resolve(__dirname, './src/locales/*.json'),
    }),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,json,vue,txt,woff2}'],
        // 排除 API 和 FastAPI 文檔路徑不被快取
        navigateFallbackDenylist: [
          /^\/api/,
          /^\/webhook/,
          /^\/docs/,
          /^\/redoc/,
          /^\/openapi\.json/,
        ],
        runtimeCaching: [
          {
            urlPattern: /\/api\//,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /\/webhook\//,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /\/docs/,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /\/redoc/,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /\/openapi\.json/,
            handler: 'NetworkOnly',
          },
        ],
      },
      manifest: {
        name: 'Movera',
        short_name: 'Movera',
        description: 'Movera is a simple media server for your home.',
        theme_color: '#ffffff',
        icons: [
          {
            src: 'android-chrome-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'android-chrome-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})