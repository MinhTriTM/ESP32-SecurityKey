# Sổ cái NCKH-010 — Bùi An, nhóm tooling, thành viên Viện, đợt 1

> Ghi chú tên: lệnh giao việc ban đầu ghi "Bùi Lan (NCKH-010)" nhưng Viện
> trưởng đã đính chính: tên chính thức theo `vien-nghien-cuu/phan-cong.json`
> là "Bùi An" (mã NCKH-010 giữ nguyên). Từ đây dùng đúng tên Bùi An.

## 2026-11-21 01:31 — nhận việc

- Thẻ: [tooling] Fuzz cbor_decode (Kanzo id 143)
- Trạng thái: todo -> doing (thử opportunistic sau; Kanzo đang nghẽn)
- Việc nhận: fuzz hàm `cbor_decode` trong `tools/fido_check.py` bằng input
  ngẫu nhiên và corpus biên (vài nghìn case, script trong `$env:TEMP`);
  mọi crash đều phải là ValueError có thông điệp — liệt kê ngoại lệ khác
  nếu có. CHỈ BÁO CÁO, không sửa code. REPO CHỈ ĐỌC.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0),
  mục NCKH-010 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, toàn bộ `tools/fido_check.py`
  (hàm `cbor_decode` dòng 176-207, `_cbor_arg` dòng 164-173).
- Môi trường: Windows, Python 3.12.0 (kiểm bằng `python --version`).
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; file tạm chỉ trong
  `$env:TEMP` (`C:\Users\user\AppData\Local\Temp`).

## 2026-11-21 01:32 — báo cáo fuzz cbor_decode

### Đã làm

- Viết script fuzz `fuzz_cbor_NCKH010.py` trong `$env:TEMP` (seed cố định
  `20261121` để tái hiện; import `cbor_decode` từ file, không sửa repo).
- Chạy 5639 case: 639 corpus biên + 5000 ngẫu nhiên, hết ~0,0 s.
  - Corpus biên: rỗng, mọi byte đơn 0x00-0xFF, header nhiều byte bị cụt
    (mọi major × info 24-27), info 28-31, số nguyên biên (uint max,
    nint min), text UTF-8 hỏng/cụt, độ dài khai báo dài hơn thực tế,
    mảng rỗng/cụt/lồng sâu (81h × 50/500/2000/5000), map rỗng/cụt/khóa
    không hash được/lồng sâu, simple/float (F4/F5/F6 hợp lệ, còn lại
    phải ValueError), tag major 6, GetInfo mẫu CANNED + cắt cụt từng độ
    dài + lật bit (200 case), vector nested ở self-test.
  - Ngẫu nhiên: độ dài 0-64 byte, một nửa thuần túy, một nửa thiên về
    byte CBOR hay gặp.
- Xác minh độc lập bằng script riêng `verify_cbor_NCKH010.py` (không dùng
  lại code fuzz): 3 repro TypeError + 1 repro RecursionError + kiểm tra
  `issubclass(UnicodeDecodeError, ValueError)`.

### Tự kiểm (lệnh đã chạy + output)

- Lệnh: `python C:\Users\user\AppData\Local\Temp\fuzz_cbor_NCKH010.py`
  -> exit 0, `tong_case=5639 (bien=639 ngau_nhien=5000)`.
- Lệnh: `python C:\Users\user\AppData\Local\Temp\verify_cbor_NCKH010.py`
  -> exit 0, cả 4 repro tái hiện đúng (xem dưới).
- Kết quả JSON đầy đủ:
  `C:\Users\user\AppData\Local\Temp\fuzz_cbor_NCKH010_ketqua.json`.

### Thống kê fuzz

- Tổng: 5639 case.
- OK (giải mã được): 2635 (int 1291, bytes 480, str 184, list 160,
  dict 265, bool 178, None 77).
- ValueError (đúng kỳ vọng): 2394 — mọi thông điệp đều KHÔNG rỗng
  (`valueerror_rong_thong_diep=0`). Histogram: "CBOR dùng kiểu
  simple/float không hỗ trợ" 1247, "CBOR dùng kiểu không hỗ trợ hoặc bị
  cụt" 883, "CBOR cụt" 264.
- UnicodeDecodeError: 580 — là lớp con của ValueError (đã kiểm
  `issubclass(...) == True`), thông điệp của codec, coi là ĐẠT về loại.
- Ngoại lệ KHÁC ValueError: 30 case — KHÔNG ĐẠT kỳ vọng "mọi crash đều
  là ValueError". Nhóm: TypeError 26, RecursionError 4.

### Ngoại lệ khác ValueError (phải liệt kê)

1. TypeError: unhashable type (26 case, gồm 6 corpus biên + 20 ngẫu
   nhiên). Nguyên nhân gốc: nhánh major 5 (dòng 194-200) lấy key giải mã
   được gán thẳng vào dict mà không kiểm tra hash được; khi key là mảng
   hoặc map (CBOR cho phép) thì `mapping[key] = value` ném TypeError.
   - Repro tối thiểu (đã xác minh độc lập): `a18000` (map khóa mảng) và
     `a1a000` (map khóa map) -> `TypeError: unhashable type: 'list'` /
     `'dict'`.
   - Repro thực tế: CANNED GetInfo thật chỉ cần lật 1 bit (byte text(8)
     `0x68` thành text(9) `0x69`, hex đầy đủ
     `a30182665532465f5632694649444f5f325f3004a162726bf505190400`) làm
     lệch khung parse, cuối cùng ném `TypeError: unhashable type:
     'dict'` thay vì ValueError. Key thật bị nhiễu 1 bit trên đường
     truyền có thể gây crash sai loại này — `main()` ở dòng 447 không
     bắt TypeError nên chương trình sẽ đổ stack trace thay vì in "Kiểm
     tra hỏng".
2. RecursionError: maximum recursion depth exceeded (4 case corpus biên).
   Nguyên nhân gốc: `cbor_decode` đệ quy không giới hạn độ sâu lồng nhau
   (dòng 188-200). Repro tối thiểu (đã xác minh): `b"\x81" * 2000 +
   b"\x00"` (mảng lồng 2000 tầng) và `b"\xa1\x00" * 1500 + b"\x00"`.
   Mức 500 tầng vẫn OK, ngưỡng gãy nằm giữa 500-2000 với recursionlimit
   mặc định 1000. Cũng không được `main()` bắt (dòng 447).

### Ghi nhận thêm (không phải crash, chỉ tham khảo)

- bstr/text khai độ dài dài hơn thực tế (vd `45 6162`) KHÔNG báo lỗi mà
  lặng lẽ trả về phần còn lại (dòng 184-187 cắt slice ngắn hơn arg). Đây
  là hành vi "cụt thân không thành lỗi", đáng để nhóm tooling quyết định
  có siết thành ValueError không — tôi chỉ báo cáo, không sửa.
- Probe ngoài hợp đồng bytes: `None` -> ValueError("CBOR cụt") (do `not
  buf` ở `_cbor_arg`); `int`/`str` -> TypeError (lỗi người gọi, đúng
  quy ước Python); `bytearray`/`memoryview` giải mã bình thường.

### Kết luận

- Kỳ vọng "mọi crash đều là ValueError có thông điệp": KHÔNG ĐẠT —
  30/5639 case (0,53%) ném TypeError (26) hoặc RecursionError (4).
- Mọi ValueError/UnicodeDecodeError đều có thông điệp (0 rỗng): ĐẠT.
- CHỈ BÁO CÁO: không sửa file repo nào; repo chỉ đọc nguyên vẹn trừ file
  sổ cái này.

### Trạng thái Kanzo

- Kanzo đang nghẽn: chỉ thử opportunistic (move todo->doing->review +
  comment báo cáo), mỗi lệnh cách nhau 5 s, timeout 30 s, tối đa 2 lần
  thử lại; hỏng thì ghi vào sổ và tiếp tục. (Kết quả thử ghi dưới.)
- Trạng thái: doing -> review (sau khi thử đồng bộ).

## 2026-11-21 01:33 — đồng bộ Kanzo (opportunistic)

- Lệnh: `pwsh -NoProfile -File
  C:\Users\user\AppData\Local\Temp\kanzo_NCKH010.ps1` (mỗi lệnh cách nhau
  5 s, timeout 30 s, tối đa 2 lần thử lại) -> exit 0.
- Kết quả thẻ id 143:
  - move todo->doing: HỎNG cả 3 lần (HTTP 500 Internal Server Error).
  - move ->review: OK ngay lần 1.
  - comment báo cáo: OK ngay lần 1.
- Trạng thái cuối (chưa GET đối chiếu lại để giảm tải cho Kanzo nghẽn,
  nhờ Viện trưởng đối chiếu): doing -> review.
- Ghi chú: bước doing tuy báo 500 nhưng bước review sau đó thành công nên
  thẻ đã sang review; nội dung báo cáo đầy đủ nằm ở mục trên trong chính
  file sổ cái này (file trước bảng sau).

## 2026-11-21 01:40 — kiểm chéo thẻ 142 của NCKH-005 Hoàng An

- Vai trò: Bùi An (NCKH-010), nhóm tooling, lượt KIỂM CHÉO đợt 1.
- Thẻ: [TAILIEU] Rà soát liên kết gãy docs (Kanzo id 142).
- Kết luận kiểm chéo: ĐẠT — xác nhận độc lập 17/17 liên kết nội bộ
  SỐNG và DẪN ĐÚNG, 0 gãy, 0 dẫn sai.
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-005.md` (báo cáo 17 link + bảng).
- REPO CHỈ ĐỌC: chỉ nối thêm chính file sổ cái này; script tạm trong
  `$env:TEMP`.

### Đường kiểm độc lập (khác công cụ tác giả)

- Tác giả dùng `Select-String -Pattern '\]\([^)]+\)'`.
- Tôi dùng Python (`re` + `pathlib`), script
  `C:\Users\user\AppData\Local\Temp\kiemcheo142_NCKH010.py`:
  regex `(?<!\!)\[([^\]]*)\]\(([^)]+)\)`, loại ảnh `![`, tách nội bộ
  khỏi `http(s)://`, `mailto:`, `#`.
- Kết quả trích: 13 file, **17 nội bộ** + 30 ngoài — khớp từng file:dòng
  với bảng của tác giả (01:34; 03:7,19; 04:41,50,62,65,75; 05:15,17;
  06:16,39; 07:25,125; research/02:7; research/04:31,32).
- Kiểm phụ: ảnh `![`, neo `](#`, link tham chiếu `^[ref]:` trong 13 file
  -> không có kết quả nào (khớp tác giả).

### Xác nhận đích (giải relative path bằng pathlib + đọc nội dung)

- Script `kiemcheo142b_NCKH010.py`: giải mọi đích tương đối từ thư mục
  file nguồn, `Path.exists()` -> **17/17 tồn tại** (gồm 3 đích thư mục
  `scripts/`, `docs/reference/`, `docs/assets/`).
- Kiểm ngẫu nhiên 5 đích + đọc nội dung:
  1. `hardware/wiring.md` — tiêu đề "Sơ đồ đấu nối" khớp chữ link.
  2. `firmware/hwtest/hwtest.ino` — đúng sketch hwtest (USB CDC/nút/LED).
  3. `config/70-u2f.rules` — đúng rules FIDO (Yubico + Espressif 303a).
  4. `docs/research/06-ml-distinguisher.md` — đúng file nghiên cứu ML.
  5. 3 đích thư mục: reference đúng 3 PDF, assets đúng 3 jpg,
     scripts có build/flash/run_tests (cả .ps1 + .sh).
- 2 file tác giả chưa nhấn mạnh (0 link nội bộ theo trích xuất), đọc toàn
  bộ để chắc không sót link do regex:
  1. `docs/02-kien-truc.md` — toàn file không có link markdown nào.
  2. `docs/research/03-du-an-lien-quan.md` — chỉ 7 link ngoài http/https,
     không có link nội bộ nào bị sót.
- Con số 17: XÁC NHẬN (tổng match kiểu tác giả = 47 = 17 + 30).

### Chênh lệch nhỏ (ngoài phạm vi, không ảnh hưởng kết luận)

- Tôi đếm 30 link ngoài, tác giả ghi 29. Nguyên nhân: có đúng 1 link
  `http://` (không -s) tại `research/03-du-an-lien-quan.md:34`
  (UMA Technology) + 29 link `https://`; tác giả dường như chỉ đếm
  `https`. Link ngoài không thuộc phạm vi nhiệm vụ nên không tính lỗi.

### Đồng bộ Kanzo (opportunistic, API nghẽn)

- Script `C:\Users\user\AppData\Local\Temp\kanzo_kiemcheo142_NCKH010.ps1`
  (mỗi lệnh cách 5 s, timeout 30 s, tối đa 2 lần thử lại = 3 lượt).
- POST comment `[KIEM-DINH] đạt...` lên thẻ 142: HỎNG cả 3 lượt
  (HTTP 500 Internal Server Error). BỎ QUA theo luật opportunistic.
- POST move 142 review->done: OK ngay lần 1.
- GET đối chứng (`/api/board` và `/api/tasks/142`): HỎNG cả hai
  (HTTP 500) nên chưa xác minh được trạng thái cuối; tin move đã ghi
  vì server trả OK (không phải timeout mập mờ).
- Kết quả cuối: thẻ 142 (dự kiến) ở `done` nhưng CHƯA có comment kiểm
  định — unresolved, nhờ Viện trưởng dán comment hoặc thử lại khi Kanzo
  hết nghẽn. Nội dung kiểm định đầy đủ nằm ở mục này trong sổ cái.
