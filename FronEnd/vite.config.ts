import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 12001,
    cors: true,
    allowedHosts: ['all', 'work-1-twveyezkjfylpous.prod-runtime.all-hands.dev', 'work-2-twveyezkjfylpous.prod-runtime.all-hands.dev'],
  },
  preview: {
    host: '0.0.0.0',
    port: 12000,
    cors: true,
  },
})
