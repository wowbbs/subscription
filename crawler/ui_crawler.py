"""
通过键盘模拟抓取网页内容
"""
import time
import win32clipboard
import win32api
import win32con
import win32gui


def copy_clipboard():
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    except:
        data = ""
    win32clipboard.CloseClipboard()
    return data


def send_keys(key, hold=False):
    win32api.keybd_event(key, 0, 0, 0)
    if not hold:
        time.sleep(0.05)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)


def select_all_copy():
    send_keys(win32con.VK_CONTROL, hold=True)
    send_keys(ord('A'))
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    time.sleep(0.5)
    
    send_keys(win32con.VK_CONTROL, hold=True)
    send_keys(ord('C'))
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    time.sleep(0.5)
    
    return copy_clipboard()


def find_and_activate_kdbrowser():
    def callback(hwnd, extra):
        title = win32gui.GetWindowText(hwnd)
        if '受理平台' in title or '乾坤' in title:
            extra.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    
    if windows:
        hwnd = windows[0]
        print(f"找到窗口: {win32gui.GetWindowText(hwnd)}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)
        return True
    return False


def main():
    print("准备抓取网页内容...")

    if not find_and_activate_kdbrowser():
        print("❌ 未找到 kdbrowser 窗口")
        return

    print("正在执行 Ctrl+A Ctrl+C...")
    content = select_all_copy()

    print(f"\n抓取到 {len(content)} 字符")
    print("前500字符预览:")
    print(content[:500])

    if content:
        with open("page_content.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("\n✅ 已保存到 page_content.txt")
    else:
        print("\n❌ 未抓取到内容")


if __name__ == "__main__":
    main()
