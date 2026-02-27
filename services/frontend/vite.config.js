import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        host: '0.0.0.0',
        port: 5173,
        proxy: {
            '/api/auth': {
                target: 'http://localhost:8001',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/auth/, '')
            },
            '/api/fields': {
                target: 'http://localhost:8002',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/fields/, '')
            },
            '/api/submissions': {
                target: 'http://localhost:8003',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/submissions/, '')
            },
            '/api/ai': {
                target: 'http://localhost:8004',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/ai/, '')
            }
        }
    }
})
