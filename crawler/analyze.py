"""
网络请求分析工具 - 用于调试和分析请求头
"""
import os
from browser import BrowserController
from config import BrowserConfig, load_config


def analyze_headers():
    """分析网络请求头"""
    config = load_config()

    if not config.target_url:
        print("错误：请设置 TARGET_URL 环境变量")
        print("示例：")
        print("  Windows: set TARGET_URL=https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2")
        print("  Linux/Mac: export TARGET_URL=https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2")
        return

    print("正在启动浏览器用于分析...")
    controller = BrowserController(BrowserConfig(headless=False))
    controller.launch()

    page = controller.get_page()
    context = controller.context

    if not page or not context:
        print("错误：页面初始化失败")
        controller.close()
        return

    # 设置请求拦截，显示所有请求
    context.on("request", lambda request: print_request(request))
    context.on("response", lambda response: print_response(response))

    print(f"\n请在浏览器中访问: {config.target_url}")
    print("所有的网络请求和响应都会显示在控制台中")
    print("按 Ctrl+C 退出\n")

    try:
        # 保持程序运行
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        controller.close()


def print_request(request):
    """打印请求信息"""
    print("\n" + "=" * 80)
    print(f"【请求】{request.method} {request.url}")
    print("-" * 80)
    print("请求头:")
    for key, value in request.headers.items():
        print(f"  {key}: {value}")


def print_response(response):
    """打印响应信息"""
    print("\n" + "=" * 80)
    print(f"【响应】{response.status} {response.url}")
    print("-" * 80)
    print("响应头:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    analyze_headers()
