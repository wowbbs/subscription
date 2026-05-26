export interface BrowserConfig {
  executablePath?: string;
  headless: boolean;
  userDataDir?: string;
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
