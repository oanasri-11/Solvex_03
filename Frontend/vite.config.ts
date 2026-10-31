import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), react()],
  // @ts-expect-error vitest config
  test: {
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
