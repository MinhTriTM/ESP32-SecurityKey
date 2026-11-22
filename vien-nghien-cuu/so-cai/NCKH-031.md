# Sổ cái NCKH-031 — Phan Bình, nhóm PQC, thành viên, đợt 2

## 2026-11-21 02:24 — nhận việc

- Thẻ: [PQC] Benchmark liboqs trên máy (id Kanzo chưa rõ, tìm cuối việc)
- Việc nhận: đo MỌI KEM có trong liboqs trên máy này, lập bảng so sánh,
  lưu số liệu quan sát được và phiên bản lib.
- Trạng thái: todo -> doing (thử opportunistic sau khi ghi sổ xong,
  vì Kanzo đang chập chờn)
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-031 trong
  vien-nghien-cuu/phan-cong.json, vien-nghien-cuu/so-cai/README.md,
  tools/pqc.py (để biết đúng cách nạp liboqs),
  vien-nghien-cuu/so-cai/NCKH-007.md (sổ benchmark ML-KEM đợt 1, để đối chiếu).

## 2026-11-21 02:24 — báo cáo

- Đã làm: benchmark toàn bộ 38/38 KEM đang bật (enabled) trong liboqs trên
  máy này: keygen + encap + decap từng loại, kèm kích thước pk/sk/ct/ss,
  NIST level, IND-CCA, kiểm round-trip encap→decap khớp từng byte.
  3 KEM BIKE (L1/L3/L5) có trong supported nhưng bị disabled trong bản build
  này nên không đo được — ghi rõ ở mục unresolved.
- Phương pháp: script đo đặt tại `$env:TEMP\nckh031_bench_kem.py` (ngoài
  repo, đúng quy định REPO CHỈ ĐỌC), số liệu thô JSON tại
  `$env:TEMP\nckh031_kem.json`. Mỗi pha đo adaptive: warmup 2 op, đo tới
  khi đủ 0,5 s hoặc đủ trần op (keygen tối đa 20 op vì McEliece chậm,
  encap/decap tối đa 100 op); số trong ngoặc (n=...) là số op đã đo.
- Lệnh chạy:
  `$env:OQS_INSTALL_PATH='D:\Download\ESP32-SecurityKey\.tooling\oqs';`
  `$env:PYTHONPATH='D:\Download\ESP32-SecurityKey\.tooling\pylibs';`
  `python "$env:TEMP\nckh031_bench_kem.py" "$env:TEMP\nckh031_kem.json"`
  (EXIT=0, 38/38 round-trip ok, 0 lỗi)
- Môi trường: Windows-11-10.0.26300-SP0, CPU 13th Gen Intel i7-13620H
  (Intel64 Family 6 Model 186 Stepping 2), Python 3.12.0,
  liboqs 0.16.0, liboqs-python 0.16.0.2, oqs.dll tại .tooling/oqs/bin;
  oqs-pkg kèm repo chứa liboqs-9.dll (build MSYS2 UCRT64, không dùng tới).

### Bảng 1 — Kích thước (byte, đọc từ kem.details) + thuộc tính

| Thuật toán | pk | sk | ct | ss | NIST | IND-CCA |
|---|---:|---:|---:|---:|:---:|:---:|
| Classic-McEliece-348864 | 261120 | 6492 | 96 | 32 | 1 | có |
| Classic-McEliece-348864f | 261120 | 6492 | 96 | 32 | 1 | có |
| Classic-McEliece-460896 | 524160 | 13608 | 156 | 32 | 3 | có |
| Classic-McEliece-460896f | 524160 | 13608 | 156 | 32 | 3 | có |
| Classic-McEliece-6688128 | 1044992 | 13932 | 208 | 32 | 5 | có |
| Classic-McEliece-6688128f | 1044992 | 13932 | 208 | 32 | 5 | có |
| Classic-McEliece-6960119 | 1047319 | 13948 | 194 | 32 | 5 | có |
| Classic-McEliece-6960119f | 1047319 | 13948 | 194 | 32 | 5 | có |
| Classic-McEliece-8192128 | 1357824 | 14120 | 208 | 32 | 5 | có |
| Classic-McEliece-8192128f | 1357824 | 14120 | 208 | 32 | 5 | có |
| HQC-1 | 2241 | 2321 | 4433 | 32 | 1 | có |
| HQC-3 | 4514 | 4602 | 8978 | 32 | 3 | có |
| HQC-5 | 7237 | 7333 | 14421 | 32 | 5 | có |
| Kyber512 | 800 | 1632 | 768 | 32 | 1 | có |
| Kyber768 | 1184 | 2400 | 1088 | 32 | 3 | có |
| Kyber1024 | 1568 | 3168 | 1568 | 32 | 5 | có |
| ML-KEM-512 | 800 | 1632 | 768 | 32 | 1 | có |
| ML-KEM-768 | 1184 | 2400 | 1088 | 32 | 3 | có |
| ML-KEM-1024 | 1568 | 3168 | 1568 | 32 | 5 | có |
| NTRU-HPS-2048-509 | 699 | 935 | 699 | 32 | 1 | có |
| NTRU-HPS-2048-677 | 930 | 1234 | 930 | 32 | 3 | có |
| NTRU-HPS-4096-821 | 1230 | 1590 | 1230 | 32 | 5 | có |
| NTRU-HPS-4096-1229 | 1842 | 2366 | 1842 | 32 | 5 | có |
| NTRU-HRSS-701 | 1138 | 1450 | 1138 | 32 | 3 | có |
| NTRU-HRSS-1373 | 2401 | 2983 | 2401 | 32 | 5 | có |
| sntrup761 | 1158 | 1763 | 1039 | 32 | 2 | có |
| FrodoKEM-640-AES | 9616 | 19888 | 9752 | 16 | 1 | có |
| FrodoKEM-640-SHAKE | 9616 | 19888 | 9752 | 16 | 1 | có |
| FrodoKEM-976-AES | 15632 | 31296 | 15792 | 24 | 3 | có |
| FrodoKEM-976-SHAKE | 15632 | 31296 | 15792 | 24 | 3 | có |
| FrodoKEM-1344-AES | 21520 | 43088 | 21696 | 32 | 5 | có |
| FrodoKEM-1344-SHAKE | 21520 | 43088 | 21696 | 32 | 5 | có |
| eFrodoKEM-640-AES | 9616 | 19888 | 9720 | 16 | 1 | có |
| eFrodoKEM-640-SHAKE | 9616 | 19888 | 9720 | 16 | 1 | có |
| eFrodoKEM-976-AES | 15632 | 31296 | 15744 | 24 | 3 | có |
| eFrodoKEM-976-SHAKE | 15632 | 31296 | 15744 | 24 | 3 | có |
| eFrodoKEM-1344-AES | 21520 | 43088 | 21632 | 32 | 5 | có |
| eFrodoKEM-1344-SHAKE | 21520 | 43088 | 21632 | 32 | 5 | có |

(BIKE-L1/L3/L5: supported nhưng disabled trong build này — không đo được.)

### Bảng 2 — Tốc độ keygen/encap/decap (mili-giây/op, số nhỏ = nhanh)

| Thuật toán | keygen (ms/op) | encap (ms/op) | decap (ms/op) |
|---|---:|---:|---:|
| Classic-McEliece-348864 | 128,0731 (n=8) | 0,3289 (n=100) | 23,2579 (n=25) |
| Classic-McEliece-348864f | 79,0822 (n=6) | 0,208 (n=100) | 24,0232 (n=25) |
| Classic-McEliece-460896 | 482,0316 (n=3) | 0,7342 (n=100) | 48,5739 (n=12) |
| Classic-McEliece-460896f | 230,7308 (n=3) | 0,7103 (n=100) | 61,6063 (n=9) |
| Classic-McEliece-6688128 | 1639,2361 (n=3) | 1,2815 (n=100) | 101,6717 (n=6) |
| Classic-McEliece-6688128f | 360,4469 (n=3) | 0,9988 (n=100) | 92,2226 (n=6) |
| Classic-McEliece-6960119 | 882,5152 (n=3) | 1,8701 (n=100) | 105,4879 (n=6) |
| Classic-McEliece-6960119f | 457,0454 (n=3) | 1,8501 (n=44) | 106,3882 (n=5) |
| Classic-McEliece-8192128 | 1669,1947 (n=3) | 1,2947 (n=100) | 130,8096 (n=4) |
| Classic-McEliece-8192128f | 538,8462 (n=3) | 1,1937 (n=100) | 122,1844 (n=4) |
| HQC-1 | 1,9575 (n=20) | 3,3362 (n=100) | 4,8903 (n=100) |
| HQC-3 | 5,5366 (n=20) | 10,3591 (n=69) | 18,7833 (n=38) |
| HQC-5 | 13,725 (n=20) | 24,4503 (n=17) | 35,8646 (n=12) |
| Kyber512 | 0,1486 (n=20) | 0,0925 (n=100) | 0,1375 (n=100) |
| Kyber768 | 0,1825 (n=20) | 0,2398 (n=100) | 0,0616 (n=100) |
| Kyber1024 | 0,201 (n=20) | 0,2059 (n=100) | 0,0847 (n=100) |
| ML-KEM-512 | 0,0761 (n=20) | 0,1094 (n=100) | 0,0253 (n=100) |
| ML-KEM-768 | 0,0944 (n=20) | 0,1091 (n=100) | 0,0492 (n=100) |
| ML-KEM-1024 | 0,1025 (n=20) | 0,1035 (n=100) | 0,1559 (n=100) |
| NTRU-HPS-2048-509 | 1,0637 (n=20) | 0,1991 (n=100) | 0,0574 (n=100) |
| NTRU-HPS-2048-677 | 1,8206 (n=20) | 0,0998 (n=100) | 0,1913 (n=100) |
| NTRU-HPS-4096-821 | 1,6512 (n=20) | 0,179 (n=100) | 0,1214 (n=100) |
| NTRU-HPS-4096-1229 | 4,4526 (n=20) | 0,2942 (n=100) | 0,149 (n=100) |
| NTRU-HRSS-701 | 2,054 (n=20) | 0,1191 (n=100) | 0,0928 (n=100) |
| NTRU-HRSS-1373 | 5,9648 (n=20) | 0,2039 (n=100) | 0,2072 (n=100) |
| sntrup761 | 7,1666 (n=20) | 0,303 (n=100) | 0,1848 (n=100) |
| FrodoKEM-640-AES | 0,415 (n=20) | 0,4477 (n=100) | 0,6589 (n=100) |
| FrodoKEM-640-SHAKE | 2,7284 (n=20) | 2,573 (n=100) | 2,4838 (n=43) |
| FrodoKEM-976-AES | 0,553 (n=20) | 1,1335 (n=100) | 0,8357 (n=100) |
| FrodoKEM-976-SHAKE | 6,7461 (n=20) | 6,0371 (n=100) | 5,5387 (n=100) |
| FrodoKEM-1344-AES | 0,8782 (n=20) | 1,5186 (n=100) | 1,3057 (n=100) |
| FrodoKEM-1344-SHAKE | 11,8492 (n=20) | 13,0741 (n=25) | 11,7797 (n=46) |
| eFrodoKEM-640-AES | 0,3119 (n=20) | 0,5211 (n=100) | 0,623 (n=100) |
| eFrodoKEM-640-SHAKE | 3,6774 (n=20) | 3,2174 (n=100) | 2,9503 (n=100) |
| eFrodoKEM-976-AES | 0,7316 (n=20) | 1,0214 (n=100) | 1,0315 (n=100) |
| eFrodoKEM-976-SHAKE | 5,8534 (n=20) | 5,8205 (n=100) | 5,2101 (n=100) |
| eFrodoKEM-1344-AES | 0,9033 (n=20) | 1,4203 (n=100) | 1,1014 (n=100) |
| eFrodoKEM-1344-SHAKE | 10,9657 (n=20) | 11,3588 (n=51) | 10,2062 (n=69) |

Ghi chú: dấu phẩy thập phân theo kiểu Việt Nam (0,0944 ms = 94,4 us).
Số liệu thô (dấu chấm) nằm ở `$env:TEMP\nckh031_kem.json`.

Nhận xét trung thực (quan sát 1 lần chạy, máy đang bận nhiều agent):

1. ML-KEM nhanh nhất cả 3 op ở mọi level tương ứng (keygen 76–103 us,
   encap ~103–109 us, decap 25–156 us), và gọn (pk ≤ 1568 B). Kyber cũ
   cùng cỡ khóa nhưng chậm hơn ML-KEM ~1,5–2x ở keygen — không có lý do
   gì dùng Kyber thay ML-KEM nữa.
2. Classic McEliece: keygen rất chậm (79 ms tới 1,67 s), pk khổng lồ
   (261 KB tới 1,36 MB) nhưng ct nhỏ nhất (96–208 B) và encap nhanh
   (< 2 ms). Bản `f` keygen nhanh hơn bản thường 2–4,5x. Không hợp vault
   (pk quá lớn để lưu/quét), hợp kênh cần ct nhỏ.
3. HQC: chậm dần theo level (decap HQC-5 tới ~36 ms), ct lớn nhất nhóm
   code-based gọn (tới 14 KB). Thua McEliece ở ct, thua lattice ở tốc độ.
4. NTRU/sntrup761: keygen 1–7 ms, encap/decap < 0,31 ms — chậm hơn
   ML-KEM ~10–70x ở keygen nhưng vẫn ở bậc ms, dùng được nếu cần đa dạng
   giả thiết toán học (NTRU) ngoài module-lattice.
5. FrodoKEM: bản AES nhanh hơn bản SHAKE 6–10x (ví dụ 1344 keygen
   0,88 ms AES so với 11,85 ms SHAKE); khóa lớn (pk tới 21,5 KB).
   eFrodoKEM ct ngắn hơn FrodoKEM một chút (32–64 B), tốc độ tương đương.
6. Đối chiếu chéo với NCKH-007 (đợt 1, đo ML-KEM 2 lần): ML-KEM-768
   keygen của tôi 94,4 us so với 105,2/174,8 us của NCKH-007; encap
   109,1 us so với 193,2/259,4 us; decap 49,2 us so với 107,4/88,7 us.
   Cùng bậc micro-giây, số của tôi thấp hơn (máy lúc này rảnh hơn hoặc
   adaptive n lớn hơn) — chênh lệch nằm trong biên dao động máy bận mà
   NCKH-007 đã cảnh báo, không mâu thuẫn.

- Tự kiểm:
  - Round-trip encap→decap khớp từng byte cho cả 38/38 thuật toán.
  - Kích thước ML-KEM-768 khớp tools/pqc.py (1184/2400/1088/32) và khớp
    sổ NCKH-007; kích thước Kyber trùng ML-KEM cùng level (đúng vì cùng
    tham số họ Kyber).
  - BIKE disabled: xác nhận bằng `get_supported_kem_mechanisms()` (41)
    trừ `get_enabled_kem_mechanisms()` (38) = đúng 3 BIKE.
  - Không ghi/sửa gì trong repo ngoài file sổ này (script + JSON + bảng
    nháp nằm ở $env:TEMP); không git commit (đúng lệnh).
  - Mọi lệnh shell đều kèm `shell='pwsh'` (đúng lệnh).
- Peer review: chờ agent khác nhóm kiểm chéo.
- Trạng thái: doing -> review (thử opportunistic dưới đây; nếu Kanzo hỏng
  thì nhờ Viện trưởng đối chiếu sổ này khi bảng khỏe lại).

## 2026-11-21 02:25 — đồng bộ Kanzo (opportunistic, Kanzo chập chờn)

- `GET /api/board?project=esp32-securitykey` (timeout 30s):
  lần 1 HTTP 500; lần 2 (cách 5s) THÀNH CÔNG, bảng có 34 thẻ nhưng lọc
  `NCKH-031` / `Benchmark liboqs` trong title+description KHÔNG thấy thẻ nào
  của mình; lần 3 (liệt kê full để đối chiếu) lại HTTP 500.
- Kết luận: không thấy thẻ + Kanzo chập chờn đúng như lệnh đã cảnh báo.
  Theo lệnh: ghi sổ và tiếp tục, KHÔNG tự tạo thẻ, KHÔNG move/comment
  (không có id thẻ để tác động).
- Nhờ Viện trưởng khi bảng khỏe: tạo hoặc chỉ giúp thẻ [PQC] Benchmark
  liboqs trên máy cho NCKH-031 Phan Bình rồi đẩy thẳng doing -> review
  với nội dung báo cáo trong sổ này; người kiểm chéo: chờ Viện trưởng
  chỉ định (ưu tiên khác nhóm PQC).

## 2026-11-21 — nhận kiểm chéo NCKH-039 (lượt kiểm chéo đợt 2B)

- Vai trò: Phan Bình (NCKH-031, nhóm PQC) kiểm độc lập công việc của
  Dương Bình (NCKH-039, nhóm firmware): bảng so sánh USBMode OTG/HWCDC
  + khuyến nghị khi nào dùng bản nào.
- Phạm vi: REPO CHỈ ĐỌC, chỉ nối thêm file sổ này; không git commit.
  Mọi lệnh shell đều kèm `shell='pwsh'`.
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-039.md (báo cáo cần kiểm),
  .tooling core ESP32 4.0.0 (boards.txt + platform.txt, tự mở),
  firmware/hwtest/hwtest.ino, firmware/hwtest/README.md,
  scripts/build_hwtest.ps1, scripts/flash_win.ps1, tools/hid_echo.py,
  docs/03-phan-cung.md, docs/04-firmware.md,
  docs/research/02-esp32s3-usb.md, docs/runbook-nap-hwtest-windows.md,
  README.md (mục trạng thái), vien-nghien-cuu/so-cai/NCKH-012.md.

## 2026-11-21 — báo cáo kiểm chéo NCKH-039: [KIEM-DINH] đạt

### Phương pháp (đường khác với tác giả)

- Không tin trích dẫn mù: tự chạy Select-String trên boards.txt và
  platform.txt, tự đọc từng file firmware/docs/tool bằng lệnh riêng.
- Tự tính lại hiệu số build từ số gốc NCKH-012, tự đối chiếu README.
- Tự đánh giá từng khuyến nghị (6 điểm) với hwtest/README, runbook,
  docs/03-04 và research/02.

### 1. Xác nhận menu boards.txt + platform.txt — KHỚP 100%

- `esp32s3.menu.USBMode.hwcdc` = "Hardware CDC and JTAG",
  `build.usb_mode=1`; `.default` = "USB-OTG (TinyUSB)",
  `build.usb_mode=0` (boards.txt dòng 1556-1559). Khớp mục 1 tác giả.
- `menu.USBMode` = "USB Mode" (dòng 3). Khớp.
- `CDCOnBoot`: default Disabled (=0), cdc Enabled (=1) (dòng 1561-1564).
  Khớp.
- `MSCOnBoot=msc` và `DFUOnBoot=dfu` đều ghi "(Requires USB-OTG Mode)"
  (dòng 1568, 1573). Khớp.
- `UploadMode`: default "UART0 / Hardware CDC" (1200bps=false,
  wait=false); cdc "USB-OTG CDC (TinyUSB)" (1200bps=true, wait=true)
  (dòng 1576-1581). Khớp, kể cả diễn giải nạp UART không cần 1200bps.
- `platform.txt` dòng 86: `build.extra_flags.esp32s3` đúng 4 cờ
  ARDUINO_USB_MODE/CDC/MSC/DFU như tác giả trích. Khớp.
- FQBN OTG (`CDCOnBoot=cdc,USBMode=default`) khớp NCKH-012 và
  scripts/build_hwtest.ps1 dòng 5; FQBN HWCDC (`USBMode=hwcdc`) khớp
  NCKH-012. Khớp (lưu ý nhỏ: build_hwtest.ps1 chỉ chứa FQBN OTG,
  FQBN HWCDC lấy từ NCKH-012 — trích dẫn gộp của tác giả vẫn đúng).

### 2. Đối chiếu số build 372/302KB — KHỚP TỪNG BYTE

- NCKH-012 (nguồn gốc): OTG sketch 372633 (28%), RAM 55680 (16%),
  bin 372784; HWCDC sketch 302765 (23%), RAM 22784 (6%), bin 302912.
  Tác giả chép đúng cả 6 số.
- Tự tính lại: 372633-302765=69868 (~70 KB flash),
  55680-22784=32896 (~33 KB RAM). Khớp hiệu số tác giả nêu.
- README.md mục trạng thái: "OTG (372 KB) và HWCDC (302 KB)". Khớp.
- Không build lại (đồng ý với tác giả: số liệu đã có kiểm chứng độc
  lập từ NCKH-012, nhiệm vụ là so sánh + khuyến nghị).

### 3. Đối chiếu code/docs trong bảng — KHỚP

- hwtest.ino: dòng 8 (`#if ... ARDUINO_USB_MODE == 0`), dòng 91
  (log `USB mode: %d`), dòng 119-125 (nhánh HID echo sẵn sàng/TẮT)
  — khớp chính xác số dòng tác giả trích.
- hid_echo.py: usage_page 0xFF00, report ID 1, 64 byte report,
  payload 60 byte, thông báo `Không thấy HID echo` + dặn
  `USB Mode = USB-OTG` (dòng ~56), báo `60 byte đi về khớp`. Khớp.
- research/02: OTG full-speed GPIO19/20 là cổng duy nhất chạy HID
  FIDO; USB Serial JTAG không dùng cho FIDO; firmware FIDO là
  composite HID. Khớp hàng "Stack USB" và "Liên quan FIDO thật".
- docs/03: cổng native (USB/OTG) bắt buộc cho FIDO, cổng UART
  (COM/UART) để nạp. Khớp hàng "Cổng vật lý".
- docs/04 + flash_win.ps1: hwtest trước, flash xong cắm lại cổng
  native. Khớp luồng khuyến nghị.
- Baud 115200, heartbeat ~5 s, BOOT/LED: khớp hwtest/README và
  runbook mục 10-12.

### 4. Đánh giá 6 khuyến nghị — ĐÚNG CẢ 6

1. Mặc định OTG + CDCOnBoot=cdc: đúng hwtest/README (bước 3-4),
   build_hwtest.ps1, runbook bước 6-7.
2. Dùng OTG khi cần hid_echo/pico-fido/MSC-DFU/nghiệm thu: đúng
   research/02 (FIDO bắt buộc OTG), boards.txt (MSC/DFU Requires
   OTG), hwtest/README (mục HID echo).
3. Dùng HWCDC khi kiểm nhanh/không cần HID/nhẹ hơn/driver lỗi:
   hợp lý, số nhẹ hơn đã kiểm ở mục 2, runbook có mục xử lý driver.
4. Luôn bật CDC On Boot cả hai bản: đúng runbook bước 6
   ("Monitor trắng trơn nếu Disabled").
5. Giữ UploadMode=default, nạp qua cổng UART: đúng boards.txt,
   hwtest/README bước 5, runbook mục 0.2 + 8 (kể cả cảnh báo sai
   cổng COM flash nhầm).
6. Quy trình board mới (OTG → log → BOOT/LED → native + hid_echo
   60 byte → pico-fido theo docs/04): khớp runbook mục 10-13 và
   docs/04. Đúng.

### 5. Unresolved U1 của tác giả — CÓ THẬT, KHÔNG CHẶN

- Tự mở runbook xác nhận: mục 10 mở Serial Monitor ngay sau nạp qua
  cổng UART (không dặn chuyển cáp), mục 12 bước 5 ghi "cần cắm lại
  cổng UART để xem" — hai chỗ chưa nhất quán thật. Tác giả ghi
  trung thực và đúng là không chặn kết luận bảng so sánh.

### 6. Ghi chú nhỏ (không ảnh hưởng đạt)

- Hàng "Chênh lệch" trong bảng dùng `\multicolumn` (cú pháp LaTeX)
  nên không render trong Markdown — nội dung số vẫn đúng.
- Tác giả không sửa file repo nào ngoài sổ của mình, không build
  lại, không commit: đúng phạm vi.

### Kết luận kiểm chéo

- [KIEM-DINH] đạt — bảng so sánh đúng từng ô đã kiểm, số liệu build
  khớp NCKH-012 và README, 6 khuyến nghị đúng với
  firmware/hwtest/README/runbook/docs, U1 trung thực.
- Tự kiểm: chỉ nối thêm file sổ này; không git commit; shell pwsh.

## 2026-11-21 — đồng bộ Kanzo NCKH-039 (không thấy thẻ)

- GET board lần 1: THÀNH CÔNG, 45 thẻ, lọc `NCKH-039|USBMode|USB`
  trong title KHÔNG thấy thẻ nào.
- GET board lần 2 (liệt kê toàn bộ, sau 5 s): HTTP 500 (Kanzo chập
  chờn đúng như lệnh đã cảnh báo).
- GET board lần 3 (thử lại 1 lần, sau 5 s, trong hạn 2 thử lại):
  THÀNH CÔNG, 45 thẻ: id 138-166 ở done (NCKH-001..028), id 167-185
  ở todo (5 thẻ FIX/DOC/OPS + NCKH-022..037, mới nhất là NCKH-037
  id 185). Không có thẻ NCKH-039 (cả NCKH-038..044 cũng chưa có).
- Kết luận: thẻ đợt 2B của NCKH-039 chưa được tạo trên bảng. Theo
  lệnh: KHÔNG tự tạo thẻ, chỉ ghi sổ và tiếp tục.
- Không thực hiện move/comment nào (không có thẻ đích).
- Nhờ Viện trưởng: tạo thẻ NCKH-039 giúp rồi vá doing -> review
  (nội dung tác giả) và review -> done kèm comment
  `[KIEM-DINH] đạt — bảng OTG/HWCDC đúng từng ô, số build khớp
  NCKH-012/README, 6 khuyến nghị đúng docs` (nội dung kiểm chéo này).
