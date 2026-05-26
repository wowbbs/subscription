import type { Browser, BrowserContext, Page } from '@playwright/test';

export interface BrowserConfig {
  headless: boolean;
  channel?: 'chrome' | 'chromium' | 'msedge';
  executablePath?: string;
  args?: string[];
}

export interface CrawlerConfig {
  targetUrl: string;
  username: string;
  password: string;
  outputPath: string;
  browser: BrowserConfig;
  customHeaders: Record<string, string>;
}

export interface CustomerData {
  id?: string;
  name?: string;
  phone?: string;
  email?: string;
  [key: string]: unknown;
}

export interface BrowserController {
  browser: Browser | null;
  context: BrowserContext | null;
  page: Page | null;
}
