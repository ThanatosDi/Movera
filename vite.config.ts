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
    VitePWA()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})