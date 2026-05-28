"""
UI Automation 抓取工具 - 通过读取窗口内容获取数据
"""
import time
from pywinauto import Application, findwindows


def find_kdbrowser_window():
    windows = findwindows.find_windows(title_re=".*受理平台.*|.*乾坤.*|.*kdbrowser.*")
    if windows:
        return windows[0]
    return None


def get_window_text(hwnd):
    try:
        app = Application().connect(handle=hwnd)
        window = app.window(handle=hwnd)
        return window.texts()
    except Exception as e:
        print(f"获取窗口内容失败: {e}")
        return []


def main():
    print("正在查找 kdbrowser 窗口...")

    hwnd = find_kdbrowser_window()
    if not hwnd:
        print("未找到 kdbrowser 窗口")
        return

    print(f"找到窗口: {hwnd}")

    print("\n获取窗口内容...")
    texts = get_window_text(hwnd)

    print(f"找到 {len(texts)} 个文本元素:")
    for i, text in enumerate(texts):
        if text.strip() and len(text) > 1:
            print(f"  [{i}] {text[:100]}")

    print("\n保存内容到文件...")
    with open("window_content.txt", "w", encoding="utf-8") as f:
        for text in texts:
            if text.strip():
                f.write(text + "\n")

    print("✅ 已保存到 window_content.txt")


if __name__ == "__main__":
    main()
