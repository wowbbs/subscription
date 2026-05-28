"""
连接已运行的 kdbrowser - 绕过客户端检测的终极方案

使用方法：
1. 修改 kdbrowser 快捷方式，添加参数：--remote-debugging-port=9222
2. 启动 kdbrowser 并登录乾坤平台
3. 运行本脚本：python connect_kdbrowser.py

这样可以复用 kdbrowser 的登录状态，绕过客户端检测
"""
import asyncio
from playwright.async_api import async_playwright


TARGET_URL = "https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2"


async def main():
    async with async_playwright() as p:
        try:
            print("正在连接 kdbrowser (localhost:9222)...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("连接成功!")

            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[0] if context.pages else await context.new_page()

            if not context.pages:
                print(f"正在导航到目标页面: {TARGET_URL}")
                await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            else:
                print("检测到已有页面，正在使用...")
                page = context.pages[0]
                await page.bring_to_front()

            print(f"页面标题: {await page.title()}")
            print("现在可以在控制台中执行抓取操作了")
            print("按 Ctrl+C 退出")

            while True:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"连接失败: {e}")
            print("\n请确保：")
            print("1. kdbrowser 已添加 --remote-debugging-port=9222 参数启动")
            print("2. kdbrowser 已登录乾坤平台")
            print("3. 端口 9222 未被占用")


if __name__ == "__main__":
    asyncio.run(main())
