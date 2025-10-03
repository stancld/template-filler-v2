import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Allow external access
    allowedHosts: ['.ngrok-free.dev', '.loca.lt'], // Allow ngrok and localtunnel domains
  },
})
