@echo off
chcp 65001 >nul
echo ========================================
echo 客户资料抓取程序 - 内网安装脚本
echo ========================================
echo.

REM 检查目录
echo [1/3] 检查离线文件...
if not exist "offline_packages" (
    echo 错误：offline_packages 文件夹不存在！
    echo 请确保已在外网运行 prepare_offline.bat 准备好文件。
    pause
    exit /b 1
)
echo.

REM 安装 Python 包
echo [2/3] 安装 Python 依赖...
pip install --no-index --find-links=./offline_packages -r requirements.txt
if errorlevel 1 (
    echo 错误：安装 Python 包失败！
    pause
    exit /b 1
)
echo Python 包安装完成！
echo.

REM 复制浏览器文件
echo [3/3] 安装浏览器...
if not exist "%LOCALAPPDATA%\ms-playwright" mkdir "%LOCALAPPDATA%\ms-playwright"

for /f "delims=" %%i in ('dir /b /ad "offline_browsers" 2^>nul') do (
    echo 复制浏览器: %%i
    if exist "%LOCALAPPDATA%\ms-playwright\%%i" (
        echo 浏览器已存在，跳过
    ) else (
        xcopy /E /I /Y "offline_browsers\%%i" "%LOCALAPPDATA%\ms-playwright\%%i"
    )
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 接下来请：
echo   1. 复制 .env.example 为 .env
echo   2. 编辑 .env，设置 TARGET_URL
echo   3. 运行 python analyze.py 测试
echo.
echo 详细说明请查看 README.md
echo.
pause
