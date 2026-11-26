import path from 'node:path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const rootDir = path.resolve(__dirname, '..');
  // Load environment variables solely from the global root .env (and host OS env)
  const globalEnv = loadEnv(mode, rootDir, '');

  const devPort = Number(process.env.VITE_PORT || globalEnv.VITE_PORT || 5173);
  const previewPort = Number(process.env.VITE_PREVIEW_PORT || globalEnv.VITE_PREVIEW_PORT || 4173);

  return {
    plugins: [react()],
    envDir: rootDir,
    server: {
      port: devPort,
      host: true,
    },
    preview: {
      port: previewPort,
      host: true,
    },
  };
});
