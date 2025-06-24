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
      },

      '/recommenditems': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/getInitialReviews': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/getAllSyntheticReviews': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/trainModel': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },

      '/getReviewsForAspect': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },
      
    },
  },
})
