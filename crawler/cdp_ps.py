"""
直接通过 PowerShell 执行 JavaScript
"""
import subprocess
import sys


def exec_js(js_code):
    escaped_js = js_code.replace('"', '`"')
    
    ps_script = f'''
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = [Threading.CancellationToken]::None
$jsonResp = Invoke-RestMethod "http://localhost:9222/json" -UseBasicParsing | Where-Object {{$_.title -like "*受理*"}}
$wsUrl = $jsonResp.webSocketDebuggerUrl
Write-Host "连接: $wsUrl"
$ws.ConnectAsync($wsUrl, $ct).Wait(5000)
if ($ws.State -ne 'Open') {{ Write-Host "状态: $($ws.State)"; return }}
Write-Host "已连接"
$msg = [Text.Encoding]::UTF8.GetBytes('{{"id":1,"method":"Runtime.evaluate","params":{{"expression":"{escaped_js}","returnByValue":true}}}}')
$ws.SendAsync([ArraySegment[byte]]$msg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
Start-Sleep -Milliseconds 800
$buf = [byte[]]::new(8192)
$r = $ws.ReceiveAsync([ArraySegment[byte]]$buf, $ct)
$r.AsyncWaitHandle.WaitOne(2000)
if ($r.IsCompleted) {{ Write-Host [Text.Encoding]::UTF8.GetString($buf,0,$r.Result.Count) }}
$ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "", $ct).Wait()
'''
    
    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout + result.stderr


def main():
    js = sys.argv[1] if len(sys.argv) > 1 else "document.title"
    print(f"执行: {js}")
    print("-" * 50)
    result = exec_js(js)
    print(result)


if __name__ == "__main__":
    main()
