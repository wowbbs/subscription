"""
浏览器控制器 - 管理浏览器启动、反检测、Electron环境模拟等
"""
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config import DEFAULT_HEADERS, BrowserConfig


class BrowserController:
    """浏览器控制器"""

    def __init__(self, config: BrowserConfig):
        self.config = config
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def launch(self):
        """启动浏览器"""
        playwright = sync_playwright().start()

        # 构建启动参数
        launch_options = {
            'headless': self.config.headless,
            'channel': self.config.channel,
            'args': [
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
        }

        if self.config.executable_path:
            launch_options['executable_path'] = self.config.executable_path

        # 启动浏览器
        self.browser = playwright.chromium.launch(**launch_options)

        # 创建上下文，设置请求头
        context_options = {
            'extra_http_headers': DEFAULT_HEADERS,
            'user_agent': DEFAULT_HEADERS['User-Agent'],
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
            'has_touch': False,
            'is_mobile': False,
            'permissions': [],
        }

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()

        # 设置反检测脚本
        self._setup_anti_detection()

        # 拦截所有请求，设置正确的标头
        self._setup_request_interception()

        return self

    def _setup_anti_detection(self):
        """设置反检测脚本，模拟 Electron/kdbrowser 环境"""

        # JavaScript 脚本：隐藏自动化特征，模拟 Electron 环境
        anti_detection_script = """
        () => {
            // 1. 隐藏 webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });

            // 2. 模拟 Electron 环境
            window.process = {
                type: 'renderer',
                versions: {
                    node: '14.16.0',
                    electron: '13.6.9',
                    chrome: '91.0.4472.164'
                }
            };

            // 3. 模拟 Node.js 全局对象
            window.require = function() {};
            window.module = { exports: {} };
            window.exports = {};

            // 4. 添加 Kd-Browser 标识
            window.KdBrowser = {
                version: '3.2.24'
            };

            // 5. 修改 chrome 对象，模拟 Electron 环境
            const originalChrome = window.chrome;
            Object.defineProperty(window, 'chrome', {
                get: () => ({
                    ...originalChrome,
                    app: {
                        isInstalled: false,
                        installState: 'disabled',
                        runningState: 'cannot_run'
                    },
                    runtime: {
                        id: undefined,
                        lastError: undefined,
                        onMessage: {
                            addListener: () => {},
                            removeListener: () => {},
                            hasListener: () => false
                        },
                        sendMessage: () => {},
                        connect: () => ({
                            onMessage: {
                                addListener: () => {},
                                removeListener: () => {},
                                hasListener: () => false
                            },
                            onDisconnect: {
                                addListener: () => {},
                                removeListener: () => {},
                                hasListener: () => false
                            },
                            disconnect: () => {},
                            postMessage: () => {},
                            name: ''
                        })
                    }
                }),
                configurable: true
            });

            // 6. 修改 navigator 属性
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
                configurable: true
            });

            Object.defineProperty(navigator, 'appVersion', {
                get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
                configurable: true
            });

            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32',
                configurable: true
            });

            // 7. 修改 permissions API
            const originalQuery = window.navigator.permissions?.query;
            if (originalQuery) {
                window.navigator.permissions.query = (parameters) => {
                    return parameters.name === 'notifications'
                        ? Promise.resolve({ state: 'granted' })
                        : originalQuery(parameters);
                };
            }

            // 8. 隐藏 Playwright 标记
            delete window.__playwright;
            delete window.__PW_inspect;
            delete window.__PW_driver;

            // 9. 修改 console.log，过滤 Playwright 信息
            const originalLog = console.log;
            console.log = function(...args) {
                if (args[0] && typeof args[0] === 'string' && args[0].includes('playwright')) {
                    return;
                }
                originalLog.apply(console, args);
            };
        }
        """

        self.page.add_init_script(anti_detection_script)

    def _setup_request_interception(self):
        """拦截所有请求，确保请求头正确"""

        def handle_route(route):
            """处理每个请求，设置正确的请求头"""
            headers = {**DEFAULT_HEADERS}

            # 移除可能暴露自动化的标头
            headers.pop('X-Playwright', None)
            headers.pop('Playwright', None)

            route.continue_(headers=headers)

        self.context.route('**/*', handle_route)

    def get_page(self) -> Page:
        """获取页面对象"""
        return self.page

    def get_browser(self) -> Browser:
        """获取浏览器对象"""
        return self.browser

    def set_custom_headers(self, headers: dict):
        """设置自定义请求头"""
        # 更新默认请求头
        DEFAULT_HEADERS.update(headers)

        # 重新设置请求拦截
        def handle_route(route):
            merged_headers = {**DEFAULT_HEADERS, **headers}
            route.continue_(headers=merged_headers)

        self.context.route('**/*', handle_route)

    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
