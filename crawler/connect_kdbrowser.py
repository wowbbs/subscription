"""
使用 Python 标准库连接 kdbrowser - 完整功能版
"""
import asyncio
import json
import base64
import urllib.request


class CDPClient:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.msg_id = 1
        self.pending = {}
        self._recv_task = None

    async def send(self, method, params=None):
        msg_id = self.msg_id
        self.msg_id += 1
        data = json.dumps({"id": msg_id, "method": method, "params": params or {}}).encode()

        frame = bytearray()
        frame.append(0x81)
        length = len(data)
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(length.to_bytes(2, "big"))
        else:
            frame.append(127)
            frame.extend(length.to_bytes(8, "big"))
        frame.extend(data)

        self.writer.write(frame)
        await self.writer.drain()

        for _ in range(10):
            result = await self._recv_one()
            if result and result.get("id") == msg_id:
                return result.get("result") or result
        return None

    async def _recv_one(self):
        header = await self.reader.read(2)
        if len(header) < 2:
            return None

        length = header[1] & 0x7F
        payload_start = 2

        if length == 126:
            ext = await self.reader.read(2)
            length = int.from_bytes(ext, "big")
            payload_start = 4
        elif length == 127:
            ext = await self.reader.read(8)
            length = int.from_bytes(ext, "big")
            payload_start = 10

        payload = b""
        while len(payload) < length:
            chunk = await self.reader.read(length - len(payload))
            if not chunk:
                break
            payload += chunk

        if payload:
            return json.loads(payload.decode())
        return None

    async def eval_js(self, code):
        result = await self.send("Runtime.evaluate", {
            "expression": code,
            "returnByValue": True
        })
        return result

    async def get_html(self):
        result = await self.eval_js("document.documentElement.outerHTML")
        if result and "result" in result:
            return result["result"].get("value", "")
        return ""


async def main():
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

        target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), targets[0])
        ws_url = target.get("webSocketDebuggerUrl", "").replace("localhost", "127.0.0.1")

        if not ws_url:
            print("未找到 WebSocket URL")
            return

        parts = ws_url.replace("ws://", "").split("/", 1)
        host_port = parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 9222
        path = "/" + parts[1] if len(parts) > 1 else "/"

        print(f"\n正在连接到: {target.get('title')}")

        reader, writer = await asyncio.open_connection(host, port)

        key = base64.b64encode(b"randomkey12345678").decode()
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        writer.write(handshake.encode())
        await writer.drain()

        response = await reader.read(1024)
        if b"101" not in response:
            print("WebSocket 握手失败")
            writer.close()
            return

        print("WebSocket 连接成功!")

        client = CDPClient(reader, writer)

        await client.send("Page.enable")
        await client.send("Runtime.enable")

        title = await client.eval_js("document.title")
        print(f"\n页面标题: {title}")

        url = await client.eval_js("location.href")
        print(f"页面 URL: {url}")

        ready = await client.eval_js("document.readyState")
        print(f"就绪状态: {ready}")

        print("\n✅ 连接成功！输入 JavaScript 代码执行抓取")
        print("按 Ctrl+C 退出\n")

        while True:
            code = input("JS > ").strip()
            if code.lower() in ("exit", "quit", "q"):
                break
            if code:
                result = await client.eval_js(code)
                print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
                print()

    except KeyboardInterrupt:
        print("\n退出中...")
    except Exception as e:
        print(f"失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            writer.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
