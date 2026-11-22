# NCKH-052 Trần Cường (nhóm tooling, đợt 2C) — Chuẩn hóa mã thoát tool

## 2026-11-21 — nhận việc
- Thẻ: [tooling] Chuẩn hóa mã thoát tool (mã NCKH-052, tìm trên Kanzo sau)
- Việc nhận: lập bảng chuẩn mã thoát + thông điệp chung cho mọi tool, sửa chỗ lệch trong tools/*.py.
- Phạm vi: CHỈ chạm mã thoát và thông điệp, KHÔNG sửa logic. Không git commit.

## Bảng chuẩn mã thoát (áp dụng mọi tool trong tools/*.py)

| Mã | Ý nghĩa | Khi nào dùng | Mẫu thông điệp |
|----|---------|--------------|----------------|
| 0 | Thành công | Lệnh chạy xong; self-test PASS | Kết quả thường; self-test in `self-test ok: ...` |
| 1 | Lỗi khi chạy | Thiết bị/HID, file hỏng, crypto sai, két sai mật khẩu, nhập liệu tương tác sai, dữ liệu đầu vào sai nội dung, self-test FAIL | Câu mô tả cụ thể, tiếng Việt có dấu (`Không thấy...`, `Không mở được...`, `Kiểm tra hỏng: ...`, `Lỗi: ...`) |
| 2 | Thiếu thư viện hoặc sai cách dùng | `ImportError` (kể cả thiếu lib native như liboqs/numpy); tham số CLI sai (số, thiếu arg, `--index`/`--words` sai giá trị, thiếu file đầu vào, `--self-test` dùng chung lệnh khác) | Thiếu lib: `Thiếu thư viện X. Chạy: pip install ...`; sai dùng: `Sai dùng: ...` hoặc câu hướng dẫn dùng đúng (`--index cần kèm số...`) |

Quy tắc phân biệt 1 và 2:
- Sai cú pháp/giá trị tham số CLI do người gõ (số, cờ, số lượng file) → 2.
- Tham số đúng nhưng dữ liệu/file/thiết bị hỏng khi chạy (share sai nội dung, cụm từ sai checksum, két sai mật khẩu, key không trả lời) → 1.
- `argparse` sai (thiếu subcommand/arg bắt buộc) tự thoát 2 — giữ nguyên, đã đúng chuẩn.
- `SystemExit("msg")` (pqc `_read_exact`) thoát 1 — giữ mã, chỉ chuẩn hóa tiền tố thông điệp.

## Danh sách rà soát và sửa (đọc trước → sửa → đọc lại → self-test)

1. `tools/fido_check.py` — LỆCH 1 chỗ: `main`, chọn `--index` vượt số key thấy → `return 1` (sai, đây là sai dùng) → sửa thành `return 2`, giữ nguyên thông điệp. Còn lại đã chuẩn (thiếu hid → 2, lỗi thiết bị → 1, self-test `self-test ok`).
2. `tools/hid_echo.py` — ĐÃ CHUẨN, không sửa (thiếu hid → 2, lỗi thiết bị/echo → 1, self-test `self-test ok`).
3. `tools/split_secret.py` — LỆCH 2 chỗ:
   - `cmd_split`: `Sai tham số: ...` (N/K sai do người gõ) `return 1` → sửa thành `return 2`.
   - `cmd_combine`: `Thiếu share: ...` (người dùng đưa thiếu file) `return 1` → sửa thành `return 2`.
   - Giữ `return 1`: nhập tương tác không khớp, file share hỏng, share không cùng lần chia (sai nội dung khi chạy), không ghép được, thiếu lib QR → 2 đã đúng.
4. `tools/mnemonic.py` — LỆCH 1 chỗ: `cmd_new`, `--words` sai giá trị → `return 1` → sửa thành `return 2`, giữ nguyên thông điệp. Còn lại đã chuẩn (cụm từ sai checksum → 1 vì sai dữ liệu khi chạy; thiếu lib QR → 2).
5. `tools/vault.py` — ĐÃ CHUẨN, không sửa (thiếu cryptography → exit 2, lỗi file/két/nhập liệu → exit 1, self-test `self-test ok`). Ghi chú: file dùng `sys.exit()` giữa hàm thay vì `return`, nhưng mã đã đúng nên không đụng (tránh sửa cấu trúc/logic).
6. `tools/pqc.py` — LỆCH 3 chỗ:
   - `main`: `--self-test` dùng chung lệnh khác → `return 1` → sửa thành `return 2` (sai dùng).
   - `self_test`: in `self-test PASS: ...` → sửa thành `self-test ok: ...` cho nhất quán mọi tool.
   - `_read_exact`: 2 thông điệp `SystemExit` (mã 1, đã đúng) thêm tiền tố `Lỗi: ` cho nhất quán.
   - Cập nhật comment `EXIT_MISSING_LIB` trỏ bảng chuẩn NCKH-052 (comment, không phải logic).
7. `tools/ml_distinguisher.py` — LỆCH 4 chỗ (file này còn viết không dấu, nhưng chỉ chuẩn hóa thông điệp liên quan mã thoát, không cải chính toàn file):
   - `import numpy` ở top-level: thiếu lib hiện văng traceback + exit 1 → bọc `try/except ImportError` in `Thiếu thư viện numpy. Chạy: pip install -r tools/requirements.txt` rồi `raise SystemExit(2)` (thêm `import sys`).
   - `--rounds` sai định dạng → giữ `return 2`, sửa thông điệp thành `Sai dùng: --rounds phải là danh sách số nguyên, ví dụ '5,6,7'.`
   - R ngoài khoảng → giữ `return 2`, sửa thông điệp thành `Sai dùng: mỗi R phải trong [1, 22].`
   - `self_test`: dòng `== KET LUAN: PASS/FAIL ==` → `self-test ok: ...` khi đạt / `self-test lỗi: ...` khi không đạt, giữ các dòng chi tiết.

## Tự kiểm (đã chạy sau khi sửa)

Self-test từng file đã sửa (thoát đúng bảng chuẩn):
- `python tools/fido_check.py --self-test` → `self-test ok: framing, gói nối, CBOR, GetInfo...` EXIT=0.
- `python tools/split_secret.py --self-test` → `self-test ok: GF(256)...` EXIT=0.
- `python tools/mnemonic.py --self-test` → `self-test ok: bảng BIP-39...` EXIT=0.
- `python tools/ml_distinguisher.py --self-test` → `self-test ok: Speck32/64 round-trip đúng, micro-train chạy được.` EXIT=0 (dòng kết luận mới).
- `PYTHONPATH=.tooling/pylibs python tools/pqc.py --self-test` → thiếu liboqs native (máy không có CMake/VS nên oqs tự build thất bại) → in đúng thông điệp `Thiếu thư viện PQC (...)` EXIT=2. Nhánh round-trip thật không chạy được trên máy này — ngoài phạm vi (không sửa logic/môi trường).

Kiểm nhánh mã 2 vừa sửa:
- `mnemonic.py new --words 13` → `--words phải là một trong...` EXIT=2.
- `ml_distinguisher.py --rounds abc` → `Sai dùng: --rounds phải là danh sách số nguyên...` EXIT=2.
- `pqc.py --self-test keygen` → `Sai dùng: không dùng --self-test chung với lệnh khác.` EXIT=2.
- `split_secret.py split --shares 300 ...` → `Sai tham số: cần 1 <= threshold...` EXIT=2.
- `split_secret.py combine <1 share, cần 2>` → `Thiếu share: cần ít nhất 2 trong 3...` EXIT=2.
- `fido_check.py` nhánh `--index` vượt: cần key thật nên không chạy được, đã đọc lại mã (return 2) đúng.
- `vault.py`, `hid_echo.py` không sửa (đã chuẩn) → không chạy lại.

## 2026-11-21 — báo cáo
- Đã làm: lập bảng chuẩn (0 ok / 1 lỗi chạy / 2 thiếu lib-sai dùng) + rà 7 tool, sửa 5 file (fido_check 1 chỗ, split_secret 2, mnemonic 1, pqc 4 gồm comment, ml_distinguisher 4), chỉ chạm mã thoát + thông điệp, không sửa logic. Mỗi file đọc trước/sửa/đọc lại.
- Tự kiểm: 4 self-test EXIT=0, pqc nhánh thiếu-lib EXIT=2 đúng chuẩn, 5 nhánh mã 2 kiểm trực tiếp đều đúng.
- Trạng thái: doing -> review (sau khi thử đồng bộ Kanzo dưới đây).

## Kanzo (thử cuối việc, 3 lần cách nhau 5s, timeout 30s)
- `GET /api/board?project=esp32-securitykey` → 500 Internal Server Error cả 3 lần. Không đọc được bảng, không tìm được thẻ mã NCKH-052 → không move/comment được.
- Theo quy tắc: ghi sổ và tiếp tục, KHÔNG tự tạo thẻ. Viện trưởng đối chiếu sổ này khi Kanzo sống lại.
- Trạng thái thẻ mong muốn: doing -> review (báo cáo đã xong ở trên).

## 2026-11-21 — kiểm chéo NCKH-047 (Lâm Bình, ghi chú tuân thủ giấy phép MIT vs AGPL)

- Vai: Trần Cường (NCKH-052) làm lượt kiểm chéo đợt 2C. REPO CHỈ ĐỌC, chỉ nối thêm sổ này. Không git commit. Shell pwsh.
- Nguồn đã đọc: vien-nghien-cuu/so-cai/NCKH-047.md, docs/tuan-thu-giay-phep.md, LICENSE (MIT, Copyright 2026 ESP32-SecurityKey contributors), docs/04-firmware.md (tag v8.2, commit 15b848d821b4995eb1b29a5c2a4c24c25d1a768e, dòng 18 AGPL-3.0), docs/06-bao-mat.md (đối chiếu điểm Secure Boot).
- Đường kiểm độc lập: đối chiếu từng khẳng định trong ghi chú với LICENSE + docs/04-firmware.md, không tin lời 047 mù.

### Đối chiếu từng khẳng định

1. Bảng mục 1 (repo MIT vs pico-fido AGPL-3.0 v8.2 + SHA): khớp 100% LICENSE dòng 1-3 và 04-firmware dòng 11-12, 18. ĐÚNG.
2. MIT được làm (dùng/copy/sửa/gộp/xuất bản/phân phối/sublicense/bán, giữ copyright + LICENSE, không bắt buộc mở source): khớp nguyên văn LICENSE dòng 5-13. ĐÚNG.
3. AGPL tự build/dùng nội bộ thoải mái, chưa đưa binary ra ngoài thì chưa sinh nghĩa vụ: đúng tinh thần AGPL (nghĩa vụ gắn với convey). ĐÚNG.
4. Phân phối binary KỂ CẢ bản gốc chưa sửa phải kèm Corresponding Source (gói cùng hoặc link + đúng SHA + mọi patch): đúng tinh thần AGPL; ghi chú còn sửa rộng điểm 04-firmware dòng 18 viết hẹp ("binary đã sửa") — đây là điểm cộng, không phải lỗi. ĐÚNG.
5. Giữ notice, không gắn thêm hạn chế, flash key giúp người khác = phân phối, điều 13 mạng (ghi rõ với key FIDO hiếm kích hoạt): đúng tinh thần, có ghi phạm vi áp dụng thực tế. ĐÚNG.
6. Không nhúng code AGPL vào repo MIT rồi gắn mác tất cả MIT (phần kết hợp chịu AGPL): đúng tinh thần. ĐÚNG.
7. Không tin tag mù, đối chiếu SHA sau checkout: khớp 04-firmware dòng 16 + quy trình dòng 42-49. ĐÚNG.
8. Checklist build/dùng/phân phối (tặng hay bán đều tính): bao phủ đúng nghĩa vụ đã nêu. ĐÚNG.
9. Điểm Secure Boot + flash encryption vs Installation Information: ghi "chưa chốt, cần ý kiến pháp lý", có căn cứ 06-bao-mat.md (khóa nạp, bịt UART, efuse một chiều). Thái độ đúng, không kết luận bừa. ĐÚNG.
10. Disclaimer "không phải tư vấn pháp lý" ngay đầu + tự khai "chưa đối chiếu toàn văn AGPL từng điều khoản": minh bạch. ĐÚNG.
11. Tự kiểm của 047: file 5791 bytes — Get-ChildItem xác nhận đúng 5791; 3 link (../LICENSE, 04-firmware.md, 06-bao-mat.md) Test-Path True cả 3. ĐÚNG.
12. Phạm vi 1 file mới: 047 giải thích checklist-bring-up-board.md và tom-tat-du-an.md do agent khác tạo song song; không có bằng chứng ngược. CHẤP NHẬN.

### Kanzo (GET board tìm thẻ NCKH-047, cách 5s, timeout 30s, tối đa 2 thử lại)

- GET lần 1: OK (parse `$r.Count` sai vì board là object, bài học giống 047 đã ghi).
- GET lần 2: 500 Internal Server Error.
- GET lần 3: OK, thấy project esp32-securitykey (id 12, open 24, total 69).
- GET lần 4: OK, keys = changes/done_hidden/hidden_properties/projects/statuses/tasks/version.
- GET tìm tasks NCKH-047/thẻ 198 (lần 5 + 2 thử lại): 500 cả 3 lần. Không thấy thẻ nên KHÔNG comment/move mù, KHÔNG tự tạo thẻ.
- Kết quả: chưa comment '[KIEM-DINH] đạt...' và chưa move review->done do Kanzo hỏng. Viện trưởng đối chiếu sổ này.

### Kết luận kiểm chéo: ĐẠT

- 12/12 điểm đối chiếu đúng hoặc chấp nhận được, bảng được/không được đúng tinh thần giấy phép ở mức kỹ thuật.
- Unresolved: (1) Kanzo chưa nhận comment kiểm định + move review->done, cần thử lại khi sống; (2) điểm Secure Boot vs Installation Information vẫn chờ ý kiến pháp lý (047 đã ghi rõ, ngoài phạm vi kiểm kỹ thuật).
