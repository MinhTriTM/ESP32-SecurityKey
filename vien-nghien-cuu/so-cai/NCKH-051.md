# Sổ cái NCKH-051 (Nguyễn Cường, nhóm firmware, đợt 2C)

## 2026-11-21 03:09 — nhận việc

- Thẻ: [firmware] Checklist bring-up board mới (mã NCKH-051, Kanzo id tra sau ở mục đồng bộ)
- Việc nhận (theo `phan-cong.json` + objective): viết checklist bring-up board mới
  từ mở hộp đến echo ok, dạng ô đánh dấu, gom từ 2 runbook + README hwtest.
  Thành FILE MỚI `docs/checklist-bring-up-board.md`.
  Chỉ được tạo đúng 1 file mới này (ngoài sổ cái bắt buộc), không git commit.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (toàn bộ),
  mục NCKH-051 trong `vien-nghien-cuu/phan-cong.json`
  (Nguyễn Cường, firmware, thành viên, đợt 2, "Checklist bring-up board mới —
  Từ mở hộp đến echo ok, dạng checklist đánh dấu"),
  `vien-nghien-cuu/so-cai/README.md` (toàn bộ),
  `firmware/hwtest/README.md` (toàn bộ, 27 dòng),
  `docs/runbook-nap-hwtest-windows.md` (toàn bộ, 252 dòng, của NCKH-015),
  `docs/runbook-nap-hwtest-ubuntu.md` (toàn bộ, 225 dòng).
  Đọc thêm `vien-nghien-cuu/so-cai/NCKH-015.md` để theo đúng mẫu sổ cái.
- Ghi chú phạm vi file: objective giới hạn "chỉ tạo đúng 1 file mới" nhưng đồng
  thời yêu cầu "ghi sổ NCKH-051.md TRƯỚC" trong khi file sổ chưa tồn tại
  (`Test-Path` = False). Làm theo tiền lệ NCKH-015: tạo 2 file gồm
  `vien-nghien-cuu/so-cai/NCKH-051.md` (sổ cái bắt buộc theo Hiến chương §2,
  "file trước bảng sau") + `docs/checklist-bring-up-board.md` (deliverable).
  Không sửa file repo nào khác, không git commit. Mọi lệnh shell kèm `shell='pwsh'`.
- Trạng thái: todo -> doing.

## 2026-11-21 03:10 — báo cáo

- Đã làm: viết xong `docs/checklist-bring-up-board.md` (163 dòng, 11034 byte,
  47 ô `- [ ]`), gồm 11 giai đoạn đánh số 0–10 + phụ lục xử lý sự cố:
  mở hộp/kiểm tra vật lý + đối chiếu BOM, phân biệt 2 cổng USB, cài phần mềm
  (IDE + core / arduino-cli / PIO + Python), cắm cáp lần đầu và xác định cổng
  (nhánh W: Device Manager; nhánh U: dmesg/ls/lsusb), riêng Ubuntu (dialout +
  udev + gỡ brltty/ModemManager), cấu hình board (sketch, ESP32S3 Dev Module,
  CDC Enabled, USB-OTG, Port), nạp + xử lý kẹt Connecting (giữ BOOT), Serial
  Monitor 115200 + log mẫu + heartbeat, thử BOOT/LED, HID echo
  (`--self-test` + 60 byte khớp + serial gửi lại 64 byte), checklist chốt 4 ô
  + quy tắc dừng. Mỗi ô ghi nguồn truy vết (W/U/R + số mục gốc).
- Tự kiểm: `(Get-Content docs/checklist-bring-up-board.md).Count` -> 163;
  `Length` -> 11034; đếm `^- \[ \]` -> 47 ô; log mẫu, lệnh pip
  (`tools/requirements.txt`), tên board, thứ tự BOOT/RESET đối chiếu từng điểm
  với 2 runbook + README hwtest; chỉ tạo 2 file (sổ cái này + deliverable),
  không sửa file repo nào khác, không git commit.
- Trạng thái: doing -> review.

## Đồng bộ Kanzo: KHÔNG THẤY THẺ NCKH-051, không move/comment được

- GET board lần 1: OK, 59 tasks, nhưng lệnh in liệt kê lỗi định dạng phía client
  (`Cannot convert value "|" to type Int64`) nên chưa đọc được danh sách.
- GET board lần 2 (sau 5s): HỎNG, `500 Internal Server Error` (lỗi Kanzo đã biết).
- GET board lần 3 = thử lại lần 1 (sau 5s): OK, 60 tasks, liệt kê đầy đủ.
  Mọi lệnh timeout 30s, shell pwsh, cách nhau 5s.
- Kết quả quét 60 thẻ: KHÔNG có thẻ nào chứa "051", "bring-up" hay "checklist".
  Thẻ firmware hiện có: 140 (NCKH-003), 148 (009), 155 (015), 161 (021),
  165 (027), 181 (033), 190 (039) — không thẻ nào của NCKH-051.
- Kết luận: không có thẻ để move todo->doing->review hay comment báo cáo.
  KHÔNG tự tạo thẻ (tránh trùng khi Viện trưởng tạo chính thức).
- Nhờ Viện trưởng: tạo thẻ "[firmware] Checklist bring-up board mới (NCKH-051)",
  vá todo->doing->review + gắn báo cáo trong sổ này. Sổ cái file là nguồn
  sự thật duy nhất; thẻ thiếu do Kanzo chưa có, không phải việc khó —
  xin đừng gọi oan theo luật nhịp tim.

## Unresolved

1. Thẻ Kanzo NCKH-051 chưa tồn tại nên move todo->doing->review và comment báo
   cáo chưa thực hiện được — cần Viện trưởng tạo thẻ và vá trạng thái
   (nội dung báo cáo ở mục "2026-11-21 03:10 — báo cáo" trên).
2. Checklist chưa được kiểm chứng runtime trên board thật (không có phần cứng
   trong phiên này); nội dung gom từng điểm từ 2 runbook + README hwtest,
   cần người có board chạy theo từng ô và xác nhận.
3. Ghi chú phạm vi file: objective giới hạn "chỉ tạo đúng 1 file mới" nhưng đồng
   thời yêu cầu "ghi sổ NCKH-051.md TRƯỚC" trong khi file sổ chưa tồn tại.
   Đã tạo 2 file: `vien-nghien-cuu/so-cai/NCKH-051.md` (sổ cái bắt buộc theo
   Hiến chương §2, tiền lệ NCKH-015) + `docs/checklist-bring-up-board.md`
   (deliverable). Không sửa file repo nào khác, không git commit.

## 2026-11-21 03:2x — kiểm chéo đợt 2C: thẻ NCKH-046 (Hứa Bình, lệnh qr)

- Vai: NCKH-051 Nguyễn Cường, kiểm độc lập công việc của NCKH-046
  (lệnh `qr`: thiếu riêng pillow traceback, `--out` thư mục thiếu traceback).
  Repo CHỈ ĐỌC, không git commit, shell pwsh, tiếng Việt.
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-046.md` (toàn bộ),
  `tools/split_secret.py` cmd_qr (dòng 288-304),
  `tools/mnemonic.py` cmd_qr (dòng 206-221).

### Tái hiện độc lập bằng ĐƯỜNG KHÁC (thư mục riêng $env:TEMP\nckh051-xcheck)

- Chuẩn bị: `split ... --from-file secret.txt --out shares` → exit 0, 3 share
  (share-1-of-3.txt 105 byte). Không dùng lại file/lệnh của tác giả.
- X1 (tương đương CA9): `split_secret.py qr shares/share-1-of-3.txt
  --out khong-co-thu-muc/x.png` → TRACEBACK `FileNotFoundError: [Errno 2]
  No such file or directory: '...khong-co-thu-muc\x.png'`, exit 1.
  Khung hình: split_secret.py:302 `.save(out)` → qrcode pil.py:54 →
  PIL Image.py:2706. KHỚP báo cáo của 046.
- X2 (tương đương MN7): `mnemonic.py qr --out khong-co-thu-muc/mn.png
  abandon x11 + about` → TRACEBACK `FileNotFoundError` y hệt, exit 1,
  khung hình mnemonic.py:219. KHỚP báo cáo của 046.
- X3 (tương đương LIB2, phương pháp khác tác giả): KHÔNG đổi tên lib;
  chặn import bằng `sys.modules['PIL']=None` rồi `runpy.run_path` tool →
  `import qrcode` đầu hàm VẪN QUA (không rơi vào except ImportError),
  rồi TRACEBACK `ModuleNotFoundError` tại split_secret.py:302 →
  qrcode/main.py:25 make → main.py:364 make_image
  (`from qrcode.image.pil import Image, PilImage`) → pil.py:2
  (`from PIL import Image, ImageDraw`), exit 1. KHỚP khung hình LIB2
  của 046 (main.py:364 ← cmd_qr).

### Xác nhận nguyên nhân gốc bằng đọc code (không chạy lại lệnh tác giả)

- Cả 2 tool: `try/except ImportError` chỉ bọc 2 dòng `import qrcode`
  (split_secret.py:289-291, mnemonic.py:207-209); dòng
  `qrcode.make(...).save(...)` (split:302, mnemonic:219) nằm ngoài mọi try.
- PIL import LƯỜI: qrcode/main.py:364 `from qrcode.image.pil import ...`
  nằm TRONG `make_image()` (không phải import đầu file); pil.py:2
  `from PIL import ...` cứng. `import qrcode` chịu được thiếu PIL nhờ
  try/except trong qrcode/image/styles/moduledrawers/__init__.py —
  kiểm chứng: `import qrcode` xong PIL mới xuất hiện trong sys.modules,
  còn trước đó `'PIL' in sys.modules` = False. Giải thích đúng vì sao
  thiếu-pillow lọt qua except đầu hàm rồi nổ ở make_image.
- `.save(out)`/`save(args.out)` không bọc try/except OSError, cmd_qr
  không mkdir cha (khác cmd_split) → --out thư mục thiếu nổ
  FileNotFoundError. Đúng như 046 phân tích.

### Kết luận kiểm định: ĐẠT

- Cả 2 lỗi 046 báo cáo đều tái hiện được độc lập, khung traceback và
  exit code khớp; nguyên nhân gốc (import lười PIL, .save ngoài try)
  xác nhận đúng bằng đọc code 2 tool + code lib qrcode 8.2.
- Phạm vi kiểm chéo: chỉ 2 lỗi trên + đọc cmd_qr; không kiểm lại toàn bộ
  17 ca của tác giả (ngoài phạm vi lượt này).
- Kiến nghị của tác giả (bọc make/save vào try ImportError/OSError,
  áp dụng cả 2 tool) là đúng hướng; việc sửa thuộc thẻ FIX-tooling
  riêng (U3 của 046), không thuộc lượt kiểm này.

### Đồng bộ Kanzo (thẻ 208, shell pwsh, timeout 30s, mỗi lệnh cách 5s)

- GET board lần 1-2: HỎNG 500 cả 2. Lần 3: OK, 143 tasks, thấy thẻ
  id=208 "[tooling] Rà soát lệnh qr hai tool (NCKH-046)", status=todo
  (thẻ tạo sau khi 046 làm xong nên chưa từng rời todo).
- POST comment `[KIEM-DINH] đạt + lý do`: OK, comment id=121.
- POST move 208 → done: HỎNG 500 cả 3 lần (chính + 2 thử lại).
  GET đối chiếu xen kẽ cũng 500 nên chưa xác minh được server có ghi
  ngầm không (đúng cảnh báo Hiến chương §6: 500 client không đồng
  nghĩa server chưa ghi).
- Ghi chú: vì thẻ đang todo (không phải review như lệnh mẫu dự kiến),
  đã cố chuyển thẳng todo → done kèm lý do trong comment (việc xong
  trước khi thẻ tồn tại, kiểm định đạt). Nhờ Viện trưởng đối chiếu và
  vá trạng thái thẻ 208 khi Kanzo sống lại; KHÔNG tự tạo thẻ mới.
- File thử kiểm chéo nằm ở $env:TEMP\nckh051-xcheck (shares, *.png),
  không đụng lib thật (X3 chỉ chặn import trong tiến trình con).

### Unresolved của lượt kiểm chéo này

- K1: Move thẻ 208 → done chưa xác nhận được (500 3/3 + board đối
  chiếu 500) — comment kiểm định đã lên (id=121), nhờ Viện trưởng
  vá trạng thái khi Kanzo ổn định.
- K2: Chỉ kiểm chéo 2 lỗi traceback + đọc cmd_qr; 17 ca còn lại của
  tác giả chấp nhận theo sổ NCKH-046, chưa kiểm độc lập.
