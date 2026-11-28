import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development the Vite server proxies API calls to FastAPI. In production
// the built frontend is served by FastAPI itself on 0.0.0.0:8000 (LAN demo).
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('/node_modules/three/examples/jsm/')) return 'three-addons'
          if (id.endsWith('/node_modules/three/build/three.core.js')) return 'three-core'
          if (id.endsWith('/node_modules/three/build/three.module.js')) return 'three-module'
          if (id.includes('/node_modules/three/')) return 'three-vendor'
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
