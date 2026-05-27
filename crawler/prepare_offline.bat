@echo off
chcp 65001 >nul
echo ========================================
echo 客户资料抓取程序 - 离线安装准备脚本
echo ========================================
echo.

REM 创建目录
echo [1/4] 创建离线包目录...
if not exist "offline_packages" mkdir offline_packages
if not exist "offline_browsers" mkdir offline_browsers
echo.

REM 下载 Python 包
echo [2/4] 下载 Python 依赖包...
pip download -r requirements.txt -d ./offline_packages
if errorlevel 1 (
    echo 错误：下载 Python 包失败！
    pause
    exit /b 1
)
echo Python 包下载完成！
echo.

REM 安装 Playwright 并下载浏览器
echo [3/4] 安装 Playwright 并下载浏览器...
pip install playwright -d ./offline_packages
pip install --no-index --find-links=./offline_packages playwright

echo 正在下载 Chromium 浏览器...
playwright install chromium
if errorlevel 1 (
    echo 警告：浏览器下载可能需要手动操作
)
echo.

REM 复制浏览器文件
echo [4/4] 整理浏览器文件...
for /f "delims=" %%i in ('dir /b /ad "%LOCALAPPDATA%\ms-playwright" 2^>nul ^| findstr /i chromium') do (
    echo 找到浏览器文件夹: %%i
    xcopy /E /I /Y "%LOCALAPPDATA%\ms-playwright\%%i" "offline_browsers\%%i"
)

echo.
echo ========================================
echo 离线准备完成！
echo ========================================
echo.
echo 请将以下文件夹一起复制到内网电脑：
echo   - offline_packages/
echo   - offline_browsers/
echo   - 其他所有程序文件
echo.
echo 然后在内网电脑上运行 install_offline.bat
echo.
pause
