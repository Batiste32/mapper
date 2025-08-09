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
        target: "https://4feae889736f.ngrok-free.app",
        changeOrigin: true,
      },
    },
    allowedHosts: ["4feae889736f.ngrok-free.app"]
  },
})
