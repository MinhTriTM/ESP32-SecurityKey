# Biên dịch sketch cổng quản trị rồi đưa file gộp vào siêu web nạp.
# arduino-cli đã tự sinh admin_portal.ino.merged.bin (nạp ở 0x0) nên chỉ cần
# kiểm tra rồi copy. Chạy: powershell -ExecutionPolicy Bypass -File scripts/build_admin.ps1
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$env:ARDUINO_DIRECTORIES_DATA = Join-Path $Root '.tooling/data'
$BuildDir = Join-Path $Root '.tooling/build-admin'

& (Join-Path $Root '.tooling/arduino-cli/arduino-cli.exe') compile `
    --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default,FlashMode=dio,PSRAM=opi' `
    --build-path $BuildDir (Join-Path $Root 'firmware/admin_portal')
if ($LASTEXITCODE -ne 0) { exit 1 }

$merged = Join-Path $BuildDir 'admin_portal.ino.merged.bin'
if (-not (Test-Path $merged)) { Write-Output 'Thiếu file gộp, dừng lại.'; exit 1 }
python -c "import sys;d=open(r'$merged','rb').read(4);sys.exit(0 if d[:1]==b'\xe9' else 1)"
if ($LASTEXITCODE -ne 0) { Write-Output 'Bin gộp thiếu bootloader (byte đầu không phải 0xE9).'; exit 1 }

$Out = Join-Path $Root 'web/firmware/admin-portal'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
Copy-Item $merged (Join-Path $Out 'admin_portal.ino.merged.bin')
python (Join-Path $Root 'tools/web_firmware.py')
python (Join-Path $Root 'tools/web_firmware.py') --check
Write-Output 'Xong cổng quản trị.'
