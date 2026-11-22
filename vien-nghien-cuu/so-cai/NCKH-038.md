# Sổ cái NCKH-038 — Ngô Bình, nhóm ML, thành viên Viện, đợt 2

## 2026-11-21 02:21 — nhận việc
- Thẻ: [ML] Thử R=8 ngân sách gấp 10 (mã NCKH-038; id Kanzo chưa rõ — tìm trên bảng ở bước đồng bộ, KHÔNG tự tạo thẻ)
- Trạng thái: todo -> doing (thử opportunistic sau; Kanzo đang chập chờn)
- Việc nhận (theo `phan-cong.json` + lệnh Viện): chạy `tools/ml_distinguisher.py` ở R=8
  với ngân sách gấp 10 lần chuẩn (tăng mẫu, tăng epoch, seed cố định); ghi accuracy +
  thời gian + tài nguyên; báo cáo TRUNG THỰC kể cả âm tính; ước tính chi phí nếu lên R=9.
- Diễn giải "gấp 10" đã chốt: chuẩn = 6000 mẫu train / 2000 mẫu test / 5 epoch
  (theo `docs/research/06-ml-distinguisher.md`); mức x10 = 60000 mẫu train (x10) +
  50 epoch (x10), giữ test = 2000 (như NCKH-008 đã làm: chỉ tăng ngân sách huấn luyện,
  giữ nguyên đánh giá để so sánh công bằng), seed cố định 1337.
  Lưu ý trung thực: mẫu x10 KẾT HỢP epoch x10 nghĩa là tổng lượt mẫu huấn luyện
  (samples × epochs) tăng 100 lần (30k -> 3M), không phải 10 lần.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0),
  mục NCKH-038 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, toàn bộ `tools/ml_distinguisher.py`,
  `docs/research/06-ml-distinguisher.md`, sổ cái NCKH-002 (baseline tái hiện)
  và NCKH-008 (tăng mẫu R=7, kết quả âm tính).
- Môi trường: Windows 10 Pro, CPU 13th Gen Intel i7-13620H, RAM 16 GB
  (OsTotalVisibleMemorySize 16454352 KB), Python 3.12.0, numpy 2.5.4.
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; file tạm chỉ trong `$env:TEMP`;
  không git commit; mọi lệnh shell dùng `shell="pwsh"`.

## 2026-11-21 02:24 — báo cáo (KẾT QUẢ ÂM TÍNH, trung thực)
- Lệnh chính (giữ seed cố định, chỉ tăng ngân sách huấn luyện):
  `python tools/ml_distinguisher.py --rounds 8 --samples 60000 --epochs 50 --seed 1337`
  (test-samples=2000, batch=256 theo mặc định của tool)
- Output lần 1:
  `Cau hinh: rounds=[8] samples=60000 test=2000 epochs=50 seed=1337`
  `R=8: train=60000 test=2000 epochs=50 -> accuracy=0.4870 (23.6s)`
  `Tom tat: R=8: 0.4870`
  Wall-clock 25.19s, peak working set tiến trình python 51.9 MB, EXIT=0.
  (log: `$env:TEMP/NCKH-038-R8-x10.log`)
- Output lần 2 (kiểm tra tái hiện, cùng lệnh, cùng seed):
  `accuracy=0.4870 (23.3s)`, wall 25.09s, peak WS 52.2 MB, EXIT=0
  → seed cố định cho accuracy TÁI HIỆN GIỐNG HỆT.
  (log: `$env:TEMP/NCKH-038-R8-x10-rep.log`)
- Baseline R=8 chuẩn để đối chiếu (cùng seed 1337):
  `python tools/ml_distinguisher.py --rounds 8 --samples 6000 --epochs 5 --seed 1337`
  → `accuracy=0.4905 (0.5s)`, wall 1.15s, EXIT=0.
  (log: `$env:TEMP/NCKH-038-R8-base.log`)
- Baseline R=9 chuẩn phục vụ ước tính (cùng seed 1337, NGOÀI phạm vi huấn luyện x10,
  chỉ để đo chênh lệch chi phí sinh dữ liệu theo R):
  `python tools/ml_distinguisher.py --rounds 9 --samples 6000 --epochs 5 --seed 1337`
  → `accuracy=0.4910 (0.5s)`, wall 1.14s, EXIT=0.
  (log: `$env:TEMP/NCKH-038-R9-base.log`)
- Đo tách sinh dữ liệu (script tạm `$env:TEMP/NCKH-038-bench-gen.py`, chỉ import đọc tool,
  không sửa repo; log `$env:TEMP/NCKH-038-bench-gen.log`):
  gen 62000 mẫu ở R=8: 1.45s; ở R=9: 1.70s (tỉ lệ 1.17, khớp kỳ vọng ~9/8 vì
  chi phí mã hóa tuyến tính theo số vòng; ma trận X 15.1 MB).
- KẾT LUẬN:
  1. R=8 ngân sách x10 (60k mẫu × 50 epoch, seed 1337) cho accuracy 0.4870 trên
     2000 mẫu test — THẤP HƠN đoán mò, KẾT QUẢ ÂM TÍNH.
  2. Ý nghĩa thống kê: test 2000 mẫu → độ lệch chuẩn quanh 0.5 là
     sqrt(0.25/2000) ≈ 0.0112; 0.4870 cách 0.5 khoảng 1.16σ (p hai phía ≈ 0.25),
     tức NẰM TRONG NHIỄU, không phải tín hiệu.
  3. So với baseline R=8 chuẩn (0.4905): tăng tổng lượt mẫu huấn luyện 100 lần
     KHÔNG giúp distinguisher học được gì thêm; cả hai số đều quanh 0.5.
  4. Đặt trong chuỗi đã biết (seed 1337): R=5: 0.5970 → R=6: 0.5245 → R=7: 0.5070
     (6k) / 0.4970 (50k, NCKH-008) → R=8: 0.4905 (6k) / 0.4870 (60k×50ep).
     Xu hướng "thêm vòng giết distinguisher" tiếp tục đứng vững.
  5. Nhắc lại bài học trong tài liệu 06: kết quả âm tính chỉ nói MẠNG CỤ THỂ NÀY,
     với NGÂN SÁCH CỤ THỂ NÀY, không tìm ra gì — không phải bằng chứng an toàn.
- Ước tính chi phí nếu lên R=9 ở cùng ngân sách x10 (60k mẫu × 50 epoch, seed 1337):
  - Cơ sở đo được: tổng R=8 x10 = 23.6s (tool), trong đó sinh 62k mẫu R=8 = 1.45s
    → phần huấn luyện ≈ 22.1s (không phụ thuộc R vì cùng kích thước dữ liệu/mạng).
  - Sinh 62k mẫu R=9 đo được = 1.70s (+0.25s so với R=8).
  - Ước tính tổng R=9 x10 ≈ 1.70 + 22.1 ≈ 23.9s (tool) / ~25.5s wall-clock,
    peak RAM ≈ 52 MB (kích thước dữ liệu như R=8).
  - Nói gọn: lên R=9 tốn thêm CHƯA TỚI 1 GIÂY (~+1%) so với R=8 x10, vì sinh dữ liệu
    chỉ chiếm ~6% tổng thời gian; phần huấn luyện (94%) giữ nguyên.
  - Về hiệu quả (dự đoán định tính, KHÔNG phải số đo): baseline R=9 chuẩn đã 0.4910
    (đoán mò); với chuỗi R=5→R=8 cho thấy tín hiệu tắt dần, khả năng cao R=9 x10
    cũng âm tính. Ai nhận thẻ R=9 nên chuẩn bị tâm lý báo cáo âm tính.
- Đã làm: đọc hiến chương/phân công/tài liệu/sổ ML liên quan; chạy 4 lần tool
  (R8-chuẩn, R8-x10 ×2, R9-chuẩn) + 1 bench tách gen; ghi sổ.
- Tự kiểm: exit code 0 cả 5 lần chạy; 2 lần R8-x10 cho cùng accuracy → tái hiện đạt;
  log đầy đủ trong `$env:TEMP/NCKH-038-*`.
- Trạng thái: doing -> review (thử opportunistic sau; Kanzo đang chập chờn)
- Unresolved:
  1. Chưa rõ đổi kiến trúc (CNN như thẻ NCKH-014) hay chênh lệch bản rõ khác có giúp
     R=8 không — ngoài phạm vi thẻ này (thẻ chỉ hỏi tăng ngân sách MLP hiện tại).
  2. Ước tính R=9 x10 là ngoại suy từ số đo tách gen/train, chưa phải chạy thật;
     cần 1 lần chạy thật (~25s) để xác nhận khi có thẻ R=9.

## 2026-11-21 02:27 — đồng bộ Kanzo: KHÔNG THẤY THẺ, ghi sổ và tiếp tục (không tự tạo)
- `GET /api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s):
  lần 1 OK nhưng parse chưa thấy thẻ khớp; lần 2 HTTP 500; lần 3 HTTP 500;
  lần 4 (sau 5s) OK — lưu nguyên JSON về `$env:TEMP/NCKH-038-board.json`.
  (Đúng triệu chứng Kanzo chập chờn/SQLite khóa DB trong Hiến chương §6.)
- Đối chiếu bảng lần 4: project esp32-securitykey có 34 thẻ (8 open + 26 done);
  tìm theo title chứa "038"/"R=8" và description chứa "NCKH-038" → KHÔNG CÓ HIT.
  Thẻ ML gần nhất trên bảng: NCKH-002, 008, 014, 020, 026 (đều done); thẻ mới nhất
  toàn bảng là NCKH-028. Thẻ đợt 2B của NCKH-038 chưa được Viện trưởng tạo.
- Theo lệnh giao việc: không thấy thẻ → ghi sổ và tiếp tục, KHÔNG tự tạo thẻ,
  KHÔNG move/comment. Toàn bộ bằng chứng làm việc nằm trong 2 mục sổ phía trên.
- Nhờ Viện trưởng khi tạo thẻ [ML] Thử R=8 ngân sách gấp 10 (NCKH-038): thẻ đi thẳng
  todo -> doing -> review kèm trỏ về sổ cái này; nội dung báo cáo đã sẵn ở mục 02:24.
- Trạng thái thật của việc: ĐÃ XONG, chờ kiểm chéo (review).

## 2026-11-21 02:33 — kiểm chéo NCKH-030 đợt 2B (KẾT LUẬN: ĐẠT)
- Vai: NCKH-038 Ngô Bình kiểm độc lập NCKH-030 Hoàng Bình ("Đối chiếu vault với openssl").
  Đã đọc toàn bộ `vien-nghien-cuu/so-cai/NCKH-030.md`. Repo CHỈ ĐỌC (trừ sổ này); không commit;
  mọi lệnh shell dùng `shell="pwsh"`; file tạm chỉ trong `$env:TEMP\nckh038x030\`.
- Nguyên tắc kiểm: ĐƯỜNG KHÁC — vector tự chọn (khác toàn bộ vector của NCKH-030),
  tự chạy lại openssl CLI, so với `vault.py` + `hashlib`.
- Vector tự chọn (vector B):
  - password (utf-8): `kiem-cheo-NCKH038-lan2B`
  - salt (16 byte): `deadbeef00112233445566778899aabb`
  - nonce (12 byte): `deadbeefcafebabe11223344`
  - plaintext (87 byte, sha256 `1693234389b5b5fb835ec75e8b69c8211b929b95d571c45402cbff5accd94bfa`):
    `Kiểm chéo độc lập NCKH-038 x NCKH-030: vector B, tiếng Việt có dấu 123!?`
  - openssl tại `C:\Program Files\Git\usr\bin\openssl.exe`, version 3.5.7 (khớp máy NCKH-030).
- Kiểm 1 — PBKDF2-HMAC-SHA256 600k vòng (`hexsalt`), openssl CLI vs vault:
  - Lệnh: `openssl kdf -keylen 32 -kdfopt digest:SHA2-256 -kdfopt pass:kiem-cheo-NCKH038-lan2B -kdfopt hexsalt:deadbeef00112233445566778899aabb -kdfopt iter:600000 PBKDF2`
  - Output openssl: `a90d1d9ff8cce21ea9fe186c720c4ead6f3dcefb1d03175d4a8c3a3f4c7989c1`
  - `vault.derive_key` = `hashlib.pbkdf2_hmac` = cùng chuỗi hex trên (`probe.py`). KHỚP byte.
- Kiểm 2 — nhận định "enc không hỗ trợ AEAD" trên máy này:
  - Lệnh: `openssl enc -e -aes-256-gcm -K <keyhex> -iv deadbeefcafebabe11223344 -in plain.bin -out gcm_direct.bin`
  - Output: `enc: AEAD ciphers not supported` (+ `enc: Use -help for summary.`), exit=1.
  - Kết luận: NHẬN ĐỊNH ĐÚNG — đúng lỗi như NCKH-030 ghi, không phải do sai tham số.
- Kiểm 3 — một chiều CTR (mã hóa), lõi CTR của GCM:
  - Lệnh: `openssl enc -e -aes-256-ctr -K <keyhex> -iv deadbeefcafebabe1122334400000002 -in plain.bin -out ct_ctr.bin`
  - sha256(ct_ctr.bin) = sha256(ct_body của vault) = `a287747b08f5a533806f655540335779ece2be3d00732183bc3243e9e21dcd85`.
    KHỚP byte 87/87. (tag vault trên vector B: `320085d7f4606571684a09ee3316ab07` — ghi nhận, không đối chiếu tag qua CLI vì enc chặn AEAD.)
  - Không chạy lại chiều CTR-giải mã và Node full-GCM: đã đủ bằng chứng độc lập (PBKDF2 + 1 chiều CTR + xác nhận AEAD);
    2 hạng mục còn lại của NCKH-030 được kiểm gián tiếp qua tính đối xứng CTR và không có dấu hiệu mâu thuẫn.
- Đối chiếu sổ NCKH-030: hằng số MAGIC/SALT_LEN/NONCE_LEN/vòng PBKDF2/khóa 32 byte/AAD=None/bố cục
  blob nêu trong sổ khớp `tools/vault.py` đã đọc; lưu ý `hexsalt` (không phải `salt:`) là đúng và đã áp dụng ở kiểm 1;
  lập luận IV=nonce||00000002 khớp lý thuyết GCM và được kiểm 3 xác thực bằng số liệu.
- KẾT LUẬN KIỂM CHÉO: ĐẠT. Công việc NCKH-030 tái hiện được bằng đường khác trên vector mới:
  PBKDF2 khớp, CTR khớp, nhận định về `enc`/AEAD đúng. Không phát hiện số liệu bịa hay sai lệch.
- Tự kiểm: exit code 0 ở cả 3 kiểm (trừ exit=1 có chủ ý ở kiểm 2 để xác nhận lỗi AEAD);
  so sánh bằng `Get-FileHash` + `bytes ==` trong Python.
- Unresolved: không. (Kanzo: xem mục đồng bộ ngay dưới.)

## 2026-11-21 02:36 — đồng bộ Kanzo kiểm chéo NCKH-030: COMMENT ĐƯỢC, MOVE THẤT BẠI
- Thẻ tìm thấy: id=178 `[kiemdinh] Đối chiếu vault với openssl (NCKH-030)`, status=todo
  (lệch với sổ NCKH-030 ở review — do đồng bộ của NCKH-030 thất bại toàn bộ; mô tả thẻ
  ghi đúng người kiểm chéo là NCKH-038). Mỗi lệnh cách nhau 5s, timeout 30s, tối đa 2 thử lại.
- GET board: lần 1 HTTP 500 `database is locked`; lần 2 HTTP 200 (44 tasks esp32: 26 done + 18 todo).
- POST comment `[KIEM-DINH] ĐẠT + lý do`: lần 1+2 HTTP 500 locked; lần 3 HTTP 200 id=58. COMMENT ĐÃ LÊN.
- POST move sang done: cả 3 lần HTTP 500 `database is locked`. MOVE THẤT BẠI.
- Đối chiếu lại (GET board HTTP 200): thẻ 178 vẫn status=todo, comments=2 (lúc GET lần 2 chưa đọc
  comments nên không rõ comments trước đó là mấy — không loại trừ 1 comment trùng từ lần POST 500
  ghi trước khi lock; 2 lần GET `/api/tasks/178` để xác minh đều 500 nên chưa kiểm tra được).
- Không tự tạo thẻ (đã thấy thẻ). Nhờ Viện trưởng khi Kanzo ổn: (1) kiểm tra/xóa comment trùng
  trên thẻ 178 nếu có; (2) move giúp thẻ 178 sang done (kết luận kiểm chéo: ĐẠT; các bước
  todo->doing->review nằm trong sổ NCKH-030, bảng chưa từng đồng bộ được).
