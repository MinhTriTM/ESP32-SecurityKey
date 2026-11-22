# Checklist bring-up board ESP32-S3 mới: từ mở hộp đến echo ok

> Tác giả: Nguyễn Cường (NCKH-051, nhóm firmware, đợt 2C).
> Phạm vi: gom 2 runbook + README hwtest thành một danh sách đánh dấu duy nhất,
> làm từ trên xuống dưới, tick từng ô khi đạt.
> Nguồn: [runbook Windows](runbook-nap-hwtest-windows.md) (ký hiệu **W**),
> [runbook Ubuntu](runbook-nap-hwtest-ubuntu.md) (ký hiệu **U**),
> [firmware/hwtest/README.md](../firmware/hwtest/README.md) (ký hiệu **R**).
> Quy tắc dừng: bất kỳ ô bắt buộc nào không đạt thì DỪNG, xử lý xong mới đi tiếp —
> tuyệt đối không flash firmware FIDO chính khi checklist chưa xanh hết.

## Giai đoạn 0 — Mở hộp và kiểm tra vật lý (W0.1, U0, R)

- [ ] Board ESP32-S3 DevKit còn nguyên trong lụa chống tĩnh điện, không cong chân,
  không trầy mạch, không mùi khét.
- [ ] Đối chiếu chữ in trên shield module với [BOM](../hardware/BOM.md)
  (module đã chốt N16R8 — xem [sơ đồ đấu nối](../hardware/wiring.md) khi cần).
- [ ] Có cáp USB-C **đủ dây dữ liệu** (cáp chỉ sạc làm mất cả buổi debug vô ích).
  Chưa chắc thì thử cáp với điện thoại/ổ cứng trước.
- [ ] Có máy tính Windows 10/11 (làm nhánh **W**) hoặc Ubuntu 22.04/24.04 (nhánh **U**),
  còn trống một cổng USB.

## Giai đoạn 1 — Phân biệt hai cổng USB trên board (W0.2, U0)

- [ ] Tìm cổng ghi `COM`/`UART` (qua chip cầu nối) — dùng để **nạp** (giai đoạn 3–6).
- [ ] Tìm cổng ghi `USB`/`OTG` (nối thẳng GPIO19/GPIO20) — cổng native, dùng cho
  **log CDC và HID echo** (giai đoạn 7–9). Firmware FIDO bắt buộc dùng cổng này.
- [ ] Chụp 1 ảnh mặt trên board: thấy rõ 2 cổng + chữ lụa, khoanh đỏ cổng UART
  ("cắm ở đây để nạp"), khoanh xanh cổng native ("để dành giai đoạn 7–9").

## Giai đoạn 2 — Cài phần mềm (W0.3+W3, U0+U5, R)

- [ ] Cài Arduino IDE bản mới (tải từ trang chủ Arduino).
- [ ] Thêm URL board ESP32 của Espressif vào File → Preferences →
  Additional Board Manager URLs, rồi vào Boards Manager cài core `esp32 by Espressif`,
  khởi động lại IDE.
- [ ] Cài Python 3.10 trở lên (cần cho giai đoạn 9). Ubuntu thiếu backend HID thì
  cài thêm `sudo apt install -y libhidapi-hidraw0`.
- [ ] (Đường thay thế, chọn 1) Muốn nạp bằng dòng lệnh: cài `arduino-cli` + core
  `esp32:esp32`. Muốn PlatformIO: tạo project board `esp32-s3-devkitc-1`, chép
  `hwtest.ino` thành `src/main.cpp`, thêm cờ `-DARDUINO_USB_CDC_ON_BOOT=1`.

## Giai đoạn 3 — Cắm cáp lần đầu, xác định đúng cổng (W1+W2, U1)

- [ ] Cắm cáp vào **cổng UART** của board, đầu kia vào máy. LED nguồn trên board sáng.
- [ ] Nhánh **W**: mở Device Manager → Ports (COM & LPT) → thấy 1 cổng mới
  (vd `COM5`), không dấu chấm than vàng. **Ghi số COM ra giấy.**
- [ ] Nhánh **U**: `dmesg | tail -n 20` thấy `cp210x ... ttyUSB0` hoặc `cdc_acm ...
  ttyACM0`; `ls -l /dev/ttyUSB* /dev/ttyACM* /dev/serial/by-id/` thấy 1 cổng mới
  xuất hiện khi cắm, biến mất khi rút. **Ghi tên cổng (vd `/dev/ttyUSB0`).**
- [ ] Nhánh **U**: `lsusb | grep -i -E 'espressif|cp210|silicon|303a'` thấy 1 dòng mới,
  VID `303a` (native/JTAG) hoặc `10c4` (CP210x cổng UART).
- [ ] Không thấy cổng mới → đổi cáp dữ liệu khác, đổi cổng USB máy tính rồi làm lại.
  W có chấm than vàng → cài driver CP210x/CH340 đúng chip cầu nối.

## Giai đoạn 4 — Riêng Ubuntu: phân quyền + udev, làm 1 lần cho mỗi máy (U2+U3)

- [ ] `id -nG` → chưa có `dialout` thì chạy `sudo usermod -aG dialout "$USER"`,
  **đăng xuất/nhập lại**, kiểm tra `id -nG` đã in ra `dialout`.
- [ ] `ls -l /dev/ttyUSB0` (đúng cổng đã ghi) hiện nhóm `dialout`. Không `chmod 666`,
  không chạy IDE bằng `sudo`.
- [ ] Cắm **cổng native**, `lsusb | grep -i espressif` ghi đúng cặp VID:PID máy mình
  in ra (vd `303a:1001`).
- [ ] Tạo `/etc/udev/rules.d/99-esp32s3.rules` cho VID đó (serial `dialout`,
  hidraw+usb `plugdev`; thêm dòng `10c4` nếu cổng UART dùng CP210x),
  `sudo udevadm control --reload-rules && sudo udevadm trigger`, rút ra cắm lại,
  `ls -l /dev/ttyUSB* /dev/ttyACM* /dev/hidraw*` đúng nhóm.
- [ ] Cổng ACM vừa cắm đã bận → `sudo dmesg | grep -i brltty`, có thì
  `sudo apt remove -y brltty`. Cổng chập chờn/tự reset → tắt ModemManager:
  `sudo systemctl disable --now ModemManager`.

## Giai đoạn 5 — Cấu hình board trong Arduino IDE (W4–W8, U4, R)

- [ ] File → Open → `firmware/hwtest/hwtest.ino` (dòng đầu là comment sketch kiểm
  tra phần cứng ESP32-S3, tab tên `hwtest`).
- [ ] Tools → Board → esp32 → **ESP32S3 Dev Module** (sai board = "thành công giả",
  log rác — lỗi hay gặp nhất).
- [ ] Tools → USB CDC On Boot → **Enabled** (để Disabled thì Serial Monitor trắng
  trơn dù nạp thành công).
- [ ] Tools → USB Mode → **USB-OTG (TinyUSB)** (bật HID echo; để HWCDC thì log in
  `HID echo: TAT` và giai đoạn 9 thất bại).
- [ ] Tools → Port → đúng cổng đã ghi ở giai đoạn 3 (W: `COMx`, U: `/dev/ttyUSBx`
  hoặc `/dev/ttyACMx`). U mà menu Port mờ → quay lại giai đoạn 4.
- [ ] (arduino-cli) `./scripts/build_hwtest.sh` biên dịch xong; nhớ `USBMode=default`
  là HWCDC (echo TẮT), muốn echo phải đổi FQBN sang `USBMode=otg`. (PIO) bật
  TinyUSB OTG trong sdkconfig (`ARDUINO_USB_MODE=0`).

## Giai đoạn 6 — Nạp sketch lên board, cổng UART (W9, U4.5+U5, R)

- [ ] Board đang cắm **cổng UART**. Nhấn Upload (`Ctrl+U`), output chạy hết
  `Connecting...` → `Writing at 0x...` → `Done uploading` / `Hash of data verified`,
  không chữ đỏ `Failed`. U không báo `Permission denied`.
- [ ] Kẹt `Connecting...` → `Failed to connect`: giữ **BOOT**, nhấn-nhả **RESET**
  (vẫn giữ BOOT), thả BOOT khi thấy `Writing at...`. Board vào chế độ download,
  lần sau thường tự vào được.

## Giai đoạn 7 — Serial Monitor 115200, đọc log + heartbeat (W10, U6, R)

- [ ] Nhánh **U**: rút cáp khỏi cổng UART, **cắm sang cổng native** (log CDC đi
  đường native), vào Tools → Port chọn lại cổng native mới hiện. Nhánh **W**: mở
  Serial Monitor ngay (`Ctrl+Shift+M`), 115200 baud, nhấn RESET 1 lần chạy lại từ đầu.
  (Không IDE: `tio /dev/ttyACM0 -b 115200`.)
- [ ] Log hiện đủ khối (giá trị chip/flash/PSRAM/SDK tùy board):
  `=== ESP32-S3 Security Key: hwtest ===`, `Chip: ESP32-S3 rev ...`, `MAC: ...`,
  `CPU: ... MHz, cores: 2`, `Flash: ... bytes`, `PSRAM: ... bytes`, `SDK: ...`,
  `USB mode: 0 (0 la OTG co HID echo, 1 la HWCDC)`,
  `Nhan nut BOOT de test. LED RGB se doi mau.`,
  `HID echo: san sang (vendor page 0xFF00, report ID 1).`
- [ ] Mỗi ~5 giây có 1 dòng `Heartbeat: uptime ... s, heap ...` — board sống ổn định.
- [ ] Monitor trắng → kiểm tra CDC Enabled (giai đoạn 5), đúng cổng, đúng 115200,
  nhấn RESET xem lại. Chữ rác → sai baud, chỉnh 115200. Thấy `HID echo: TAT` hoặc
  `USB mode: 1` → quay lại giai đoạn 5 nạp lại bản OTG.

## Giai đoạn 8 — Thử nút BOOT và LED RGB (W11, U6, R)

- [ ] Giữ Serial Monitor mở. **Nhấn-giữ BOOT** → log `BOOT: nhan`, LED sang
  **xanh dương**.
- [ ] **Thả BOOT** → log `BOOT: nha`, LED về **xanh lá** (màu chờ).
- [ ] (LED RGB địa chỉ thường ở GPIO38 hoặc GPIO48 tùy bản board.)

## Giai đoạn 9 — Kiểm tra HID echo: echo ok (W12, U7, R)

- [ ] Điều kiện vào: giai đoạn 7–8 đạt, board đang bản USB-OTG, cáp cắm **cổng native**
  (W: chuyển cáp từ UART sang native, chờ máy nhận HID mới).
- [ ] Cài thư viện: `pip install -r tools/requirements.txt`
  (U chạy `python3`; thiếu backend thì cài `libhidapi-hidraw0` trước).
- [ ] Kiểm nhanh không cần board: `python tools/hid_echo.py --self-test`
  → `self-test ok: đóng gói report HID echo đúng.`
- [ ] Chạy `python tools/hid_echo.py` từ gốc repo → tool in
  `HID echo ok: 60 byte đi về khớp từng byte. Đường USB HID sống.`
  (Tool gửi 60 byte ngẫu nhiên, đối chiếu từng byte trả về.)
- [ ] Đồng thời log serial hiện `HID echo: da gui lai 64 byte.`
  (W muốn xem dòng này thì cắm lại cổng UART để mở Monitor.)
- [ ] `Không thấy HID echo (usage page 0xFF00)` → cắm nhầm cổng UART / bản HWCDC /
  U thiếu quyền hidraw (quay lại giai đoạn 4–5). `Thiết bị không trả lời` → rút
  cắm lại cổng native, chạy lại test đơn (không dùng echo hiện tại làm kênh tin cậy
  vì race `echoPending` khi host gửi OUT dồn dập — phát hiện của NCKH-003).

## Giai đoạn 10 — Checklist chốt: board đạt bring-up (W13, U8, R)

- [ ] Log in đúng chip `ESP32-S3`, dung lượng flash và PSRAM khớp chữ in trên module.
- [ ] Nhấn BOOT → log `BOOT: nhan` + LED xanh dương; thả → log `BOOT: nha` +
  LED xanh lá.
- [ ] Heartbeat đều mỗi ~5 giây, không treo, không reset lạ.
- [ ] Tool `hid_echo.py` báo 60 byte khớp (bản OTG), serial hiện đã gửi lại 64 byte.
- [ ] **Cả 4 ô trên xanh mới được flash firmware FIDO chính**
  (xem [04-firmware.md](04-firmware.md)). Thiếu 1 ô → dừng, kiểm tra board và cáp.

## Phụ lục — Xử lý sự cố nhanh (W + U9)

| Triệu chứng | Nguyên nhân hay gặp | Quay lại |
|---|---|---|
| `Permission denied` / `Failed to open port` (U) | Chưa vào `dialout` / chưa đăng nhập lại | Giai đoạn 4 |
| Cổng ACM bận ngay khi cắm (U) | `brltty` chiếm | Giai đoạn 4: gỡ `brltty` |
| Cổng chập chờn, tự reset (U) | ModemManager thăm dò | Giai đoạn 4: tắt ModemManager |
| Không thấy cổng mới | Cáp sạc, sai cổng, udev chưa ăn, thiếu driver (W) | Giai đoạn 3 (+ 4 nếu U) |
| Menu Port mờ (U) | Quyền serial / udev | Giai đoạn 4, không `sudo` IDE |
| Kẹt `Connecting...` → `Failed to connect` | Chưa vào download mode | Giai đoạn 6: giữ BOOT + RESET |
| Monitor trắng trơn | CDC Disabled, sai cổng/baud, U xem nhầm cổng | Giai đoạn 5 + 7 |
| `HID echo: TAT` / `USB mode: 1` | Nạp bản HWCDC | Giai đoạn 5: nạp lại bản OTG |
| `Không thấy HID echo 0xFF00` | Nhầm cổng UART, bản HWCDC, thiếu quyền hidraw | Giai đoạn 4 + 5 + 9 |
| `Thiết bị không trả lời` | Race echo / OUT dồn dập | Giai đoạn 9: rút cắm lại, chạy lại |
| Thiếu thư viện `hid` | Chưa `pip install` | Giai đoạn 9 (+ `libhidapi-hidraw0` nếu U) |
