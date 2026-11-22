# Sổ cái NCKH-053 — Lê Cường (nhóm tailieu, đợt 2C)

## 2026-11-21 03:10 — nhận việc
- Nhiệm vụ (phan-cong.json): Tóm tắt dự án 1 trang — người mới đọc 5 phút hiểu toàn bộ (loại t1-tay-chon).
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-053 trong phan-cong.json, vien-nghien-cuu/so-cai/README.md, README.md.
- Nguồn đối chiếu số liệu: docs/03, 04, 05, 06, 07, FAQ.md, hardware/BOM.md.
- Kế hoạch: tạo đúng 1 file mới docs/tom-tat-du-an.md, mọi số liệu đối chiếu đúng nguồn. Không git commit.
- Trạng thái: todo -> doing (ghi sổ trước, đồng bộ Kanzo sau).

## 2026-11-21 03:11 — báo cáo
- Đã làm: tạo đúng 1 file mới docs/tom-tat-du-an.md (37 dòng, 1 trang: key là gì, dùng thế nào, khôi phục ra sao, bắt đầu từ đâu). Sửa 1 câu LED cho đúng nguồn ("thường là WS2812").
- Tự kiểm: Select-String đối chiếu commit 15b848d8…/v8.2/ESP-IDF v5.5.1 (04-firmware), N16R8 16MB/8MB (BOM), 12 Mbps + 7 tool (FAQ), Android 9+/5-share-cần-3/32 byte (05, 07) — tất cả khớp nguồn, mỗi đoạn trong file đều ghi nguồn.
- Không git commit theo lệnh.
- Trạng thái: doing -> review (chờ Kanzo bên dưới).

## 2026-11-21 03:11 — đồng bộ Kanzo
- GET /api/board?project=esp32-securitykey, timeout 30s, 3 lần cách nhau 5s: cả 3 lần lỗi 500 Internal Server Error, không đọc được bảng, không tìm được thẻ NCKH-053.
- Theo lệnh: ghi sổ và tiếp tục, KHÔNG tự tạo thẻ, không move/comment.
- Unresolved: thẻ Kanzo chưa đồng bộ (nhận việc doing + báo cáo review) — chờ Viện trưởng vá khi Kanzo sống lại.

## 2026-11-21 03:29 — kiểm chéo đợt 2C: thẻ NCKH-048 Chu Bình (báo cáo bao phủ kiểm thử)
- Vai trò: Lê Cường (NCKH-053) kiểm độc lập báo cáo của NCKH-048 Chu Bình (nhóm kiemdinh).
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-048.md` (toàn bộ, §0-§11 + đồng bộ Kanzo).
- Phương pháp (đường khác với tác giả): tác giả đọc code + tổng hợp sổ cái; tôi xác minh ngẫu nhiên 4 ô trong bảng bao phủ §9 bằng cách mở trực tiếp self-test tương ứng trong code, đối chiếu mô tả từng khối/dòng; kiểm 2 điểm nóng (runtime phần cứng = 0, tầng CLI vắng mặt) bằng nguồn độc lập (sổ cái khác + đọc code); đối chiếu số liệu build với sổ gốc NCKH-012; kiểm `scripts/run_tests.ps1`. REPO CHỈ ĐỌC (chỉ nối thêm file sổ này), không git commit, mọi lệnh shell kèm shell='pwsh'.

### Mẫu xác minh 1/4 — hid_echo (§9: "1 khối đóng gói")
- Mở `tools/hid_echo.py`: `self_test()` đúng dòng 29-40, 1 khối duy nhất: `build_report(b"abc")` assert dài 65 byte (1 byte report ID + 64 byte dữ liệu), `report[0]==REPORT_ID`, pad `b"\x00"*61`, `build_report(bytes(65))` phải ném AssertionError (từ chối payload 65 byte). KHỚP mô tả §2 của tác giả ("đóng gói report 1+64 byte, pad 0, từ chối payload 65 byte"). ĐẠT.

### Mẫu xác minh 2/4 — pqc (§9: "5 bước trên liboqs")
- Mở `tools/pqc.py`: `self_test()` đúng dòng 184-240, 5 bước đánh số 1-5: (1) keygen + assert kích thước đọc từ `kem.details` (không hardcode), (2) round-trip encap->decap khớp từng byte + assert cỡ ct/ss, (3) sai khóa cho ss khác (từ chối ngầm, `!=` assert), (4) sửa 1 bit ct cho ss khác, (5) ct cắt ngắn phải ValueError sạch. KHỚP mô tả §6 (kể cả pk 1184/sk 2400/ct 1088/ss 32 trong docstring dòng 24-26). ĐẠT.

### Mẫu xác minh 3/4 — vault (§9: "round-trip + từ chối")
- Mở `tools/vault.py`: `self_test()` đúng 1 khối dòng 107-129: `os.urandom(200)` round-trip đúng, 2 lần mã hóa khác nhau (salt/nonce ngẫu nhiên), vòng lặp sai mật khẩu + sửa 1 bit đều ValueError, magic `RAC` cũng ValueError. KHỚP mô tả §5 ("round-trip 200 byte, salt/nonce ngẫu nhiên, sai mật khẩu / sửa 1 bit / sai magic đều bị từ chối"). ĐẠT.

### Mẫu xác minh 4/4 — split_secret (§9: "5 khối (GF+round-trip)")
- Mở `tools/split_secret.py`: `self_test()` đúng dòng 211-261, 5 khối đánh số 1-5: (1) bảng exp đủ 255 + vector nhân/chia AES (`_gf_mul(0x53,0xCA)==0x01`), (2) round-trip đúng 4 cặp (3,2),(5,3),(5,5),(8,2) mọi tập con K + thừa share, (3) thiếu share cho kết quả khác, (4) `parse_share` đúng + 3 mẫu hỏng bị từ chối, (5) trùng x và khác độ dài bị từ chối. KHỚP mô tả §3. ĐẠT.

### Điểm nóng 1 — "runtime phần cứng = 0" (firmware §8)
- Kiểm bằng đường khác: tìm kiếm toàn bộ `vien-nghien-cuu/so-cai` cho `board thật|key vật lý|phần cứng|nạp thật|flash_win|flash_linux` (regex). Kết quả: NCKH-003 ("Chưa kiểm chứng runtime trên board thật (không có phần cứng trong phiên này)"), NCKH-004 (U1 "chưa kiểm chứng trên key vật lý thật"), NCKH-008, NCKH-013, NCKH-015, NCKH-021 ("Không build/chạy board (không có phần cứng trong phiên...)"), NCKH-024 (U1 "thiếu board thật"), NCKH-051 — tất cả đồng thanh không có phần cứng, không sổ nào ghi đã nạp/chạy board thật. Không tìm thấy bằng chứng runtime phần cứng nào trái với báo cáo. ĐÚNG.

### Điểm nóng 2 — "tầng CLI vắng mặt trong self-test" (pqc §6)
- Kiểm bằng đường khác: đọc `self_test()` pqc (dòng 184-240) — chỉ gọi `load_oqs/check_alg/alg_details/generate_keypair/encapsulate/decapsulate`, KHÔNG gọi `cmd_keygen/cmd_encapsulate/cmd_decapsulate/_read_exact` và không chạm parser/alias encap/decap. Xác nhận tầng CLI file-based hoàn toàn vắng mặt trong self-test. ĐÚNG. (Phụ: `cmd_qr` của split_secret và `qr` của mnemonic cũng không xuất hiện trong self-test tương ứng — đã thấy khi đọc code mẫu 4 và nhất quán với "lệnh qr chưa chạm" của tác giả.)

### Đối chiếu phụ
- `scripts/run_tests.ps1`: vòng lặp đúng 7 tool `fido_check, hid_echo, split_secret, mnemonic, vault, pqc, ml_distinguisher` — khớp §0 ("chạy đúng 7 self-test"). ĐẠT.
- Số liệu build §8 (OTG 372633B flash/55680B RAM, HWCDC 302765B/22784B): đối chiếu sổ gốc NCKH-012 dòng 22-29 — khớp từng con số, cả 2 exit 0. ĐẠT.
- Không kiểm lại toàn bộ 7 tool và mọi số case fuzz/probe (ngoài phạm vi mẫu 3-4 ô + 2 điểm nóng theo lệnh); các mục S1-S5/F5-F8/U1-U3 ghi nhận nguyên văn, không phát hiện mâu thuẫn nội bộ khi đọc.

### Đồng bộ Kanzo (thẻ NCKH-048, opportunistic)
- GET `http://100.101.100.100:4242/api/board?project=esp32-securitykey` (shell='pwsh', `Invoke-RestMethod`, timeout 30s, mỗi lần cách 5s): lần 1 + 2 thử lại = HỎNG 3/3, HTTP 500 cả 3 lần (đúng triệu chứng SQLite database is locked đã biết).
- Không đọc được bảng nên không tìm được thẻ NCKH-048 (dù sổ tác giả ghi id 199, KHÔNG dám comment/move theo id đoán vì có thể chạm nhầm thẻ người khác), không comment/move được. Theo lệnh: ghi sổ và tiếp tục, KHÔNG tự tạo thẻ.
- Nhờ Viện trưởng khi Kanzo sống lại: tìm thẻ `[kiemdinh] Báo cáo bao phủ kiểm thử (NCKH-048)` của Chu Bình, dán comment `[KIEM-DINH] đạt — Lê Cường (NCKH-053) xác minh độc lập 4/4 ô mẫu (hid_echo 1 khối dòng 29-40, pqc 5 bước dòng 184-240, vault round-trip dòng 107-129, split_secret 5 khối dòng 211-261) khớp code; điểm nóng runtime phần cứng = 0 đúng (NCKH-003/004/008/013/015/021/024/051 đồng thanh không có phần cứng); điểm nóng CLI vắng mặt đúng (pqc self-test không chạm cmd_*/_read_exact); số build khớp NCKH-012, run_tests.ps1 đúng 7 tool` và move thẻ `review` -> `done` (nếu thẻ còn kẹt `doing` do lần move hỏng của tác giả thì move lên `done` qua `review`).

### Kết luận kiểm định: ĐẠT
- Báo cáo của NCKH-048 chính xác trong phạm vi đã kiểm: 4/4 ô mẫu khớp code từng khối/dòng, 2/2 điểm nóng đứng vững qua nguồn độc lập, 2/2 đối chiếu phụ khớp.
- Unresolved của lượt kiểm chéo này: (1) thẻ Kanzo của NCKH-048 chưa được comment/move do Kanzo hỏng 3/3 (xem nhờ Viện trưởng ở trên); (2) các mục S1-S5/F5-F8 và con số fuzz 5639 case của NCKH-010 chưa kiểm độc lập (ngoài phạm vi mẫu theo lệnh).
