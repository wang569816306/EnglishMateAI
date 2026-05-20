import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0', // 允许通过 IP 访问
    port: 5173, // 开发服务器端口（可选）
    strictPort: false, // 如果端口被占用，尝试下一个可用端口（可选）
    // 开发环境代理配置
    proxy: {
      '/ai': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true // 支持 WebSocket
      }
    }
  }
})
