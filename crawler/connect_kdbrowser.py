"""
连接已运行的 kdbrowser - 直接连接到已有页面
"""
import asyncio
import json
import urllib.request
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        try:
            req = urllib.request.Request(
                "http://localhost:9222/json",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                targets = json.loads(resp.read().decode())

            print(f"发现 {len(targets)} 个页面:")
            for i, t in enumerate(targets):
                print(f"  [{i}] {t.get('title', '无标题')}")

            if targets:
                target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), targets[0])
                ws_url = target.get('webSocketDebuggerUrl')

                if ws_url:
                    print(f"\n正在连接到: {target.get('title')}")
                    cdp = await p.chromium.connect(ws_url)
                    page = cdp.pages[0] if cdp.pages else await cdp.new_page()
                    print(f"页面 URL: {page.url}")
                    print(f"页面标题: {await page.title()}")
                    print("\n连接成功！现在可以抓取数据了")
                else:
                    print("未找到 WebSocket URL")

        except Exception as e:
            print(f"失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
