"""
通过 HTTP 接口获取 kdbrowser 页面内容
"""
import json
import urllib.request


def get_browser_targets():
    req = urllib.request.Request(
        "http://localhost:9222/json",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


def get_page_screenshot(target_id):
    req = urllib.request.Request(
        f"http://localhost:9222/json/screenshot",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


def main():
    print("正在获取浏览器页面列表...")

    try:
        targets = get_browser_targets()

        print(f"\n发现 {len(targets)} 个页面:")
        for i, t in enumerate(targets):
            print(f"  [{i}] {t.get('title', '无标题')}")
            print(f"       URL: {t.get('url', '')}")
            print(f"       ID:  {t.get('id', '')}")
            print()

        target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), targets[0])
        print(f"目标页面: {target.get('title')}")
        print(f"页面 ID:  {target.get('id')}")
        print(f"页面 URL: {target.get('url')}")

    except Exception as e:
        print(f"获取页面列表失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
