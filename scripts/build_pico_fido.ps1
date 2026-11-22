# Build pico-fido v8.2 cho ESP32-S3 rồi gộp binary (U001).
# Dùng ESP-IDF + pico-fido trong .tooling (không động vào bản ngoài).
#   powershell -ExecutionPolicy Bypass -File scripts/build_pico_fido.ps1            # bản thử
#   powershell -ExecutionPolicy Bypass -File scripts/build_pico_fido.ps1 -Variant hardened  # bản ký
param([ValidateSet('plain', 'hardened')]$Variant = 'plain')
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Idf = Join-Path $Root '.tooling/esp-idf'
$Pico = Join-Path $Root '.tooling/pico-fido'
$env:IDF_TOOLS_PATH = Join-Path $Root '.tooling/esp-tools'
$Pinned = '15b848d821b4995eb1b29a5c2a4c24c25d1a768e'  # tag v8.2

if (-not (Test-Path (Join-Path $Idf 'export.ps1'))) { Write-Output "Thiếu $Idf. Cài ESP-IDF v5.5.1 vào .tooling/esp-idf trước."; exit 1 }
if (-not (Test-Path $Pico)) { Write-Output "Thiếu $Pico. Clone pico-fido vào .tooling/pico-fido trước."; exit 1 }
$Head = (git -C $Pico rev-parse HEAD).Trim()
if ($Head -ne $Pinned) { Write-Output "pico-fido không đúng commit v8.2 ($Head). Dừng để kiểm tra."; exit 1 }
if ($Variant -eq 'hardened') {
    $Key = Join-Path $Root 'keys/secure-boot-signing.key'
    $Frag = Join-Path $Root 'config/sdkconfig.hardened'
    if (-not (Test-Path $Key)) { Write-Output "Thiếu $Key. Chạy python tools/gen_sign_key.py trước."; exit 1 }
    if (-not (Test-Path $Frag)) { Write-Output "Thiếu $Frag."; exit 1 }
    $env:SDKCONFIG_DEFAULTS = "$Pico/pico-keys-sdk/config/esp32/sdkconfig.defaults;$Frag"
    Write-Output "Build bản ký (hardened) với $Frag."
} else {
    Write-Output "Build bản thử (plain, không ký)."
}

& (Join-Path $Idf 'export.ps1')
$env:IDF_PATH = ($Idf -replace '\\', '/')  # CMake vỡ với backslash Windows
Set-Location $Pico
if ($Variant -eq 'hardened') { idf.py fullclean }  # đổi sdkconfig phải sạch
idf.py set-target esp32s3
idf.py all
New-Item -ItemType Directory -Force -Path (Join-Path $Pico 'release') | Out-Null
Set-Location (Join-Path $Pico 'build')
esptool.py --chip ESP32-S3 merge_bin -o ../release/pico_fido_esp32-s3.bin '@flash_args'
Set-Location $Root
$Out = Join-Path $Root 'web/firmware/pico-fido-v8.2'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
Copy-Item (Join-Path $Pico "release/pico_fido_esp32-s3.bin") (Join-Path $Out "pico_fido_esp32-s3-$Variant.bin")
python (Join-Path $Root 'tools/web_firmware.py')
python (Join-Path $Root 'tools/web_firmware.py') --check
Write-Output "Xong bản $Variant."
