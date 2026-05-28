"""
通过 PowerShell 连接 kdbrowser CDP 执行 JavaScript
"""
import subprocess
import json
import sys


def get_targets():
    ps_script = '''
$response = Invoke-WebRequest -Uri "http://localhost:9222/json" -UseBasicParsing
$targets = $response.Content | ConvertFrom-Json
Write-Output $targets
'''
    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True, text=True, timeout=10
    )
    if result.stdout:
        return json.loads(result.stdout)
    return []


def exec_js(js_code):
    escaped_js = js_code.replace('"', '`"').replace("'", "''")
    
    ps_script = f'''
$ErrorActionPreference = "Stop"
$wsUrl = "ws://localhost:9222/devtools/page/75E4582215992EFDFF78D10E4770CAFF"

$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = [Threading.CancellationToken]::None

try {{
    $asyncResult = $ws.ConnectAsync((Invoke-RestMethod "http://localhost:9222/json" | Where-Object {{$_.title -like "*受理*"}}).webSocketDebuggerUrl, $ct)
    $asyncResult.AsyncWaitHandle.WaitOne(5000)
    
    if ($ws.State -ne 'Open') {{
        Write-Output "连接失败: $($ws.State)"
        exit 1
    }}
    
    $enable1 = [Text.Encoding]::UTF8.GetBytes('{{"id":1,"method":"Runtime.enable"}}')
    $ws.SendAsync([ArraySegment[byte]]$enable1, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
    
    Start-Sleep -Milliseconds 100
    
    $msg = [Text.Encoding]::UTF8.GetBytes('{{"id":2,"method":"Runtime.evaluate","params":{{"expression":"{escaped_js}","returnByValue":true}}}}')
    $ws.SendAsync([ArraySegment[byte]]$msg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
    
    Start-Sleep -Milliseconds 500
    
    $buf = [byte[]]::new(16384)
    $result = $ws.ReceiveAsync([ArraySegment[byte]]$buf, $ct)
    $result.AsyncWaitHandle.WaitOne(3000)
    
    if ($result.IsCompleted) {{
        $text = [Text.Encoding]::UTF8.GetString($buf, 0, $result.Result.Count)
        Write-Output $text
    }}
    
    $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "Done", $ct).Wait()
}} catch {{
    Write-Output "错误: $_"
}}
'''
    
    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout, result.stderr


def main():
    print("正在获取页面信息...")
    
    targets = get_targets()
    if targets:
        print(f"发现 {len(targets)} 个页面")
        for t in targets:
            print(f"  - {t.get('title', '无标题')}")
    
    print("\n正在执行 JavaScript...")
    print("=" * 50)
    
    js_code = sys.argv[1] if len(sys.argv) > 1 else "document.title"
    
    stdout, stderr = exec_js(js_code)
    
    print(f"输出:\n{stdout}")
    if stderr:
        print(f"错误:\n{stderr}")


if __name__ == "__main__":
    main()
