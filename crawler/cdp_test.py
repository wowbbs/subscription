"""
使用标准库连接 kdbrowser CDP 接口
"""
import asyncio
import json
import base64
import urllib.request


async def main():
    print("正在获取浏览器信息...")
    
    req = urllib.request.Request(
        "http://localhost:9222/json/version",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        version = json.loads(resp.read().decode())
        print(f"浏览器版本: {version.get('Browser')}")
        print(f"User-Agent: {version.get('User-Agent')}")

    req = urllib.request.Request(
        "http://localhost:9222/json",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        targets = json.loads(resp.read().decode())

    print(f"\n发现 {len(targets)} 个页面:")
    for i, t in enumerate(targets):
        print(f"  [{i}] {t.get('title', '无标题')}")
        print(f"       URL: {t.get('url', '')[:60]}")
        print(f"       wsUrl: {t.get('webSocketDebuggerUrl', '')[:60]}")

    target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), targets[0])
    ws_url = target.get("webSocketDebuggerUrl", "").replace("localhost", "127.0.0.1")

    print(f"\n目标页面: {target.get('title')}")
    print(f"WebSocket URL: {ws_url}")

    parts = ws_url.replace("ws://", "").split("/", 1)
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 9222
    path = "/" + parts[1] if len(parts) > 1 else "/"

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

    print("\nWebSocket 连接成功!")

    async def send(method, params=None, msg_id=1):
        data = json.dumps({"id": msg_id, "method": method, "params": params or {}}).encode()
        frame = bytearray()
        frame.append(0x81)
        length = len(data)
        if length < 126:
            frame.append(length)
        else:
            frame.append(126)
            frame.extend(length.to_bytes(2, "big"))
        frame.extend(data)
        writer.write(frame)
        await writer.drain()

    await send("Runtime.enable", msg_id=1)
    await send("Page.enable", msg_id=2)

    await send("Runtime.evaluate", {
        "expression": "document.title",
        "returnByValue": True
    }, msg_id=3)

    print("等待响应...")
    for _ in range(5):
        try:
            header = await asyncio.wait_for(reader.read(2), timeout=2)
            if len(header) < 2:
                continue
            length = header[1] & 0x7F
            if length == 126:
                ext = await reader.read(2)
                length = int.from_bytes(ext, "big")
            payload = await reader.read(length)
            if payload:
                result = json.loads(payload.decode())
                print(f"收到响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
        except asyncio.TimeoutError:
            pass

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
