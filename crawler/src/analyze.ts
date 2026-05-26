import { getConfig } from './config.js';
import { BrowserController } from './browser.js';

async function analyzeHeaders() {
  const config = getConfig();

  if (!config.targetUrl) {
    console.error('请设置 TARGET_URL 环境变量');
    process.exit(1);
  }

  const browserController = new BrowserController({
    ...config.browser,
    headless: false,
  });

  try {
    console.log('启动浏览器用于分析...');
    await browserController.launch();
    const page = browserController.getPage();
    const context = browserController.getContext();

    if (!page || !context) throw new Error('页面初始化失败');

    await context.route('**/*', (route) => {
      const request = route.request();
      console.log('\n=== 请求信息 ===');
      console.log('URL:', request.url());
      console.log('方法:', request.method());
      console.log('请求头:');
      const headers = request.headers();
      Object.entries(headers).forEach(([key, value]) => {
        console.log(`  ${key}: ${value}`);
      });

      route.continue();
    });

    page.on('response', (response) => {
      console.log('\n=== 响应信息 ===');
      console.log('URL:', response.url());
      console.log('状态:', response.status());
      console.log('响应头:');
      const headers = response.headers();
      Object.entries(headers).forEach(([key, value]) => {
        console.log(`  ${key}: ${value}`);
      });
    });

    console.log(`请在浏览器中访问目标网站: ${config.targetUrl}`);
    console.log('所有的网络请求和响应头都会显示在控制台中');
    console.log('按 Ctrl+C 退出');

    await new Promise(() => {});

  } catch (error) {
    console.error('分析过程中出错:', error);
  } finally {
    await browserController.close();
  }
}

analyzeHeaders();
