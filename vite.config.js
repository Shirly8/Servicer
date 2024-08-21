import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/generateReviews': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/analyzeSentiment': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/computeMetrics': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/Querychat': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      }
    
    },
  },
})
