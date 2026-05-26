import puppeteer, { Browser, Page } from 'puppeteer-core';
import { BrowserConfig } from './types.js';
import { defaultHeaders } from './config.js';

export class BrowserController {
  private browser: Browser | null = null;
  private page: Page | null = null;

  constructor(private config: BrowserConfig) {}

  async launch(): Promise<void> {
    const launchOptions: puppeteer.PuppeteerLaunchOptions = {
      headless: this.config.headless,
      executablePath: this.config.executablePath || this.findChromePath(),
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
      ],
      defaultViewport: null,
    };

    if (this.config.userDataDir) {
      launchOptions.userDataDir = this.config.userDataDir;
    }

    this.browser = await puppeteer.launch(launchOptions);
    this.page = await this.browser.newPage();

    await this.setupPage();
  }

  private findChromePath(): string {
    const possiblePaths = [
      '/usr/bin/google-chrome',
      '/usr/bin/chromium-browser',
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    ];

    return possiblePaths[0];
  }

  private async setupPage(): Promise<void> {
    if (!this.page) return;

    await this.page.setUserAgent(defaultHeaders['User-Agent']);
    await this.page.setExtraHTTPHeaders(defaultHeaders);

    await this.page.evaluateOnNewDocument(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    });
  }

  getPage(): Page | null {
    return this.page;
  }

  getBrowser(): Browser | null {
    return this.browser;
  }

  async setCustomHeaders(headers: Record<string, string>): Promise<void> {
    if (!this.page) return;
    await this.page.setExtraHTTPHeaders({ ...defaultHeaders, ...headers });
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
    }
  }
}
