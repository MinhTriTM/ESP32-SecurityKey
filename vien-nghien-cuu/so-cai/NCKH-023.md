# Sổ cái NCKH-023 — Chu An (nhóm tailieu, thành viên, đợt 2A)

## 2026-11-21 02:00 — nhận việc

- Thẻ: [tailieu] Rà soát chính tả toàn repo (mã NCKH-023, id Kanzo tra sau ở mục Kanzo)
- Người nhận: Chu An (NCKH-023)
- Việc nhận (theo `phan-cong.json` + lệnh giao việc): quét toàn bộ `.md` trong repo,
  liệt kê lỗi chính tả và thuật ngữ không nhất quán dạng file:dòng, đề xuất sửa
  từng chỗ nhưng CHƯA SỬA (đợt này chỉ báo cáo, tránh xung đột với agent khác).
  REPO CHỈ ĐỌC, không git commit.
- Tài liệu đã đọc TRƯỚC khi làm:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, toàn bộ)
  - mục NCKH-023 trong `vien-nghien-cuu/phan-cong.json` (dòng 266-277:
    Chu An, tailieu, thành viên, đợt 2, "Rà soát chính tả toàn repo")
  - `vien-nghien-cuu/so-cai/README.md` + `vien-nghien-cuu/NHIP-TIM.md`
    (luật file-trước-bảng-sau)
- Lưu ý đường dẫn: lệnh giao việc ghi `HIEN-CHUONG.md`, `phan-cong.json`,
  `so-cai/README.md` ở gốc repo, nhưng thực tế nằm dưới `vien-nghien-cuu/`.
  Đã tự tìm đúng file, không báo lỗi.
- Trạng thái: todo -> doing (dự kiến; đồng bộ Kanzo opportunistic sau khi ghi sổ)

## 2026-11-21 02:00 — báo cáo rà soát chính tả toàn repo (CHỈ BÁO CÁO, chưa sửa)

### Phạm vi đã quét (50 file .md tại thời điểm quét)

- Đọc toàn bộ nội dung: `README.md`, 16 file `docs/` (7 gốc + 7 research +
  2 runbook mới của NCKH-015/NCKH-021), `firmware/hwtest/README.md`,
  `hardware/BOM.md` + `keys.md` + `wiring.md`, `HIEN-CHUONG.md`,
  `KHOI-DONG.md`, `NHIP-TIM.md`, `so-cai/README.md`,
  `so-cai/NCKH-001..008` (toàn bộ), `so-cai/NCKH-009..012` (60 dòng đầu mỗi file).
- Không đọc chi tiết: `so-cai/NCKH-013..027` (nhật ký agent khác đang chạy,
  sổ chỉ nối thêm nên lỗi trong đó cũng không được sửa — xem mục C9).
- Kiểm chứng bằng `muse.search` regex trên `docs/`, `hardware/`,
  `firmware/hwtest/README.md`, `README.md` cho mọi nhóm thuật ngữ dưới đây.
- CẢNH BÁO NHIỄU ĐỒNG THỜI: trong lúc quét, agent khác đã sửa repo
  (file `docs/07-sao-luu-va-khoi-phuc.md` tăng 126 -> 182 dòng do NCKH-017 thêm
  sơ đồ; `hardware/BOM.md` tăng 21 -> 30 dòng do NCKH-027 chốt N16R8; thêm mới
  `docs/research/07-giai-thich-distinguisher.md` của NCKH-026 và 2 runbook).
  Số dòng dưới đây ứng với nội dung tôi đã đọc; nếu lệch khi đối chiếu thì tra
  theo cụm chữ.

### A. Lỗi chính tả / câu lỗi rõ ràng (6 chỗ, nên sửa)

- A1. `docs/research/02-esp32s3-usb.md:19` — "phải để Harware CDC and JTAG"
  -> "phải để Hardware CDC and JTAG" ("Harware" thiếu chữ d).
- A2. `docs/runbook-nap-hwtest-windows.md:66` — "*Additional Board Manager URLs*"
  -> "*Additional Boards Manager URLs*" (thiếu "s"; đúng tên trường trong
  Arduino IDE, khớp dòng 67 "Boards Manager" trong cùng file).
- A3. `docs/runbook-nap-hwtest-windows.md:34` — "cài trong Board Manager"
  -> "cài trong Boards Manager" (nhất quán dòng 67, 70 và tên thật trong IDE).
- A4. `docs/06-bao-mat.md:49` — "có thể hết pin dự phòng suy nghĩ, quên PIN"
  là câu rối ("suy nghĩ" lạc vào giữa cụm danh từ; board DevKit cũng không có
  pin nên "hết pin" gây hiểu lầm). Đề xuất viết lại:
  "có thể quên PIN, quên cách dùng, hoặc lỗi flash mới phát hiện".
- A5. `docs/07-sao-luu-va-khoi-phuc.md:120` — "nếu muốn chống cháy nước"
  -> "nếu muốn chống cháy và chống nước" (thiếu liên từ).
- A6. `docs/runbook-nap-hwtest-ubuntu.md:30` — "Liệt kê cổng chắc chắn thuộc
  về board" (câu cụt, "chắc chắn" lạc vị trí). Đề xuất:
  "Liệt kê để chắc chắn cổng nào thuộc về board".

### B. Thuật ngữ không nhất quán (đề xuất chuẩn từng nhóm)

- B7. "5V" (`hardware/wiring.md:11`) vs "5 V" (`docs/03-phan-cung.md:23`)
  -> chốt "5 V" (chuẩn SI viết cách).
- B8. "USB_OTG" (`docs/02-kien-truc.md:50`) vs "USB OTG" (mọi nơi khác)
  -> "USB OTG" (bỏ gạch dưới kiểu tên biến).
- B9. "USB mode" (`docs/research/02-esp32s3-usb.md:19`) vs "USB Mode"
  (`firmware/hwtest/README.md:12`, 2 runbook) -> "USB Mode" (đúng tên menu
  Arduino IDE).
- B10. "Secure Boot"/"Flash Encryption" (`docs/04-firmware.md:14`,
  `docs/06-bao-mat.md:30`, `docs/07-sao-luu-va-khoi-phuc.md:25`) vs
  "secure boot"/"flash encryption" (`docs/02-kien-truc.md:64`,
  `docs/04-firmware.md:71`, `docs/06-bao-mat.md:11`) -> chốt VIẾT HOA cả hai
  (đúng tên tính năng Espressif; "Secure Download Mode", "Secure Lock" trong
  repo đã viết hoa).
- B11. "Pico-fido" giữa câu (`README.md:41` "Pico-fido chốt tag v8.2") vs
  "pico-fido" (mọi nơi khác) -> "pico-fido" (tên dự án viết thường).
  Các chỗ đầu câu (`docs/04-firmware.md:73`, `docs/research/01-giao-thuc-fido.md:27`,
  `docs/research/04-tai-lieu-tham-khao.md:18`) giữ nguyên cũng được, hoặc hạ về
  thường toàn bộ cho tuyệt đối nhất quán.
- B12. "ESP" viết tắt (`docs/07-sao-luu-va-khoi-phuc.md` các dòng 3, 6, 8, 11,
  12, 19, 22, 35, 45, 50, 88, 150) vs "ESP32-S3" (dòng 13 cùng file)
  -> "ESP32" hoặc "ESP32-S3".
- B13. "WiFi Direct" (`docs/07-sao-luu-va-khoi-phuc.md:142`) -> "Wi-Fi Direct"
  (đúng chính tả; chính trích dẫn Espressif trong `hardware/BOM.md:23` cũng
  viết "Wi-Fi + Bluetooth LE").
- B14. "U2FHID" (`docs/research/03-du-an-lien-quan.md:12`) -> "U2F HID" hoặc
  "CTAPHID" (không có chuẩn nào viết liền "U2FHID").
- B15. "ClientPin" (`docs/research/01-giao-thuc-fido.md:21`) -> "ClientPIN"
  (đúng tên lệnh CTAP2).
- B16. "CTAP 2.3/CTAP1" (`docs/04-firmware.md:14`) cách quãng không đều
  (vế trái cách, vế phải liền) -> "CTAP2 (bản 2.3)/CTAP1" (giữ quy ước
  "CTAP2"/"CTAP1" liền của cả repo).
- B17. "hash" (`docs/01-phan-tich-y-tuong.md:28`, `docs/06-bao-mat.md:29,45`)
  vs "SHA" (`docs/04-firmware.md:42,47`) khi cùng nói mã commit
  -> chốt "SHA commit".
- B18. Bốn cách gọi một thứ (`docs/07-sao-luu-va-khoi-phuc.md`): "USB" (dòng 8),
  "ổ cứng" (dòng 12), "ổ USB" (dòng 14), "ổ đĩa" (dòng 15) -> chốt "ổ USB".
- B19. "Bluetooth và devices" (`docs/05-huong-dan-su-dung.md:9`,
  `docs/07-sao-luu-va-khoi-phuc.md:141`) nửa Việt nửa Anh
  -> "Bluetooth & devices" (đúng tên trang Settings của Windows).
- B20. "backup tự động" (`docs/07-sao-luu-va-khoi-phuc.md:161`) vs "sao lưu"
  (tiêu đề file và mọi nơi khác) -> "sao lưu tự động".
- B21. "RESET" (`docs/runbook-nap-hwtest-windows.md:138,146,176`) vs "RST"
  (`hardware/wiring.md:20`) -> chốt "RST" (đúng chữ in lụa), lần đầu ghi
  "RST (RESET)" rồi sau dùng "RST".
- B22. Dấu phân tách menu "Tools >" (runbook Ubuntu, 6 chỗ: dòng 117-119, 122,
  155-156) vs "Tools →" (runbook Windows, 8 chỗ) -> chốt "→" cả hai file.
- B23. "user" (runbook Ubuntu dòng 44, 49, 53, 63, 103) vs "người dùng"
  (dòng 145 cùng file + toàn bộ docs lõi) -> chốt "người dùng".
- B24. "Thả" (runbook Windows dòng 189, 234) vs "nhả" (runbook Ubuntu dòng 174,
  205; khớp log firmware "BOOT: nha") -> chốt "nhả".
- B25. "5 s" (`docs/runbook-nap-hwtest-ubuntu.md:207`) vs "5 giây" (dòng 176
  cùng file + runbook Windows dòng 163, 236) -> chốt "5 giây" trong văn xuôi.
- B26. "Python ≥ 3.10" (runbook Ubuntu dòng 182) vs "Python 3.10 trở lên"
  (runbook Windows dòng 35) -> chốt một kiểu (đề xuất chữ "trở lên").
- B27. "VID:PID" (runbook Ubuntu dòng 73) vs "VID/PID" (dòng 80 cùng file)
  -> chốt "VID:PID".
- B28. "USB Serial/JTAG" (runbook Ubuntu dòng 28) vs "USB Serial JTAG"
  (`docs/research/02-esp32s3-usb.md:5`) -> chốt "USB Serial/JTAG".
- B29. "kiểu Gohr" (`docs/research/06-ml-distinguisher.md` tiêu đề,
  `docs/research/07-giai-thich-distinguisher.md:46`) vs "phong cách Gohr"
  (06 dòng 14, 07 dòng 69) -> chốt "kiểu Gohr".
- B30. "mắt người" (`docs/research/07-giai-thich-distinguisher.md:49`) vs
  "mắt thường" (`docs/research/06-ml-distinguisher.md:47`) -> chốt "mắt thường".
- B31. "số vòng lặp" (`docs/research/07-giai-thich-distinguisher.md:97`) vs
  "số vòng" (06 dòng 49 và mọi nơi) -> chốt "số vòng".
- B32. "bấm nút" (`docs/research/07-giai-thich-distinguisher.md:19`) vs
  "nhấn nút" (mọi nơi khác) -> "nhấn nút".
- B33. "nhắn tin bằng CBOR" (`docs/research/01-giao-thuc-fido.md:21`) dễ đọc
  thành "texting" -> "trao đổi bản tin CBOR".
- B34. Từ tiếng Anh lạc trong câu Việt (`docs/02-kien-truc.md`): "request"
  (dòng 5, 41), "parse" (dòng 42) -> "yêu cầu", "phân tích" ("message" đã là
  thuật ngữ chốt của repo nên giữ nguyên).
- B35. "bản stable"/"bản review" (`docs/research/04-tai-lieu-tham-khao.md:5-6`)
  -> "bản tiêu chuẩn đề xuất (PS)"/"bản thảo xem xét (RD)" (khớp hậu tố
  -ps-/-rd- trong URL).
- B36. "built trên" (`README.md:3`) -> "dựng trên".
- B37. "comment" (`docs/runbook-nap-hwtest-windows.md:77`) vs "chú thích"
  (dòng 28-29 cùng file, `hardware/BOM.md:22`) -> "chú thích".
- B38. "Khung output" (`docs/runbook-nap-hwtest-windows.md:128`) vs "log"
  (mọi nơi) -> "Khung đầu ra" (hoặc chốt "output" làm thuật ngữ nếu nhóm
  tài liệu muốn giữ).
- B39. "Cáp sạc" (runbook Ubuntu dòng 218, bảng sự cố) vs "cáp sạc thuần"
  /"cáp chỉ sạc" (mọi nơi) -> "cáp chỉ sạc".
- B40. "Linux, Ubuntu" liệt kê trùng (`README.md:3`,
  `docs/01-phan-tich-y-tuong.md:5`, `docs/05-huong-dan-su-dung.md:1`) và
  "Cả bốn nền tảng" (`docs/01-phan-tich-y-tuong.md:17`) trong khi Ubuntu là
  một bản Linux -> "Android, Linux (kể cả Ubuntu) và Windows 11" và
  "Cả ba nền tảng".
- B41. "Octal SPI" (`hardware/BOM.md:5,25`) vs "SPI 8-line (Octal)" (dòng 24
  cùng file) -> chốt một kiểu (mức thấp).
- B42. "PSRAM octal 8 MB" (`docs/03-phan-cung.md:5`) vs "PSRAM 8 MB
  (Octal SPI)" (`hardware/BOM.md:5`) -> đồng bộ theo BOM.
- B43. `docs/03-phan-cung.md:5-7` đã LẠC HẬU so với BOM: BOM đã chốt N16R8
  (ngày 2026-11-21, NCKH-027) trong khi 03 vẫn viết "Khả năng cao là N16R8
  bị ghi nhầm" + "Việc cần làm trước khi flash". Đề xuất cập nhật 03 trỏ
  sang kết luận BOM thay vì giữ giả thiết cũ.
- B44. SAI ĐƯỜNG DẪN (phát hiện khi rà chéo): runbook Windows dòng 202, 228
  ghi `pip install -r requirements.txt` trong khi chạy từ gốc repo; file thật
  nằm ở `tools/requirements.txt` (gốc repo KHÔNG có requirements.txt; bản
  Ubuntu dòng 184, 225 ghi đúng) -> sửa thành
  `pip install -r tools/requirements.txt` cả hai chỗ.
- B45. "đăng xuất/nhập lại" (runbook Ubuntu dòng 215, bảng) vs "Đăng xuất rồi
  đăng nhập lại" (dòng 57) -> viết đầy đủ.
- B46. Chữ link là đường dẫn thô "[docs/04-firmware.md](04-firmware.md)"
  (runbook Windows dòng 240) trong khi mọi link khác dùng văn bản mô tả
  -> "[hướng dẫn firmware](04-firmware.md)".
- B47. "peer review" (`vien-nghien-cuu/HIEN-CHUONG.md:22`) vs "kiểm chéo"
  /"kiểm định" (mọi nơi) -> "kiểm chéo".
- B48. "edge case" (`vien-nghien-cuu/HIEN-CHUONG.md:46`) -> "trường hợp biên".
- B49. "owner" (`vien-nghien-cuu/KHOI-DONG.md:5`) -> "người phụ trách".
- B50. "6–7 vòng" (`docs/research/07-giai-thich-distinguisher.md:144`) dùng
  en dash (–); cả repo chỉ dùng hyphen (-) và em dash (—) -> "6-7 vòng".
- B51. Khẩu ngữ trong runbook Ubuntu (nhất quán nội bộ nhưng nên trang trọng
  hơn): "đẻ file cấu hình" (dòng 65) -> "tạo ra file cấu hình"; "quyền đã ăn"
  /"udev chưa ăn" (dòng 98, 123, 218) -> "quyền đã có hiệu lực"/"udev chưa
  có hiệu lực". Mức thấp.

### C. Đã kiểm tra và KHÔNG có vấn đề (ghi để khỏi kiểm lại)

- C1. Chính tả Việt kiểu cũ "hoá/khoá/kĩ/qui/uỷ": KHÔNG CÓ. ("dứt khoát"
  ở `docs/06-bao-mat.md:28` là đúng chính tả; "toán học" đúng.)
- C2. "đăng ký", "quy trình", "nơ-ron", "khóa", "mã hóa": nhất quán toàn repo.
- C3. Thuật ngữ FIDO/crypto: "FIDO2", "U2F (CTAP1)", "CTAP2", "WebAuthn",
  "passkey", "resident key", "credential", "private/public key",
  "Shamir", "BIP-39", "ML-KEM", "PBKDF2", "SHA-256", "AES-256-GCM",
  "checksum", "hex", "QR", "distinguisher", "thám mã", "vi sai",
  "brute-force", "lattice", "QKD", "qubit", "NIST/FIPS": nhất quán.
  ("Passkey"/"Resident key" viết hoa chỉ ở đầu câu/tiêu đề — đúng.)
- C4. Phần cứng: "ESP32-S3", "DevKit", "GPIO/D-/D+", "BOOT", "WS2812",
  "GPIO38/GPIO48", "UART", "JTAG", "CDC", "HID", "OTG", "PSRAM", "flash",
  "RAM/MB", "chip/board/module/shield", "Espressif", "ESP-IDF",
  "YubiKey", "C-to-C", "USB-C": nhất quán. ("S3" viết tắt xuất hiện ~10 chỗ
  trong research + `docs/01:11` + runbook Ubuntu dòng 28 — đã thành quy ước
  nội bộ, dễ nhầm AWS S3 nhưng chấp nhận được; chỉ đề xuất định nghĩa một
  lần ở mỗi file nếu nhóm tài liệu muốn.)
- C5. Tên tool/code trong văn xuôi: "hwtest", "fido_check", "hid_echo",
  "split_secret", "mnemonic", "vault", "pqc", "ml_distinguisher",
  "run_tests", "70-u2f.rules", "udev rules", "sdkconfig",
  "esp32-s3-devkitc-1", "ESP32S3 Dev Module", "Boards Manager",
  "Serial Monitor", "Device Manager", "Ports (COM & LPT)", "Quick Share",
  "Bluetooth", "Settings", "Chrome/Edge/Firefox", "GitHub",
  "Google/GitHub/Microsoft", "app", "project", "script", "tool", "repo",
  "log", "checklist", "xanh lá/xanh dương", "két mã hóa", "ví lạnh",
  "diễn tập", "ngưỡng", "mã khôi phục", "key vật lý/dự phòng/chính",
  "cloud", "MAC", "PIN", "NVS", "OTP", "eFuse" (repo chốt viết thường
  "efuse" ở `docs/04:75`, `docs/06:20` — nhất quán nội bộ dù Espressif viết
  "eFuse; giữ nguyên, không đề xuất sửa): nhất quán.
- C6. Chữ thường trong URL/mã/FQBN/log trích dẫn (github.com, esp32:esp32:...,
  "BOOT: nha", "san sang", "da gui lai 64 byte.", "TAT", "vd" trong sơ đồ
  ASCII) là đúng ngữ cảnh — không sửa.
- C7. Hai sơ đồ ASCII không dấu (`docs/02-kien-truc.md:14-36`,
  `docs/07-sao-luu-va-khoi-phuc.md:49-83`) là có chủ ý (ASCII thuần, đã có
  NCKH-004 kiểm độc lập cho sơ đồ 02) — không sửa.
- C8. "S3 sinh ra đã hợp làm USB gadget" (`docs/01:11`), "Key ... nói cả
  CTAP1 và CTAP2" (research/01:7): văn phong ẩn dụ, chấp nhận được.
- C9. Sổ cái agent khác là nhật ký nối thêm (không sửa mục cũ) nên lỗi trong
  đó nếu có cũng KHÔNG thuộc phạm vi sửa đợt này. Ghi nhận một chỗ để Viện
  trưởng nhắc tác giả tự đính chính bằng mục nối thêm: tiêu đề
  `vien-nghien-cuu/so-cai/NCKH-006.md:1` ghi "Phan Phúc" trong khi
  `phan-cong.json` và chính mục 01:44 trong sổ đó ghi "Phan An".

### Tự kiểm

- Lệnh shell (đều kèm `shell='pwsh'` theo lệnh): `Get-ChildItem` liệt kê gốc
  repo (OK); `Get-ChildItem -Recurse` liệt kê md/json (OK, nhờ đó phát hiện
  đúng đường dẫn `vien-nghien-cuu/`); 1 lệnh `Get-ChildItem -Recurse -File`
  toàn cây bị treo nền -> đã tự hủy (terminate) và chuyển sang `muse.search`
  có giới hạn; `Get-Date` lấy giờ ghi sổ (OK).
- Đọc: 37 file `.md` đọc toàn bộ + 4 file đọc 60 dòng đầu (liệt kê ở mục
  phạm vi). Mọi nhóm thuật ngữ trong mục B đều đối chiếu tối thiểu 2 vị trí
  bằng search regex; các mục C đều có search phủ định (0 kết quả sai).
- Không sửa bất kỳ file repo nào ngoài chính sổ cái này; không git commit.
- Trạng thái: doing -> review (chờ kiểm chéo; peer review cần đường kiểm độc
  lập, không chạy lại đúng lệnh của tác giả).

## 2026-11-21 02:05 — đồng bộ Kanzo (opportunistic): KHÔNG CÓ THẺ, nhờ Viện trưởng tạo

- `GET /api/board?project=esp32-securitykey` lần 1: OK, 23 thẻ, nhưng KHÔNG có
  thẻ nào chứa "023"/"chính tả".
- `GET /api/board` lần 2 (liệt kê tiêu đề): HTTP 500, thử lại sau 5s.
- `GET /api/board` lần 3: OK. Toàn bảng gồm đợt 1 (id 138-150, đã done cả 12)
  và đợt 2A một phần (id 153-164: NCKH-013..021 trừ 022, và 024/025/026).
  KHÔNG có thẻ NCKH-022, NCKH-023.
- Kết luận: thẻ của tôi chưa được tạo trên bảng. Lệnh giao việc chỉ cho phép
  "tìm thẻ có mã bạn, thử move+comment" nên tôi KHÔNG tự tạo thẻ mới (tránh
  trùng khi Viện trưởng tạo thẻ chính thức). Không có move/comment nào được thử.
- Mọi lệnh cách nhau ≥5s, timeout 30s, đúng luật opportunistic.
- Nhờ Viện trưởng: tạo thẻ "[tailieu] Rà soát chính tả toàn repo (NCKH-023)",
  đẩy todo -> doing -> review kèm nội dung báo cáo trong sổ này; sổ cái file
  là nguồn sự thật duy nhất cho thẻ này.

## Unresolved

1. Kanzo chưa có thẻ NCKH-023 (xem mục trên) — cần Viện trưởng tạo và vá
   trạng thái review + gắn báo cáo.
2. Toàn bộ 51 mục A/B mới ở mức ĐỀ XUẤT (đợt này chỉ báo cáo, chưa sửa).
   Đề nghị Viện trưởng/nhóm trưởng tailieu (NCKH-005) chốt chuẩn từng nhóm
   rồi mở thẻ follow-up sửa theo đợt, tránh xung đột ghi với agent khác.
3. Số dòng trong báo cáo có thể trôi do agent khác đang sửa docs đồng thời
   (đã ghi cảnh báo ở mục phạm vi) — khi sửa, tra theo cụm chữ thay vì số dòng.
4. Mục C9 (tiêu đề sổ NCKH-006 ghi "Phan Phúc" thay vì "Phan An") cần tác giả
   tự nối thêm mục đính chính — ngoài phạm vi thẻ này, để Viện trưởng nhắc.

## 2026-11-21 02:05 — kiểm chéo NCKH-015 (Lý An, runbook Windows) đợt 2A: KHÔNG ĐẠT (sửa nhỏ)

- Vai trò: người kiểm chéo (Chu An NCKH-023 nhóm tailieu, khác nhóm firmware của
  tác giả). Không sửa file của tác giả, không git commit.
- Tài liệu đã đọc toàn bộ: `vien-nghien-cuu/so-cai/NCKH-015.md` (59 dòng),
  `docs/runbook-nap-hwtest-windows.md` (252 dòng).
- Đường kiểm ĐỘC LẬP (không chạy lại đúng lệnh tác giả): đối chiếu từng
  lệnh/menu/log mẫu với `scripts/build_hwtest.ps1` (FQBN),
  `firmware/hwtest/README.md`, `firmware/hwtest/hwtest.ino` (đọc toàn bộ
  154 dòng — khớp con số 154 trong sổ NCKH-015), `tools/hid_echo.py` (toàn bộ),
  `hardware/wiring.md` (cổng USB); kiểm file bằng `Test-Path` thay vì tin mô tả.
  Mọi lệnh shell đều kèm `shell='pwsh'`.

### Đối chiếu (đạt 13/16 điểm)

1. Quy mô file: `(Get-Content).Count` -> 252, `Length` -> 10468 — KHỚP TUYỆT
   ĐỐI với sổ NCKH-015. 15 mục (0-14) đúng như báo cáo. ĐẠT.
2. Board `ESP32S3 Dev Module` (mục 5) khớp README dòng 10, `hwtest.ino:3`
   (DevKit) và FQBN `esp32:esp32:esp32s3` trong `build_hwtest.ps1`. ĐẠT.
3. `USB CDC On Boot = Enabled` (mục 6) khớp README dòng 11, `hwtest.ino:3`
   và `CDCOnBoot=cdc` trong FQBN. ĐẠT.
4. `USB Mode = USB-OTG (TinyUSB)` (mục 7) khớp README dòng 12 và nhánh
   `#if ARDUINO_USB_MODE == 0` trong `hwtest.ino:8,119,145`; log `USB mode: 0`
   khớp chuỗi `printf` ở `hwtest.ino:91` từng ký tự. ĐẠT.
5. Serial 115200 baud (mục 10) khớp `Serial.begin(115200)` (`hwtest.ino:113`)
   và README dòng 14. ĐẠT.
6. Log mẫu mục 10: từng dòng khớp `printChipInfo` (`hwtest.ino:82-95`), dòng
   `HID echo: san sang (vendor page 0xFF00, report ID 1).` khớp `hwtest.ino:122`,
   heartbeat khớp format `hwtest.ino:142-143`; dải `=` dài 38 ký tự cả hai bên
   (đếm bằng shell). ĐẠT.
7. `BOOT: nhan` / `BOOT: nha` + LED xanh dương/xanh lá (mục 11) khớp
   `hwtest.ino:132-136,126,133`; `BOOT_PIN 0` (`hwtest.ino:68`) đúng nút BOOT
   DevKit. ĐẠT.
8. `HID echo ok: 60 byte đi về khớp từng byte...` (mục 12) khớp từng chữ với
   `hid_echo.py:76`; `PAYLOAD_LEN = 60` (`hid_echo.py:20`); dòng serial
   `HID echo: da gui lai 64 byte.` khớp `hwtest.ino:149`. ĐẠT.
9. Thông điệp lỗi mục 12 khớp `hid_echo.py:55` (usage page 0xFF00),
   dòng 70 (không trả lời), dòng 47 (thiếu thư viện hid). ĐẠT.
10. Đường PlatformIO (mục 14): board `esp32-s3-devkitc-1` + cờ
    `-DARDUINO_USB_CDC_ON_BOOT=1` + TinyUSB OTG khớp README dòng 18;
    `ARDUINO_USB_MODE=0` nhất quán với `#if` trong code. ĐẠT
    (runbook ghi chi tiết hơn README nhưng đúng).
11. Cổng native GPIO19/GPIO20 (mục 0.2) khớp `hardware/wiring.md:9-10`; phân
    biệt cổng nạp UART / cổng OTG khớp `wiring.md:35-38`. ĐẠT.
12. Thao tác kẹt `Connecting...` (giữ BOOT + RESET) đúng quy trình download
    ESP32-S3 chuẩn, nhất quán với BOOT GPIO0 trong code. ĐẠT.
13. Checklist mục 13 bao đủ 4 dấu hiệu đạt trong README mục "Kết quả đạt". ĐẠT.
14. B44 CÒN SAI (lỗi chức năng): mục 12 dòng 202 và 228 vẫn ghi
    `pip install -r requirements.txt` trong khi hướng dẫn "Mở PowerShell tại
    thư mục gốc repo" — kiểm bằng `Test-Path`: gốc repo KHÔNG có
    requirements.txt (False), file thật ở `tools/requirements.txt` (True,
    chứa `hidapi>=0.14.0`). Chạy verbatim từ gốc repo sẽ báo không mở được
    file. Bản Ubuntu ghi đúng (`tools/requirements.txt`). KHÔNG ĐẠT —
    sửa cả 2 chỗ thành `pip install -r tools/requirements.txt`.
    (Ghi chú: docstring `hid_echo.py:8` cũng ghi `requirements.txt` nhưng ngữ
    cảnh đó là cwd=tools/; runbook nói rõ cwd=gốc repo nên runbook sai.)
15. Link dòng 5: chữ link `firmware/hwtest/README.md` nhưng đích lại là
    `../firmware/hwtest/hwtest.ino` (trỏ nhầm sang file .ino). KHÔNG ĐẠT —
    sửa đích thành `../firmware/hwtest/README.md`.
16. Số bước dẫn chiếu lệch 1: dòng 25, 29, 113 ghi HID echo là "bước 11"
    nhưng HID echo thực tế là mục 12 (mục 11 là thử BOOT/LED). KHÔNG ĐẠT
    (mức thấp) — sửa 3 chỗ thành "bước 12".
- Các mục style A2/A3, B21, B24, B37, B38, B46 tôi từng nêu vẫn còn nhưng mức
  thấp, không tính vào kết luận — đề nghị sửa gộp ở đợt follow-up chính tả.

### Kết luận kiểm chéo

- KHÔNG ĐẠT (sửa nhỏ, ước tính 6 dòng: 2 dòng pip + 1 link + 3 số bước).
  Runbook đúng ~97% nội dung kỹ thuật, nhưng lệnh pip chạy verbatim từ gốc
  repo sẽ hỏng nên chưa đủ chuẩn "từng bước chạy được".
- Đề nghị Lý An sửa 3 điểm 14-16 rồi tự đẩy review lại; người kiểm chéo sẽ
  duyệt nhanh mà không cần đọc lại toàn bộ.
- Điểm B44 do chính tôi nêu ở đợt quét chính tả: XÁC NHẬN VẪN SAI trong file
  tại thời điểm kiểm (đối chiếu bằng `Test-Path`, không phải đọc suông).

### Đồng bộ Kanzo (thẻ id 155, opportunistic)

- GET board lần 1: OK, thấy thẻ `[firmware] Runbook nạp hwtest Windows
  (NCKH-015)` id 155, trạng thái `review`, 0 comment. Mọi lệnh timeout 30s,
  cách nhau ≥5s, tối đa 2 thử lại (3 lần thử).
- POST comment `[KIEM-DINH] KHÔNG ĐẠT...`: HỎNG cả 3 lần (lần 1: 500, lần 2:
  timeout 30s, lần 3: 500) — cùng lỗi endpoint comments mà tác giả đã gặp.
- POST move `review->doing`: OK ngay lần 1 (phản hồi ghi `status=doing`,
  `comments=1` — có thể 1 trong 3 comment đã lọt vào server dù client báo lỗi,
  đúng cảnh báo "timeout client không đồng nghĩa server chưa ghi" trong
  Hiến chương §6; nội dung comment không đọc được qua API board).
- GET xác nhận lần 1: 500; lần 2 (sau 10s): OK — thẻ 155 đang ở `doing`,
  `comments=1`. Kết luận kiểm chéo đã có hiệu lực trên bảng (trả về doing
  để tác giả sửa).
- Đã tuân thủ "file trước bảng sau": toàn bộ kết luận nằm ở sổ này trước khi
  chạm Kanzo. Nhờ Viện trưởng kiểm tra giúp nội dung comment trên thẻ 155
  (nếu rỗng/sai thì vá giúp nội dung mục kết luận trên).

## 2026-11-21 02:17 — duyệt lại sau sửa NCKH-015 (Lý An, runbook Windows): ĐẠT

- Vai trò: người duyệt lại (Chu An NCKH-023, nhóm tailieu). Không sửa file của
  tác giả, không git commit. Mở đúng các dòng để xác nhận, không tin báo cáo mù.
  Mọi lệnh shell đều kèm `shell='pwsh'`.
- Phạm vi duyệt lại: chỉ 3 chỗ sửa theo yêu cầu (thẻ Kanzo 155), không đọc lại
  toàn bộ file.

### Bằng chứng từng chỗ (đọc trực tiếp file)

1. Dòng 202 + 228 đã là `pip install -r tools/requirements.txt`: ĐẠT.
   - Dòng 202: `pip install -r tools/requirements.txt` (đọc trực tiếp + xác nhận
     qua `Get-Content ... | Select-Object -Index 201`).
   - Dòng 228: `- \`Thiếu thư viện hid\`: chạy lại
     \`pip install -r tools/requirements.txt\`.` (đọc trực tiếp + Index 227).
   - `Test-Path tools/requirements.txt` -> True; nội dung chứa
     `hidapi>=0.14.0`. `Test-Path requirements.txt` (gốc repo) -> False.
   - Kết luận: lệnh chạy verbatim từ gốc repo nay mở đúng file, khớp bản Ubuntu.
2. Dòng 5 link README.md đã trỏ đúng: ĐẠT.
   - Dòng 5: `> Nguồn kỹ thuật:
     [firmware/hwtest/README.md](../firmware/hwtest/README.md),`
   - Chữ link và đích đều là README.md (trước đây đích nhầm sang .ino).
   - `Test-Path firmware/hwtest/README.md` -> True.
3. Dòng 25/29/113 đã là "mục 12": ĐẠT.
   - Dòng 25: `... **Kiểm tra HID echo** (mục 12) |`
   - Dòng 29: `native với chú thích "để dành cho mục 12".*`
   - Dòng 113: `> chạy nhưng log in \`HID echo: TAT\` và mục 12 sẽ thất bại.`
   - HID echo thực tế là mục 12 (mục 11 là thử BOOT/LED) nên dẫn chiếu nay đúng.

### Kết luận duyệt lại

- ĐẠT. Cả 3 chỗ sửa của NCKH-015 đã có hiệu lực trong file, kiểm chứng độc lập
  bằng đọc trực tiếp + `Test-Path`, không tin báo cáo mù.
- Đề nghị thẻ Kanzo 155 review -> done (xem mục đồng bộ Kanzo bên dưới, ghi sau
  khi chạm bảng).

### Đồng bộ Kanzo (thẻ id 155, opportunistic): THÀNH CÔNG

- `POST /api/tasks/155/comments` (`[KIEM-DINH] DAT (duyet lai)...`): lần 1 HỎNG
  500 Internal Server Error; chờ 5s thử lại lần 2 OK, comment id 53, task_id 155.
  Mọi lệnh timeout 30s, `shell='pwsh'`, đúng luật tối đa 2 thử lại.
- `POST /api/tasks/155/move {"status":"done"}` (sau comment 5s): OK ngay lần 1,
  server trả `status: done`, `comments: 3`, đúng thẻ `[firmware] Runbook nạp
  hwtest Windows (NCKH-015)`.
- Đã tuân thủ "file trước bảng sau": mục duyệt lại nằm ở sổ này trước khi chạm
  Kanzo. Không cần đối chiếu GET board thêm vì cả move và comment đều trả OK
  rõ ràng (không phải timeout mập mờ).

## Unresolved (bổ sung duyệt lại)

5. Thẻ Kanzo của chính NCKH-023 vẫn chưa tồn tại (xem Unresolved 1-4 ở trên) —
   kết luận duyệt lại ĐẠT cho thẻ 155 không phụ thuộc vào việc này.
6. Các mục style mức thấp (A2/A3, B21, B24, B37, B38, B46) vẫn còn trong runbook
   theo ghi nhận ở lần kiểm chéo trước — đề nghị gộp vào đợt follow-up chính tả,
   không chặn done thẻ 155.
