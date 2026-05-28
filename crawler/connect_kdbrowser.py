"""
连接已运行的 kdbrowser - 绕过客户端检测
"""
import asyncio
import json
from playwright.async_api import async_playwright


TARGET_URL = "https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2"


async def main():
    async with async_playwright() as p:
        try:
            print("正在获取浏览器信息...")
            version = await p.chromium.connect_over_cdp("http://localhost:9222")
            print(f"已连接 Chrome 版本: {version}")
        except Exception as e:
            print(f"获取版本失败: {e}")

        try:
            import urllib.request
            req = urllib.request.Request(
                "http://localhost:9222/json",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                targets = json.loads(resp.read().decode())
                print(f"\n发现 {len(targets)} 个页面:")
                for t in targets:
                    print(f"  - {t.get('title', '无标题')} | {t.get('url', '')[:80]}")
        except Exception as e:
            print(f"获取页面列表失败: {e}")

        print("\n尝试直接导航到目标页面...")
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            page = await browser.new_page()
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            print(f"页面标题: {await page.title()}")
        except Exception as e:
            print(f"导航失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
