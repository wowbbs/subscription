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
        '--disable-infobars',
        '--disable-extensions',
        '--disable-popup-blocking',
        '--disable-notifications',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-features=VizDisplayCompositor',
        '--disable-ipc-flooding-protection',
        '--disable-renderer-backgrounding',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-client-side-phishing-detection',
        '--disable-component-update',
        '--disable-domain-reliability',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-sync',
        '--metrics-recording-only',
        '--no-first-run',
        '--safebrowsing-disable-auto-update',
        '--enable-automation=false',
        '--password-store=basic',
        '--use-mock-keychain',
      ],
    };

    if (this.config.executablePath) {
      launchOptions.executablePath = this.config.executablePath;
    }

    this.browser = await chromium.launch(launchOptions);
    this.context = await this.browser.newContext({
      extraHTTPHeaders: defaultHeaders,
      userAgent: defaultHeaders['User-Agent'],
      viewport: { width: 1920, height: 1080 },
      locale: 'zh-CN',
      timezoneId: 'Asia/Shanghai',
      hasTouch: false,
      isMobile: false,
      permissions: [],
    });
    this.page = await this.context.newPage();

    await this.setupPage();
  }

  private async setupPage(): Promise<void> {
    if (!this.page) return;

    // 隐藏自动化特征
    await this.page.addInitScript(() => {
      // 1. 隐藏 webdriver
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true,
      });

      // 2. 隐藏 chrome 属性
      const originalChrome = window.chrome;
      Object.defineProperty(window, 'chrome', {
        get: () => originalChrome,
        configurable: true,
      });

      // 3. 隐藏 navigator.plugins 和 navigator.mimeTypes 的检查
      const originalPlugins = navigator.plugins;
      const originalMimeTypes = navigator.mimeTypes;
      Object.defineProperty(navigator, 'plugins', {
        get: () => originalPlugins,
        configurable: true,
      });
      Object.defineProperty(navigator, 'mimeTypes', {
        get: () => originalMimeTypes,
        configurable: true,
      });

      // 4. 修改 navigator.languages
      Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en'],
        configurable: true,
      });

      // 5. 修改 permissions API
      const originalQuery = window.navigator.permissions.query;
      if (originalQuery) {
        window.navigator.permissions.query = (parameters: PermissionDescriptor) => {
          return parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission } as PermissionStatus)
            : originalQuery(parameters);
        };
      }

      // 6. 隐藏 Playwright 注入的标记
      delete window.__playwright;
      delete window.__PW_inspect;
      delete window.__PW_driver;

      // 7. 移除 console 中的调试标记
      const originalLog = console.log;
      console.log = function (...args) {
        if (args[0] && typeof args[0] === 'string' && args[0].includes('playwright')) {
          return;
        }
        originalLog.apply(console, args);
      };
    });

    // 8. 拦截所有请求，设置正确的标头
    await this.context?.route('**/*', (route) => {
      const headers = { ...defaultHeaders };
      
      // 移除或修改可能暴露自动化的标头
      delete headers['X-Playwright'];
      delete headers['Playwright'];
      
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
