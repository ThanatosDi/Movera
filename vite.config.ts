import vueI18n from '@intlify/unplugin-vue-i18n/vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

const packageJson = fs.readFileSync(path.resolve(__dirname, './package.json'), 'utf-8')
const { version } = JSON.parse(packageJson)

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    vueDevTools(),
    vueI18n({
      runtimeOnly: false,
    }),
  ],
  resolve: {
    alias: {
      // '@': path.resolve(__dirname, './src'),
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  define: {
    '__APP_VERSION__': JSON.stringify(version),
    // 確保 vue-i18n 在生產版本中完全安裝
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: true,
  },
})
