"""
通过 PowerShell 连接 kdbrowser CDP
"""
import subprocess
import json


def get_targets():
    result = subprocess.run(
        ['powershell', '-Command', 
         '(Invoke-RestMethod http://localhost:9222/json | ConvertTo-Json -Depth 10)'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        targets = json.loads(result.stdout)
        if isinstance(targets, dict):
            targets = [targets]
        return targets
    return []


def get_websocket_url():
    targets = get_targets()
    target = next((t for t in targets if 'qiankun' in t.get('url', '').lower() or '受理' in t.get('title', '')), None)
    return target.get('webSocketDebuggerUrl') if target else None


def run_js_via_powershell(ws_url, js_code):
    escaped_js = js_code.replace('"', '\\"').replace('\n', ' ').replace('\r', '')
    
    ps_script = f'''
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = [Threading.CancellationToken]::None
$ws.ConnectAsync((Invoke-RestMethod "http://localhost:9222/json" | Where-Object {{$_.url -match "qiankun"}}).webSocketDebuggerUrl, $ct).Wait()

$msg = [Text.Encoding]::UTF8.GetBytes('{{"id":1,"method":"Runtime.evaluate","params":{{"expression":"{escaped_js}","returnByValue":true}}}}')
$ws.SendAsync([ArraySegment[byte]]$msg, 'Text', $true, $ct).Wait()

$buf = [byte[]]::new(8192)
$resp = $ws.ReceiveAsync([ArraySegment[byte]]$buf, $ct).Result
$text = [Text.Encoding]::UTF8.GetString($buf,0,$resp.Count)
Write-Output $text
$ws.CloseAsync('NormalClosure', "", $ct).Wait()
'''
    
    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout, result.stderr


def main():
    print("正在获取页面信息...")
    
    targets = get_targets()
    print(f"发现 {len(targets)} 个页面")
    
    ws_url = get_websocket_url()
    if ws_url:
        print(f"WebSocket URL: {ws_url}")
        
        print("\n正在执行 JavaScript...")
        stdout, stderr = run_js_via_powershell(ws_url, "document.title")
        
        if stdout:
            print(f"结果: {stdout[:500]}")
        if stderr:
            print(f"错误: {stderr[:500]}")
    else:
        print("未找到目标页面")


if __name__ == "__main__":
    main()
