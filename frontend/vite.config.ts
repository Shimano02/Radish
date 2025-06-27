import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

      export default defineConfig({
      plugins: [react()],
      server: {
      port: 3000,
        proxy: {
        '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        },
        },
        // HMR 設定: 不要な自動リロードを抑制
        hmr: {
        // エラーオーバーレイを無効化
        overlay: false,
        // HMR クライアントのポートを無効化（自動再接続を停止）
        clientPort: 0,
        },
        },
        })