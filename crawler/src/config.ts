import dotenv from 'dotenv';
import { CrawlerConfig } from './types.js';

dotenv.config();

export const defaultHeaders: Record<string, string> = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Accept-Encoding': 'gzip, deflate, br',
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Cache-Control': 'max-age=0',
};

export function getConfig(): CrawlerConfig {
  return {
    targetUrl: process.env.TARGET_URL || '',
    username: process.env.USERNAME || '',
    password: process.env.PASSWORD || '',
    outputPath: process.env.OUTPUT_PATH || './data/customers.json',
    browser: {
      executablePath: process.env.CHROME_PATH,
      headless: process.env.HEADLESS === 'true',
      userDataDir: process.env.USER_DATA_DIR,
    },
    customHeaders: {},
  };
}
