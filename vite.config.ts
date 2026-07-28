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
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/webhook': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
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
        // 導覽請求改由下方 NetworkFirst 規則處理，因此關閉 precache 的導覽路由。
        //
        // Why: precache 是 cache-first，會讓 `/` 完全不經過網路。部署在帶 SSO 的
        // 反向代理（Pangolin、Cloudflare Zero Trust 等）之後時，閘道就沒有機會把
        // 過期 session 以 302 導向登入頁，使用者會停在快取的畫面上。
        // navigateFallback 為 vite-plugin-pwa 預設值，需顯式覆寫；directoryIndex
        // 則是 workbox 用來讓 `/` 命中 precache 的 `index.html`。
        navigateFallback: undefined,
        directoryIndex: null,
        runtimeCaching: [
          {
            // 導覽請求一律先問網路，離線時才回退到最近一次成功的回應
            urlPattern: ({ request, url }) =>
              request.mode === 'navigate' &&
              !/^\/(api|webhook|docs|redoc)\b/.test(url.pathname) &&
              url.pathname !== '/openapi.json',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'movera-navigations',
              networkTimeoutSeconds: 3,
              cacheableResponse: { statuses: [200] },
            },
          },
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