import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue2'

// https://vitejs.dev/config/
export default defineConfig({
  root: './frontend',
  base: '/static/',
  plugins: [
    vue(),
  ],
  define: {
    API_ROOT: JSON.stringify(process.env.API_ROOT || null),
  },
  resolve: {
    alias: {
      'vue': 'vue/dist/vue.esm.js'
    }
  }

})
