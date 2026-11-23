# 04 — Firmware

## Hai tầng firmware

Tầng kiểm tra: sketch hwtest trong repo, chạy Arduino để xác nhận board sống, USB CDC lên, nút BOOT, LED và HID echo. Nạp tầng này trước.

Tầng dùng thật: pico-fido bản ESP32-S3. Đây mới là firmware FIDO cắm vào trình duyệt.

## Bản pico-fido đã chốt

- Tag: `v8.2` (ngày 2026-10-18, tag ký PGP, GitHub xác thực chữ ký).
- Commit ghim: `15b848d821b4995eb1b29a5c2a4c24c25d1a768e`.
- ESP-IDF yêu cầu: `v5.5.1` (lấy từ script `workflows/autobuild.sh` của repo gốc ở đúng tag này).
- Tính năng chính: CTAP 2.3/CTAP1, passkey, PIN, resident key, credProtect, hmac-secret, OATH/TOTP/HOTP, sao lưu 24 từ, Pico Vault xuất/nhập credential có xác thực, Secure Boot và Secure Lock trên ESP32-S3.

Trạng thái: đã build kiểm chứng trên máy này (2026-11-22, xem dưới). Khi build, đối chiếu SHA commit sau checkout, không tin tag mù vì tag có thể bị dời.

## Bản build đã kiểm chứng trên máy này

Build từ commit đã ghim bằng ESP-IDF v5.5.1 trong `.tooling` (xem
[script build](../scripts/build_pico_fido.ps1)):

- Bản thử `pico_fido_esp32-s3-plain.bin` (799200 byte, gộp ở `0x0`): app
  668128 byte, phân vùng pico (nvs@0x11000, factory@0x20000, part0@0x200000).
- Bản chốt `pico_fido_esp32-s3-hardened.bin`: Secure Boot V2 (RSA-3072,
  khóa ký ngoại tuyến trong `keys/`, vân tay SHA-256 `5060aeae…aa4d6`) và
  KHÔNG bật Flash Encryption — object store của pico-fido v8.2 hỏng vĩnh
  viễn khi bật FE (đã xác minh trên board thật 2026-11-23, xem
  [mục bảo mật](#bật-bảo-mật-phần-cứng)). Phân vùng pico giữ nguyên.
  `espsecure.py verify_signature --version 2` báo chữ ký RSA hợp lệ cho cả
  app và bootloader.
- Cả hai có mặt trong siêu web nạp (mục pico-fido v8.2), đã kiểm SHA-256 qua
  `tools/web_firmware.py --check`.

Lưu ý đã xác minh khi build:

- USB VID/PID mặc định của pico-fido là `0x2E8A:0x10FE` (của Raspberry Pi,
  dùng nội bộ theo giấy phép của dự án gốc). Tool và udev rules của repo
  khớp theo usage page nên không ảnh hưởng.
- Cấu hình flash là DIO 80 MHz, 4 MB (dù board N16R8 có 16 MB): flash Boya
  trên board này chết với QIO và treo với OPI (đã xác minh trên board thật
  2026-11-23), chỉ DIO boot được. Nạp và boot bình thường, chỉ không dùng
  phần trên 4 MB.
- Bootloader bản ký (~45 KB) vượt giới hạn 32 KB mặc định nên bảng phân vùng
  dời lên `0x10000` (xem `config/sdkconfig.hardened`); phân vùng pico dùng
  địa chỉ tuyệt đối nên vẫn khớp.
- Trên Windows phải đặt `IDF_PATH` dạng gạch chéo (`D:/...`) trước khi chạy
  `idf.py`, nếu không CMake vỡ với backslash (script build đã làm sẵn).

Giấy phép pico-fido là AGPL-3.0 (bản cộng đồng): tự build dùng cá nhân thoải mái, nhưng phân phối binary đã sửa thì phải công bố source theo giấy phép. Code trong repo này vẫn là MIT, hai phần độc lập.

## Chuẩn bị máy build (Linux/Ubuntu)

Cài gói hệ thống theo đúng script gốc:

```
sudo apt install -y git wget flex bison gperf python3 python3-pip python3-venv \
  cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```

Cài ESP-IDF đúng bản v5.5.1:

```
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf && git checkout tags/v5.5.1 && ./install.sh esp32s3
. ./export.sh
```

Trên Windows thì cài ESP-IDF qua bộ cài chính thức của Espressif, chọn bản v5.5.1.

## Nạp bằng siêu web (cách dễ nhất)

Mở siêu web nạp trong repo rồi nạp thẳng từ trình duyệt, không cần cài esptool:

```
powershell -ExecutionPolicy Bypass -File scripts/web_flasher.ps1   # Windows
bash scripts/web_flasher.sh                                        # Linux
```

Web tự mở tại `http://localhost:8000`. Cắm board bằng cổng USB-UART, bấm Kết nối,
chọn gói hwtest có sẵn (đã kiểm tra SHA-256) rồi bấm Nạp. Nạp xong web tự mở
Serial Monitor để xem log. Pico-fido tự build thì thêm file gộp `.bin` ở địa chỉ
`0x0` trong mục file tự chọn. Cần Chrome/Edge trên máy tính. Chi tiết xem
[web/README](../web/README.md).

## Quy trình build và flash

1. Đọc chữ in trên shield module để xác định đúng dung lượng flash. Xem [BOM](../hardware/BOM.md).
2. Clone pico-fido, checkout đúng commit đã ghim, kiểm tra SHA, cập nhật submodule:
   ```
   git clone https://github.com/polhenarejos/pico-fido
   cd pico-fido
   git checkout 15b848d821b4995eb1b29a5c2a4c24c25d1a768e
   git rev-parse HEAD   # phải in ra đúng SHA trên
   git submodule update --init --recursive
   ```
3. Nạp sketch [hwtest](../firmware/hwtest/hwtest.ino) trước để xác nhận cổng USB native, nút, LED và HID echo.
4. Build cho ESP32-S3 rồi gộp binary:
   ```
   idf.py set-target esp32s3
   idf.py all
   esptool.py --chip ESP32-S3 merge_bin -o release/pico_fido_esp32-s3.bin @flash_args
   ```
5. Flash qua cổng UART (thay PORT bằng cổng thật, kiểm tra kỹ trước khi chạy):
   ```
   esptool.py --chip ESP32-S3 -p PORT write_flash 0x0 release/pico_fido_esp32-s3.bin
   ```
6. Rút ra cắm lại bằng cổng USB native, kiểm tra máy tính nhận HID FIDO.
7. Chạy [tool kiểm tra](../tools/fido_check.py) để gửi INIT, PING và CTAP2 GetInfo.
8. Đăng ký thử trên một dịch vụ phụ trước khi đưa vào tài khoản chính.

Script mẫu nằm ở [scripts](../scripts). Đọc kỹ từng lệnh trước khi chạy vì sai cổng COM là flash nhầm thiết bị.

Đường dễ nhất (nhưng tin binary người khác build): công cụ ESP32 Flasher trên web của PicoKeys. Bản dùng thật nên tự build từ commit đã ghim để kiểm soát chuỗi cung ứng.

## Bật bảo mật phần cứng

Bản dùng thật bật Secure Boot V2 + Flash Encryption release theo tài liệu ESP-IDF, kèm điều kiện bắt buộc: phân vùng part0 phải có cờ `encrypted` (xem `config/partitions-pico-encrypted.csv`). Nguyên nhân đã xác minh từ source (2026-11-23): `esp_partition_write` chỉ mã hóa phân vùng có cờ, trong khi mọi lệnh đọc qua mmap đều giải mã cứng khi FE bật — thiếu cờ là ghi thô + đọc rác, kho hỏng, CTAP trả `0x21`. Đây chính là bệnh của key-01 lúc đầu.

Bài học thứ hai từ key-01 (xác minh bằng log ROM `invalid header` lặp vô tận): ở Secure Download Mode, ROM **không** mã hóa khi ghi — nạp bản thô + `--force` lên chip FE đã khóa là tự gạch khả năng boot. Muốn nạp lại phải mã hóa trước ảnh bằng đúng khóa FE của chip. Vì vậy khi provision key mới **bắt buộc tự sinh khóa FE trên máy, đốt vào eFuse và cất offline + backup cùng khóa ký RSA** (mặc định chip tự sinh rồi giấu luôn là mất đường cứu hộ). Lần nạp đầu trên chip mới vẫn nạp bản thô bình thường, lần boot đầu chip tự mã hóa toàn bộ gồm cả part0 có cờ. Cấu hình này mạch lạc về lý thuyết và chờ chứng minh trên chip mới — xem [nghiên cứu cứu hộ](../docs/research/11-cuu-key-01.md).

Pico-fido còn hỗ trợ Secure Lock và lưu khóa mã hóa chính trong vùng OTP của ESP32-S3. Bật theo tài liệu của dự án gốc sau khi flash xong.

Sau khi flash bản cuối, làm tiếp danh sách khóa cổng nạp và bịt cổng UART trong [tài liệu bảo mật](06-bao-mat.md). Các thao tác efuse là một chiều, sai cấu hình có thể khóa luôn board nên đọc kỹ tài liệu trước.

## Cập nhật firmware

Pico-fido v8.2 trên ESP32-S3 KHÔNG có OTA (bảng phân vùng không có khe ota, code không gọi API OTA nào — đã đối chiếu source 2026-11-23). Đường cập nhật duy nhất là cắm cáp flash qua UART/USB.

Chỉ flash bản build từ commit đã ghim và đã kiểm tra SHA. Giữ lại bản cũ đang chạy ổn cho tới khi bản mới vượt qua kiểm tra đăng nhập thử. Không cập nhật cả hai key dự phòng cùng lúc.

Nguồn: [pico-fido v8.2](https://github.com/polhenarejos/pico-fido/releases/tag/v8.2),
[autobuild.sh ở v8.2](https://github.com/polhenarejos/pico-fido/blob/v8.2/workflows/autobuild.sh).
