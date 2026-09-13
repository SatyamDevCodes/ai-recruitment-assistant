import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite ka basic config, React plugin ke saath
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
