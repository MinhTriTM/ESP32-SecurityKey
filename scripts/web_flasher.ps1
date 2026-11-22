# Mở siêu web nạp ESP32-S3: dựng server localhost rồi mở trình duyệt.
# Chạy từ thư mục gốc repo:  powershell -ExecutionPolicy Bypass -File scripts/web_flasher.ps1
$Root = Split-Path -Parent $PSScriptRoot
$WebDir = Join-Path $Root 'web'
if (-not (Test-Path (Join-Path $WebDir 'index.html'))) {
    Write-Output "Không thấy web/index.html. Hãy chạy từ thư mục gốc repo."
    exit 1
}
$Url = 'http://localhost:8000/index.html'
Write-Output "Mở $Url ..."
Start-Process $Url
Write-Output "Server chạy tại http://localhost:8000 (nhấn Ctrl+C để dừng)."
Set-Location $WebDir
python -m http.server 8000
