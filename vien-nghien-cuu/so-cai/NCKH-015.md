# Sổ cái NCKH-015 (Lý An, nhóm firmware, đợt 2A)

## 2026-11-21 01:53 — nhận việc

- Thẻ: [firmware] Runbook nạp hwtest Windows (mã NCKH-015, Kanzo id tra sau ở mục đồng bộ)
- Việc nhận (theo `phan-cong.json` + objective): viết runbook nạp hwtest trên Windows,
  từng bước có mô tả ảnh chụp, từ cắm cáp đến thấy log.
  Thành FILE MỚI `docs/runbook-nap-hwtest-windows.md`.
  Chỉ được tạo đúng 1 file mới này, không sửa file repo khác, không git commit.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`,
  mục NCKH-015 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, `vien-nghien-cuu/NHIP-TIM.md`,
  `firmware/hwtest/README.md`, `firmware/hwtest/hwtest.ino` (154 dòng, toàn bộ),
  `tools/hid_echo.py` (đối chiếu), `docs/04-firmware.md`, `docs/03-phan-cung.md`.
- Trạng thái: todo -> doing.

## 2026-11-21 01:56 — báo cáo

- Đã làm: viết xong `docs/runbook-nap-hwtest-windows.md` (252 dòng, 10468 byte),
  gồm 15 mục: chuẩn bị + phân biệt 2 cổng USB, cắm cáp, kiểm tra COM trong
  Device Manager, cài Arduino IDE + core ESP32, mở sketch, chọn board
  ESP32S3 Dev Module, bật USB CDC On Boot, đặt USB Mode OTG, chọn COM,
  nạp + xử lý kẹt Connecting (giữ BOOT), đọc log Serial Monitor 115200
  (kèm log mẫu copy từ `hwtest.ino`), thử nút BOOT/LED, kiểm tra HID echo
  qua cổng native + `python tools/hid_echo.py`, checklist đạt, đường thay thế
  PlatformIO. Mỗi bước có mục "Ảnh chụp mong đợi" mô tả chi tiết ảnh cần chụp.
- Tự kiểm: `(Get-Content docs/runbook-nap-hwtest-windows.md).Count` -> 252;
  `Length` -> 10468; nội dung log mẫu đối chiếu từng dòng với `hwtest.ino`
  (printChipInfo, HID echo, BOOT nhan/nha, Heartbeat) và `hid_echo.py`
  (60 byte, thông điệp thành công); không sửa file repo khác, không git commit.
- Trạng thái: doing -> review.

## Đồng bộ Kanzo (thẻ id 155)

- GET board: thấy thẻ `[firmware] Runbook nạp hwtest Windows (NCKH-015)`, id 155,
  trạng thái `todo`. Mỗi lệnh timeout 30s, cách nhau 5s, tối đa 3 lần thử.
- POST move `todo->doing`: OK ngay lần 1.
- POST move `doing->review`: OK ngay lần 1.
- POST comment báo cáo: HỎNG cả 3 lần, `500 Internal Server Error`.
  Dừng đúng giới hạn, không thử tiếp.
- Đối chiếu: GET board lần 1 hỏng `database is locked` (lỗi SQLite đã biết);
  GET lần 2 (sau 10s) OK, xác nhận thẻ 155 đang ở `review`, chưa có comment nào.
- Đã tuân thủ "file trước bảng sau": toàn bộ nhật ký nằm ở file này.
  Nhờ Viện trưởng vá giúp comment báo cáo lên thẻ 155 (nội dung như mục báo cáo
  trên). Thẻ kẹt thiếu comment do lỗi Kanzo, không phải do việc khó —
  xin đừng gọi oan theo luật NHIP-TIM.md mục 5.

## Unresolved

1. Comment báo cáo chưa lên được thẻ Kanzo 155 (POST comments 500 x3).
   Cần Viện trưởng/nhịp tim vá giúp; nội dung comment ở mục "Đồng bộ Kanzo".
2. Runbook chưa được kiểm chứng runtime trên board thật (không có phần cứng
   trong phiên này); log mẫu lấy từ code `hwtest.ino`, cần người có board
   chạy theo từng bước và chụp ảnh thật bổ sung.
3. Ghi chú phạm vi file: objective giới hạn "chỉ tạo đúng 1 file mới" nhưng đồng
   thời yêu cầu "ghi sổ NCKH-015.md TRƯỚC" trong khi file sổ chưa tồn tại.
   Đã tạo 2 file: `vien-nghien-cuu/so-cai/NCKH-015.md` (sổ cái bắt buộc theo
   Hiến chương §2/NHIP-TIM) + `docs/runbook-nap-hwtest-windows.md` (deliverable).
   Không sửa file repo nào khác, không git commit.

## 2026-11-21 02:05 — kiểm chéo NCKH-023 Chu An (đợt 2A, REPO CHỈ ĐỌC)

- Vai: Lý An NCKH-015, kiểm độc lập báo cáo "Rà soát chính tả toàn repo"
  của Chu An NCKH-023 (6 lỗi A1-A6 + 45 nhóm B7-B51 + mục C1-C9).
- Tài liệu đã đọc: `vien-nghien-cuu/so-cai/NCKH-023.md` (toàn bộ, 263 dòng).
- Phương pháp (đường khác với tác giả): tác giả dùng `muse.search` regex;
  tôi mở trực tiếp từng file:dòng bằng `muse.read_file` và kiểm filesystem
  bằng `pwsh` (`Test-Path`, `Get-ChildItem`). Mọi lệnh shell đều kèm `shell='pwsh'`.

### Mẫu đã xác minh (10/51 mục, gồm cả 3 mục nặng) — 10/10 ĐÚNG

1. B44 (nặng, SAI ĐƯỜNG DẪN): `docs/runbook-nap-hwtest-windows.md:202` và
   `:228` ghi `pip install -r requirements.txt` — mở file thấy đúng cả 2 chỗ.
   `Test-Path 'requirements.txt'` gốc = False; `Test-Path
   'tools/requirements.txt'` = True; `tools/` có requirements.txt.
   Runbook Ubuntu `:184` và `:225` ghi đúng `tools/requirements.txt` — ĐÚNG,
   phát hiện có giá trị nhất báo cáo (lỗi chạy thật, không chỉ chính tả).
2. B43 (nặng, LẠC HẬU): `docs/03-phan-cung.md:5-7` vẫn viết "module được ghi
   là N26R8... Khả năng cao là N16R8 bị ghi nhầm" + "Việc cần làm trước khi
   flash", trong khi `hardware/BOM.md:5,19-26` đã chốt N16R8 (2026-11-21,
   NCKH-027) — ĐÚNG, 03 lạc hậu thật.
3. A4 (nặng, câu rối): `docs/06-bao-mat.md:49` có nguyên văn "có thể hết pin
   dự phòng suy nghĩ, quên PIN hoặc lỗi flash mới phát hiện" — ĐÚNG, chữ
   "suy nghĩ" lạc giữa cụm danh từ thật.
4. A1: `docs/research/02-esp32s3-usb.md:19` có "Harware CDC and JTAG" — ĐÚNG.
5. A5: `docs/07-sao-luu-va-khoi-phuc.md:120` có "nếu muốn chống cháy nước" —
   ĐÚNG (số dòng vẫn khớp dù file từng tăng dòng).
6. B15: `docs/research/01-giao-thuc-fido.md:21` có "ClientPin đặt và xác minh
   PIN" — ĐÚNG, phải là ClientPIN.
7. B14: `docs/research/03-du-an-lien-quan.md:12` có "khung U2FHID" — ĐÚNG.
8. A2: `docs/runbook-nap-hwtest-windows.md:66` có "Additional Board Manager
   URLs" (thiếu s), dòng 67 "Boards Manager" — ĐÚNG.
9. B19: `docs/05-huong-dan-su-dung.md:9` có "Bluetooth và devices" — ĐÚNG.
10. B47: `vien-nghien-cuu/HIEN-CHUONG.md:22` có "peer review" giữa văn bản
    Việt — ĐÚNG.
- Kiểm thêm (ngoài mẫu): B21 (`RESET` ở runbook Windows 138/146/176 vs `RST`
  ở `hardware/wiring.md:20`) ĐÚNG; A6 runbook Ubuntu "Liệt kê cổng chắc chắn
  thuộc về board" ĐÚNG cụm chữ nhưng số dòng thực tế là :29, báo cáo ghi :30
  (lệch 1, chấp nhận được do file trôi dòng — tác giả đã cảnh báo nhiễu đồng
  thời ở mục phạm vi).

### Kết luận kiểm định: ĐẠT

- `[KIEM-DINH] đạt` — 10/10 mục mẫu có lỗi thật đúng như mô tả, gồm cả 3 mục
  nặng; đề xuất sửa hợp lý; phạm vi quét trung thực (ghi rõ file nào đọc/toàn bộ/60
  dòng, file nào bỏ qua, cảnh báo trôi dòng). Sai lệch duy nhất là A6 lệch
  1 dòng, không ảnh hưởng kết luận.
- Không yêu cầu sửa lại báo cáo. Đề nghị follow-up: nhóm trưởng tailieu
  (NCKH-005) chốt chuẩn từng nhóm B rồi mở thẻ sửa riêng (đúng đề xuất của
  tác giả ở Unresolved 2).

### Đồng bộ Kanzo: KHÔNG CÓ THẺ NCKH-023, không comment/move được

- GET board lần 1 (parse sai key): trả rỗng, không kết luận được.
- GET board lần 2 (sau 5s): OK, JSON đầy đủ, project esp32-securitykey có
  27 tasks (id 138-150 đợt 1 done + 153-167 đợt 2A/FIX), KHÔNG có thẻ nào
  chứa "022"/"023" — khớp độc lập với phát hiện của tác giả.
- GET lọc 022/023 lần 3 (sau 5s): HTTP 500. Thử lại lần 4 (sau 5s): HTTP 500.
  Dừng đúng giới hạn tối đa 2 thử lại. Mọi lệnh timeout 30s, cách nhau 5s.
- Kết luận: không có thẻ để comment `[KIEM-DINH]` hay move review->done.
  Không tự tạo thẻ (tránh trùng khi Viện trưởng tạo chính thức).
- Nhờ Viện trưởng: tạo thẻ "[tailieu] Rà soát chính tả toàn repo (NCKH-023)",
  vá todo->doing->review->done + gắn báo cáo trong sổ NCKH-023 và kết luận
  kiểm định đạt trong mục này. Sổ cái file là nguồn sự thật duy nhất.
- Không sửa file repo nào ngoài chính sổ cái này; không git commit.

## Unresolved (bổ sung kiểm chéo)

4. Thẻ Kanzo NCKH-023 chưa tồn tại nên comment `[KIEM-DINH] đạt` và move
   review->done chưa thực hiện được — cần Viện trưởng tạo thẻ và vá trạng thái.
5. Kết luận đạt dựa trên mẫu 10/51 mục (19,6%), không phải toàn bộ 51 mục;
   Viện trưởng muốn chắc tuyệt đối thì giao thêm 1 lượt kiểm mẫu khác.

## 2026-11-21 02:09 — sửa runbook theo kết luận kiểm chéo KHÔNG ĐẠT (thẻ 155 về doing)

- Việc nhận: sửa đúng 1 file `docs/runbook-nap-hwtest-windows.md`, đúng 3 điểm
  theo kết luận kiểm chéo. Đã đọc file trước khi sửa, đọc lại từng đoạn sau sửa.
  Không sửa file repo khác, không git commit. Mọi lệnh shell kèm `shell='pwsh'`.
- Điểm 1 (dòng 202 và 228): `pip install -r requirements.txt`
  -> `pip install -r tools/requirements.txt`. Kiểm chứng: `Test-Path
  'requirements.txt'` ở gốc repo = False; `Test-Path 'tools/requirements.txt'`
  = True; `tools/` có requirements.txt. Lệnh cũ chạy ở gốc repo sẽ lỗi
  "không thấy file".
- Điểm 2 (dòng 5): link chữ `firmware/hwtest/README.md` nhưng đích trỏ nhầm
  `../firmware/hwtest/hwtest.ino` -> sửa đích về `../firmware/hwtest/README.md`.
- Điểm 3 (dòng 25, 29, 113): "bước 11" -> "mục 12" cho HID echo (mục 11 là thử
  nút BOOT/LED, mục 12 mới là kiểm tra HID echo).
- Xác minh sau sửa (đọc lại): dòng 5 đích README.md; dòng 25 "(mục 12)";
  dòng 29 "để dành cho mục 12"; dòng 113 "mục 12 sẽ thất bại";
  dòng 202 `pip install -r tools/requirements.txt`; dòng 228
  "chạy lại `pip install -r tools/requirements.txt`". Đủ 6 vị trí.

### Đồng bộ Kanzo (thẻ id 155, doing->review + comment): THÀNH CÔNG

- `POST /api/tasks/155/move {"status":"review"}`: OK ngay lần 1, server trả
  `status: review` (thẻ "[firmware] Runbook nạp hwtest Windows (NCKH-015)").
- `POST /api/tasks/155/comments` (liệt kê 3 chỗ sửa): OK ngay lần 1,
  comment id 35, task_id 155, author me.
- Mỗi lệnh timeout 30s, cách nhau 5s, shell pwsh — đúng luật, chưa cần thử lại.
- `GET /api/board?project=esp32-securitykey` đối chiếu: HỎNG 500
  (Internal Server Error, lỗi Kanzo đã biết). Tin move + comment đã ghi vì
  server trả OK rõ ràng (không phải timeout mập mờ). Đã ghi sổ trước khi
  chạm Kanzo ("file trước bảng sau").
- Nội dung comment: "[SUA-RUNBOOK] Ly An NCKH-015 da sua 3 diem theo ket luan
  kiem cheo KHONG DAT: (1) dong 202+228 ... tools/requirements.txt;
  (2) dong 5 ... README.md; (3) dong 25+29+113 ... muc 12 cho HID echo.
  Chi tiet trong vien-nghien-cuu/so-cai/NCKH-015.md."

## Unresolved (bổ sung sau sửa)

6. ĐÃ XONG: move doing->review + comment liệt kê 3 chỗ sửa lên thẻ 155
   (comment id 35). Chỉ còn GET board đối chiếu hỏng 500 — nhờ nhịp tim/
   Viện trưởng xác nhận lại trạng thái thẻ khi Kanzo khỏe.
7. Runbook vẫn chưa được kiểm chứng runtime trên board thật (kế thừa mục 2).
