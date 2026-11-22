# Sổ cái NCKH-040 — Lý Bình (nhóm tooling, đợt 2B)

## 2026-11-21 02:22 — nhận việc
- Nhiệm vụ: Rà soát vault file hỏng (loại t1-tay-chon)
- Mô tả: Két cụt, salt/nonce sai dài, magic sai, mật khẩu rỗng.
- Nguồn đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-040), vien-nghien-cuu/so-cai/README.md, tools/vault.py
- Kế hoạch: repo chỉ đọc, không git commit; probe riêng trong $env:TEMP phủ két cụt từng đoạn, salt/nonce sai dài, magic sai, mật khẩu rỗng/sai, file 0 byte; đối chiếu thông điệp lỗi có rõ và phân biệt được các ca không; ghi sổ TRƯỚC rồi mới đồng bộ Kanzo.
- Trạng thái: todo -> doing

## 2026-11-21 02:22 — báo cáo rà soát tools/vault.py với file hỏng
- Đã làm: đọc tools/vault.py (định dạng két MAGIC 9B `ESKVAULT1` + salt 16B + nonce 12B + cipher; header HDR = 37B). Viết probe riêng `$env:TEMP\nckh040_vault_probe.py` tạo két chuẩn (GOOD len 95B, cipher 58B, plain 42B) rồi thử API `decrypt_bytes` và CLI `decrypt --password-file` trên các ca hỏng. Probe phụ `$env:TEMP\nckh040_nonce_probe.py` soi ngoại lệ gốc bị nuốt. Không sửa file repo nào.
- Kết luận chính: vault.py chỉ có đúng 2 thông điệp lỗi ValueError nên KHÔNG phân biệt được các ca hỏng. Mọi két cụt (dù cụt trong salt, trong nonce, thiếu cipher, hay mất 1B tag cuối) đều báo y hệt sai mật khẩu, rất dễ khiến người dùng nhập lại mật khẩu vô ích trong khi file đã cụt. File 0 byte lại báo "sai magic" gây hiểu lầm. Đường `encrypt --password-file` chấp nhận mật khẩu rỗng (tạo két mở được bằng rỗng), trong khi đường gõ tương tác thì chặn rỗng — không nhất quán.
- Tự kiểm:
  - `python $env:TEMP\nckh040_vault_probe.py` -> exit 0, toàn bộ ca đều bị từ chối đúng (không ca hỏng nào giải mã lọt), nhưng thông điệp gộp (xem bảng dưới).
  - `python $env:TEMP\nckh040_nonce_probe.py` -> nonce < 8B gốc là `ValueError: Nonce must be between 8 and 128 bytes`, nonce sai/cipher cụt gốc là `InvalidTag` rỗng — cả hai đều bị `except Exception` ở decrypt_bytes nuốt thành một câu chung.
  - `python tools/vault.py --self-test` -> exit 0, "self-test ok: mã hóa/giải mã đúng, sai mật khẩu và file sửa bị từ chối."
- Trạng thái: doing -> review (chờ peer review)

### Bảng ca hỏng (API decrypt_bytes, GOOD 95B, HDR 37B)
| # | Ca | Blob | Kết quả | Thông điệp |
|---|----|------|---------|------------|
| 1 | Baseline đúng mk | 95B chuẩn | OK, khớp plain | (không lỗi) |
| 2 | File 0 byte | 0B | ValueError | file không phải két của tool này (sai magic) — GÂY HIỂU LẦM, đáng lẽ báo file rỗng |
| 3 | Cụt 1B / 8B | magic dở | ValueError | sai magic (đúng nhóm, nhưng không nói "cụt") |
| 4 | Chỉ magic 9B | thiếu salt+nonce+cipher | ValueError | sai mật khẩu hoặc file bị sửa đổi — GÂY HIỂU LẦM |
| 5 | Magic sai (9B `XX..`, text lạ, lệch 1 bit đầu/giữa) | 9–95B | ValueError | sai magic — RÕ, phân biệt được duy nhất |
| 6 | Cụt trong salt (10/15/24B) | salt thiếu | ValueError | sai mật khẩu hoặc file bị sửa đổi — KHÔNG phân biệt |
| 7 | 25B = MAGIC+salt, thiếu toàn bộ nonce | salt đủ, nonce rỗng | ValueError | sai mật khẩu hoặc file bị sửa đổi — KHÔNG phân biệt |
| 8 | Cụt trong nonce (26/30/36B) | nonce thiếu 11/6/1B | ValueError | sai mật khẩu hoặc file bị sửa đổi — KHÔNG phân biệt |
| 9 | Header đủ 37B, cipher rỗng | thiếu toàn bộ cipher+tag | ValueError | sai mật khẩu hoặc file bị sửa đổi — KHÔNG phân biệt |
| 10 | Cụt cipher/tag (38/52/53/78/94B) | cipher dở | ValueError | sai mật khẩu hoặc file bị sửa đổi — KHÔNG phân biệt |
| 11 | Sai mật khẩu | 95B chuẩn + mk sai | ValueError | sai mật khẩu hoặc file bị sửa đổi — đúng nhưng TRÙNG với mọi ca cụt |
| 12 | Mật khẩu rỗng | 95B chuẩn + b"" | ValueError | sai mật khẩu hoặc file bị sửa đổi — đúng (từ chối) nhưng TRÙNG ca cụt |
| 13 | Lật 1 bit salt/nonce/cipher/tag cuối | 95B, 6 vị trí | ValueError | sai mật khẩu hoặc file bị sửa đổi — từ chối đúng, không chỉ vị trí (chấp nhận được về an toàn) |
| 14 | Thêm 1B rác cuối | 96B | ValueError | sai mật khẩu hoặc file bị sửa đổi — từ chối đúng |

### Bảng ca CLI (`decrypt --password-file`, exit code + stdout)
| # | Ca | Kết quả |
|---|----|---------|
| C1 | Baseline | exit 0, "Đã giải mã ra ..." |
| C2 | 0 byte / magic sai | exit 1, "Không mở được két: file không phải két của tool này (sai magic)" |
| C3 | Cụt 10B / 25B / header-only 37B / cụt 1B cuối | exit 1, "Không mở được két: sai mật khẩu hoặc file bị sửa đổi" — trùng C5 |
| C4 | File vào không tồn tại | exit 1, "Không đọc được két: [Errno 2] No such file..." — RÕ, phân biệt được |
| C5 | Sai mk / mk rỗng | exit 1, "Không mở được két: sai mật khẩu hoặc file bị sửa đổi" — trùng C3 |
| C6 | `encrypt --password-file` rỗng | exit 0, TẠO KÉT THÀNH CÔNG, két mở được bằng mk rỗng — KHÔNG NHẤT QUÁN với đường gõ tương tác (read_password confirm=True chặn rỗng, "Hai lần nhập không khớp hoặc rỗng.") |

### Đối chiếu thông điệp lỗi
- Chỉ 2 câu ValueError cho ~15 tình huống khác nhau: (a) "sai magic" khi `blob[:9] != MAGIC` (kể cả file rỗng!), (b) "sai mật khẩu hoặc file bị sửa đổi" cho mọi `except Exception` quanh AESGCM — gồm nonce ngắn (gốc ValueError), tag sai (gốc InvalidTag rỗng), salt ngắn (PBKDF2 nhận mọi dài salt nên thành sai key thầm lặng).
- `decrypt_bytes` không kiểm tra `len(blob)` tối thiểu (tối thiểu phải là HDR + 16B tag = 53B) trước khi cắt lát, nên "salt/nonce sai dài" về bản chất chỉ là két cụt — code không có khái niệm dài sai vì định dạng dài cố định, và cũng không báo tách riêng.
- Gộp "sai mk + sửa 1 bit" làm một là ĐÚNG về an toàn (tránh oracle), nhưng gộp cả "két cụt" vào là SAI về chẩn đoán: cụt file kiểm được bằng độ dài mà không lộ gì về key.
- Đề xuất (không sửa code vì repo chỉ đọc, để chủ tool quyết): (1) nếu `len(blob) < HDR + 16` báo riêng "file cụt/thiếu (độ dài X, tối thiểu 53)"; (2) file 0B báo riêng "file rỗng"; (3) chặn mật khẩu rỗng ở nhánh `--password-file` như nhánh tương tác (hoặc bắt `--allow-empty-password` tường minh); (4) giữ gộp sai-mk/sửa-bit.

### Unresolved
- U1: Chưa thử đường gõ mật khẩu tương tác (getpass) vì probe phi tương tác — chỉ suy từ code `read_password` rằng encrypt chặn rỗng còn decrypt cho qua (đúng vì decrypt không confirm).
- U2: Chưa đo PBKDF2 600k vòng có làm việc thử lại mật khẩu sau báo nhầm "sai mật khẩu" cho file cụt tốn bao lâu — ngoài phạm vi rà soát thông điệp.
- U3: Đề xuất tách thông điệp "két cụt" chỉ là kiến nghị, chưa được chủ tool/Hội đồng duyệt; repo chỉ đọc nên không vá.
- U4: Kanzo chập chờn — xem mục đồng bộ dưới; nếu hỏng thì sổ file này là bản chính.

## 2026-11-21 02:23 — đồng bộ Kanzo (opportunistic, không thấy thẻ)
- GET board: OK ngay lần 1 (timeout 30s, không cần thử lại), 32 thẻ project esp32-securitykey; grep `NCKH-040` trong toàn bộ JSON = không trùng. Chữ `vault` duy nhất nằm ở mô tả thẻ 145 (khuyến nghị ML-KEM cho vault, của NCKH-007) — không liên quan.
- Move/comment: KHÔNG thực hiện — không có thẻ mang mã NCKH-040 để move/comment; theo lệnh KHÔNG tự tạo thẻ.
- Ghi chú cho Viện trưởng: việc "Rà soát vault file hỏng" của NCKH-040 chưa có thẻ Kanzo riêng; sổ cái file này là nguồn chính, trạng thái tự nhận doing -> review.

## 2026-11-21 02:34 — kiểm chéo NCKH-032 (Vũ Bình, Speck) — ĐẠT
- Vai: Lý Bình (NCKH-040, nhóm tooling) làm lượt kiểm chéo đợt 2B cho NCKH-032 Vũ Bình (nhóm ML), khác nhóm, kiểm độc lập bằng đường khác.
- Tài liệu đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-032.md` (3 trụ + mục Kanzo), `vien-nghien-cuu/HIEN-CHUONG.md` §6 (API Kanzo). KHÔNG đọc `tools/ml_distinguisher.py`, KHÔNG đọc/chạy script `$env:TEMP/NCKH-032-*` của tác giả — giữ độc lập tuyệt đối.
- Cam kết repo: CHỈ ĐỌC, trừ nối thêm chính file sổ cái này; không git commit; mọi script kiểm trong `$env:TEMP`; mọi lệnh `muse.powershell` kèm `shell="pwsh"`.
- Đường kiểm độc lập (tự viết, không dùng tool/script tác giả):
  - File `$env:TEMP/NCKH-040-speck-rieng.py`: cài đặt Speck32/64 từ đặc tả Beaulieu et al. (n=16, m=4, T=22, alpha=7, beta=2; hàm `xoay_phai_16/xoay_trai_16/dan_lich_khoa/ma_hoa_mot_khoi/giai_ma_mot_khoi`, tên và cấu trúc khác tác giả; khóa vào theo thứ tự tài liệu, từ CUỐI là k0).
  - Vector chuẩn: khóa tài liệu (0x1918,0x1110,0x0908,0x0100), pt (0x6574,0x694c) -> ct chuẩn (0xa868,0x42f2), full 22 vòng, cả 2 thứ tự khóa + giải mã ngược.
  - Round-trip với seed riêng: R=9 (1 R, khác R=5,22 của tool gốc), seed=40040 (khác 32032 của tác giả), 1000 cặp khóa/bản rõ ngẫu nhiên + 7 cặp biên (toàn 0, toàn FFFF, hỗn hợp, bit đơn, xen kẽ AA/55) = 1007 case.
- Kết quả chạy (`python $env:TEMP/NCKH-040-speck-rieng.py`, Python 3.12.0, EXIT=0):
  - Vector k0=từ cuối -> ct (a868,42f2) KHỚP chuẩn; rk0=0100 rk21=ed64.
  - Vector k0=từ đầu (đảo khóa, k0=0x1918) -> ct (8b78,ab2e) LỆCH chuẩn (đúng kỳ vọng: chỉ một thứ tự đúng).
  - Giải mã ngược ct chuẩn (k0=từ cuối) -> pt (6574,694c) KHỚP.
  - Round-trip R=9 seed 40040: 1007 case, LỖI=0 -> PASS.
  - Kết luận riêng: PASS.
- Đối chiếu với báo cáo NCKH-032 (02:22):
  - Trụ 1 (vector k0=từ cuối khớp, k0=từ đầu lệch 8b78/ab2e, decrypt ngược đúng): KHỚP HOÀN TOÀN — code riêng của tôi cho cùng ct đúng (a868,42f2), cùng ct sai (8b78,ab2e), cùng rk0=0100 rk21=ed64 mà tác giả ghi. Xác nhận độc lập "k0=từ cuối".
  - Trụ 2 (round-trip 4420 case R=1..22 lỗi 0): HỢP LÝ — số học đúng (22×200+4×5=4420); kiểm riêng của tôi trên R=9/seed khác (1007 case lỗi 0) củng cố, dù không phủ lại toàn bộ 1..22 (đúng tinh thần kiểm bằng đường khác, không chạy lại đúng lệnh tác giả).
  - Trụ 3 (implement độc lập khớp tool 4400 cặp + lịch khóa 22/22): ĐƯỢC CỦNG CỐ — nay có cài đặt độc lập THỨ BA (của tôi) cho cùng vector, cùng cặp rk đầu/cuối và cùng ct sai khi đảo khóa; ba cài đặt hội tụ về một đáp án.
  - Không phát hiện bug, không phát hiện số liệu mâu thuẫn.
- Kết luận kiểm chéo: ĐẠT. Đề nghị Viện trưởng duyệt `review -> done` (thẻ thực tế ở `todo` khi tôi kiểm — xem mục Kanzo dưới); nhắc lại kiến nghị ngoài phạm vi của tác giả (U2: cập nhật trạng thái vector "khớp Gohr deep_speck (k0=từ cuối)" trong docs/research/06 và comment tool).
- Kanzo (xem mục đồng bộ dưới): thấy thẻ id 180, comment `[KIEM-DINH] đạt` OK, move sang `done` OK.

## 2026-11-21 02:34 — đồng bộ Kanzo kiểm chéo NCKH-032: THÀNH CÔNG (thẻ đã done)
- GET board lần 1 (timeout 30s): OK, TOTAL=44, thấy thẻ id 180 `[todo] [ML] Kiểm thử chéo Speck (NCKH-032)` (Viện trưởng đã tạo sau khi tác giả đồng bộ lúc 02:24 không thấy thẻ; thẻ ghi "Nguoi kiem cheo: NCKH-040"). Lưu ý: thẻ ở `todo`, không phải `review` như tác giả dự kiến.
- Comment `[KIEM-DINH] đạt + lý do` lên id 180: lần 1 sau 5s LỖI 500; lần 2 (sau 5s nữa, trong 2 lần thử lại) OK, trả về comment id 55, task_id 180.
- Move id 180 sang `done` (sau 5s, timeout 30s, đạt nên về done): OK ngay lần 1; server trả về status `done`, comments=1, updated_at 2026-11-20T19:33:24Z. Vì thẻ đang ở `todo` chứ không ở `review`, đây là move `todo -> done` (thay vì `review -> done` theo chữ), phản ánh đúng thực tế việc đã xong + đã kiểm chéo đạt.
- Verify GET board sau move: 2 lần đều LỖI 500 (Kanzo chập chờn, đúng như cảnh báo). Dừng theo giới hạn thử lại; lấy response của chính lệnh move (status done) làm bằng chứng, sổ file này là nguồn chân lý.
- Unresolved kiểm chéo:
  - U-C1: GET board verify sau ghi lỗi 500 hai lần liên tiếp — chưa đối chiếu lại được bảng sau move; nhờ Viện trưởng nhìn bảng xác nhận thẻ 180 ở `done` với 1 comment kiểm định (id 55). Nếu server ghi trùng do thử lại, nhờ Viện trưởng xóa comment trùng (chỉ Viện trưởng được xóa/sửa thẻ).
  - U-C2 (kế thừa U2 của tác giả, ngoài phạm vi): trạng thái vector Speck vẫn ghi "chưa xác nhận" trong tài liệu/tool — sau hai lượt độc lập (tác giả + kiểm chéo) đã đủ bằng chứng đổi thành "khớp Gohr deep_speck (k0=từ cuối)".
