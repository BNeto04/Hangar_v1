import { defineConfig } from '@playwright/test';
import path from 'path';

/**
 * Hangar V1 — Configuração Canônica do Playwright Test para Extensão Manifest V3.
 * Suporta Persistent Context com `--load-extension` e `--disable-extensions-except`.
 */
const extensionPath = path.resolve(__dirname, 'bridge/extension');

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 0,
  workers: 1,
  reporter: [['list'], ['json', { outputFile: 'evidence/playwright-results.json' }]],
  use: {
    channel: 'chrome',
    headless: false,
    launchOptions: {
      args: [
        '--headless=new',
        `--disable-extensions-except=${extensionPath}`,
        `--load-extension=${extensionPath}`
      ]
    },
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  }
});
