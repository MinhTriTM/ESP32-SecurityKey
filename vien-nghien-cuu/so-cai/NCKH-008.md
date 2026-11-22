# Sổ cái NCKH-008 — Võ An, nhóm ML, thành viên Viện, đợt 1

> Ghi chú tên (ĐÃ CHỐT): lệnh giao việc ban đầu ghi "Võ Hạnh (NCKH-008)" nhưng
> Viện trưởng đã đính chính: tên chính thức theo `phan-cong.json` là "Võ An",
> mã NCKH-008 giữ nguyên. Từ mục này trở đi dùng đúng tên Võ An.

## 2026-11-21 01:29 — nhận việc
- Thẻ: [ML] Tăng mẫu lên 50k ở R=7 (Kanzo id 147)
- Trạng thái: todo -> doing (thử opportunistic sau; Kanzo đang nghẽn)
- Việc nhận: chạy `tools/ml_distinguisher.py` với 50k mẫu ở R=7, seed cố định
  để tái hiện; ghi accuracy và thời gian; báo cáo TRUNG THỰC kể cả không vượt 0.5.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0),
  mục NCKH-008 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, toàn bộ `tools/ml_distinguisher.py`,
  sổ cái NCKH-002 (nhóm trưởng ML, để đối chiếu baseline).
- Baseline đã biết: tài liệu ghi R=7 → 0.5070 với 6k mẫu train (theo sổ NCKH-002);
  nhiệm vụ của tôi kiểm tra 50k mẫu có vượt 0.5 rõ ràng không.
- Môi trường: Windows, Python 3.12.0, numpy 2.5.4 (đã kiểm bằng lệnh).
- Lưu ý shell: `powershell` (5.1) không có trên máy (`program not found`),
  dùng `pwsh` thay thế cho mọi lệnh.
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; file tạm chỉ trong `$env:TEMP`.

## 2026-11-21 01:32 — báo cáo (KẾT QUẢ ÂM TÍNH, trung thực)
- Lệnh chạy (giữ nguyên mọi mặc định, chỉ tăng mẫu, seed cố định để tái hiện):
  `python tools/ml_distinguisher.py --rounds 7 --samples 50000 --seed 1337`
  (test-samples=2000, epochs=5, batch=256 theo mặc định của tool)
- Output lần 1:
  `Cau hinh: rounds=[7] samples=50000 test=2000 epochs=5 seed=1337`
  `R=7: train=50000 test=2000 epochs=5 -> accuracy=0.4970 (2.9s)`
  `Tom tat: R=7: 0.4970`
  Wall-clock lần 1 (lần chạy đo riêng bằng Measure-Command, output bị nuốt nên
  chạy lại để lấy số): 4.76s; wall-clock lần lấy số: 3.81s.
- Output lần 2 (kiểm tra tái hiện, cùng lệnh, cùng seed): `accuracy=0.4970 (3.8s)`
  → seed cố định cho kết quả tái hiện bit-identical về accuracy.
- KẾT LUẬN: 50k mẫu ở R=7 KHÔNG vượt 0.5 — accuracy 0.4970, tức ngang/thấp hơn
  đoán mò. So với baseline tài liệu (6k mẫu, R=7 → 0.5070): tăng mẫu gấp ~8 lần
  không giúp distinguisher MLP học được gì ở R=7; cả hai số đều nằm trong nhiễu
  quanh 0.5 với test 2000 mẫu (độ lệch chuẩn ~0.011).
- Đã làm: đọc tool, chạy 3 lần (1 lần đo + 2 lần lấy số/xác nhận), ghi sổ.
- Tự kiểm: exit code 0 cả 3 lần; 2 lần lấy số cho cùng accuracy → tái hiện đạt.
- Trạng thái: doing -> review (thử opportunistic sau; Kanzo đang nghẽn)
- Unresolved: (1) [ĐÃ XONG — Viện trưởng chốt tên Võ An] ;
  (2) chưa rõ tăng epoch/batch hay đổi kiến trúc có giúp R=7 không — ngoài phạm
  vi thẻ này (thẻ chỉ hỏi tăng mẫu), đề xuất cho nhóm ML cân nhắc.

## 2026-11-21 01:36 — đồng bộ Kanzo (thẻ id 147, opportunistic)
- Move todo -> doing: THẤT BẠI sau 3 lần thử (500 Internal Server Error cả 3).
- Comment [BAO-CAO] lần 1: THẤT BẠI sau 3 lần thử (500, 500, timeout 30s).
- Move -> review: THÀNH CÔNG ở lần thử 2 (lần 1 lỗi 500). Trạng thái trả về: review.
- GET /api/board đối chiếu: thẻ 147 = status review, comments = 1.
- Comment [BAO-CAO] lần 2 (dùng tên Võ An): THÀNH CÔNG ngay lần 1 (comment id 9).
  Nội dung: lệnh, accuracy=0.4970, kết luận âm tính, tái hiện đạt, trỏ về sổ cái này.
- Mỗi lệnh API cách nhau ≥5s, timeout 30s, đúng luật opportunistic.
- Kết quả cuối trên bảng: thẻ 147 ở cột review, có comment báo cáo → chờ NCKH-001
  kiểm chéo (người kiểm ghi trên thẻ: NCKH-001, khác nhóm).

## 2026-11-21 01:40 — kiểm chéo thẻ 140 của NCKH-003 (Võ An, lượt kiểm đợt 1)
- Thẻ: [firmware] Rà soát hwtest.ino (Kanzo id 140), tác giả NCKH-003 Lê An.
- Phạm vi: xác nhận/từ chối từng phát hiện trong `vien-nghien-cuu/so-cai/NCKH-003.md`
  (race echoPending P1, SendReport nuốt lỗi P1, các P2/P3) bằng đường độc lập:
  tự đọc toàn bộ `firmware/hwtest/hwtest.ino` (154 dòng) + đối chiếu
  `tools/hid_echo.py` + `firmware/hwtest/README.md`, trích dòng code cụ thể.
  Soi thêm từ góc khác: vòng đời USB, tràn số, macro guard.
- Chế độ: REPO CHỈ ĐỌC — không sửa firmware, chỉ nối thêm sổ cái này.

### Xác nhận từng phát hiện của tác giả (XÁC NHẬN toàn bộ, không false positive)
1. P1 race `echoPending` (dòng 36, 53-61, 146-147): XÁC NHẬN. `volatile bool`
   dòng 36 không làm cặp đọc-dòng-146/xóa-dòng-147 thành nguyên tử; kịch bản A
   (OUT mới xen giữa → mất echo) và B (OUT sau xóa cờ → `SendReport` dòng 148
   đọc `echoBuf` đang bị `memcpy` dòng 56 ghi dở + gửi trùng vòng sau) đều tái
   hiện được bằng lập luận xen kẽ. Coalescing theo chu kỳ `delay(20)` dòng 153:
   đúng. Bổ sung làm chắc: `echoBuf` dòng 35 còn không `volatile`, và trên
   ESP32-S3 dual-core `volatile` không thay critical section — đề xuất
   portMUX/double-buffer của tác giả đúng hướng.
2. P1 `SendReport` nuốt lỗi (dòng 146-151): XÁC NHẬN. Cờ xóa dòng 147 TRƯỚC khi
   gửi dòng 148; `if (SendReport) { println }` không nhánh else → false là mất
   frame không dấu vết. Đề xuất retry + log: hợp lý.
3. P2 bỏ qua `report_id` (dòng 53-54): XÁC NHẬN, vô hại hiện tại. Descriptor chỉ
   định nghĩa ID 1 (dòng 19 `0x85,0x01`); tool gửi ID 1 (`hid_echo.py` dòng 26).
4. P2 nút BOOT thiếu debounce (dòng 129-138): XÁC NHẬN. Cạnh + `INPUT_PULLUP` +
   LOW đúng (dòng 108, 130-138); chống dội chỉ nhờ lấy mẫu/`delay(20)` một cách
   tình cờ. Tác động thấp (test thủ công).
5. P2 `_onGetDescriptor` memcpy không kiểm tra đích (dòng 48-51): XÁC NHẬN ở mức
   ghi nhận, nhưng rủi ro THẤP HƠN cả tác giả nói — kiểm từ góc vòng đời USB:
   buffer do stack cấp theo đúng len đã đăng ký `HID.addDevice(this, sizeof(...))`
   dòng 44 (= 36), callback chép đúng `sizeof` dòng 49, hai đầu cùng một hằng số
   nên khớp theo cấu trúc; wLength của host do tầng thấp xử lý, không vào đây.
   Giữ như defense-in-depth, không nâng severity.
6. Descriptor ĐÚNG + khớp tool: XÁC NHẬN ĐỘC LẬP (tự đếm lại từng byte).
   Tổng 3+2+2+2+2+2+3+2+2+2+2+2+3+2+2+2+1 = 36 byte, khớp `sizeof` dùng ở dòng
   44, 49-50. Usage Page 0xFF00 (LE) ✓; Report ID 1 khớp `REPORT_ID = 1`
   (hid_echo.py dòng 18) ✓; Size 8 × Count 64 = 64 byte khớp `REPORT_LEN = 64`
   (dòng 19) ✓; Input `81 02`/Output `91 02` đối xứng, `C0` kết thúc ✓.
   IN/OUT chung ID 1 hợp lệ. Tool pad `ljust(64)` + firmware zero-pad dòng 57-59
   + so 60 byte đầu: nhất quán. OUT > 64 bị cắt dòng 55 — "không tràn echoBuf":
   XÁC NHẬN (clamp + `memset` bù, `sizeof - n` an toàn vì n ≤ 64).
7. Nút/LED/heartbeat/khởi tạo USB: XÁC NHẬN, trừ 1 điểm LED tác giả bỏ sót (M1
   dưới). Heartbeat `millis() - lastPrint > 5000` unsigned-safe ✓ (dòng 140);
   `while (!Serial && ... < 3000)` không treo ✓ (dòng 115); thứ tự
   addDevice → `HID.begin()` → `USB.begin()` ✓ (dòng 44, 120-121); `HID` dòng 11
   khai báo trước `echoDev` dòng 64 nên không dính static-init-order fiasco ✓
   (kiểm từ góc vòng đời); echo ≤ ~20ms trong timeout 2000ms của tool ✓.
8. P3 góp ý nhỏ: XÁC NHẬN cả 4 điểm. (a) LED không phản hồi echo, chỉ Serial
   dòng 149: đúng. (b) `%d` cho `uint32_t` (heap dòng 142): đúng, nên `%u`, vô
   hại thực tế — MỞ RỘNG: cùng mẫu còn ở dòng 86 (`getCpuFreqMHz`), 87-88
   (Flash/PSRAM), tác giả chỉ nêu heap. (c) `static bool initialized` làm
   instance thứ hai chết lặng (dòng 41-46): đúng, vô hại (1 instance).
   (d) README thiếu cờ PIO cho echo: đúng — `README.md` dòng 18 chỉ nêu
   `ARDUINO_USB_CDC_ON_BOOT` + "bật TinyUSB OTG trong sdkconfig" mơ hồ.

### Lỗi tác giả bỏ sót (góc nhìn khác, toàn P3/P4 — không đổi kết luận)
- M1 (P3, LED/nhánh digital, dòng 97-105 + 126 + 133-136): `setLed` nhánh
  `LED_BUILTIN` dòng 101 quy mọi màu khác đen về HIGH. Idle gọi
  `setLed(0,32,0)` → HIGH, nhấn gọi `setLed(0,0,64)` → HIGH: trên board KHÔNG có
  `RGB_BUILTIN`, LED không bao giờ đổi theo nút, mất phản hồi BOOT mà README
  dòng 26 hứa. Tác giả chỉ kiểm `pinMode` đúng nhánh mà chưa kiểm giá trị logic.
  Sửa: nhánh digital idle LOW / nhấn HIGH. Tác động thấp (S3 DevKit thường có RGB).
- M2 (P3, macro guard, dòng 8/119/145 + 124): khi `ARDUINO_USB_MODE` undefined
  (cấu hình PIO tối thiểu), cả 3 guard lặng lẽ loại HID khỏi bản build, chỉ còn
  log runtime "TAT" dòng 124 — không có cảnh báo lúc biên dịch, người dùng tưởng
  đã bật echo. Tác giả nêu thiếu cờ ở README nhưng chưa gắn đây là thiếu
  diagnostic trong code. Đề xuất: `#warning` khi macro undefined.
- M3 (P4/info, vòng đời USB): `echoPending`/`echoBuf` sống qua USB
  disconnect/re-enumerate — frame bắt trước khi ngắt sẽ echo sau khi nối lại mà
  không kiểm tra freshness; tool có thể nhận frame cũ. Rất thấp với hwtest.
- M4 (không tính lỗi mới): `echoBuf` non-volatile + torn-read là nửa còn lại của
  P1 race; bản vá copy-dưới-khóa tác giả đề xuất đã bao hàm. Chỉ ghi rõ phạm vi P1.

### Kết luận kiểm chéo: ĐẠT
- Mọi P1/P2/P3 của tác giả được xác nhận bằng đọc độc lập + trích dòng; không có
  phóng đại severity (P2-descriptor thậm chí còn an toàn hơn tác giả nói); các
  điểm bỏ sót chỉ P3/P4. Đồng ý đề xuất của tác giả: mở thẻ follow-up gom 2 P1
  (race, nuốt lỗi) + M1/M2.
- Trạng thái đề nghị: review -> done (thẻ 140). Do thẻ còn kẹt `todo` trên bảng
  (tác giả shell hỏng, chưa đẩy được — xem sổ NCKH-003 mục "đồng bộ Kanzo"),
  lượt này sẽ comment [KIEM-DINH] và chuyển thẳng sang done kèm lý do cả hai
  chặng (làm + kiểm) đều đã xong trong file.

## 2026-11-21 01:42 — đồng bộ Kanzo (thẻ id 140, opportunistic)
- Đầu đọc `GET /api/board`: thẻ 140 = status todo, comments 0 (tác giả chưa đẩy
  được do shell hỏng, khớp sổ NCKH-003). `GET /api/tasks/140` → 500;
  `GET .../comments` → 405 (route tồn tại, sai method); `GET /api` → 404.
- Comment [KIEM-DINH] (`POST /api/tasks/140/comments`): lần 1 timeout 30s,
  lần 2 lỗi 500, lần 3 lỗi 500 — dừng đúng giới hạn 2 lần thử lại. Tuy nhiên
  bảng sau đó báo comments = 1: một trong các lần thử đã ghi được phía server
  dù client nhận timeout/500 (ghi nhận, không phán đoán lần nào).
- Move sang done (`PATCH /api/tasks/140 {"status":"done"}`): lần 1 lỗi 500,
  lần 2 THÀNH CÔNG — status trả về: done. Chuyển thẳng todo -> done (thay vì
  review -> done như lệnh) vì thẻ kẹt todo từ đầu; lý do đã nằm trong comment:
  cả hai chặng (tác giả làm + kiểm chéo) đều xong trong file.
- Đối chiếu `GET /api/board?project=esp32-securitykey`: thẻ 140 = status done,
  comments = 1. Mỗi lệnh cách nhau ≥5s, timeout 30s, đúng luật opportunistic.
- Kết quả cuối: thẻ 140 done + comment kiểm định → lượt kiểm chéo hoàn tất.

## Unresolved (lượt kiểm chéo thẻ 140)
1. Chưa kiểm runtime trên board thật (không có phần cứng trong phiên này);
   kịch bản race A/B vẫn là phân tích tĩnh — cần NCKH-012/NCKH-016 bắn OUT dồn
   dập để xác nhận (kế thừa unresolved-4 của NCKH-003).
2. Race `echoPending`, nuốt lỗi SendReport, M1 (LED digital), M2 (`#warning`
   macro): mới ở mức đề xuất, chưa có bản vá (cả hai lượt đều chỉ đọc). Đề nghị
   mở thẻ follow-up cho nhóm firmware (đồng ý unresolved-3 của NCKH-003).
3. Lệch tên tác giả ("Lê Cường" vs "Lê An", unresolved-1 của NCKH-003): ngoài
   phạm vi kiểm chéo, để Viện trưởng chốt.
4. Comment Kanzo nào trong 3 lần thử đã lọt qua server không xác định được từ
   phía client (timeout/500 nhưng comments = 1); nội dung 3 lần thử tương đương
   nhau (rút gọn dần), không ảnh hưởng kết luận.
