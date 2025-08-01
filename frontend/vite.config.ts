import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),
    tailwindcss(),
  ],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: "https://cccf686aa06d.ngrok-free.app",
        changeOrigin: true,
      },
    },
    allowedHosts: ["cccf686aa06d.ngrok-free.app"]
  },
})
