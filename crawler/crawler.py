"""
数据抓取逻辑 - 处理登录、数据提取等
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from playwright.sync_api import Page
from browser import BrowserController
from config import CrawlerConfig, load_config


class CustomerCrawler:
    """客户数据抓取器"""

    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.browser_controller = BrowserController(config.browser)

    def initialize(self):
        """初始化浏览器"""
        print("正在启动浏览器...")
        self.browser_controller.launch()
        print("浏览器启动成功！")

    def navigate_to_target(self):
        """导航到目标网站"""
        page = self.browser_controller.get_page()
        if not page:
            raise Exception("页面未初始化")

        print(f"正在导航到: {self.config.target_url}")
        page.goto(self.config.target_url, wait_until='networkidle')
        print("导航完成！")

    def login(self, username: str = None, password: str = None) -> bool:
        """尝试自动登录"""
        page = self.browser_controller.get_page()
        if not page:
            raise Exception("页面未初始化")

        user = username or self.config.username
        passwd = password or self.config.password

        try:
            # 等待登录表单出现
            page.wait_for_selector(
                'input[type="text"], input[name="username"], input[name="user"]',
                timeout=10000
            )

            # 填写用户名
            username_input = page.locator('input[type="text"], input[name="username"], input[name="user"]').first
            if username_input.is_visible():
                username_input.fill(user)

            # 填写密码
            password_input = page.locator('input[type="password"], input[name="password"]').first
            if password_input.is_visible():
                password_input.fill(passwd)

            # 点击登录按钮
            login_button = page.locator('button[type="submit"], input[type="submit"], .login-btn').first
            if login_button.is_visible():
                login_button.click()
                page.wait_for_load_state('networkidle')

            print("自动登录完成！")
            return True

        except Exception as e:
            print(f"自动登录失败: {e}")
            print("请手动登录...")
            return False

    def wait_for_manual_input(self):
        """等待手动操作"""
        page = self.browser_controller.get_page()
        if not page:
            raise Exception("页面未初始化")

        print("请在浏览器中完成登录和导航到客户列表页面...")
        print("准备好后，在控制台按回车键继续...")

        input("按回车键继续...")

    def extract_customer_data(self) -> List[Dict[str, Any]]:
        """提取客户数据 - 需要根据实际页面结构修改"""
        page = self.browser_controller.get_page()
        if not page:
            raise Exception("页面未初始化")

        print("开始提取客户数据...")

        # 使用 JavaScript 提取数据
        data = page.evaluate("""
            () => {
                const customers = [];
                const rows = document.querySelectorAll('table tr, .customer-row, [class*="customer"]');

                rows.forEach(row => {
                    const customer = {};
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
            }
        """)

        print(f"提取到 {len(data)} 条客户数据")
        return data

    def save_data(self, data: List[Dict[str, Any]]):
        """保存数据到文件"""
        output_path = Path(self.config.output_path)

        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存为 JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"数据已保存到: {output_path}")

    def close(self):
        """关闭浏览器"""
        self.browser_controller.close()

    def get_page(self) -> Page:
        """获取页面对象"""
        return self.browser_controller.get_page()


def main():
    """主函数"""
    # 加载配置
    config = load_config()

    if not config.target_url:
        print("错误：请设置 TARGET_URL 环境变量")
        print("示例：")
        print("  Windows: set TARGET_URL=https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2")
        print("  Linux/Mac: export TARGET_URL=https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2")
        return

    # 创建抓取器
    crawler = CustomerCrawler(config)

    try:
        # 初始化
        crawler.initialize()

        # 导航
        crawler.navigate_to_target()

        # 登录
        login_success = crawler.login()
        if not login_success:
            crawler.wait_for_manual_input()

        # 提取数据
        data = crawler.extract_customer_data()

        if data:
            # 保存数据
            crawler.save_data(data)
        else:
            print("未找到数据，可能需要自定义提取逻辑")

        print("\n按 Ctrl+C 退出，或关闭浏览器窗口")

        # 保持浏览器打开
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        crawler.close()


if __name__ == '__main__':
    main()
