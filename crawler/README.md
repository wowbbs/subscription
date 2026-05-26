# 客户资料抓取程序

## 功能简介

这是一个使用 **Playwright** 和 Chrome 浏览器开发的客户资料抓取工具，主要用于绕过浏览器头检测限制，从内网客户查询系统获取数据。

### 为什么选择 Playwright？

- ✅ **更强的反检测能力** - 更难被识别为自动化工具
- ✅ **多浏览器支持** - 支持 Chrome、Chromium、Edge
- ✅ **更智能的等待** - 自动等待机制减少失败率
- ✅ **更好的开发者体验** - API 设计更友好

## 目录结构

```
crawler/
├── src/
│   ├── types.ts        # 类型定义
│   ├── config.ts       # 配置管理
│   ├── browser.ts      # 浏览器控制器
│   ├── crawler.ts      # 数据抓取逻辑
│   ├── index.ts        # 主程序入口
│   └── analyze.ts      # 网络请求分析工具
├── .env.example        # 环境变量示例
├── package.json        # 项目依赖
└── tsconfig.json       # TypeScript 配置
```

## 快速开始

### 1. 安装依赖

```bash
cd crawler
pnpm install
```

### 2. 安装浏览器

```bash
pnpm install-browser
```

Playwright 会自动下载 Chromium 浏览器。

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置项。

### 4. 分析浏览器头（第一步）

首先运行分析工具，查看需要哪些特殊的浏览器头：

```bash
pnpm analyze
```

在打开的浏览器中，手动访问目标网站，观察控制台输出的请求头信息。

### 5. 运行抓取程序

```bash
pnpm start
```

## 环境变量配置

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| TARGET_URL | 目标网站 URL | 是 | - |
| HEADLESS | 是否使用无头模式 | 否 | true |
| BROWSER_CHANNEL | 浏览器通道 | 否 | chromium |
| USERNAME | 登录用户名 | 否 | - |
| PASSWORD | 登录密码 | 否 | - |
| OUTPUT_PATH | 数据输出路径 | 否 | ./data/customers.json |
| CHROME_PATH | Chrome 可执行文件路径 | 否 | 自动检测 |

## 使用步骤

### 方法一：使用专用 .exe 的浏览器头

1. 使用抓包工具（如 Fiddler、Charles 或 Wireshark）捕获专用 .exe 访问网站时的请求
2. 记录下所有关键的 HTTP 请求头
3. 在 `src/config.ts` 或创建自定义的头配置文件
4. 更新代码使用这些自定义头

### 方法二：使用我们的分析工具

1. 运行 `pnpm analyze`
2. 在打开的浏览器中尝试访问目标网站
3. 观察被拒绝时的请求和响应
4. 同时用专用 .exe 访问，对比两者的区别
5. 将找到的特殊头添加到配置中

## 自定义数据提取

默认的数据提取逻辑可能不适用于你的网站。你需要修改 `src/crawler.ts` 中的 `extractCustomerData` 方法：

```typescript
async extractCustomerData(): Promise<CustomerData[]> {
  const page = this.browserController.getPage();
  if (!page) throw new Error('Page not initialized');

  const data = await page.evaluate(() => {
    // 在这里自定义你的数据提取逻辑
    // 例如：
    // const name = document.querySelector('.name')?.textContent;
    // ...
  });

  return data;
}
```

## 常见问题

### 浏览器下载失败

如果 Playwright 无法下载浏览器，可以手动指定已安装的 Chrome 路径：

```bash
# Windows
CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe pnpm start

# macOS
CHROME_PATH=/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome pnpm start

# Linux
CHROME_PATH=/usr/bin/google-chrome pnpm start
```

### 仍然被识别为自动化浏览器

Playwright 已经内置了反检测机制，但如果还有问题：

1. 使用系统已安装的 Chrome（channel 设置为 'chrome'）
2. 手动下载并指定 executablePath
3. 添加更多自定义请求头
4. 调整页面行为模拟真实用户操作

### 浏览器选择建议

可以通过 BROWSER_CHANNEL 选择不同的浏览器：

- **chromium** - Playwright 自带的 Chromium，推荐
- **chrome** - 使用系统安装的 Chrome
- **msedge** - 使用 Microsoft Edge

## Playwright vs Puppeteer

### Playwright 优势

1. 更强的反检测能力
2. 自动等待机制更智能
3. 支持多种浏览器
4. 更好的 TypeScript 支持

### 适用场景

- 需要更强的反爬虫能力
- 希望代码更稳定可靠
- 需要支持多种浏览器
- 新手友好，不想处理复杂的等待问题

## 技术支持

如果你能提供以下信息，我可以帮你进一步定制：
1. Chrome 浏览器访问时的禁止提示信息
2. F12 控制台中的相关数据
3. 专用 .exe 访问时的抓包数据
