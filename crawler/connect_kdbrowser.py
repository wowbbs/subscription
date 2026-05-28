"""
通过 HTTP 接口操作 kdbrowser
"""
import json
import urllib.request
import urllib.parse


TARGET_URL = "https://qiankundg.web.guosen.com.cn/apps/opp/operator/index.html?version=3801_20250224&theme=web2&F_YZT_CHANNEL=1"
TARGET_ID = "D44484BB32DE0692EE58DEF6AA3002D9"


def cdp_http(method, params=None):
    data = json.dumps({"method": method, "params": params or {}}).encode()
    req = urllib.request.Request(
        f"http://localhost:9222/{TARGET_ID}/{method}",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_targets():
    req = urllib.request.Request(
        "http://localhost:9222/json",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


def main():
    print("正在获取页面信息...")

    targets = get_targets()
    target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), targets[0])
    global TARGET_ID
    TARGET_ID = target.get("id", TARGET_ID)

    print(f"页面 ID: {TARGET_ID}")

    print("\n尝试执行 CDP 命令...")

    result = cdp_http("json")
    print(f"json: {result}")

    result = cdp_http("DOM.getDocument")
    print(f"DOM.getDocument: {result}")

    result = cdp_http("Runtime.evaluate", {
        "expression": "document.title",
        "returnByValue": True
    })
    print(f"Runtime.evaluate: {result}")


if __name__ == "__main__":
    main()
