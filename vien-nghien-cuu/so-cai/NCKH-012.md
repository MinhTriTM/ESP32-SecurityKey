# Sổ cái — Hồ An (NCKH-012), nhóm kiemdinh, đợt 1

## 2026-11-21 01:31 — nhận việc
- Thẻ: [KIEMDINH] Build sạch hai chế độ (Kanzo id 150)
- Nhiệm vụ (theo phan-cong.json): Xóa cache arduino rồi build OTG+HWCDC để chắc tái hiện được
- Phạm vi sửa repo: REPO CHỈ ĐỌC, ngoại trừ cache build của chính arduino-cli và file sổ cái này
- Đã đọc trước khi làm: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-012 trong
  vien-nghien-cuu/phan-cong.json, vien-nghien-cuu/so-cai/README.md,
  firmware/hwtest/README.md, firmware/hwtest/hwtest.ino, scripts/build_hwtest.ps1,
  README.md (mục trạng thái: OTG 372 KB, HWCDC 302 KB)
- Hai chế độ USB (theo boards.txt core ESP32 4.0.0):
  - OTG: --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default' (usb_mode=0, TinyUSB, có HID echo)
  - HWCDC: --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc' (usb_mode=1, Hardware CDC and JTAG)
- Môi trường build: .tooling/arduino-cli/arduino-cli.exe, ARDUINO_DIRECTORIES_DATA=.tooling/data
- Trạng thái: todo -> doing (thử Kanzo opportunistic SAU khi ghi sổ, xem mục Kanzo bên dưới)

## 2026-11-21 01:35 — báo cáo
- Đã làm: xóa cache build arduino-cli rồi build sạch firmware/hwtest cả hai chế độ USB,
  mỗi chế độ --clean + --build-path riêng dưới %TEMP% (không ghi gì vào repo).
- Lệnh xóa cache: `arduino-cli cache clean` -> exit 0; kiểm tra trước đó: không còn
  thư mục arduino* trong %TEMP%, firmware/hwtest/build không tồn tại, .tooling/data/tmp rỗng.
- Build OTG (--fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default'): exit 0
  - Flash: Sketch uses 372633 bytes (28%), maximum 1310720 bytes
  - RAM: Global variables use 55680 bytes (16%), còn 272000 bytes, maximum 327680 bytes
  - Binary: hwtest-otg/hwtest.ino.bin, 372784 bytes
- Build HWCDC (--fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc'): exit 0
  - Flash: Sketch uses 302765 bytes (23%), maximum 1310720 bytes
  - RAM: Global variables use 22784 bytes (6%), còn 304896 bytes, maximum 327680 bytes
  - Binary: hwtest-hwcdc/hwtest.ino.bin, 302912 bytes
- Tự kiểm: grep 'error|warning|Error' trên cả hai log build -> không có dòng nào;
  số liệu khớp README.md (OTG ~372 KB, HWCDC ~302 KB); arduino-cli 1.6.0, core ESP32 4.0.0.
- Kết luận: [KIEM-DINH] đạt — cả hai chế độ build sạch tái hiện được từ cache trống.
- Trạng thái: doing -> review (thử Kanzo opportunistic, xem mục Kanzo bên dưới)

## 2026-11-21 01:35 — Kanzo (opportunistic, nghẽn SQLite)
- (ghi kết quả từng lệnh move/comment tại đây sau khi thử)
- Kanzo kẹt (thử 01:35: move doing hỏng 3/3 — 1 timeout 30s + 2 HTTP 500; dừng theo lệnh Viện trưởng, không thử thêm; thẻ 150 vẫn todo, nhờ Viện trưởng vá sau). [Viện trưởng ghi hộ vì phiên follow-up mất quyền file/shell]

## 2026-11-21 01:39 — nhận kiểm chéo thẻ 145 (lượt kiểm chéo đợt 1)
- Thẻ: [PQC] So sánh ML-KEM-512/768/1024 (Kanzo id 145) của Vũ An (NCKH-007)
- Vai trò: kiểm định viên khác nhóm, kiểm độc lập bằng ĐƯỜNG KHÁC
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-007.md (báo cáo 01:30 + đồng bộ Kanzo 01:38),
  tools/pqc.py (ALG ML-KEM-768, kích thước chuẩn trong docstring)
- Phạm vi: REPO CHỈ ĐỌC, script đo riêng ngoài repo, chỉ nối thêm file sổ này

## 2026-11-21 01:43 — báo cáo kiểm chéo thẻ 145
- Phương pháp (đường khác với tác giả):
  - Script riêng `C:\Users\user\AppData\Local\Temp\mlkem_xcheck_012.py` (tự viết,
    không dùng lại script của tác giả).
  - Số vòng khác: đợt A 120 vòng, đợt B 300 vòng (tác giả dùng 200/500).
  - Thứ tự bản khác để tránh thiên lệch cache: đợt A 1024->768->512 (ngược tác
    giả), đợt B 512->1024->768 (xen kẽ). Warmup 20 vòng riêng trước mỗi op.
  - Chốt bằng MEDIAN + stdev (tác giả dùng mean), đo bằng perf_counter_ns.
  - Kiểm dương tính: round-trip encap->decap khớp từng byte 5/5 cặp mỗi bản.
  - Kiểm âm tính (tác giả không có): sửa 1 bit ct -> ss PHẢI khác (implicit
    rejection), PASS cả 3 bản.
- Môi trường: Windows, Python 3.12.0, liboqs 0.16.0, liboqs-python 0.16.0.2
  (cùng máy với tác giả nên cùng bản lib).
- Lệnh chạy:
  `$env:OQS_INSTALL_PATH='D:\Download\ESP32-SecurityKey\.tooling\oqs';`
  `$env:PYTHONPATH='D:\Download\ESP32-SecurityKey\.tooling\pylibs';`
  `python "$env:TEMP\mlkem_xcheck_012.py"` -> exit 0, XCHECK DONE.

### Kích thước (byte, đọc từ kem.details) — PASS, khớp FIPS 203 từng ô
| Bản         | pk   | sk   | ct   | ss | FIPS 203 |
|-------------|------|------|------|----|----------|
| ML-KEM-512  | 800  | 1632 | 768  | 32 | KHỚP     |
| ML-KEM-768  | 1184 | 2400 | 1088 | 32 | KHỚP     |
| ML-KEM-1024 | 1568 | 3168 | 1568 | 32 | KHỚP     |
Khớp 100% Bảng 1 của tác giả và docstring tools/pqc.py (768: 1184/2400/1088/32).

### Tốc độ độc lập (MEDIAN, micro-giây/op, số nhỏ = nhanh)
| Bản         | keygen A | keygen B | encap A | encap B | decap A | decap B |
|-------------|----------|----------|---------|---------|---------|---------|
| ML-KEM-512  | 80,3     | 120,4    | 141,8   | 116,8   | 34,1    | 41,2    |
| ML-KEM-768  | 166,1    | 154,2    | 134,9   | 166,2   | 61,6    | 72,7    |
| ML-KEM-1024 | 121,3    | 126,0    | 116,8   | 162,0   | 63,8    | 101,5   |
(A = 120 vòng, B = 300 vòng; mean/stdev/min đầy đủ trong output script.)

### Đối chiếu với số của tác giả
- Cùng bậc toàn bộ: mọi op mọi bản đều < 200 us median (tác giả < 260 us mean).
  Chênh lệch từng ô giữa 2 bên đa số < 2x, phù hợp máy đang bận nhiều agent
  (stdev của tôi có ô lên tới ~800 us vì outlier — chính vì vậy chốt median).
- Điểm nhất quán độc lập: ML-KEM-512 nhanh nhất ở keygen và decap cả 2 đợt;
  encap thứ tự lộn xộn giữa các đợt (đợt A 1024 nhanh nhất, đợt B 512 nhanh
  nhất) — tôi xác nhận nhận định trung thực của tác giả: thứ tự tương đối
  KHÔNG ổn định, và với vault (mỗi lần mở két chỉ 1 lần encap/decap) thì chênh
  ~100 us là không đáng kể. Tốc độ KHÔNG phải yếu tố quyết định: XÁC NHẬN.
- Không phát hiện số liệu nào của tác giả sai định tính.

### Đánh giá khuyến nghị ML-KEM-768 — VỮNG
1. Kiểm lại biên an toàn: level 3 (AES-192) cho dữ liệu két dài hạn là hợp lý;
   level 1 của 512 mỏng trước kịch bản "thu hôm nay, giải mã sau". Đồng ý.
2. Kiểm lại chênh kích thước 768 vs 1024 từ số đo độc lập: pk -384, sk -768,
   ct -480 byte — tiết kiệm thật, trong khi level 5 của 1024 là thừa cho vault.
3. Hạ tầng: tools/pqc.py đã chốt ALG = "ML-KEM-768" (đã đọc code, dòng 38);
   chọn bản khác tốn công sửa tool + self-test vô ích. Đồng ý.
- Không có bằng chứng tốc độ nào lật ngược khuyến nghị (512 chỉ nhanh hơn ở
  mức chục~trăm us, không bù được biên an toàn).

### Kết luận kiểm chéo
- [KIEM-DINH] đạt — số liệu tác giả trung thực và tái hiện được độc lập bằng
  đường khác; khuyến nghị ML-KEM-768 vững cả 3 lý do.
- Tự kiểm: script đo ngoài repo; repo chỉ nối thêm file sổ này; không git commit.
- Unresolved: không có về chuyên môn. Về quy trình: thẻ 150 của chính tôi vẫn
  kẹt todo vì Kanzo (mục trên), nhờ Viện trưởng vá sau.

## 2026-11-21 01:43 — đồng bộ Kanzo id 145 (opportunistic, Kanzo nghẽn)
- GET board (xem thẻ 145 ở cột nào): HỎNG 3/3 (500 x3). Mỗi attempt timeout 30s,
  cách nhau 5s.
- POST comment [KIEM-DINH] đợt 1: HỎNG 3/3 (500 x3).
- POST move -> review: log bị hứng vào biến pwsh nên không in ra được, nhưng lệnh
  tiếp theo thành công nên nhiều khả năng đã lên review ở lần 1 (không xác minh
  riêng được — ghi trung thực).
- POST move -> done: THÀNH CÔNG lần 1 (response status=done, comments=1).
- GET task 145 (xác minh): lần 1 500, lần 2 THÀNH CÔNG — xác nhận mới có 1 comment
  (của tác giả), comment kiểm định đợt 1 chưa lên.
- POST comment [KIEM-DINH] đợt bổ sung: THÀNH CÔNG lần 1 (comment id 17).
- Comment dùng tiếng Việt không dấu để tránh lỗi encoding JSON qua API.
- Trạng thái cuối: thẻ 145 ở `done`, đủ comment kiểm định. Kiểm chéo hoàn tất
  cả sổ file lẫn bảng.
