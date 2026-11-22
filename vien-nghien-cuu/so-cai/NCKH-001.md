# Sổ cái NCKH-001 — Nguyễn An (nhóm PQC, nhóm trưởng, tổ trưởng đợt 1)

## 2026-11-21 01:29 — nhận việc

- Thẻ: [PQC] Rà soát tools/pqc.py (Kanzo id 138)
- Người nhận: Nguyễn An (NCKH-001)
- Việc nhận: đọc toàn bộ `tools/pqc.py`, kiểm API oqs đúng bản, nhánh lỗi,
  self-test đủ chưa. Báo cáo [KIEM-DINH]. REPO CHỈ ĐỌC, không git commit.
- Tài liệu đã đọc TRƯỚC khi làm (theo lệnh giao việc):
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, đã đọc toàn bộ)
  - mục NCKH-001 trong `vien-nghien-cuu/phan-cong.json` (dòng 2-13)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu nhật ký sổ cái)
- Trạng thái thẻ: todo -> doing (dự kiến; Kanzo đang nghẽn — xem mục Kanzo bên dưới)

## 2026-11-21 01:30 — quá trình rà soát

### Lệnh đã chạy + output quan sát được

Shell `muse.powershell` (pwsh) KHÔNG khả dụng trong phiên này: mọi lệnh đều
thất bại với `tool failed: program not found`, kể cả lệnh tối thiểu
`Get-Location`. Vì vậy:

- KHÔNG chạy được `python tools/pqc.py --self-test`, `scripts/run_tests.*`,
  `pip show liboqs-python`, hay bất kỳ lệnh thực thi nào.
- KHÔNG gọi được API Kanzo (`Invoke-RestMethod` cần pwsh) — xem mục Kanzo.
- Toàn bộ rà soát bên dưới là ĐỌC TĨNH qua `muse.read_file` / `muse.search`
  (thành công). Repo giữ nguyên chỉ-đọc, đúng lệnh giao việc.

Các file đã đọc toàn bộ (read_file thành công):

1. `tools/pqc.py` — 297 dòng, đọc hết dòng 1-297.
2. `tools/requirements-pqc.txt` — 7 dòng: `liboqs-python>=0.16`.
3. `tools/hid_echo.py` — 88 dòng (đối chiếu quy ước mã thoát).
4. `scripts/run_tests.ps1` (13 dòng) và `scripts/run_tests.sh` (13 dòng).
5. `vien-nghien-cuu/HIEN-CHUONG.md`, `vien-nghien-cuu/phan-cong.json`
   (mục NCKH-001), `vien-nghien-cuu/so-cai/README.md`.

Các tìm kiếm đã chạy (muse.search, thành công):

- `oqs` trong `tools/` — mọi điểm chạm API oqs đều nằm trong `tools/pqc.py`.
- regex `pqc|ML-KEM|EXIT_MISSING` trong `tools/` — xác nhận mã thoát 2.
- regex `run_tests|self-test|self_test` toàn repo — pqc có mặt trong
  `run_tests.ps1/.sh` (vòng 7 tool) và tài liệu.
- regex `pqc|ML-KEM|PQC` trong `README.md`, `docs/07-sao-luu-va-khoi-phuc.md` —
  README dòng 43 xác nhận self-test + CLI thật đã PASS trước đây.

### Đối chiếu API oqs (liboqs-python >= 0.16)

| Điểm dùng trong code | Kết luận |
|---|---|
| `ALG = "ML-KEM-768"` (dòng 38) | ĐÚNG bản: tên chuẩn FIPS 203 từ liboqs ≥ 0.12, thay `Kyber768` cũ. |
| `oqs.get_enabled_kem_mechanisms()` / `get_supported_kem_mechanisms()` (82, 85) | ĐÚNG tên hàm public của liboqs-python. |
| `oqs.KeyEncapsulation(ALG)` + context manager (99, 105, 113) | ĐÚNG: class hỗ trợ `with` (tự giải phóng). |
| `KeyEncapsulation(ALG, secret_key=...)` (119) | ĐÚNG tên tham số `secret_key` của upstream. |
| `generate_keypair()` → pk, `export_secret_key()` → sk (106-107) | ĐÚNG thứ tự 2 bước của wrapper. |
| `encap_secret(pk)` → (ct, ss) (114) | ĐÚNG chữ ký, trả tuple 2 phần tử. |
| `decap_secret(ct)` → ss (120) | ĐÚNG chữ ký. |
| `kem.details` dict `length_*` (100) | ĐÚNG: không hardcode kích thước, khớp docstring dòng 26. |
| `oqs_version()`, `oqs_python_version()` (196) | ĐÚNG tên hàm. |
| `load_oqs` gom ImportError/RuntimeError/OSError/SystemExit (59-66) | HỢP LÝ: wrapper ctypes hỏng 3 kiểu đúng như comment. |
| `EXIT_MISSING_LIB = 2` (41) | ĐÚNG quy ước `hid_echo.py` dòng 48 (`return 2` khi thiếu lib). |
| `tuple[bytes, bytes]`, `int \| None` | ĐÚNG yêu cầu "Python 3.10+" (union `X \| Y` cần 3.10). |

### Nhánh lỗi — đã đi từng nhánh

ĐẠT:

- Thiếu lib (chưa pip / thiếu DLL / build native hỏng) → `OqsMissingError`,
  in hướng dẫn tiếng Việt + mã thoát 2, cả 4 đường vào (self-test + 3 lệnh).
- Thuật toán vắng mặt: phân biệt 2 nhánh "có nhưng chưa bật" (88) và
  "không có trong bản này" (91) — thông điệp khác nhau, đúng.
- File vào hỏng: `_read_exact` (123-132) bắt `OSError` và lệch độ dài →
  `SystemExit` có nêu đường dẫn + số byte thực tế/kỳ vọng.
- Khóa/bản mã đúng cỡ nhưng sai nội dung: ML-KEM từ chối ngầm, code KHÔNG
  mong exception mà assert khác secret (self-test bước 3, 4) — đúng ngữ nghĩa.
- `--self-test` kèm lệnh khác → từ chối, mã 1 (277-279). Lệnh lạ → AssertionError (293).

CHƯA ĐẠT / THIẾU (xếp theo mức độ):

1. (Trung bình) `cmd_keygen` (142-143) và mọi `write_bytes` output (159-160,
   179) KHÔNG bọc `OSError`: đĩa đầy / không quyền ghi / thư mục cha chưa có
   → traceback thô, trong khi đường ĐỌC (`_read_exact`) lại báo sạch.
   Mất đối xứng đọc/ghi.
2. (Trung bình) Self-test bước 5 (232-237) chỉ chấp nhận `ValueError` cho bản
   mã cắt ngắn, nhưng CLI (`cmd_encapsulate`/`cmd_decapsulate`, dòng 156, 176)
   lại bắt `(ValueError, RuntimeError)`. Nếu wrapper ném `RuntimeError` cho
   input ngắn thì self-test crash thay vì PASS — hai chỗ mâu thuẫn nhau,
   chưa được kiểm chứng vì phiên này không chạy được Python.
3. (Nhẹ, bảo mật) Khóa bí mật `.sk` ghi bằng `write_bytes` với umask mặc định
   → trên Linux file có thể world-readable. Nên `chmod 0o600` sau khi ghi.
4. (Nhẹ) `--prefix` không khử `../` hay ký tự phân cách → `keygen --prefix
   ../x` ghi ra ngoài `--out-dir`. Nên chặn hoặc dùng basename.
5. (Nhẹ, tài liệu) Docstring (16-22) chỉ nói liboqs build vào `_oqs` trong home,
   trong khi `run_tests.ps1` dòng 5-6 đặt `OQS_INSTALL_PATH` tới `.tooling/oqs`
   và README dòng 43 cũng nói `.tooling/oqs`. Hai nguồn mâu thuẫn về vị trí DLL.
6. (Nhẹ, tài liệu) Chạy trần `python tools/pqc.py` (không tham số) sẽ chạy
   self-test (dòng 276, `lenh is None`) nhưng docstring không ghi hành vi này.

### Self-test đủ chưa

5 bước hiện có (đúng + khớp nhau + 2 ca từ chối ngầm + 1 ca input ngắn) là
KHÁI QUÁT TỐT cho tầng thư viện, nhưng CHƯA ĐỦ cho một tool CLI:

- Thiếu kiểm đường CLI: `keygen → encap → decap` qua file tạm (tmp_path),
  `_read_exact` lệch cỡ, file rỗng/không tồn tại — các nhánh `SystemExit`
  chưa bao giờ được self-test chạm tới.
- Thiếu kiểm `encap` với public key sai cỡ và `decap` với secret key sai cỡ
  ở tầng hàm (mới chỉ có ct cắt ngắn).
- Thiếu kiểm alias `encap`/`decap` của argparse.
- Nên có (không bắt buộc): hai lần `encap` cùng pk phải ra ct khác nhau
  (tính ngẫu nhiên của KEM), và assert `length_shared_secret == 32` theo
  chuẩn FIPS 203 chứ không chỉ so với `kem.details`.

### Trạng thái thẻ Kanzo (tôi kiêm tổ trưởng đợt 1)

- Kanzo `http://100.101.100.100:4242/api` được lệnh trên báo NGHẼN (SQLite
  khóa khi ghi dồn dập), quy tắc: opportunistic, mỗi lệnh cách nhau 5s,
  timeout 30s, tối đa 2 lần thử lại, hỏng thì ghi sổ và tiếp tục.
- Thực tế phiên NCKH-001: shell pwsh hỏng hoàn toàn (`program not found`)
  nên KHÔNG THỬ được bất kỳ lệnh Kanzo nào (0 lần thử, không phải do Kanzo
  từ chối mà do phía agent không có shell). Không thể xác nhận thẻ 138 còn
  ở `todo` hay đã ai di chuyển.
- Kết luận tổ trưởng: thẻ 138 và toàn bộ đợt 1 hiện chỉ có SỔ CÁI FILE làm
  nguồn sự thật; Viện trưởng cần đối chiếu và vá bảng khi Kanzo/shell sống
  lại. Đề nghị các agent đợt 1 khác tự báo trong sổ của mình xem shell của
  họ có sống không để phân biệt lỗi cục bộ hay lỗi toàn viện.

## 2026-11-21 01:35 — báo cáo

- Đã làm: đọc tĩnh toàn bộ `tools/pqc.py` (297 dòng) + 6 file đối chiếu,
  kiểm từng lời gọi API oqs, đi từng nhánh lỗi, đánh giá 5 bước self-test.
- Tự kiểm: KHÔNG chạy được lệnh thực thi nào (shell `program not found`,
  đã thử 2 lệnh: `Get-ChildItem...` gộp và `Get-Location`, đều hỏng).
  Mọi kết luận trên suy từ đọc code, CHƯA được kiểm chứng bằng chạy thật —
  cần một agent có shell chạy `scripts/run_tests.ps1` để xác nhận, nhất là
  mục 2 (ValueError/RuntimeError).
- [KIEM-DINH] KHÔNG ĐẠT có điều kiện (conditional fail): code đúng API,
  đúng quy ước mã thoát, self-test tầng lib tốt — nhưng mất đối xứng lỗi
  đọc/ghi (mục 1), mâu thuẫn loại exception giữa CLI và self-test (mục 2),
  file `.sk` ghi không khóa quyền (mục 3), và self-test chưa chạm tầng CLI.
  Đề nghị sửa 3 mục trung bình + khóa quyền `.sk` rồi review lại; các mục
  nhẹ còn lại có thể làm gộp.
- Trạng thái thẻ: doing -> review (dự kiến; chưa đẩy được lên Kanzo — xem trên).
- Unresolved: (1) chưa chạy self-test thật; (2) chưa xác nhận loại exception
  wrapper ném cho input ngắn; (3) chưa đồng bộ Kanzo thẻ 138; (4) mâu thuẫn
  tài liệu vị trí DLL liboqs (`.tooling/oqs` vs `_oqs` trong home) cần chủ
  repo chốt.

## 2026-11-21 01:39 — kiểm chéo thẻ 147 của NCKH-008 (Võ An)

- Vai trò lượt này: NCKH-001 Nguyễn An, nhóm PQC, kiểm chéo khác nhóm thẻ
  [ML] Tăng mẫu lên 50k ở R=7 (Kanzo id 147), đợt 1.
- Đối tượng kiểm: sổ NCKH-008 mục 01:32 — train 50k mẫu R=7 seed 1337,
  accuracy 0.4970, kết luận ÂM TÍNH (không vượt 0.5), tái hiện đạt.
- Đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-008.md`, toàn bộ
  `tools/ml_distinguisher.py` (331 dòng, để chọn đường kiểm khác).
- Khác biệt phiên này so với phiên 01:30: shell pwsh ĐÃ SỐNG (trước đó
  `program not found`) nên chạy được Python và gọi được API Kanzo.
  Lỗi shell trước là cục bộ theo phiên, không phải toàn viện.

### Kiểm bằng đường khác (seed khác, mẫu vừa 10k)

| Lần | Lệnh | Kết quả |
|---|---|---|
| 1 | `python tools/ml_distinguisher.py --rounds 7 --samples 10000 --seed 99` | `accuracy=0.4970 (0.8s)`, exit 0 |
| 2 | `--seed 1234`, còn lại giống lần 1 | `accuracy=0.4965 (0.8s)`, exit 0 |
| 3 | lặp lại lần 1 (seed 99) | `accuracy=0.4970`, exit 0 — tái hiện bit-identical |

- Nhận xét: seed 99/10k cho đúng 0.4970 như NCKH-008 (50k/seed 1337) —
  trùng hợp ngẫu nhiên (xác suất 2 lần độc lập rơi cùng ô ~1%, vẫn xảy ra);
  seed 1234 cho 0.4965, chứng tỏ có biến thiên thật quanh 0.5 chứ không
  phải tool hằng số. Xu hướng đoán mò GIỮ VỮNG trên đường kiểm độc lập.
- Tái hiện: cùng seed cho cùng accuracy → khẳng định nhận định "seed cố
  định tái hiện được" của NCKH-008.

### Kiểm nhận định thống kê (độ lệch chuẩn ~0.011 với test 2000)

- Tính lại: test nhị phân cân bằng, H0 đoán mò p=0.5, n=2000 →
  σ = sqrt(0.25/2000) = 0.01118 ≈ 0.011. Nhận định ĐÚNG.
- z-score các số liệu: 0.4970 → -0.27σ; 0.4965 → -0.31σ; baseline tài liệu
  0.5070 → +0.63σ. Tất cả nằm gọn trong nhiễu (|z| < 1) → kết luận "cả hai
  số đều nằm trong nhiễu quanh 0.5" ĐÚNG, và kết quả âm tính của NCKH-008
  không phải do thiếu mẫu test.

### Kết luận kiểm định

- [KIEM-DINH] ĐẠT: lệnh trung thực, số liệu tái hiện được, nhận định thống
  kê đúng, kết luận âm tính đứng vững trên đường kiểm độc lập (2 seed khác,
  mẫu 10k). Không yêu cầu sửa gì; unresolved của NCKH-008 (thử epoch/batch/
  kiến trúc khác) thuộc thẻ mới, ngoài phạm vi thẻ 147.
- Trạng thái thẻ: review -> done (đẩy opportunistic; xem mục Kanzo dưới).
- Unresolved lượt kiểm chéo: không có.

## 2026-11-21 01:44 — đồng bộ Kanzo (thẻ id 147, opportunistic, THẤT BẠI)

- Comment [KIEM-DINH]: THẤT BẠI cả 3 lần thử (500 Internal Server Error).
- Move review -> done: THẤT BẠI cả 3 lần thử (500 cả 3).
- GET /api/board đối chiếu: THẤT BẠI (500) — Kanzo đợt này sập nặng hơn
  phiên NCKH-008 (khi đó GET còn sống); không xác nhận được thẻ 147 có
  nhận ghi nửa vời nào không.
- Mỗi lệnh cách nhau ≥5s, timeout 30s, tối đa 2 lần thử lại — đúng luật.
- Kết quả: thẻ 147 (theo sổ NCKH-008) vẫn ở review; Viện trưởng cần đẩy
  tay comment [KIEM-DINH] ĐẠT + move review -> done khi Kanzo sống lại.
  Sổ cái file là nguồn sự thật duy nhất cho lượt kiểm chéo này.
