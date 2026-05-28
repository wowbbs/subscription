"""
直接使用 CDP 协议连接 kdbrowser - 绕过 Playwright 兼容性问题
"""
import asyncio
import json
import websockets


TARGET_URL = "https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2"


async def send_cmd(ws, method, cmd_id=1, params=None):
    msg = {"id": cmd_id, "method": method}
    if params:
        msg["params"] = params
    await ws.send(json.dumps(msg))
    resp = await ws.recv()
    return json.loads(resp)


async def main():
    try:
        import urllib.request
        req = urllib.request.Request(
            "http://localhost:9222/json",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            targets = json.loads(resp.read().decode())

        print(f"发现 {len(targets)} 个页面:")
        for i, t in enumerate(targets):
            print(f"  [{i}] {t.get('title', '无标题')} | {t.get('url', '')[:60]}")

        target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), targets[0])
        ws_url = target.get('webSocketDebuggerUrl')

        if not ws_url:
            print("未找到 WebSocket URL")
            return

        print(f"\n正在连接到: {target.get('title')}")

        async with websockets.connect(ws_url) as ws:
            print("已连接 WebSocket")

            result = await send_cmd(ws, "Target.getTargets")
            print(f"目标信息: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")

            result = await send_cmd(ws, "Page.getFrameTree")
            print(f"\n页面框架: {json.dumps(result, indent=2, ensure_ascii=False)[:800]}")

            result = await send_cmd(ws, "Runtime.evaluate", params={
                "expression": "document.title",
                "returnByValue": True
            })
            print(f"\n页面标题: {result}")

            print("\n连接成功！现在可以执行抓取脚本了")

    except ImportError:
        print("需要安装 websockets: pip install websockets")
    except Exception as e:
        print(f"失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
