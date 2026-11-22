# Hướng dẫn dựng môi trường dev trên Windows (từ máy trắng)

> Tác giả: Bùi Bình (NCKH-035, nhóm tailieu, đợt 2B).
> Đích đến: từ một máy Windows trắng dựng tới khi chạy được hai lệnh
> `scripts/run_tests.ps1` (7 self-test Python) và `scripts/build_hwtest.ps1`
> (biên dịch sketch hwtest cho ESP32-S3).
> Máy mẫu đã kiểm chứng: Windows + Python 3.12.0, arduino-cli 1.6.0, core ESP32 4.0.0.

## 0. Bản đồ toàn cảnh

| Thành phần | Để làm gì | Bản đã kiểm chứng |
|---|---|---|
| Python ≥ 3.10 | Chạy tool trong `tools/` | 3.12.0 |
| hidapi | `fido_check`, `hid_echo` nói chuyện HID | 0.15.0 |
| liboqs-python + DLL liboqs native | `pqc` (ML-KEM-768) | 0.16.0.2 |
| cryptography | `vault` (AES-256-GCM + PBKDF2) | 50.0.2 |
| qrcode + pillow | Lệnh QR của `split_secret`, `mnemonic` | 8.2 / 13.0.0 |
| numpy (cài system) | `ml_distinguisher` | 2.5.4 |
| arduino-cli + core ESP32 | Build `firmware/hwtest` | 1.6.0 / 4.0.0 |

Quy ước của repo: thư viện Python cài vào `.tooling/pylibs` (không cài
system-wide), DLL liboqs nằm ở `.tooling/oqs`, dữ liệu arduino-cli nằm ở
`.tooling/data`. Hai script `.ps1` tự đặt biến môi trường khi chạy, xem mục 6.

## 1. Cài Python

1. Tải bản cài Windows từ trang chủ Python (python.org), chọn bản **3.10 trở lên**
   (khuyến nghị 3.12, đúng bản máy mẫu).
2. Khi cài đặt, **tick ô "Add python.exe to PATH"** rồi mới nhấn Install.
3. Mở PowerShell mới, kiểm tra:

```powershell
python --version
pip --version
```

Kỳ vọng: in ra `Python 3.12.x` (hoặc ≥ 3.10) và phiên bản pip, không báo lỗi.

## 2. Lấy repo về máy

```powershell
git clone <url-repo>
cd ESP32-SecurityKey
```

Mọi lệnh từ đây trở đi chạy tại **thư mục gốc repo** (nơi chứa `scripts/`, `tools/`).

## 3. Cài thư viện Python

Repo chia requirements theo tool. Cài tất cả vào `.tooling/pylibs`:

```powershell
pip install --target .tooling/pylibs -r tools/requirements.txt
pip install --target .tooling/pylibs -r tools/requirements-vault.txt
pip install --target .tooling/pylibs -r tools/requirements-qr.txt
pip install --target .tooling/pylibs -r tools/requirements-pqc.txt
```

Riêng numpy cài system-wide (vì `ml_distinguisher.py` import `numpy` trực tiếp,
không nằm trong `.tooling/pylibs`):

```powershell
pip install numpy
```

Kiểm tra nhanh:

```powershell
$env:PYTHONPATH = "$PWD\.tooling\pylibs"
python -c "import hid, oqs, cryptography, qrcode, numpy; print('lib ok')"
```

## 4. DLL liboqs native (bước dễ hỏng nhất)

`liboqs-python` chỉ là lớp bọc ctypes, nó cần DLL native `oqs.dll`.
`tools/pqc.py` tìm DLL trong thư mục `bin` bên dưới `OQS_INSTALL_PATH`,
tức repo kỳ vọng file `.tooling/oqs/bin/oqs.dll`.

Có hai đường:

- **Đường A — để `import oqs` tự build:** lần đầu import, gói tự clone +
  build liboqs vào `%USERPROFILE%\_oqs`. Đường này đòi máy có **CMake** và
  **Visual Studio workload "Desktop development with C++"**. Cài đủ hai thứ
  rồi chạy `python -c "import oqs"` một lần cho nó build.
- **Đường B — DLL có sẵn:** chép `oqs.dll` đã build vào `.tooling/oqs/bin/`.
  Không cần CMake/VS, nhưng phải đúng kiến trúc x64 và đúng bản liboqs
  tương thích với liboqs-python đang cài.

Chạy xong kiểm tra:

```powershell
$env:PYTHONPATH = "$PWD\.tooling\pylibs"
$env:OQS_INSTALL_PATH = "$PWD\.tooling\oqs"
python tools/pqc.py --self-test
```

Kỳ vọng: self-test keygen/encap/decap PASS, shared secret hai đầu khớp.

## 5. Cài arduino-cli và core ESP32

Repo dùng arduino-cli đặt trong `.tooling/arduino-cli/arduino-cli.exe`
và dữ liệu riêng trong `.tooling/data` (không dùng chung cấu hình máy).

1. Tải arduino-cli bản Windows x64 (máy mẫu dùng **1.6.0**), giải nén sao cho có
   file `.tooling/arduino-cli/arduino-cli.exe`.
2. Trỏ data dir về repo (mở PowerShell tại gốc repo):

```powershell
$env:ARDUINO_DIRECTORIES_DATA = "$PWD\.tooling\data"
```

3. Thêm URL board của Espressif, cập nhật chỉ mục, cài core đúng bản **4.0.0**:

```powershell
.tooling\arduino-cli\arduino-cli.exe config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
.tooling\arduino-cli\arduino-cli.exe core update-index
.tooling\arduino-cli\arduino-cli.exe core install esp32:esp32@4.0.0
```

4. Kiểm tra:

```powershell
.tooling\arduino-cli\arduino-cli.exe core list
```

Kỳ vọng: dòng `esp32:esp32 4.0.0`.

> Ghi chú: bước `core install` tải vài trăm MB toolchain, mạng yếu có thể
> timeout giữa chừng — chạy lại cùng lệnh là nó tiếp tục, không cần xóa gì.

## 6. Biến môi trường (ai đặt cái gì)

| Biến | Giá trị | Ai đặt |
|---|---|---|
| `PYTHONPATH` | `<repo>\.tooling\pylibs` | `run_tests.ps1` tự đặt; chạy tool lẻ thì tự set |
| `OQS_INSTALL_PATH` | `<repo>\.tooling\oqs` | `run_tests.ps1` tự đặt; chạy `pqc.py` lẻ thì tự set |
| `ARDUINO_DIRECTORIES_DATA` | `<repo>\.tooling\data` | `build_hwtest.ps1` tự đặt; gọi arduino-cli lẻ thì tự set |

Không cần set vĩnh viễn trong System Environment. Set tay trong PowerShell
chỉ có hiệu lực ở cửa sổ hiện tại:

```powershell
$env:PYTHONPATH = "$PWD\.tooling\pylibs"
$env:OQS_INSTALL_PATH = "$PWD\.tooling\oqs"
$env:ARDUINO_DIRECTORIES_DATA = "$PWD\.tooling\data"
```

## 7. Chạy kiểm chứng

### 7.1. Self-test Python

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_tests.ps1
```

Script chạy lần lượt 7 tool với `--self-test`: `fido_check`, `hid_echo`,
`split_secret`, `mnemonic`, `vault`, `pqc`, `ml_distinguisher`.
Kỳ vọng: mỗi mục in `=== tên-tool ===` rồi PASS, lệnh thoát mã 0.
(Cờ `-ExecutionPolicy Bypass` chỉ để Windows không chặn file `.ps1` tải từ mạng.)

### 7.2. Build sketch hwtest

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_hwtest.ps1
```

Script gọi arduino-cli biên dịch `firmware/hwtest` với FQBN
`esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default`, tức **USB CDC On Boot
bật + USB-OTG (TinyUSB)** — đúng cấu hình bản OTG có HID echo.
Kỳ vọng: build xong không lỗi. Muốn build bản HWCDC (không HID echo) thì đổi
`USBMode=default` thành `USBMode=hwcdc`.

Build xong mà có board thật thì làm tiếp theo
[runbook nạp hwtest Windows](runbook-nap-hwtest-windows.md)
(từ cắm cáp tới thấy log) — phần đó cần phần cứng, ngoài phạm vi bài này.

## 8. Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `python` không nhận lệnh | Quên tick Add to PATH | Cài lại Python có tick PATH, mở PowerShell mới |
| `ModuleNotFoundError: hid/oqs/...` | Chưa cài vào pylibs hoặc thiếu `PYTHONPATH` | Chạy 4 lệnh mục 3, set `PYTHONPATH` rồi chạy lại |
| `Thiếu thư viện hid` (mã thoát 2) | Thiếu hidapi | `pip install --target .tooling/pylibs -r tools/requirements.txt` |
| `oqs` báo thiếu shared library / `OqsMissingError` | Thiếu DLL native | Làm mục 4 (đường A hoặc B), set `OQS_INSTALL_PATH` |
| `import oqs` treo/rớt giữa chừng | Thiếu CMake hoặc VS C++ | Cài CMake + VS workload Desktop C++, thử lại |
| `ModuleNotFoundError: numpy` | numpy chưa cài system | `pip install numpy` |
| arduino-cli không thấy core esp32 | Thiếu URL board Espressif | Chạy lại lệnh `config add ...` ở mục 5 rồi `core update-index` |
| `core install` timeout | Mạng yếu, gói toolchain lớn | Chạy lại cùng lệnh |
| PowerShell chặn file `.ps1` | ExecutionPolicy | Thêm `-ExecutionPolicy Bypass` như mục 7 |
| Build báo sai FQBN/option | Gõ sai `CDCOnBoot`/`USBMode` | Đối chiếu đúng chuỗi ở mục 7.2 |
| Tool chạy trên máy khác rớt dù repo giống hệt | Lệch kiến trúc DLL (x86/arm64) hoặc Python khác bản | Đồng bộ Python x64 + `oqs.dll` x64 |

## 9. Checklist chốt

- [ ] `python --version` ≥ 3.10.
- [ ] 4 requirements đã cài vào `.tooling/pylibs`, numpy đã cài.
- [ ] `python tools/pqc.py --self-test` PASS (có DLL native).
- [ ] `arduino-cli core list` hiện `esp32:esp32 4.0.0`.
- [ ] `scripts/run_tests.ps1` xanh cả 7 mục, mã thoát 0.
- [ ] `scripts/build_hwtest.ps1` biên dịch sạch.

## 10. Đọc tiếp

- [runbook nạp hwtest Windows](runbook-nap-hwtest-windows.md) — từ build tới log trên board thật.
- [README sketch hwtest](../firmware/hwtest/README.md) — ý nghĩa từng chế độ USB.
- [Hướng dẫn firmware](04-firmware.md) — build/flash pico-fido chính (cần ESP-IDF).
- Bản song sinh cho Linux do NCKH-041 phụ trách (chưa xuất bản lúc viết bài này).
