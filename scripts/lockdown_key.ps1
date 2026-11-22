# Danh mục khóa chip sau khi flash bản hardened (U002/U015).
# AN TOÀN THEO THIẾT KẾ: script chỉ đọc eFuse và in hướng dẫn từng bước,
# KHÔNG tự đốt fuse nào (fuse một chiều, mỗi lệnh đốt phải gõ tay).
#   powershell -ExecutionPolicy Bypass -File scripts/lockdown_key.ps1 -SerialPort COM5
param([Parameter(Mandatory=$true)]$SerialPort)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$env:IDF_TOOLS_PATH = Join-Path $Root '.tooling/esp-tools'
$Idf = Join-Path $Root '.tooling/esp-idf'
if (-not (Test-Path (Join-Path $Idf 'export.ps1'))) { Write-Output "Thiếu $Idf."; exit 1 }
& (Join-Path $Idf 'export.ps1') | Out-Null

function Read-Summary($tag) {
    $out = Join-Path $env:TEMP "espefuse-summary-$tag.txt"
    espefuse.py -p $SerialPort summary | Tee-Object $out
    Write-Output "(Đã lưu $out)"
}

Write-Output ''
Write-Output 'BƯỚC 1/4: đọc trạng thái eFuse HIỆN TẠI (chỉ đọc, chưa đốt gì).'
Read-Summary 'truoc'
Write-Output 'Đối chiếu: chip mới thì Secure Boot và Flash Encryption đều CHƯA bật.'
Read-Host 'Nhấn Enter để tiếp tục'
Write-Output ''
Write-Output 'BƯỚC 2/4: flash bản hardened rồi boot lần đầu.'
Write-Output '  1. Mở web nạp, chọn gói pico-fido-v8.2-hardened, nạp qua cổng UART.'
Write-Output '  2. Rút ra cắm lại, chờ 30 giây cho lần boot đầu (bootloader tự mã'
Write-Output '     hóa flash và bật Secure Boot, không rút điện giữa chừng).'
Read-Host 'Xong bước 2 thì nhấn Enter'
Write-Output ''
Write-Output 'BƯỚC 3/4: đọc lại eFuse, xác nhận đã khóa.'
Read-Summary 'sau'
Write-Output 'Đối chiếu: Secure Boot phải BẬT, bộ đếm mã hóa flash phải LẺ (1, 3...).'
Write-Output 'Nếu chưa bật: kiểm tra lại đã nạp đúng file -hardened chưa, rồi boot lại.'
Read-Host 'Nhấn Enter để tiếp tục'
Write-Output ''
Write-Output 'BƯỚC 4/4 (TÙY CHỌN, MỘT CHIỀU, CẤM LÀM VỘI): khóa hẳn cổng nạp UART.'
Write-Output '  Đọc mục "UART ROM download mode" trong tài liệu ESP-IDF v5.5.1'
Write-Output '  (bản trong .tooling/esp-idf/docs) TRƯỚC KHI gõ bất kỳ lệnh đốt nào.'
Write-Output '  Khóa rồi thì không flash lại qua UART nữa — chỉ làm khi có key thứ 2'
Write-Output '  chạy ổn và không còn nhu cầu cập nhật qua cổng này.'
Write-Output 'Xong danh mục. Giữ lại 2 file summary trong $env:TEMP để đối chiếu sau.'
