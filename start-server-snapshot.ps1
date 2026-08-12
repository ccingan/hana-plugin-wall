# 在本机打开最新的服务器快照，不修改快照内容，也不监听局域网。
param(
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'
$snapshotRoot = Join-Path $PSScriptRoot '_server-snapshot'
$snapshot = Get-ChildItem -LiteralPath $snapshotRoot -Directory -ErrorAction Stop |
    Sort-Object Name -Descending |
    Select-Object -First 1

if (-not $snapshot) {
    throw "没有找到服务器快照：$snapshotRoot"
}

$env:HANA_WALL_DATA_DIR = $snapshot.FullName
$env:PORT = $Port
$env:HANA_WALL_BIND = '127.0.0.1'

Write-Output "正在打开服务器快照：$($snapshot.FullName)"
Write-Output "本地地址：http://127.0.0.1:$Port/"

Set-Location -LiteralPath $snapshot.FullName
python -c @'
import os
import server

os.makedirs(server.DATA_DIR, exist_ok=True)
server.load_tokens()
server.load_sensitive()
host = os.environ.get("HANA_WALL_BIND", "127.0.0.1")
port = int(os.environ.get("PORT", "8765"))
print(f"Hana 插件需求墙本地快照：http://{host}:{port}/", flush=True)
server.ThreadingHTTPServer((host, port), server.Handler).serve_forever()
'@
