# Sổ cái NCKH-021 (nhóm firmware, thành viên, đợt 2A)

> Tên theo `phan-cong.json`: Hứa An. Ký theo mã NCKH-021.

## 2026-11-21 01:53 — nhận việc

- Việc nhận (theo `phan-cong.json` + objective): viết runbook nạp hwtest trên Ubuntu,
  tương tự bản Windows, gồm phân quyền serial và udev. File mới duy nhất:
  `docs/runbook-nap-hwtest-ubuntu.md`. Không sửa file repo khác, không git commit.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`,
  mục NCKH-021 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, `vien-nghien-cuu/NHIP-TIM.md`,
  `firmware/hwtest/README.md`, `firmware/hwtest/hwtest.ino` (154 dòng, toàn bộ),
  `tools/hid_echo.py` + `tools/requirements.txt`, `scripts/build_hwtest.sh`,
  `scripts/build_hwtest.ps1`, `scripts/flash_linux.sh`, `scripts/flash_win.ps1`,
  `docs/03-phan-cung.md`, `docs/04-firmware.md`, `docs/research/02-esp32s3-usb.md`.
- Ghi nhận: bản Windows của NCKH-015 chưa có file trong repo (cùng đợt 2, chưa viết),
  nên runbook Ubuntu bám cấu trúc `firmware/hwtest/README.md` + các script build/flash
  hiện có, đối xứng từng bước "từ cắm cáp đến thấy log", thêm phần Ubuntu riêng
  (nhóm dialout, quy tắc udev, brltty/ModemManager, mô tả output mẫu thay ảnh chụp).
- Trạng thái: todo -> doing (đồng bộ Kanzo cuối việc, xem mục "đồng bộ Kanzo").

## 2026-11-21 02:00 — báo cáo

- Đã làm: tạo file mới duy nhất `docs/runbook-nap-hwtest-ubuntu.md` (225 dòng),
  10 mục: chuẩn bị → xác định cổng → phân quyền serial (dialout) → udev →
  cài đặt board Arduino IDE → nạp dòng lệnh (arduino-cli/PIO) → xem log + thử
  BOOT/LED → HID echo → checklist đạt → bảng xử lý sự cố 12 dòng.
  Không sửa file repo khác, không git commit. Đối xứng bản Windows theo từng bước
  "từ cắm cáp đến thấy log", output mẫu thay ảnh chụp; ghi nhận phát hiện của
  NCKH-003 (cờ `ARDUINO_USB_MODE=0` cho PIO, race `echoPending`) để không rơi.
- Tự kiểm: `git status --short` (repo chưa có commit nào nên mọi thứ hiện `??`,
  xác nhận bằng tay: chỉ tạo đúng 2 file là sổ cái này + runbook, không chạm file
  khác); `(Get-Content docs/runbook-nap-hwtest-ubuntu.md).Count` -> 225 dòng.
  Không build/chạy board (không có phần cứng trong phiên, runbook là tài liệu).
- Trạng thái: doing -> review (đồng bộ Kanzo, xem mục "đồng bộ Kanzo").

## Đồng bộ Kanzo (opportunistic) — HỎNG, Kanzo nghẽn

- `GET /api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s):
  lần 1, lần 2, lần 3 đều HỎNG `500 Internal Server Error`. Dừng đúng giới hạn
  2 lần thử lại, không thử tiếp.
- Không đọc được bảng nên không tìm được thẻ mang mã NCKH-021, không move/comment.
  Thẻ kẹt do lỗi Kanzo, không phải do việc khó — xin đừng gọi oan theo NHIP-TIM.md mục 5.
- Đã tuân thủ "file trước bảng sau": toàn bộ nhật ký nằm ở file này.
  Nhờ Viện trưởng vá giúp: thẻ NCKH-021 todo -> doing -> review kèm nội dung
  mục nhận việc + báo cáo trên.

## Unresolved

1. Bản Windows của NCKH-015 chưa có file trong repo tại thời điểm viết (cùng đợt 2):
   runbook Ubuntu bám `firmware/hwtest/README.md` + script hiện có. Khi bản Windows
   xong, nhờ Viện trưởng đối chiếu chéo 2 bản cho khớp số bước.
2. Chưa kiểm chứng runtime trên board thật và máy Ubuntu thật (không có phần cứng
   trong phiên); VID:PID `303a:1001` trong mẫu udev lấy theo quy ước Espressif,
   runbook đã dặn dùng đúng số `lsusb` in ra.
3. Kanzo: xem mục "đồng bộ Kanzo" — nếu hỏng, nhờ Viện trưởng vá bảng giúp.

## 2026-11-21 02:10 — kiểm chéo thẻ 153 [PQC] Đặc tả két lai X25519+ML-KEM (NCKH-013 Ngô An): ĐẠT

- Vai: NCKH-021 Hứa An, nhóm firmware (khác nhóm PQC của tác giả — đúng yêu
  cầu peer review khác nhóm), lượt KIỂM CHÉO đợt 2A, xét 013.
- Đã đọc toàn bộ: `vien-nghien-cuu/so-cai/NCKH-013.md` (đặc tả bản 0.1),
  `tools/pqc.py` (297 dòng), `tools/vault.py` (152 dòng),
  `vien-nghien-cuu/so-cai/NCKH-007.md` (số đo ML-KEM),
  `vien-nghien-cuu/so-cai/NCKH-001.md` (lưu ý rà soát pqc).
- Nguyên tắc: KHÔNG tin số tác giả tự cộng; kiểm bằng ĐƯỜNG KHÁC
  (tự tính lại + chạy đo độc lập). Mọi lệnh shell đều kèm `shell="pwsh"`.

### 1. Tự cộng lại offset layout ESKVAULT2 (đường khác: script pwsh độc lập)

- Cộng dồn từng trường theo bảng mục 2 của đặc tả:
  9+2+2+16+32+1088+12+48+12 = 1221. KHỚP.
- Overhead = 1221 + 16 (tag thân) = 1237. KHỚP.
- Biên AAD bọc = 9+2+2+16+32+1088 = 1149. KHỚP.
- Biên AAD thân = 1149+12+48+12 = 1221. KHỚP.
- Không khe hở, không chồng lấn giữa 9 trường header (script kiểm từng
  offset khai báo với offset cộng dồn — 0 lệch).
- `len("ESKVAULT1") = len("ESKVAULT2") = 9`. KHỚP (nối tiếp magic).
- `wrapped_dek = 32 DEK + 16 tag = 48`. KHỚP.

### 2. Đối chiếu số đo ML-KEM-768 với FIPS 203 (đường khác: chạy liboqs trực tiếp)

- Tác giả chỉ trích sổ NCKH-007; tôi chạy độc lập liboqs trên máy này
  (`oqs.KeyEncapsulation("ML-KEM-768")`, keygen + encap thật):
  pk=1184, sk=2400, ct=1088, ss=32, `version=FIPS203`,
  `claimed_nist_level=3`. KHỚP TUYỆT ĐỐI đặc tả + NCKH-007 + FIPS 203.
- X25519 kiểm qua thư viện `cryptography` (keygen + DH thật):
  sk=32, pk=32, ss=32. KHỚP RFC 7748 như đặc tả ghi.

### 3. Logic HKDF dual-PRF (đọc chuẩn + thực nghiệm tách nhãn)

- Công thức đặc tả: `KEK = HKDF-SHA256(salt=kdf_salt ngẫu nhiên mỗi lần
  bọc, ikm = len_pref(ss_x)||ss_x || len_pref(ss_m)||ss_m || suite_id ||
  "ESK-HYBRID-v1")`, thứ tự X trước M sau cố định.
- Đánh giá ĐÚNG chuẩn combiner lai (NIST SP 800-56Cr2, nguyên tắc hybrid
  KEM như X-Wing/TLS hybrid design): nối hai shared secret rồi qua KDF
  là bộ trộn dual-PRF — chỉ cần MỘT vế còn bí mật thì KEK vẫn an toàn.
  Length-prefix chống nhập nhằng ranh giới, nhãn miền chống dùng chéo
  ss sang giao thức khác, nhét `suite_id` chống tráo suite, salt ngẫu
  nhiên mỗi lần bọc — đủ 4 lớp phòng thủ.
- Thực nghiệm (HKDF-SHA256 thật): KEK hai vế ≠ KEK một vế
  (`ss còn lại || "ESK-SINGLE-LEG-v1"`) — tách nhãn hiệu quả, hai chế độ
  không bao giờ trùng khóa; cùng input cho cùng KEK (xác định).

### 4. Quy tắc cấm tự hạ cấp (đọc chuẩn hybrid)

- Mặc định HYBRID-BOTH: mất 1 sk mà không dự phòng thì KHÔNG MỞ — đúng
  chủ ý (két 2 vế mở được bằng 1 vế thì vế còn lại vô nghĩa).
- Gãy cài đặt (thiếu liboqs): KHÔNG tự hạ sang một vế; muốn mở một vế
  phải gõ cờ tường minh `--cho-phep-mo-mot-ve=X|M` + cảnh báo đỏ + ghi
  nhật ký + bọc lại ngay, chỉ dùng cứu hộ. ĐÚNG chuẩn: không downgrade
  thầm lặng, mọi hạ cấp đều tường minh và có dấu vết kiểm toán.
- Cấm "bỏ vế cho gọn" không đổi version/suite_id + log di chuyển — đúng
  nguyên tắc agility có kiểm soát.

### 5. Kiểm bổ trợ (AAD, tương thích, oracle)

- AAD bọc phủ bytes[0..1149): gồm magic, version, suite_id, kdf_salt,
  eph_x_pk, mlkem_ct — không sót trường nào trước wrap_nonce; AAD thân
  phủ bytes[0..1221): gồm cả wrapped_dek — không trường nào trước
  body_ct nằm ngoài xác thực. ĐÚNG, chống tráo đầu/cắt ghép.
- Tương thích một chiều: CHẠY THẬT `vault.decrypt_bytes` với blob magic
  `ESKVAULT2` → két cũ từ chối "sai magic" đúng như đặc tả mục 0.4
  (script `$env:TEMP\NCKH-021-xet013-magic.py`, ngoài repo).
- Giữ ngữ nghĩa từ chối ngầm ML-KEM, thông điệp lỗi chung "sai khóa hoặc
  két bị sửa" chống oracle phân biệt + cờ `--chan-doan-ve` tường minh —
  ĐÚNG thực hành tốt; kiểm điểm bậc thấp X25519 theo RFC 7748 — ĐÚNG.

### 6. Ghi nhận nhỏ (KHÔNG chặn ĐẠT, đề nghị chốt ở bản 0.2 trước khi code)

- G1. `len_pref` chưa chốt độ rộng/endian (mục 1 nói LE chung nhưng chưa
  ghi `len_pref` là u16 LE hay u32 LE) — cần chốt 1 dòng.
- G2. Mã hóa `suite_id` trong IKM chưa chốt độ rộng (nên ghi rõ u16 LE
  như trong header).
- G3. Bước mở 1 "đọc tối thiểu 1221 byte" trong khi file hợp lệ tối thiểu
  là 1237 (thân rỗng + tag 16) — nên chốt ngưỡng 1237 hoặc ghi rõ bước 9
  xử lý thân cụt thế nào.
- G4. Salt HKDF 16 byte là chấp nhận được (salt ngẫu nhiên khác rỗng),
  có thể cân nhắc 32 byte cho tròn hàm băm — tùy hội đồng, không bắt buộc.

### 7. Kết luận kiểm định

- [KIEM-DINH] ĐẠT: đặc tả đúng số (offset, ML-KEM, X25519), đúng chuẩn
  (combiner dual-PRF, cấm tự hạ cấp, AAD phủ kín, tương thích một chiều),
  trung thực về unresolved (U1-U5) và bài học NCKH-001. 4 ghi nhận G1-G4
  là siết chặt văn bản, không phải lỗi mật mã — chuyển cho tác giả/hội
  đồng chốt ở bản 0.2 trước khi mở thẻ code.
- Trạng thái thẻ: review -> done (đẩy opportunistic; xem mục Kanzo dưới).
- Unresolved lượt kiểm chéo: không có (ngoài G1-G4 đã giao lại).

### 8. Đồng bộ Kanzo thẻ 153 (opportunistic, Kanzo nghẽn — HỎNG)

- `GET /api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s):
  lần 1 HTTP 500, lần 2 HTTP 500, lần 3 trả về nhưng không thấy thẻ
  NCKH-013 (nghi parse rỗng lúc Kanzo chập chờn, không đáng tin).
- Liệt kê toàn bộ thẻ (2 lần): 1 lần lỗi cú pháp Select-Object của tôi
  (không tính), 1 lần HTTP 500; xem JSON thô 1 lần: HTTP 500.
- `GET /api/tasks/153` trực tiếp (id theo sổ NCKH-013): HTTP 500.
- Đã hết hạn 2 lần thử lại cho từng lệnh cần thiết; KHÔNG comment/move
  được gì. Nhờ Viện trưởng vá giúp khi Kanzo khỏe: gắn comment
  "[KIEM-DINH] ĐẠT — đặc tả đúng số (offset 1221/overhead 1237/AAD
  1149/1221, ML-KEM-768 khớp FIPS 203 qua đo độc lập), combiner HKDF
  dual-PRF đúng chuẩn, cấm tự hạ cấp đúng, 4 ghi nhận văn bản G1-G4 chốt
  ở bản 0.2 (xem sổ NCKH-021)" + chuyển thẻ 153 -> done.
  Sổ cái file này là nguồn sự thật cho lượt kiểm chéo.
- Cam kết repo: chỉ nối thêm file sổ này; không sửa code/docs; không git
  commit; script kiểm ở `$env:TEMP`; mọi lệnh shell đều kèm `shell="pwsh"`.
