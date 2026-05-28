"""
通过 PowerShell 连接 kdbrowser CDP
"""
import subprocess
import json


def main():
    print("正在获取页面列表...")
    
    result = subprocess.run(
        ['powershell', '-Command', 
         'Invoke-RestMethod http://localhost:9222/json -UseBasicParsing'],
        capture_output=True, text=True, timeout=10
    )
    
    print(f"原始输出:\n{result.stdout}")
    print(f"错误:\n{result.stderr}")


if __name__ == "__main__":
    main()
