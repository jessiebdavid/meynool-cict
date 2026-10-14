import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// 5173 sits inside a Windows excluded TCP range (5141-5240) on this machine,
// so binding it fails with EACCES. Default to a port outside that range; set
// DEV_PORT to override without editing this file.
const devPort = Number(process.env.DEV_PORT) || 4319;

export default defineConfig({
  plugins: [react()],
  server: { host: '127.0.0.1', port: devPort },
});
