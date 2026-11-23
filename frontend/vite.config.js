import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('html5-qrcode')) {
              return 'vendor-scanner'
            }
            if (id.includes('recharts') || id.includes('d3-') || id.includes('victory')) {
              return 'vendor-charts'
            }
            if (id.includes('framer-motion')) {
              return 'vendor-motion'
            }
            if (id.includes('react-icons')) {
              return 'vendor-icons'
            }
            if (id.includes('@tanstack/react-query') || id.includes('axios')) {
              return 'vendor-query'
            }
            // All other vendor packages (react, react-dom, react-router, etc.) bundled in vendor-core
            return 'vendor-core'
          }
        },
      },
    },
  },
})
