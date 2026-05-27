#!/bin/bash
echo "========================================"
echo "客户资料抓取程序 - 离线安装准备脚本"
echo "========================================"
echo ""

# 创建目录
echo "[1/4] 创建离线包目录..."
mkdir -p offline_packages
mkdir -p offline_browsers
echo ""

# 下载 Python 包
echo "[2/4] 下载 Python 依赖包..."
pip download -r requirements.txt -d ./offline_packages
if [ $? -ne 0 ]; then
    echo "错误：下载 Python 包失败！"
    exit 1
fi
echo "Python 包下载完成！"
echo ""

# 安装 Playwright 并下载浏览器
echo "[3/4] 安装 Playwright 并下载浏览器..."
pip install playwright -d ./offline_packages
pip install --no-index --find-links=./offline_packages playwright

echo "正在下载 Chromium 浏览器..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "警告：浏览器下载可能需要手动操作"
fi
echo ""

# 复制浏览器文件
echo "[4/4] 整理浏览器文件..."
PLAYWRIGHT_CACHE="$HOME/.cache/ms-playwright"
if [ -d "$PLAYWRIGHT_CACHE" ]; then
    for dir in "$PLAYWRIGHT_CACHE"/chromium*; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            echo "找到浏览器文件夹: $dirname"
            cp -r "$dir" "offline_browsers/$dirname"
        fi
    done
fi

echo ""
echo "========================================"
echo "离线准备完成！"
echo "========================================"
echo ""
echo "请将以下文件夹一起复制到内网电脑："
echo "  - offline_packages/"
echo "  - offline_browsers/"
echo "  - 其他所有程序文件"
echo ""
echo "然后在内网电脑上运行 install_offline.sh"
echo ""
