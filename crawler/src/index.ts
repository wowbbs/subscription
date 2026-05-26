import { getConfig } from './config.js';
import { CustomerCrawler } from './crawler.js';
import { CustomerData } from './types.js';

async function main() {
  const config = getConfig();

  if (!config.targetUrl) {
    console.error('请设置 TARGET_URL 环境变量');
    process.exit(1);
  }

  const crawler = new CustomerCrawler(config);

  try {
    console.log('初始化浏览器...');
    await crawler.initialize();

    console.log('导航到目标网站...');
    await crawler.navigateToTarget();

    console.log('尝试自动登录...');
    const loginSuccess = await crawler.login();

    if (!loginSuccess) {
      await crawler.waitForManualInput();
    }

    console.log('提取客户数据...');
    const data: CustomerData[] = await crawler.extractCustomerData();

    if (data.length > 0) {
      console.log('保存数据...');
      await crawler.saveData(data);
    } else {
      console.log('未找到数据，你可能需要自定义数据提取逻辑');
    }

    console.log('按 Ctrl+C 退出，或关闭浏览器窗口');
    await new Promise(() => {});

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await crawler.close();
  }
}

main();
