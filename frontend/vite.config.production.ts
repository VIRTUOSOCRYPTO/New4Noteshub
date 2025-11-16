import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Production configuration for Render deployment
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '3000'),
    strictPort: true,
  },
  preview: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '3000'),
    strictPort: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-tabs'],
        },
      },
    },
  },
})
