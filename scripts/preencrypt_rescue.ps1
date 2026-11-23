# Mã hóa trước ảnh hardened bằng khóa FE của đúng board để nạp lại chip đã khóa.
# Chip SB+FE+secure-download chỉ boot được ảnh vừa ký RSA vừa mã hóa đúng khóa
# FE (bài học key-01: nạp bản thô + --force là gạch boot). Script này chỉ làm
# bước mã hóa (an toàn), rồi IN RA lệnh write_flash để người chạy tự kiểm tra
# trước khi nạp (bước phá hoại). Xem hardware/provision-runbook.md mục 7.
#   powershell -ExecutionPolicy Bypass -File scripts/preencrypt_rescue.ps1 -FeKey keys/fe-key-02.bin
param(
    [Parameter(Mandatory = $true)][string]$FeKey,
    [string]$In = '',
    [string]$Out = ''
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Idf = Join-Path $Root '.tooling/esp-idf'
$env:IDF_TOOLS_PATH = Join-Path $Root '.tooling/esp-tools'

if (-not (Test-Path $FeKey)) { Write-Output "Không thấy khóa FE: $FeKey"; exit 1 }
$keyLen = (Get-Item $FeKey).Length
if ($keyLen -ne 32 -and $keyLen -ne 64) { Write-Output "Khóa FE phải 32 byte (AES-128) hoặc 64 byte (AES-256), thấy $keyLen."; exit 1 }
if ($In -eq '') { $In = Join-Path $Root 'web/firmware/pico-fido-v8.2/pico_fido_esp32-s3-hardened.bin' }
if (-not (Test-Path $In)) { Write-Output "Không thấy ảnh vào: $In"; exit 1 }
$first = [System.IO.File]::ReadAllBytes($In)[0]
if ($first -ne 0xE9) { Write-Output 'Ảnh vào thiếu bootloader (byte đầu không phải 0xE9). Dừng.'; exit 1 }
if ($Out -eq '') { $Out = Join-Path $env:TEMP ("rescue-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + ".bin") }
if (-not (Test-Path (Join-Path $Idf 'export.ps1'))) { Write-Output "Thiếu $Idf. Cài ESP-IDF v5.5.1 vào .tooling/esp-idf trước."; exit 1 }

& (Join-Path $Idf 'export.ps1') | Out-Null
espsecure.py encrypt_flash_data --aes_xts --keyfile $FeKey --address 0x0 --output $Out $In
if ($LASTEXITCODE -ne 0) { exit 1 }
$n = (Get-Item $Out).Length
Write-Output "Đã mã hóa: $Out ($n byte)."
Write-Output ''
Write-Output 'Chạy tay lệnh nạp (thay COMx bằng cổng COM thật, KHÔNG rút cáp giữa chừng):'
Write-Output "esptool.py --chip ESP32-S3 -p COMx -b 115200 --no-stub write_flash --force --flash_mode dio --flash_freq 80m --flash_size keep 0x0 $Out"
