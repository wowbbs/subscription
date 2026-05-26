import { chromium, Browser, BrowserContext, Page } from '@playwright/test';
import { BrowserConfig } from './types.js';
import { defaultHeaders } from './config.js';

export class BrowserController {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;

  constructor(private config: BrowserConfig) {}

  async launch(): Promise<void> {
    const launchOptions: any = {
      headless: this.config.headless,
      channel: this.config.channel || 'chromium',
      args: [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
      ],
    };

    if (this.config.executablePath) {
      launchOptions.executablePath = this.config.executablePath;
    }

    this.browser = await chromium.launch(launchOptions);
    this.context = await this.browser.newContext({
      extraHTTPHeaders: defaultHeaders,
      userAgent: defaultHeaders['User-Agent'],
    });
    this.page = await this.context.newPage();

    await this.setupPage();
  }

  private async setupPage(): Promise<void> {
    if (!this.page) return;

    await this.page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
      });
    });

    await this.context?.route('**/*', (route) => {
      const headers = { ...defaultHeaders };
      route.continue({ headers });
    });
  }

  getPage(): Page | null {
    return this.page;
  }

  getBrowser(): Browser | null {
    return this.browser;
  }

  getContext(): BrowserContext | null {
    return this.context;
  }

  async setCustomHeaders(headers: Record<string, string>): Promise<void> {
    if (!this.context) return;

    await this.context.addInitScript((customHeaders) => {
      window.customHeaders = customHeaders;
    }, headers);

    await this.context.route('**/*', (route) => {
      const mergedHeaders = { ...defaultHeaders, ...headers };
      route.continue({ headers: mergedHeaders });
    });
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
    }
  }
}
