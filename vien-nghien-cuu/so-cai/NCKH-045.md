# Sổ cái — Đoàn Bình (NCKH-045), nhóm firmware, đợt 2C

## 2026-11-21 03:10 — nhận việc

- Thẻ: [FIRMWARE] Rà soát RAM/flash hai bản build (mã NCKH-045, tìm id trên Kanzo sau)
- Nhiệm vụ (theo phan-cong.json + objective): rà soát RAM/flash hai bản build hwtest
  (OTG 372633/55680, HWCDC 302765/22784 — tự xác minh lại bằng build hoặc đọc log build),
  đánh giá còn dư bao nhiêu %, đề xuất cắt giảm cụ thể nếu vượt ngưỡng 70%
  (kèm đo lại sau khi đề xuất — nếu đề xuất cần sửa code thì chỉ viết đề xuất, không sửa).
- Đã đọc trước khi làm: vien-nghien-cuu/HIEN-CHUONG.md,
  mục NCKH-045 trong vien-nghien-cuu/phan-cong.json,
  vien-nghien-cuu/so-cai/README.md, firmware/hwtest/hwtest.ino (154 dòng),
  firmware/hwtest/README.md, scripts/build_hwtest.ps1, scripts/build_hwtest.sh,
  docs/04-firmware.md, README.md (mục trạng thái: OTG 372 KB, HWCDC 302 KB),
  vien-nghien-cuu/so-cai/NCKH-012.md (build sạch hai chế độ, nguồn số liệu gốc),
  vien-nghien-cuu/so-cai/NCKH-039.md (so sánh USBMode OTG/HWCDC).
- Phạm vi: REPO CHỈ ĐỌC — build ra thư mục riêng dưới %TEMP%, không sửa file nguồn,
  chỉ ghi thêm file sổ cái này; không git commit; mọi lệnh shell kèm shell='pwsh'.
- Trạng thái: todo -> doing (thử Kanzo opportunistic SAU khi ghi sổ).

## 2026-11-21 03:15 — báo cáo: rà soát RAM/flash hai bản build hwtest

### 1. Xác minh lại số liệu bằng build sạch (không đọc chay log cũ)

- Môi trường: arduino-cli 1.6.0, core esp32:esp32 4.0.0, Windows,
  ARDUINO_DIRECTORIES_DATA=D:\Download\ESP32-SecurityKey\.tooling\data.
  Khớp môi trường của NCKH-012.
- FQBN (theo scripts/build_hwtest.ps1 + NCKH-039):
  - OTG: `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default` (usb_mode=0, TinyUSB + HID echo)
  - HWCDC: `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc` (usb_mode=1, Hardware CDC/JTAG)
- Lệnh OTG:
  `arduino-cli compile --clean --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default' --build-path $env:TEMP\hwtest-nckh045-otg firmware/hwtest`
  -> exit 0:
  `Sketch uses 372633 bytes (28%) of program storage space. Maximum is 1310720 bytes.`
  `Global variables use 55680 bytes (16%) of dynamic memory, leaving 272000 bytes for local variables. Maximum is 327680 bytes.`
  Binary `hwtest.ino.bin` 372784 byte.
- Lệnh HWCDC:
  `arduino-cli compile --clean --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc' --build-path $env:TEMP\hwtest-nckh045-hwcdc firmware/hwtest`
  -> exit 0:
  `Sketch uses 302765 bytes (23%) of program storage space. Maximum is 1310720 bytes.`
  `Global variables use 22784 bytes (6%) of dynamic memory, leaving 304896 bytes for local variables. Maximum is 327680 bytes.`
  Binary `hwtest.ino.bin` 302912 byte.
- Kết luận xác minh: KHỚP TỪNG BYTE với số trong objective (OTG 372633/55680,
  HWCDC 302765/22784), với NCKH-012 (build sạch --clean) và README.md
  (OTG ~372 KB, HWCDC ~302 KB). Số liệu tái hiện được 100%.

### 2. Bảng số liệu + đánh giá % dư (ngưỡng 70%)

Giới hạn (partition default 4MB, core 4.0.0): flash app tối đa 1310720 byte,
RAM động tối đa 327680 byte. Ngưỡng 70% = flash 917504 byte, RAM 229376 byte.

| Bản | Flash dùng / tối đa | % flash | Flash còn dư | RAM dùng / tối đa | % RAM | RAM còn dư | .bin |
|---|---|---|---|---|---|---|---|
| OTG | 372633 / 1310720 | 28,43% | 938087 B (71,57% ~ 916 KB) | 55680 / 327680 | 16,99% | 272000 B (83,01% ~ 266 KB) | 372784 B |
| HWCDC | 302765 / 1310720 | 23,10% | 1007955 B (76,90% ~ 984 KB) | 22784 / 327680 | 6,95% | 304896 B (93,05% ~ 298 KB) | 302912 B |

- Chênh OTG − HWCDC: flash +69868 B (~68,2 KB), RAM +32896 B (~32,1 KB) do stack TinyUSB + USBHID.
- Headroom tới ngưỡng 70% (còn được phép tăng thêm trước khi chạm ngưỡng):
  - OTG: flash +544871 B (~532 KB), RAM +173696 B (~170 KB).
  - HWCDC: flash +614739 B (~600 KB), RAM +206592 B (~202 KB).
- Kết luận: CẢ 4 CHỈ SỐ ĐỀU DƯỚI 70% (cao nhất là flash OTG 28,43%).
  KHÔNG vượt ngưỡng → KHÔNG yêu cầu cắt giảm bắt buộc.

### 3. Đề xuất cắt giảm

Vì không vượt ngưỡng 70% nên KHÔNG có đề xuất bắt buộc và KHÔNG sửa code
(đúng lệnh: đề xuất cần sửa code thì chỉ viết, không sửa). Dưới đây là các
đòn dự phòng đã xếp hạng, chỉ áp dụng khi flash/RAM tiến gần ngưỡng 70%
(đặc biệt khi hwtest phình thêm tính năng hoặc chuyển sang firmware FIDO lớn):

1. Dùng bản HWCDC khi không cần HID (KHÔNG sửa code, chỉ đổi FQBN):
   tiết kiệm ngay ~69868 B flash + 32896 B RAM so với OTG. Đã kiểm chứng ở mục 1.
2. Gọn log Serial (sửa code, ước tính tiết kiệm vài KB flash):
   rút ngắn chuỗi trong `printChipInfo()`/`printMac()`/heartbeat (hwtest.ino dòng 74-95, 140-144),
   bỏ `Serial.printf` trang trí khi build release, giữ lại 1 dòng heartbeat tối thiểu.
3. Tắt nhánh HID echo khi build kiểm tra nhanh (sửa 1 cờ build, không sửa logic):
   build với `USBMode=hwcdc` thay vì `#if ARDUINO_USB_MODE == 0` — tương đương mục 1
   nhưng diễn đạt theo hướng quy trình: mặc định HWCDC, chỉ OTG khi cần chạy `tools/hid_echo.py`.
4. Bỏ `Serial.printf` định dạng nặng / chuỗi format dài (sửa code, tiết kiệm flash):
   thay `%02X:%02X...` bằng hàm in hex gọn, tránh kéo thêm mã định dạng.
5. Đổi partition scheme nếu app lớn dần (KHÔNG sửa code, chỉ đổi menu build):
   `no_ota` (2 MB APP), `huge_app` (3 MB APP) tăng trần flash thay vì giảm dùng —
   chỉ dùng khi đã cạn dư và chấp nhận mất OTA/SPIFFS.
6. Cờ biên dịch (KHÔNG sửa code, cần đo lại): giữ `-Os` mặc định, không bật debug
   (`-g`), không bật exception RTTI thừa; mọi đổi cờ phải build lại cả 2 FQBN mục 1.

Đo lại sau đề xuất: vì KHÔNG sửa code trong nhiệm vụ này nên KHÔNG có vòng đo lại.
Khi áp dụng bất kỳ mục nào ở trên, đo lại đúng 2 lệnh mục 1 rồi đối chiếu với bảng
mục 2 (pass = cả 4 chỉ số vẫn dưới 70% và HID echo/log còn đủ theo README).

### 4. Tự kiểm

- Build lại cả 2 bản từ `--clean`, exit 0, số liệu khớp từng byte với NCKH-012
  và objective; grep lỗi build: không có error/warning (output build chỉ còn
  2 dòng Sketch/Global variables + danh sách .bin).
- Tính % dư bằng pwsh từ số byte thô (không chép % làm tròn của arduino-cli):
  OTG 28,4296%/16,9922%, HWCDC 23,0991%/6,9531%.
- Không sửa file repo nào ngoài sổ cái này; build-path nằm ngoài repo (%TEMP%);
  không git commit.
- Trạng thái: doing -> review (thử Kanzo opportunistic, xem mục Kanzo bên dưới).

### 5. Unresolved

- Không có unresolved chuyên môn: cả hai bản còn dư lớn (thấp nhất 71,57% flash OTG),
  ngưỡng 70% còn xa, không cần vòng cắt giảm.
- Bóc tách .elf thô (`xtensa-esp32s3-elf-size -B`, core 4.0.0):
  OTG text/data/bss = 295007/77662/735599, HWCDC = 228403/74398/508931.
  Chênh text +66604 B (≈95% trong 69868 B chênh flash) tới từ mã TinyUSB+USBHID;
  chênh data +3264 B. BSS thô gồm cả vùng ngoài DRAM nên số arduino-cli
  (RAM OTG 55680, HWCDC 22784) mới là căn cứ ngưỡng. Chưa bóc tới từng
  object/lib — không cần cho kết luận ngưỡng, để dành khi tiến gần 70% mới bóc.

## 2026-11-21 03:20 — Kanzo (opportunistic, không thấy thẻ của mình)

- GET board lần 1: THÀNH CÔNG ngay lần đầu (timeout 30s), TOTAL_TASKS=64.
  Lọc title/description chứa `NCKH-045` chỉ trúng 1 thẻ: id 203, status=todo,
  title=`[tooling] Chuẩn hóa mã thoát tool (NCKH-052)` — là thẻ của NCKH-052,
  KHÔNG phải thẻ của NCKH-045 (trùng khớp nằm ở description, chưa xác minh được).
- GET chi tiết thẻ 203: lần 1 HTTP 500; lần 2 (sau 5s) HTTP 500;
  lần 3 (sau 5s) trả 200 nhưng thân rỗng (id/title/status/description đều trống).
  Hết quota thử lại (tối đa 2 thử lại), dừng.
- GET board đối chiếu (2 lần sau, cách 5s, timeout 30s): cả 2 lần HTTP 500 —
  Kanzo chập chờn đúng như lệnh cảnh báo.
- Quyết định: KHÔNG move/comment lên thẻ 203 vì đó là thẻ todo của agent khác
  (NCKH-052); tự ý chuyển cột/bình luận sẽ làm sai trạng thái việc của họ.
  Thẻ riêng của NCKH-045 chưa được tạo trên bảng → theo lệnh Viện trưởng:
  KHÔNG tự tạo thẻ, chỉ ghi sổ và tiếp tục.
- Trạng thái thẻ: N/A (chưa có thẻ) — nhờ Viện trưởng tạo thẻ
  `[FIRMWARE] Rà soát RAM/flash hai bản build (NCKH-045)` và vá
  todo -> doing -> review sau; nội dung báo cáo đã đủ trong mục trên.

## 2026-11-21 03:30 — kiểm chéo đợt 2C: việc của NCKH-052 Trần Cường

- Vai trò: Đoàn Bình (NCKH-045) kiểm độc lập công việc NCKH-052
  (chuẩn hóa mã thoát + thông điệp 7 tool), theo objective Viện trưởng.
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-052.md (bảng chuẩn 0 ok /
  1 lỗi chạy / 2 thiếu lib-sai dùng + danh sách sửa 5 file).
- Phạm vi: REPO CHỈ ĐỌC (không sửa file nguồn nào), không git commit,
  mọi lệnh shell kèm shell='pwsh'. Kiểm bằng ĐƯỜNG KHÁC: các ca lỗi
  và self-test dưới đây đều khác ca 052 đã chạy.

### 1. Bốn ca lỗi độc lập (4 tool, đủ 3 nhóm: thiếu lib / sai dùng / file hỏng)

- Ca 1 — thiếu lib → mã 2 (052 chưa chạy ca này):
  `python tools/fido_check.py` (máy không có hid) →
  `Thiếu thư viện hid. Chạy: pip install -r requirements.txt` EXIT=2. ĐÚNG.
- Ca 2 — dữ liệu sai checksum → mã 1 (052 chỉ chạy `new --words 13` → 2):
  `python tools/mnemonic.py to-entropy abandon abandon ... (12 từ)` →
  `Cụm từ sai: sai checksum: gõ nhầm từ hoặc sai thứ tự` EXIT=1. ĐÚNG.
- Ca 3 — file hỏng → mã 1 (052 chỉ chạy nhánh thiếu-share → 2):
  tạo file rác dưới %TEMP% (ngoài repo, đã xóa sau kiểm),
  `python tools/split_secret.py combine <file rác>` →
  `File ... lỗi: file không phải share Shamir của tool này` EXIT=1. ĐÚNG.
- Ca 4 — sai dùng, giá trị khác 052 (052 chạy `--rounds abc`, tôi chạy `--rounds 99`):
  `python tools/ml_distinguisher.py --rounds 99` →
  `Sai dùng: mỗi R phải trong [1, 22].` EXIT=2. ĐÚNG.

### 2. Hai self-test xác nhận không vỡ (đúng 2 tool 052 bỏ qua không chạy lại)

- `python tools/vault.py --self-test` →
  `self-test ok: mã hóa/giải mã đúng, sai mật khẩu và file sửa bị từ chối.` EXIT=0.
- `python tools/hid_echo.py --self-test` →
  `self-test ok: đóng gói report HID echo đúng.` EXIT=0.

### 3. Kết luận kiểm định: ĐẠT

- 6/6 ca khớp bảng chuẩn NCKH-052 (4 ca lỗi đúng mã + đúng mẫu thông điệp,
  2 self-test EXIT=0). Không phát hiện chỗ lệch mã thoát/thông điệp nào thêm.
- Nhánh `fido_check.py --index` vượt (052 sửa 1→2, cần key thật):
  kiểm định này không chạy được vì thiếu phần cứng — giống 052, chỉ xác nhận
  bằng đọc mã (dòng `return 2` đúng). Ghi nhận là giới hạn chung, không trừ điểm.

### 4. Kanzo (thẻ NCKH-052 id=203, mỗi lệnh cách 5s, timeout 30s)

- GET board lần 1, 2: HTTP 500. Lần 3: 200, TOTAL=69,
  trúng thẻ id=203 status=todo title=`[tooling] Chuẩn hóa mã thoát tool (NCKH-052)`.
  (Còn 1 hit NCKH-047 là trùng khớp ở description, bỏ qua.)
  Ghi chú: thẻ vẫn todo, chưa đúng `doing -> review` như 052 mong muốn
  (052 cũng gặp Kanzo 500 nên chưa move được).
- GET chi tiết `/api/tasks/203`: cả 3 lần HTTP 500 → không đọc được cấu trúc thẻ.
- POST `/api/tasks/203/comments` lần 1 (field `text`): HTTP 400 (sai shape body,
  endpoint tồn tại). Lần 2 (field `body`): HTTP 500. Hết quota thử → dừng,
  KHÔNG comment được, KHÔNG tự tạo thẻ.
- KHÔNG move cột: tiền đề lệnh là `review -> done` nhưng thẻ thực tế đang `todo`;
  move mù `todo -> done` bằng API đoán mò có thể làm sai trạng thái việc của
  agent khác → để Viện trưởng vá cột sau khi đối chiếu 2 sổ.
- Nội dung comment dự định (chưa gửi được):
  `[KIEM-DINH] đạt — 6/6 ca đúng bảng chuẩn, chi tiết trong sổ NCKH-045.`

### 5. Unresolved

- Kanzo: comment + move thẻ 203 chưa thực hiện được (API 500/400, hết quota thử).
  Nhờ Viện trưởng vá trạng thái thẻ 203 todo -> review -> done sau khi đối chiếu.
- Phần cứng: nhánh `--index` vượt và mọi nhánh cần key/USB thật chưa ai chạy được
  (052 và kiểm định đều chỉ đọc mã). Không chặn kết luận đạt.
