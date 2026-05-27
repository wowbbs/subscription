#!/bin/bash
echo "========================================"
echo "客户资料抓取程序 - 内网安装脚本"
echo "========================================"
echo ""

# 检查目录
echo "[1/3] 检查离线文件..."
if [ ! -d "offline_packages" ]; then
    echo "错误：offline_packages 文件夹不存在！"
    echo "请确保已在外网运行 prepare_offline.sh 准备好文件。"
    exit 1
fi
echo ""

# 安装 Python 包
echo "[2/3] 安装 Python 依赖..."
pip install --no-index --find-links=./offline_packages -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误：安装 Python 包失败！"
    exit 1
fi
echo "Python 包安装完成！"
echo ""

# 复制浏览器文件
echo "[3/3] 安装浏览器..."
PLAYWRIGHT_CACHE="$HOME/.cache/ms-playwright"
mkdir -p "$PLAYWRIGHT_CACHE"

for dir in offline_browsers/*; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        echo "复制浏览器: $dirname"
        if [ -d "$PLAYWRIGHT_CACHE/$dirname" ]; then
            echo "浏览器已存在，跳过"
        else
            cp -r "$dir" "$PLAYWRIGHT_CACHE/$dirname"
        fi
    fi
done

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "接下来请："
echo "  1. 复制 .env.example 为 .env"
echo "  2. 编辑 .env，设置 TARGET_URL"
echo "  3. 运行 python analyze.py 测试"
echo ""
echo "详细说明请查看 README.md"
echo ""
