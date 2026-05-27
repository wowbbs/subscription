# 客户资料抓取程序 - Python 版本

## 📋 程序说明

这是一个使用 **Python + Playwright** 开发的客户资料抓取工具，专门用于访问内网乾坤-集中运营平台。

### ✨ 为什么选择这个方案？

- ✅ **无需安装 Node.js** - 使用你已有的 Python 环境
- ✅ **已配置 Electron 模拟** - 模拟 kdbrowser 的运行环境
- ✅ **已设置正确的请求头** - 与 kdbrowser 完全一致
- ✅ **支持离线安装** - 为内网环境专门准备
- ✅ **操作简单** - 只需几个命令就能运行

---

## 📁 文件说明

| 文件 | 作用 |
|------|------|
| [crawler.py](file:///workspace/crawler/crawler.py) | 主程序 - 登录并抓取数据 |
| [analyze.py](file:///workspace/crawler/analyze.py) | 分析工具 - 测试访问，查看请求 |
| [browser.py](file:///workspace/crawler/browser.py) | 浏览器控制器 - 管理浏览器 |
| [config.py](file:///workspace/crawler/config.py) | 配置文件 - 请求头、参数等 |
| [requirements.txt](file:///workspace/crawler/requirements.txt) | Python 依赖列表 |
| [.env.example](file:///workspace/crawler/.env.example) | 环境变量模板 |
| [prepare_offline.bat](file:///workspace/crawler/prepare_offline.bat) | Windows - 外网准备脚本 |
| [install_offline.bat](file:///workspace/crawler/install_offline.bat) | Windows - 内网安装脚本 |
| [prepare_offline.sh](file:///workspace/crawler/prepare_offline.sh) | Linux/Mac - 外网准备脚本 |
| [install_offline.sh](file:///workspace/crawler/install_offline.sh) | Linux/Mac - 内网安装脚本 |
| [离线安装准备.md](file:///workspace/crawler/离线安装准备.md) | 详细离线安装说明 |

---

## 🔌 离线安装说明（内网环境）

如果内网无法访问外网，请使用离线安装方式。

### 第一步：在外网电脑上准备安装包

**Windows 用户：**
```cmd
# 双击运行
prepare_offline.bat
```

**Linux/Mac 用户：**
```bash
chmod +x prepare_offline.sh
./prepare_offline.sh
```

这一步会：
1. 下载所有 Python 依赖包到 `offline_packages/` 文件夹
2. 下载浏览器到 `offline_browsers/` 文件夹
3. 自动整理好所有文件

准备完成后，把**整个 crawler 文件夹**复制到内网电脑。

### 第二步：在内网电脑上安装

**Windows 用户：**
```cmd
# 双击运行
install_offline.bat
```

**Linux/Mac 用户：**
```bash
chmod +x install_offline.sh
./install_offline.sh
```

安装完成后，继续下面的「配置环境变量」步骤。

---

## 🌐 在线安装说明（有外网环境）

如果有外网环境，可以直接使用在线安装。

---

## 🚀 小白安装步骤（一步步来）

### 第一步：安装 Python 依赖

打开命令行（cmd 或 PowerShell），进入 crawler 文件夹：

```bash
cd crawler
```

安装依赖：

```bash
pip install -r requirements.txt
```

等它安装完成，看到 `Successfully installed` 就好了。

### 第二步：安装浏览器

```bash
playwright install chromium
```

这一步会下载 Chromium 浏览器，可能需要几分钟，耐心等待。

### 第三步：配置环境变量

1. 在 crawler 文件夹里，找到 `.env.example` 文件
2. 复制一份，重命名为 `.env`（注意：Windows 可能默认隐藏扩展名，要确保真的改成了 `.env`）
3. 右键用记事本打开 `.env`，修改以下内容：
   ```
   TARGET_URL=https://qiankundg.web.guosen.com.cn/apps/opp/index.html?theme=web2
   ```
   保存关闭。

### 第四步：测试访问

先测试一下能不能访问：

```bash
python analyze.py
```

如果一切正常，会打开一个浏览器窗口，显示目标网站。

- 如果能正常访问 ✅ - 继续下一步
- 如果还提示「非配套客户端」❌ - 告诉我，我们继续调整

### 第五步：运行抓取程序

```bash
python crawler.py
```

会自动打开浏览器，尝试登录并抓取数据。

---

## 💡 常用命令

| 命令 | 作用 |
|------|------|
| `pip install -r requirements.txt` | 安装依赖 |
| `playwright install chromium` | 安装浏览器 |
| `python analyze.py` | 测试访问 |
| `python crawler.py` | 运行抓取程序 |

---

## ⚙️ 常见问题

### 1. pip 不是内部或外部命令

**问题**：命令行输入 `pip` 提示找不到命令

**解决**：
```bash
# 方法1：使用 python -m pip
python -m pip install -r requirements.txt

# 方法2：检查 Python 安装
python --version
# 如果显示版本号，尝试：
py -m pip install -r requirements.txt
```

### 2. playwright 安装失败

**问题**：安装 playwright 报错

**解决**：
```bash
# 先升级 pip
python -m pip install --upgrade pip

# 再安装
pip install playwright
playwright install chromium
```

### 3. 浏览器打不开

**问题**：程序运行但浏览器窗口没出来

**解决**：
- 确认已运行 `playwright install chromium`
- 确认 Chrome 已正确安装
- 尝试手动指定 Chrome 路径（编辑 `.env` 中的 `CHROME_PATH`）

### 4. 还提示「非配套客户端」

**问题**：浏览器能打开，但还是被检测到

**解决**：
这是我们最需要你反馈的情况！请告诉我：
1. 具体的错误提示
2. 是 `analyze.py` 还是 `crawler.py` 出问题
3. 浏览器里显示的内容

我会帮你调整配置。

---

## 📊 程序工作流程

```
1. 启动浏览器（模拟 Electron/kdbrowser 环境）
   ↓
2. 访问目标网站（使用正确的请求头）
   ↓
3. 尝试自动登录（或手动登录）
   ↓
4. 提取客户数据
   ↓
5. 保存到 data/customers.json
```

---

## 🔧 自定义配置

如果你需要调整配置，编辑 `.env` 文件：

```env
TARGET_URL=你的目标URL
HEADLESS=false          # true = 无头模式，false = 显示浏览器
BROWSER_CHANNEL=chromium  # chromium/chrome/msedge
USERNAME=你的用户名
PASSWORD=你的密码
OUTPUT_PATH=./data/customers.json
```

---

## 🎯 后续步骤

当程序能正常访问后，你需要告诉我：

1. **需要提取哪些字段？**（比如：姓名、手机号、身份证、地址...）
2. **客户列表页面长什么样？**（可以截图）
3. **数据导出格式？**（JSON、Excel、还是其他？）

我会根据你的需求，调整数据提取逻辑。

---

## 📞 需要帮助？

随时告诉我：
- 遇到了什么错误
- 截图或错误信息
- 你想实现什么功能

我会帮你解决！😊
