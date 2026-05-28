"""
使用 Python 标准库连接 kdbrowser - 无需额外安装
"""
import asyncio
import json
import base64
import urllib.request


async def websocket_connect(url):
    url = url.replace("localhost", "127.0.0.1")

    parts = url.replace("ws://", "").split("/", 1)
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 9222
    path = "/" + parts[1] if len(parts) > 1 else "/"

    import asyncio
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
        print("WebSocket 握手失败:", response.decode()[:200])
        writer.close()
        return None, None

    print("WebSocket 握手成功!")
    return reader, writer


async def ws_send(writer, msg_id, method, params=None):
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
    writer.write(frame)
    await writer.drain()


async def ws_recv(reader):
    data = await reader.read(8192)
    if len(data) < 2:
        return None
    length = data[1] & 0x7F
    payload_start = 2
    if length == 126:
        length = int.from_bytes(data[2:4], "big")
        payload_start = 4
    elif length == 127:
        length = int.from_bytes(data[2:10], "big")
        payload_start = 10
    payload = data[payload_start:payload_start + length]
    return json.loads(payload.decode())


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
        ws_url = target.get("webSocketDebuggerUrl")

        if not ws_url:
            print("未找到 WebSocket URL")
            return

        print(f"\n正在连接到: {target.get('title')}")

        reader, writer = await websocket_connect(ws_url)
        if not reader:
            return

        await ws_send(writer, 1, "Page.enable")
        resp = await ws_recv(reader)
        print(f"Page.enable: {resp}")

        await ws_send(writer, 2, "Runtime.enable")
        resp = await ws_recv(reader)
        print(f"Runtime.enable: {resp}")

        await ws_send(writer, 3, "Runtime.evaluate", {
            "expression": "document.title",
            "returnByValue": True
        })
        resp = await ws_recv(reader)
        print(f"\n页面标题: {resp}")

        print("\n✅ 连接成功！现在可以执行抓取")

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
