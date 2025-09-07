import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'node:path'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

const packageJson = fs.readFileSync(path.resolve(__dirname, './package.json'), 'utf-8')
const { version } = JSON.parse(packageJson)

export default defineConfig({
  plugins: [vue(), tailwindcss(), vueDevTools()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  define: {
    '__APP_VERSION__': JSON.stringify(version)
  }
})

