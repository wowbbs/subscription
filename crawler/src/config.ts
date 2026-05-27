import dotenv from 'dotenv';
import { CrawlerConfig } from './types.js';

dotenv.config();

export const defaultHeaders: Record<string, string> = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
};

export function getConfig(): CrawlerConfig {
  return {
    targetUrl: process.env.TARGET_URL || '',
    username: process.env.USERNAME || '',
    password: process.env.PASSWORD || '',
    outputPath: process.env.OUTPUT_PATH || './data/customers.json',
    browser: {
      headless: process.env.HEADLESS !== 'true',
      channel: (process.env.BROWSER_CHANNEL as 'chrome' | 'chromium' | 'msedge') || 'chromium',
      executablePath: process.env.CHROME_PATH,
    },
    customHeaders: {},
  };
}
