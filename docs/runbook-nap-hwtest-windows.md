# Runbook: nạp sketch hwtest trên Windows

> Tác giả: Lý An (NCKH-015, nhóm firmware, đợt 2A).
> Phạm vi: từ cắm cáp tới khi thấy log hwtest trên Serial Monitor.
> Nguồn kỹ thuật: [firmware/hwtest/README.md](../firmware/hwtest/README.md),
> [firmware/hwtest/hwtest.ino](../firmware/hwtest/hwtest.ino),
> [tools/hid_echo.py](../tools/hid_echo.py),
> [docs/03-phan-cung.md](03-phan-cung.md).

## 0. Chuẩn bị

### 0.1. Phần cứng cần có

- Board ESP32-S3 DevKit (module trong lụa, đối chiếu [BOM](../hardware/BOM.md)).
- Cáp USB-C **có đủ dây dữ liệu** (không dùng cáp chỉ sạc).
- Một máy Windows 10/11, một cổng USB còn trống.

### 0.2. Phân biệt hai cổng USB trên board (đọc kỹ trước khi cắm)

Nhiều board DevKit có **hai cổng USB-C**:

| Cổng | Chữ in trên lụa (thường gặp) | Dùng để |
|---|---|---|
| Cổng UART (qua chip cầu nối) | `COM`, `UART` | **Nạp firmware** (bước 1–10) |
| Cổng USB native (nối thẳng GPIO19/GPIO20) | `USB`, `OTG` | **Kiểm tra HID echo** (mục 12) |

*Ảnh chụp mong đợi: ảnh chụp mặt trên board, thấy rõ hai cổng USB-C và chữ in lụa
kế bên; khoanh đỏ cổng UART với chú thích "cắm ở đây để nạp", khoanh xanh cổng
native với chú thích "để dành cho mục 12".*

### 0.3. Phần mềm cần cài

- Arduino IDE bản mới (tải từ trang chủ Arduino).
- Core ESP32 của Espressif (cài trong Board Manager, xem bước 3).
- Python 3.10 trở lên (chỉ cần cho bước kiểm tra HID echo).

## 1. Cắm cáp vào cổng UART

1. Cắm đầu USB-C vào **cổng UART** của board (cổng ghi `COM`/`UART`).
2. Cắm đầu còn lại vào máy Windows.
3. LED nguồn trên board sáng lên.

*Ảnh chụp mong đợi: board đã cắm cáp, LED nguồn sáng; đầu cáp nằm ở cổng có chữ
`UART`/`COM`, cổng còn lại để trống.*

## 2. Kiểm tra máy nhận cổng COM

1. Nhấn `Win + X` → chọn **Device Manager**.
2. Mở nhánh **Ports (COM & LPT)**.
3. Phải thấy một cổng mới, ví dụ `USB Serial Device (COM5)` hoặc
   `Silicon Labs CP210x USB to UART Bridge (COM4)`. **Ghi nhớ số COM này.**

*Ảnh chụp mong đợi: cửa sổ Device Manager, nhánh Ports mở rộng, thấy một dòng
cổng COM của board, không có dấu chấm than vàng.*

Xử lý sự cố:

- Không thấy cổng nào mới: đổi cáp khác (nghi cáp chỉ sạc), đổi cổng USB máy tính.
- Có dấu chấm than vàng: thiếu driver chip cầu nối (CP210x hoặc CH340 tùy board),
  tải driver từ trang chủ hãng chip, cài xong rút ra cắm lại.

## 3. Cài Arduino IDE và core ESP32

1. Cài Arduino IDE, mở lên.
2. Vào **File → Preferences**, thêm URL board ESP32 của Espressif vào ô
   *Additional Board Manager URLs* (lấy URL mới nhất từ tài liệu Espressif).
3. Vào **Tools → Board → Boards Manager**, tìm `esp32`, cài core của Espressif.
4. Khởi động lại Arduino IDE.

*Ảnh chụp mong đợi: cửa sổ Boards Manager hiện `esp32 by Espressif Systems` với nút
`INSTALLED`; ô tìm kiếm gõ "esp32".*

## 4. Mở sketch hwtest

1. Trong Arduino IDE: **File → Open**.
2. Trỏ tới file `firmware/hwtest/hwtest.ino` trong repo này.
3. Cửa sổ soạn thảo hiện code, dòng đầu là comment
   `Sketch kiểm tra phần cứng cho ESP32-S3 Security Key.`

*Ảnh chụp mong đợi: Arduino IDE mở file `hwtest.ino`, thấy tab tên `hwtest`,
thanh tiêu đề hiện đúng đường dẫn file trong repo.*

## 5. Chọn đúng board

1. Vào **Tools → Board → esp32 → ESP32S3 Dev Module**.
2. Kiểm tra thanh trạng thái góc dưới IDE hiện `ESP32S3 Dev Module`.
3. BẮT BUỘC với module N16R8: vào **Tools → Flash Mode → DIO 80MHz** và
   **Tools → PSRAM → OPI PSRAM**. Flash QIO/OPI làm board reset liên tục
   (`TG0WDT`/`RTCWDT` trên log UART) và cổng USB chập chờn (đã xác minh
   trên board thật 2026-11-23).

*Ảnh chụp mong đợi: menu Tools → Board đang mở, mục `ESP32S3 Dev Module` được
đánh dấu tick; góc dưới IDE hiện tên board này.*

> Sai board là lỗi hay gặp nhất: nạp cho board khác có thể "thành công giả" rồi
> log rác hoặc không chạy. Đọc chữ in trên shield module và đối chiếu
> [BOM](../hardware/BOM.md) nếu chưa chắc.

## 6. Bật USB CDC On Boot = Enabled

1. Vào **Tools → USB CDC On Boot → Enabled**.

*Ảnh chụp mong đợi: menu Tools mở tới mục `USB CDC On Boot`, giá trị `Enabled`
được tick.*

> Nếu để Disabled, `Serial` trong sketch không nối ra USB, Serial Monitor sẽ
> trắng trơn dù nạp thành công.

## 7. Đặt USB Mode = USB-OTG (TinyUSB)

1. Vào **Tools → USB Mode → USB-OTG (TinyUSB)**.

*Ảnh chụp mong đợi: menu Tools mở tới mục `USB Mode`, giá trị
`USB-OTG (TinyUSB)` được tick.*

> Chế độ này bật HID echo (log sẽ in `USB mode: 0`). Nếu để HWCDC thì sketch vẫn
> chạy nhưng log in `HID echo: TAT` và mục 12 sẽ thất bại.

## 8. Chọn đúng cổng COM

1. Vào **Tools → Port**, chọn đúng số COM đã ghi ở bước 2
   (ví dụ `COM5`).

*Ảnh chụp mong đợi: menu Tools → Port, cổng COM của board được tick, trùng số COM
đã thấy trong Device Manager ở bước 2.*

> Kiểm tra kỹ trước khi nạp: sai cổng COM là flash nhầm thiết bị khác.

## 9. Nạp sketch lên board

1. Nhấn nút **Upload** (mũi tên sang phải) hoặc `Ctrl + U`.
2. Khung output phía dưới chạy biên dịch, rồi hiện `Connecting...` và các dòng
   `Writing at 0x...`, cuối cùng báo nạp xong (`Done uploading` / `Hash of data
   verified`).

*Ảnh chụp mong đợi: khung output Arduino IDE hiện các dòng nạp và dòng cuối báo
thành công, không có chữ đỏ `Failed`.*

Xử lý khi kẹt ở `Connecting...` mãi rồi báo `Failed to connect`:

1. Nhấn **giữ nút BOOT** trên board.
2. Nhấn-nhả nút **RESET** (vẫn giữ BOOT).
3. Thả nút BOOT sau khi IDE bắt đầu ghi (`Writing at...`).
4. Board vào chế độ download, lần nạp sau thường tự vào được.

## 10. Mở Serial Monitor và đọc log

1. Vào **Tools → Serial Monitor** (hoặc `Ctrl + Shift + M`).
2. Đặt tốc độ góc dưới khung Monitor là **115200 baud**.
3. Nhấn nút **RESET** trên board một lần để chạy lại từ đầu.
4. Log kỳ vọng (giá trị chip/flash/PSRAM/SDK tùy board):

```
=== ESP32-S3 Security Key: hwtest ===
Chip: ESP32-S3 rev 0
MAC: 30:AE:A4:12:34:56
CPU: 240 MHz, cores: 2
Flash: 16777216 bytes
PSRAM: 8388608 bytes
SDK: v5.x.x
USB mode: 0 (0 la OTG co HID echo, 1 la HWCDC)
Nhan nut BOOT de test. LED RGB se doi mau.
======================================
HID echo: san sang (vendor page 0xFF00, 64 byte, khong report ID).
```

5. Khoảng mỗi 5 giây có thêm một dòng heartbeat:

```
Heartbeat: uptime 10 s, heap 123456
```

*Ảnh chụp mong đợi: cửa sổ Serial Monitor 115200 baud hiện đủ khối log trên, từ
dòng `=== ESP32-S3 Security Key: hwtest ===` tới dòng `HID echo: san sang...`,
kèm ít nhất một dòng `Heartbeat`.*

Xử lý sự cố:

- Monitor trắng trơn: kiểm tra lại bước 6 (USB CDC On Boot), đúng cổng COM,
  đúng 115200 baud; nhấn RESET rồi xem lại.
- Chữ rác (ký tự lạ): sai baud, chỉnh lại 115200.
- Thấy `HID echo: TAT (can USB Mode = USB-OTG)`: quay lại bước 7, nạp lại.
- Thấy `USB mode: 1`: đang ở HWCDC, quay lại bước 7, nạp lại.

## 11. Thử nút BOOT và LED

1. Giữ Serial Monitor mở.
2. **Nhấn và giữ** nút BOOT trên board → log hiện `BOOT: nhan`, LED đổi sang
   **xanh dương**.
3. **Thả** nút BOOT → log hiện `BOOT: nha`, LED về **xanh lá**.

*Ảnh chụp mong đợi (2 ảnh): (a) đang giữ nút BOOT, Serial Monitor hiện dòng
`BOOT: nhan`, LED trên board màu xanh dương; (b) sau khi thả, Monitor hiện thêm
dòng `BOOT: nha`, LED về xanh lá.*

> LED RGB địa chỉ thường ở GPIO38 hoặc GPIO48 tùy bản board
> (xem [sơ đồ đấu nối](../hardware/wiring.md)).

## 12. Kiểm tra HID echo (cổng native + tool Python)

1. **Chuyển cáp** từ cổng UART sang **cổng USB native** (cổng ghi `USB`/`OTG`).
2. Chờ vài giây cho Windows nhận thiết bị HID mới.
3. Mở PowerShell tại thư mục gốc repo, cài thư viện rồi chạy tool:

```powershell
pip install -r tools/requirements.txt
python tools/hid_echo.py
```

4. Kết quả đạt: tool in

```
HID echo ok: 60 byte đi về khớp từng byte. Đường USB HID sống.
```

5. Đồng thời trên Serial Monitor (nếu còn mở qua cổng UART — cần cắm lại cổng
   UART để xem) hiện dòng:

```
HID echo: da gui lai 64 byte.
```

*Ảnh chụp mong đợi: cửa sổ PowerShell hiện lệnh `python tools/hid_echo.py` và
dòng `HID echo ok: 60 byte đi về khớp từng byte...` ngay dưới; cửa sổ Serial
Monitor (ảnh thứ hai) hiện dòng `HID echo: da gui lai 64 byte.`*

Xử lý sự cố:

- `Không thấy HID echo (usage page 0xFF00)`: đang cắm nhầm cổng UART, hoặc bản
  đã nạp là HWCDC (quay lại bước 7, nạp lại, rồi cắm cổng native).
- `Thiết bị không trả lời`: rút ra cắm lại cổng native, chạy lại tool.
- `Thiếu thư viện hid`: chạy lại `pip install -r tools/requirements.txt`.

## 13. Kết quả đạt (checklist chốt)

- [ ] Log in đúng chip `ESP32-S3`, dung lượng flash và PSRAM khớp chữ in trên
      module ([BOM](../hardware/BOM.md)).
- [ ] Nhấn BOOT → log `BOOT: nhan`, LED xanh dương; thả → log `BOOT: nha`,
      LED xanh lá.
- [ ] Heartbeat đều mỗi ~5 giây.
- [ ] Tool `hid_echo.py` báo 60 byte khớp.

**Thiếu bất kỳ điểm nào thì dừng lại**, kiểm tra board và cáp trước khi flash
firmware FIDO chính (xem [docs/04-firmware.md](04-firmware.md)).

## 14. Nạp bằng PlatformIO (đường thay thế)

1. Tạo project PlatformIO với board `esp32-s3-devkitc-1`.
2. Chép `firmware/hwtest/hwtest.ino` thành `src/main.cpp`.
3. Thêm cờ build `-DARDUINO_USB_CDC_ON_BOOT=1`.
4. Muốn HID echo thì project phải bật TinyUSB OTG trong sdkconfig
   (tương đương `ARDUINO_USB_MODE=0`).
5. Nạp qua cổng UART như bình thường, rồi kiểm tra từ bước 10 trở đi.

*Ảnh chụp mong đợi: cửa sổ build PlatformIO báo `SUCCESS`, dòng nạp hiện cổng COM
đúng của board.*
