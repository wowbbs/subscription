"""
配置文件 - 包含请求头、浏览器配置等
"""
import os
from dataclasses import dataclass, field
from typing import Dict

# 与 kdbrowser 完全一致的请求头
DEFAULT_HEADERS: Dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'sec-ch-ua': '"Chromium";v="91", "Google Chrome";v="91", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Kd-Browser': '3.2.24',
}


@dataclass
class BrowserConfig:
    """浏览器配置"""
    headless: bool = False
    channel: str = 'chrome'  # 默认使用系统已安装的 Chrome
    executable_path: str = None


@dataclass
class CrawlerConfig:
    """抓取器配置"""
    target_url: str = ''
    username: str = ''
    password: str = ''
    output_path: str = './data/customers.json'
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    custom_headers: Dict[str, str] = field(default_factory=dict)


def load_config() -> CrawlerConfig:
    """从环境变量加载配置"""
    return CrawlerConfig(
        target_url=os.getenv('TARGET_URL', ''),
        username=os.getenv('USERNAME', ''),
        password=os.getenv('PASSWORD', ''),
        output_path=os.getenv('OUTPUT_PATH', './data/customers.json'),
        browser=BrowserConfig(
            headless=os.getenv('HEADLESS', 'false').lower() != 'true',
            channel=os.getenv('BROWSER_CHANNEL', 'chrome'),  # 默认使用系统 Chrome
            executable_path=os.getenv('CHROME_PATH'),
        ),
        custom_headers={},
    )
