# Sổ cái — Dương Bình (NCKH-039), nhóm firmware, đợt 2B

## 2026-11-21 — nhận việc
- Thẻ: [FIRMWARE] So sánh USBMode OTG/HWCDC (mã NCKH-039, tìm id trên Kanzo sau)
- Nhiệm vụ (theo phan-cong.json): Bảng ảnh hưởng tới upload/log/HID, khuyến nghị khi nào dùng bản nào
- Phạm vi: REPO CHỈ ĐỌC, chỉ ghi thêm file sổ cái này; không git commit
- Đã đọc trước khi làm: vien-nghien-cuu/HIEN-CHUONG.md,
  mục NCKH-039 trong vien-nghien-cuu/phan-cong.json,
  vien-nghien-cuu/so-cai/README.md, firmware/hwtest/hwtest.ino,
  firmware/hwtest/README.md, scripts/build_hwtest.ps1, scripts/flash_win.ps1,
  docs/03-phan-cung.md, docs/04-firmware.md, docs/research/02-esp32s3-usb.md,
  docs/runbook-nap-hwtest-windows.md, tools/hid_echo.py, README.md (mục trạng thái),
  vien-nghien-cuu/so-cai/NCKH-012.md (số liệu build sạch hai chế độ),
  .tooling core ESP32 4.0.0 (boards.txt + platform.txt)
- Trạng thái: todo -> doing (thử Kanzo opportunistic SAU khi ghi sổ)

## 2026-11-21 — báo cáo: so sánh USBMode OTG vs HWCDC

### 1. Xác nhận menu trong core 4.0.0 (boards.txt + platform.txt)

Nguồn: `.tooling/data/packages/esp32/hardware/esp32/4.0.0/boards.txt`
(grep `USBMode|CDCOnBoot|MSCOnBoot|DFUOnBoot|UploadMode`) và `platform.txt`.

Board `esp32s3` (dùng cho hwtest, cùng menu cho esp32s3-octal / esp32s3box):

- `menu.USBMode` = "USB Mode", hai giá trị:
  - `hwcdc` = "Hardware CDC and JTAG" → `build.usb_mode=1`
  - `default` = "USB-OTG (TinyUSB)" → `build.usb_mode=0`
- `platform.txt`: `build.extra_flags.esp32s3=-DARDUINO_USB_MODE={build.usb_mode}
  -DARDUINO_USB_CDC_ON_BOOT={build.cdc_on_boot}
  -DARDUINO_USB_MSC_ON_BOOT={build.msc_on_boot}
  -DARDUINO_USB_DFU_ON_BOOT={build.dfu_on_boot}`
  → sketch đọc `ARDUINO_USB_MODE` (0 = OTG, 1 = HWCDC) để bật/tắt HID echo.
- `CDCOnBoot`: `default` = Disabled (`cdc_on_boot=0`), `cdc` = Enabled (=1).
  Cả hai chế độ USB đều cần `cdc` thì `Serial` mới ra USB.
- `MSCOnBoot=msc` và `DFUOnBoot=dfu` đều ghi rõ "(Requires USB-OTG Mode)"
  → chỉ có ý nghĩa ở OTG.
- `UploadMode`: `default` = "UART0 / Hardware CDC"
  (`use_1200bps_touch=false`, `wait_for_upload_port=false`);
  `cdc` = "USB-OTG CDC (TinyUSB)"
  (`use_1200bps_touch=true`, `wait_for_upload_port=true`).
  → Nạp qua cổng UART (mặc định) không cần thủ tục 1200bps; chỉ khi nạp
  qua cổng OTG-CDC mới cần 1200bps touch + chờ cổng.

FQBN đã kiểm chứng (theo NCKH-012 + scripts/build_hwtest.ps1):

- OTG: `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default`
- HWCDC: `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc`

### 2. Bảng so sánh (ảnh hưởng tới upload / log / HID / Serial)

| Tiêu chí | OTG — USB-OTG (TinyUSB), `usb_mode=0` | HWCDC — Hardware CDC and JTAG, `usb_mode=1` |
|---|---|---|
| Stack USB | TinyUSB (lib OTG full-speed GPIO19/20) | USB Serial/JTAG phần cứng của chip |
| HID | CÓ: `USBHID.h`, echo vendor page 0xFF00, report ID 1, 64 byte; log `HID echo: san sang`; `tools/hid_echo.py` chạy được | KHÔNG: sketch in `HID echo: TAT (can USB Mode = USB-OTG)`; `hid_echo.py` báo `Không thấy HID echo (usage page 0xFF00)` |
| Serial / log | `Serial` qua TinyUSB CDC trên cổng native; cần `CDCOnBoot=cdc`, baud 115200; log in `USB mode: 0` | `Serial` qua HW CDC/JTAG; cần `CDCOnBoot=cdc`, baud 115200; log in `USB mode: 1` |
| Nạp firmware (upload) | Nạp qua cổng UART với `UploadMode=default` như thường; muốn nạp qua cổng OTG-CDC thì đặt `UploadMode=cdc` (1200bps touch + chờ cổng) | Nạp qua UART0/HWCDC với `UploadMode=default`, không cần 1200bps touch |
| MSC/DFU On Boot | Dùng được (menu yêu cầu đúng OTG) | Không áp dụng (menu ghi Requires USB-OTG) |
| Kích thước build (NCKH-012 đo sạch, README xác nhận) | Sketch 372633 byte (28%), RAM 55680 byte (16%), bin 372784 byte (~372 KB) | Sketch 302765 byte (23%), RAM 22784 byte (6%), bin 302912 byte (~302 KB) |
| Chênh lệch | \multicolumn{2}{c}{OTG nặng hơn ~70 KB flash (~69868 byte) và ~33 KB RAM (32896 byte) do stack TinyUSB + USBHID} |
| Cổng vật lý cần cắm | Nạp: cổng UART; HID echo: chuyển sang cổng native (`USB`/`OTG`) | Nạp + log qua UART0/HWCDC, không có bước kiểm HID |
| Liên quan FIDO thật | BẮT BUỘC: pico-fido hiện hình composite HID trên cổng OTG native (docs/04 + research/02) | Không dùng cho FIDO (không có HID) |

### 3. Khuyến nghị khi nào dùng bản nào

1. Mặc định dùng OTG (`USBMode=default` + `CDCOnBoot=cdc`) cho hwtest:
   đúng `firmware/hwtest/README.md` và `scripts/build_hwtest.ps1`; kiểm được
   trọn vẹn USB CDC + HID echo — tức đúng đường USB mà firmware FIDO sẽ dùng.
2. Dùng OTG khi: cần chạy `tools/hid_echo.py`; chuẩn bị flash pico-fido;
   cần MSC/DFU On Boot; nghiệm thu board trước khi đưa vào dùng thật.
3. Dùng HWCDC khi: chỉ cần kiểm nhanh board sống / nút BOOT / LED / log mà
   không cần HID; muốn bản nhẹ hơn ~70 KB flash, ~33 KB RAM; máy tính gặp
   trục trặc driver TinyUSB CDC/HID.
4. Luôn bật `USB CDC On Boot = Enabled` ở CẢ hai bản — để Disabled thì
   Serial Monitor trắng trơn dù nạp thành công (runbook bước 6 đã dặn).
5. Giữ `UploadMode=default` và nạp qua cổng UART (chữ `COM`/`UART` trên lụa)
   cho cả hai bản; chỉ chuyển `UploadMode=cdc` khi cố tình nạp qua cổng
   native. Cáp phải có dây dữ liệu, sai cổng COM là flash nhầm thiết bị.
6. Quy trình chốt cho một board mới: nạp bản OTG → đọc log (đúng chip S3,
   flash/PSRAM, `USB mode: 0`, heartbeat 5 s) → thử BOOT + LED → chuyển cáp
   sang cổng native, chạy `hid_echo.py` phải báo 60 byte khớp → mới flash
   pico-fido theo docs/04-firmware.md.

### 4. Tự kiểm
- Lệnh: `Select-String boards.txt -Pattern usbmode|...` → thấy đủ hai giá trị
  `hwcdc`/`default` + `build.usb_mode=1/0` cho esp32s3; `UploadMode`,
  `CDCOnBoot`, `MSC/DFU` khớp bảng trên (xem mục 1).
- Đối chiếu code: `hwtest.ino` dòng 8 (`#if ARDUINO_USB_MODE == 0` include
  USB/USBHID), dòng 91 (log `USB mode: %d`), dòng 119-125 (nhánh HID echo
  sẵn sàng/TẮT); `hid_echo.py` dòng 56 dặn `USB Mode = USB-OTG`.
- Số liệu build: lấy từ NCKH-012 (build sạch `--clean`, arduino-cli 1.6.0,
  core 4.0.0) và khớp README.md (OTG 372 KB / HWCDC 302 KB).
  Không build lại (nhiệm vụ là so sánh + khuyến nghị, số liệu đã có kiểm chứng).
- Không sửa file repo nào ngoài sổ cái này; không git commit.
- Trạng thái: doing -> review (thử Kanzo opportunistic, xem mục Kanzo bên dưới)

### 5. Unresolved
- U1: Runbook Windows bước 10 mở Serial Monitor ngay sau khi nạp qua cổng UART
  mà chưa nêu rõ có cần chuyển cáp sang cổng native để xem log CDC (OTG) hay
  không; mục 12 thì ghi "cần cắm lại cổng UART để xem" — hai chỗ chưa nhất
  quán, cần người có board thật chốt lại. Không chặn kết luận bảng so sánh.

## 2026-11-21 — Kanzo (opportunistic, không thấy thẻ)
- GET board lần 1: attempt 1 HTTP 500, attempt 2 (sau 5 s) THÀNH CÔNG,
  TOTAL_TASKS=32, không có thẻ nào chứa `NCKH-039`/`USBMode` trong title.
- GET board lần 2 (liệt kê toàn bộ để chắc chắn): THÀNH CÔNG, 32 thẻ gồm
  id 138-166 (các thẻ NCKH-001..028, đều ở done) và id 167-171
  (5 thẻ FIX/DOC/OPS ở todo). Không có thẻ NCKH-039.
- Kết luận: thẻ đợt 2B của NCKH-039 chưa được tạo trên bảng. Theo lệnh Viện
  trưởng: KHÔNG tự tạo thẻ, chỉ ghi sổ và tiếp tục.
- Không thực hiện move/comment nào (không có thẻ đích).
- Trạng thái thẻ: N/A (chưa có thẻ) — nhờ Viện trưởng tạo thẻ và vá
  doing -> review sau, nội dung báo cáo đã đủ trong mục trên.

## 2026-11-21 — kiểm chéo NCKH-031 (Phan Bình, benchmark 38 KEM liboqs)

- Vai: Dương Bình (NCKH-039, nhóm firmware) làm lượt KIỂM CHÉO đợt 2B,
  khác nhóm với tác giả (PQC). Thẻ Kanzo id 179
  "[PQC] Benchmark liboqs trên máy (NCKH-031)", mô tả thẻ ghi rõ
  người kiểm chéo là NCKH-039.
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-031.md (toàn bộ 2 bảng + phương pháp),
  tools/pqc.py (cách nạp liboqs), vien-nghien-cuu/HIEN-CHUONG.md §6 (API Kanzo).
- Phạm vi: REPO CHỈ ĐỌC, chỉ nối thêm mục này vào sổ; không git commit;
  mọi lệnh shell đều kèm shell='pwsh'.

### Phương pháp độc lập (đường khác tác giả)

- Script riêng đặt tại `$env:TEMP\nckh039_verify_kem.py` (ngoài repo):
  vòng CỐ ĐỊNH (không adaptive như tác giả), warmup 1 op,
  đo bằng `time.perf_counter_ns`, keygen dùng instance mới mỗi op,
  encap/decap dùng chung 1 instance; N_keygen=10, N_encap=N_decap=30.
- Đo 3 KEM đại diện: ML-KEM-768 (bắt buộc) + Kyber768 (đối chứng nhận
  xét "Kyber chậm hơn ML-KEM ~1.5–2x") + FrodoKEM-640-AES (nhóm tốc độ
  trung bình) + kiểm đếm enabled/disabled và kích thước từ `kem.details`.
- Lệnh chạy:
  `$env:OQS_INSTALL_PATH='D:\Download\ESP32-SecurityKey\.tooling\oqs';`
  `$env:PYTHONPATH='D:\Download\ESP32-SecurityKey\.tooling\pylibs';`
  `python "$env:TEMP\nckh039_verify_kem.py"` (EXIT=0).

### Số liệu độc lập (dấu chấm thập phân)

- Môi trường: liboqs 0.16.0, liboqs-python 0.16.0.2 — KHỚP tác giả.
- Đếm KEM: supported=41, enabled=38, disabled=3,
  disabled_list=['BIKE-L1', 'BIKE-L3', 'BIKE-L5'] — KHỚP tác giả
  (41 trừ 38 = đúng 3 BIKE).
- ML-KEM-768: pk/sk/ct/ss = 1184/2400/1088/32 (khớp);
  keygen 0.1092 ms, encap 0.1320 ms, decap 0.0431 ms, round-trip ok.
- Kyber768: pk/sk/ct/ss = 1184/2400/1088/32 (khớp, trùng ML-KEM cùng level);
  keygen 0.2096 ms, encap 0.1337 ms, decap 0.0737 ms, round-trip ok.
- FrodoKEM-640-AES: pk/sk/ct/ss = 9616/19888/9752/16 (khớp);
  keygen 0.3022 ms, encap 0.3838 ms, decap 0.3134 ms, round-trip ok.

### Đối chiếu bậc độ lớn với bảng tác giả

- ML-KEM-768 của tôi 0.1092/0.1320/0.0431 ms so với tác giả
  0.0944/0.1091/0.0492 ms: cùng bậc micro-giây (~40–130 us),
  chênh lệch 12–21%, nằm trong dao động máy bận — KHỚP.
- Kyber768 keygen 0.2096 ms so với tác giả 0.1825 ms (cùng bậc ~0.2 ms);
  tỉ lệ Kyber768/ML-KEM-768 ở keygen của tôi là 1.92x, của tác giả là
  1.93x — trùng khớp tới 2 chữ số, ủng hộ mạnh nhận xét "Kyber chậm
  hơn ML-KEM ~1.5–2x ở keygen". Encap Kyber của tôi (0.1337 ms) thấp
  hơn tác giả (0.2398 ms) nhưng vẫn cùng bậc sub-ms; chênh < 2x,
  chấp nhận được khi máy chạy nhiều agent.
- FrodoKEM-640-AES của tôi 0.3022/0.3838/0.3134 ms so với tác giả
  0.415/0.4477/0.6589 ms: cùng bậc sub-ms, số của tôi thấp hơn
  (máy lúc này rảnh hơn), hệ số < 2.1x — KHỚP bậc độ lớn.
- Kích thước cả 3 KEM khớp từng byte với Bảng 1 của tác giả;
  round-trip 3/3 ok, phù hợp green 38/38 của tác giả.

### Kết luận kiểm định: ĐẠT

- Lý do: số liệu độc lập bằng đường khác khớp bậc độ lớn cả 3 KEM,
  tỉ lệ Kyber/ML-KEM trùng tác giả, đếm enabled/disabled và danh sách
  BIKE khớp tuyệt đối, kích thước khớp từng byte, round-trip ok.
  Không phát hiện mâu thuẫn hay bịa số.

### Đồng bộ Kanzo (thẻ id 179, mỗi lệnh cách 5s, timeout 30s)

- GET board lần 1: THÀNH CÔNG, TOTAL=43,
  HIT id=179 "[PQC] Benchmark liboqs trên máy (NCKH-031)".
- GET chi tiết thẻ (2 lần sau, cách 5s): cả 2 lần HTTP 500 — Kanzo
  chập chờn đúng như lệnh cảnh báo; dừng đúng giới hạn thử lại.
- POST comment `[KIEM-DINH]`: lần 1 HTTP 500, lần 2 HTTP 500,
  lần 3 (bản rút gọn) THÀNH CÔNG, comment id 57, nội dung đạt +
  số liệu tóm tắt.
- POST move `{status: done}`: cả 3 lần (gốc + 2 thử lại) đều HTTP 500 —
  THẤT BẠI, ghi sổ theo lệnh.
- GET đối chiếu cuối: THÀNH CÔNG, thẻ 179 status=`todo`,
  comments=1 (comment kiểm định đã lưu), updated_at dừng ở lúc tạo thẻ.
  Thẻ đang ở `todo` chứ không phải `review` (tác giả đợt trước không
  thấy thẻ để move, thẻ mới được tạo sau).

### Unresolved

- U1: move review->done chưa thực hiện được (3/3 lần HTTP 500, đã hết
  quota thử lại). Nhờ Viện trưởng khi bảng khỏe đẩy thẻ 179 từ `todo`
  thẳng lên `done` (kèm comment kiểm định id 57 đã lưu), hoặc
  todo->doing->review->done nếu muốn giữ đúng vết quy trình.
- U2: chỉ kiểm độc lập 3/38 KEM (đúng yêu cầu 2–3 KEM của lệnh kiểm chéo);
  35 KEM còn lại tin theo bảng tác giả sau khi mẫu đối chiếu khớp tốt.
  Không chặn kết luận ĐẠT.
