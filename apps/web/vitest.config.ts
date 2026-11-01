import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.')
    }
  },
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['components/**/*.{ts,tsx}', 'hooks/**/*.{ts,tsx}', 'lib/**/*.{ts,tsx}', 'app/**/*.{ts,tsx}'],
      exclude: ['**/*.test.*', '**/*.spec.*', '**/*.d.ts', '**/types/**', '**/index.ts', 'node_modules/**', '.next/**'],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70
      }
    },
    environment: 'jsdom',
    setupFiles: ['./__tests__/setup.ts'],
    include: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
    exclude: ['node_modules', 'e2e', 'dist', '.next'],
    css: true,
    globals: true
  }
});
