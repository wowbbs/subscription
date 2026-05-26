import { Page } from 'puppeteer-core';
import { BrowserController } from './browser.js';
import { CrawlerConfig, CustomerData } from './types.js';
import * as fs from 'fs';
import * as path from 'path';

export class CustomerCrawler {
  private browserController: BrowserController;

  constructor(private config: CrawlerConfig) {
    this.browserController = new BrowserController(config.browser);
  }

  async initialize(): Promise<void> {
    await this.browserController.launch();
    
    if (Object.keys(this.config.customHeaders).length > 0) {
      await this.browserController.setCustomHeaders(this.config.customHeaders);
    }
  }

  async navigateToTarget(): Promise<void> {
    const page = this.browserController.getPage();
    if (!page) throw new Error('Page not initialized');

    console.log(`正在导航到: ${this.config.targetUrl}`);
    await page.goto(this.config.targetUrl, { waitUntil: 'networkidle2' });
  }

  async login(username?: string, password?: string): Promise<boolean> {
    const page = this.browserController.getPage();
    if (!page) throw new Error('Page not initialized');

    const user = username || this.config.username;
    const pass = password || this.config.password;

    try {
      await page.waitForSelector('input[type="text"], input[name="username"], input[name="user"]', { timeout: 10000 });
      
      const usernameInput = await page.$('input[type="text"], input[name="username"], input[name="user"]');
      const passwordInput = await page.$('input[type="password"], input[name="password"]');
      const loginButton = await page.$('button[type="submit"], input[type="submit"], .login-btn');

      if (usernameInput) {
        await usernameInput.type(user);
      }

      if (passwordInput) {
        await passwordInput.type(pass);
      }

      if (loginButton) {
        await loginButton.click();
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
      }

      console.log('登录操作完成');
      return true;
    } catch (error) {
      console.log('自动登录失败，请手动登录');
      return false;
    }
  }

  async waitForManualInput(): Promise<void> {
    const page = this.browserController.getPage();
    if (!page) throw new Error('Page not initialized');

    console.log('请在浏览器中完成登录和导航到客户列表页面...');
    console.log('准备好后，在控制台按回车键继续...');
    
    await new Promise(resolve => {
      process.stdin.once('data', resolve);
    });
  }

  async extractCustomerData(): Promise<CustomerData[]> {
    const page = this.browserController.getPage();
    if (!page) throw new Error('Page not initialized');

    console.log('开始提取客户数据...');

    const data = await page.evaluate(() => {
      const customers: CustomerData[] = [];
      const rows = document.querySelectorAll('table tr, .customer-row, [class*="customer"]');
      
      rows.forEach(row => {
        const customer: CustomerData = {};
        const cells = row.querySelectorAll('td, .customer-cell, [class*="cell"]');
        
        cells.forEach((cell, index) => {
          const text = cell.textContent?.trim() || '';
          if (text) {
            customer[`field_${index}`] = text;
          }
        });

        if (Object.keys(customer).length > 0) {
          customers.push(customer);
        }
      });

      return customers;
    });

    console.log(`提取到 ${data.length} 条客户数据`);
    return data;
  }

  async saveData(data: CustomerData[]): Promise<void> {
    const outputDir = path.dirname(this.config.outputPath);
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(this.config.outputPath, JSON.stringify(data, null, 2), 'utf-8');
    console.log(`数据已保存到: ${this.config.outputPath}`);
  }

  async close(): Promise<void> {
    await this.browserController.close();
  }

  async getPage(): Promise<Page | null> {
    return this.browserController.getPage();
  }
}
