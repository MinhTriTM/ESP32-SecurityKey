# Sổ cái NCKH-048 — Chu Bình (nhóm kiemdinh, đợt 2C)

## 2026-11-21 03:11 — nhận việc
- Nhiệm vụ (theo phan-cong.json): "Báo cáo bao phủ kiểm thử" — Cái gì đã test, cái gì chưa, theo từng tool và firmware (loại t1-tay-chon).
- Đã đọc TRƯỚC khi làm: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0), mục NCKH-048 trong `vien-nghien-cuu/phan-cong.json` (Chu Bình, kiemdinh, kiểm định viên, đợt 2), `vien-nghien-cuu/so-cai/README.md`.
- Phương pháp: đọc từng self-test trong code (7 tool) + firmware + scripts, đối chiếu với sổ cái kiểm định đã có (NCKH-001..044, quét toàn bộ `KIEM-DINH|self-test|bao phu`).
- Ràng buộc: REPO CHỈ ĐỌC (chỉ ghi đúng file sổ cái này), không git commit, shell pwsh.
- Trạng thái: todo -> doing

## 2026-11-21 03:11 — báo cáo bao phủ kiểm thử

### 0. Toàn cảnh (7 tool Python + 1 firmware + scripts)

- `scripts/run_tests.ps1` / `.sh` chạy đúng 7 self-test: fido_check, hid_echo, split_secret, mnemonic, vault, pqc, ml_distinguisher.
- NCKH-006 (nhóm trưởng kiemdinh) đã chạy `run_tests.ps1` tiến trình sạch ngày 2026-11-21: **7/7 xanh, exit 0**. NCKH-011 chạy lại từng tool riêng lẻ: **7/7 xanh, khớp 100%**.
- Kết luận nhanh: tầng self-test xanh toàn bộ, nhưng self-test các tool mới chỉ bao happy-path + vài nhánh lỗi; phần chưa bao nằm ở tầng CLI, đường lỗi hiếm, và toàn bộ runtime phần cứng.

### 1. tools/fido_check.py — self-test mạnh nhất, vẫn thiếu đường lỗi

Self-test gồm 5 khối (đọc code dòng 294-375):
1. Framing gói đơn: INIT/PING, từ chối PING đơn quá 57 byte.
2. Gói nối: 100 byte thành 2 gói, ghép lại đúng.
3. Bóc INIT mẫu (nonce/CID/version/capabilities).
4. CBOR: GetInfo mẫu, lồng nhau, bool/null, gói cụt.
5. Hội thoại đầu-cuối với FakeDevice, cả 2 kiểu report ID (có/không 65/64 byte): INIT -> PING ngắn -> PING dài 100 byte -> GetInfo -> lệnh lạ báo 0x01 -> đọc rỗng timeout.

Đã kiểm ngoài self-test (sổ cái):
- NCKH-004 (rà soát đường lỗi, 3 probe): timeout per-packet, CID gói nối, seq lệch, CTAP2 status giữ code, HID error fallback, `python -O`, `--index` âm, INIT ngắn, gói dài lạ. Kết luận self-test "bao hết happy path".
- NCKH-010 (fuzz cbor_decode, 5639 case): phát hiện TypeError key unhashable (26 case) và RecursionError lồng sâu (4 case) — self-test không bao.
- NCKH-009 kiểm chéo thẻ NCKH-004: ĐẠT.

Chưa test (theo từng mục, đối chiếu NCKH-004):
- S1: timeout gói nối (self-test chỉ bao timeout gói đầu).
- S2: CID sai — cả gói đầu (không caller nào kiểm CID trả về, F1) lẫn gói nối.
- S3: thứ tự seq sai; INIT/ERROR xen giữa gói nối bị báo nhầm thứ tự (F2); seq không wrap mod 128, message > 7609 byte không nhận lại được (F3).
- S4: rút thiết bị giữa chừng (OSError từ hidapi) — FakeDevice không raise OSError; `set_nonblocking` ngoài try (F4).
- S5 (lớn nhất): mọi nhánh lỗi GetInfo/CTAP2 — Ctap2Error, rỗng, non-map, sai lệnh CBOR; nhãn CTAP2_STATUS sai ngữ nghĩa chuẩn (F5); rác đuôi CBOR và bytes/text cụt bị bỏ qua im lặng (F6); CBOR lồng sâu RecursionError (F7).
- F8: assert trong build_*/fragment (mất tác dụng dưới `python -O`, traceback thay vì ValueError).
- U1 lớn nhất: **chưa chạy `main()` trên key vật lý thật** — toàn bộ đường hid thật chưa ai chạy.

### 2. tools/hid_echo.py — self-test mỏng nhất

Self-test chỉ 1 khối (dòng 29-40): đóng gói report 1+64 byte, pad 0, từ chối payload 65 byte.

Đã kiểm ngoài self-test:
- NCKH-016 (probe biên + mock hid, 6/6 biên đóng gói, 6/6 case main qua mock): payload 0/1/59/60/63/64/65/100, echo 65/64 byte, thiết bị câm, echo sai, dài lạ, report ID sai; quét HID thật thấy 2 thiết bị lạ 0xFF00 (không có ESP32); `python -O` làm self-test gốc FAIL (assert bị lược).
- NCKH-009 (parse descriptor độc lập, script riêng): descriptor 36 byte khớp tool/firmware từng trường.
- NCKH-024 kiểm chéo NCKH-016: ĐẠT.

Chưa test:
- `main()` end-to-end với ESP32 thật (U1 của NCKH-016, chưa ai có board) — toàn bộ kiểm main mới qua mock.
- Lọc thiết bị chỉ theo usage_page 0xFF00, không lọc usage/VID/PID (phát hiện NẶNG của NCKH-016): trên máy thật bắt nhầm HIDI2C/AW-ELC — chưa có test chọn đúng thiết bị khi nhiều ứng viên.
- Không kiểm report ID trả về (ID=2 vẫn chấp nhận); 4 byte cuối của report không kiểm tra (PAYLOAD_LEN=60/64).
- Chưa kiểm trên Linux (read 64 hay 65 byte thực tế); chưa đo `_onOutput` với report ID khác 1 hoặc dài hơn 64 byte trên phần cứng thật.

### 3. tools/split_secret.py — self-test tốt tầng toán, hở tầng parse/CLI phụ

Self-test gồm 5 khối (dòng 211-261):
1. Bảng GF(256) đủ 255 giá trị + vector nhân/chia AES (FIPS-197).
2. Round-trip ngẫu nhiên (3,2), (5,3), (5,5), (8,2), mọi tập con K share + thừa share.
3. Thiếu share cho kết quả khác.
4. File share hỏng bị từ chối (3 mẫu).
5. Share trùng x và khác độ dài bị từ chối.

Đã kiểm ngoài self-test:
- NCKH-022 (2 probe, 49 case nhóm A-F + x âm): N=255/K=1/K=N, secret 1 byte/1KB/rỗng, tham số sai, combine lỗi, parse 19 case hỏng, CLI lẫn lộn/thiếu share/file mất/--from-file/--out; phát hiện P1 (KeyError thiếu key -> traceback), P2 (index=-1 cho bí mật SAI LẶNG, nguy hiểm nhất), P3 (index=300 IndexError), P4 (thông điệp int() tiếng Anh), P5 (lẫn 2 lần chia cho rác mà rc=0, giới hạn thiết kế).
- NCKH-026 kiểm định nền GF(256): ĐẠT (khớp vector).
- NCKH-018 kiểm định split_secret: ĐẠT 10/10.

Chưa test:
- Lệnh `qr` (vẽ share thành PNG, dòng 288-304) — self-test và probe NCKH-022 đều không chạm (U2 của NCKH-022).
- Đường nhập tay `getpass` (nhập 2 lần, khớp/rỗng) — chưa ai test (U2 của NCKH-022).
- Các phát hiện P1-P4 chưa có test hồi quy (repo chỉ đọc, chưa sửa code).
- N=255 K=255 với secret 1KB chưa đo (U1 của NCKH-022, ước ~14s).

### 4. tools/mnemonic.py — self-test + vector ngoài mạnh, hở lệnh qr/seed-UX

Self-test gồm 5 khối (dòng 126-167):
1. Bảng từ: đủ 2048, đầu/cuối đúng, tiền tố 4 chữ phân biệt.
2. Vector BIP-39 chuẩn: entropy 16 byte 0 -> `abandon×11 + about`, 2 chiều.
3. Round-trip ngẫu nhiên mọi độ dài 16/20/24/28/32 byte.
4. Cụm hỏng bị từ chối (checksum sai, từ lạ, số từ sai).
5. Seed ổn định 64 byte, nhạy passphrase.

Đã kiểm ngoài self-test:
- NCKH-024: 24/24 vector BIP-39 chuẩn trezor (8 vector 24 từ) KHỚP cả 3 chiều from-entropy/to-entropy/seed-TREZOR (72 lệnh CLI).
- NCKH-016 kiểm chéo: 4/24 vector gõ tay KHỚP cả 3 chiều, nguồn trezor trùng khớp. ĐẠT.
- NCKH-034 (27 case input lạ + CLI): chữ hoa, khoảng trắng/tab/CRLF/NBSP, từ gần đúng, thiếu/thừa từ, sai checksum, đảo thứ tự; phát hiện P1 (input rỗng báo `nhận 1` do `.split(" ")`) và P2 (`seed` im lặng với input hỏng, vẫn exit 0).

Chưa test:
- Lệnh `qr` (dòng 206-221, cần thư viện qrcode) — self-test và probe NCKH-034 đều không chạm.
- Lệnh `new` chỉ mới test `--words 13` (NCKH-034 #26); chưa test sinh thật 12/24 từ + `--out` ghi entropy.
- P1/P2 chưa có test hồi quy (chưa sửa code).
- Không có gợi ý từ gần đúng (ghi nhận, chờ quyết định UX).

### 5. tools/vault.py — self-test gọn, đã đối chiếu chuẩn ngoài, hở chẩn đoán lỗi

Self-test 1 khối (dòng 107-129): round-trip 200 byte, salt/nonce ngẫu nhiên (2 lần mã hóa khác nhau), sai mật khẩu / sửa 1 bit / sai magic đều bị từ chối.

Đã kiểm ngoài self-test:
- NCKH-030 (đối chiếu openssl + Node): PBKDF2-HMAC-SHA256 600k vòng khớp byte openssl `kdf`; AES-GCM ciphertext khớp byte lõi CTR openssl, tag khớp Node.js `node:crypto`; vault mở ciphertext openssl đúng; sửa 1 bit ct/tag, sai magic, sai mk đều từ chối. ĐẠT.
- NCKH-040 (probe két hỏng, API + CLI): két cụt từng đoạn, salt/nonce sai dài, magic sai, mk rỗng/sai, file 0 byte — mọi ca hỏng đều bị từ chối (không lọt), nhưng chỉ có 2 thông điệp nên không phân biệt két cụt với sai mk; phát hiện `encrypt --password-file` rỗng tạo két thành công (không nhất quán với đường gõ tương tác chặn rỗng).
- NCKH-032 chạy lại self-test vault: exit 0.

Chưa test:
- Đường gõ mật khẩu tương tác `getpass` (U1 của NCKH-040, probe phi tương tác không thử).
- CLI `encrypt` file lỗi (file vào không tồn tại/quyền ghi) — mới chỉ test chiều decrypt (C4 của NCKH-040).
- Chưa có test phân biệt "két cụt" (đề xuất báo riêng khi `len < 53`, file 0B báo "file rỗng") — chờ duyệt và sửa code.
- Chưa đo chi phí thử lại mật khẩu sau báo nhầm (PBKDF2 600k vòng, U2 của NCKH-040).

### 6. tools/pqc.py — self-test tầng lib tốt, tầng CLI chưa chạm

Self-test gồm 5 bước (dòng 184-240, chạy trên liboqs thật):
1. Keygen đúng kích thước đọc từ `kem.details` (pk 1184/sk 2400/ct 1088/ss 32).
2. Round-trip encap->decap khớp từng byte.
3. Sai khóa -> từ chối ngầm (ss khác, không khớp lén).
4. Sửa 1 bit ct -> ss khác.
5. Ct cắt ngắn -> ValueError sạch.

Đã kiểm ngoài self-test:
- NCKH-006 (kiểm chéo thẻ 138, thực thi trên liboqs 0.16.0): probe 4 ca sai cỡ (chỉ ValueError), vòng CLI thật keygen->encap->decap + alias encap/decap PASS, nhánh đọc lỗi sạch, nhánh ghi lỗi traceback (FileNotFoundError/FileExistsError), traversal `--prefix ../` ghi ra ngoài out-dir, không có chmod `.sk`. Xác nhận 3/4 điểm của NCKH-001, hiệu chỉnh điểm 2 xuống NHẸ.
- NCKH-043 (kiểm chéo độc lập, script chỉ `import oqs`): 50 vòng round-trip + 12 ca lỗi + luồng CLI file + SHA256 ss khớp; đối chiếu self-test khớp 100%, phủ thêm ngẫu nhiên hóa encap, tất định decap, ct thừa, sk/pk sai cỡ, kiểu sai, rỗng, tên sai. Tự kiểm 21/21 ĐẠT.
- NCKH-035 kiểm chéo NCKH-043: script oqs trực tiếp 8/8 ĐẠT (oracle FIPS 203 độc lập) + self-test 5/5 PASS. ĐẠT.
- NCKH-001 (đọc tĩnh, 297 dòng): đúng API oqs bản 0.16, đúng mã thoát 2; kết luận tool KHÔNG ĐẠT có điều kiện (đọc/ghi mất đối xứng, self-test chưa chạm CLI, `.sk` không chmod, prefix traversal).

Chưa test (chưa có test hồi quy trong repo vì chưa sửa code):
- Tầng CLI hoàn toàn vắng mặt trong self-test: keygen/encap/decap qua file, `_read_exact` lệch cỡ/rỗng/không tồn tại, alias encap/decap (NCKH-006 đã chạy tay ngoài repo, nhưng không thành test tự động).
- Nhánh ghi lỗi OSError (đĩa đầy/quyền/thư mục cha) — hiện traceback, chưa test sau sửa.
- `chmod 0o600` cho `.sk` và chặn prefix `../` — chưa sửa nên chưa test.
- Self-test bước 5 chỉ bắt ValueError (đề nghị gộp thêm RuntimeError cho bền bản liboqs khác 0.16).
- Chưa assert `length_shared_secret == 32` theo FIPS 203 và tính ngẫu nhiên encap (2 lần encap cùng pk ra ct khác) trong self-test.
- Mâu thuẫn tài liệu vị trí DLL (`.tooling/oqs` vs `_oqs` trong home) chưa chốt.

### 7. tools/ml_distinguisher.py — self-test + tái hiện + kiểm chéo 3 lớp, đầy nhất

Self-test (dòng 261-278): vector Speck (KHOP k0=tu-cuoi, ghi "chưa xác nhận độc lập"), round-trip 200 mẫu × R=5,22, micro-train R=5 400 mẫu 1 epoch (chỉ kiểm acc trong [0,1]).

Đã kiểm ngoài self-test:
- NCKH-002: full run R=5/6/7 khớp tuyệt đối tài liệu (0.5970/0.5245/0.5070), chạy lặp bit-identical. Tái hiện thành công.
- NCKH-032 (kiểm chéo Speck, 3 trụ): vector khớp Gohr deep_speck (k0=từ cuối -> a868/42f2, đảo khóa lệch đúng kỳ vọng, decrypt ngược đúng); round-trip R=1..22 tổng 4420 case lỗi 0 (tool gốc chỉ R=5,22); implement độc lập thứ hai khớp tool. ĐẠT.
- NCKH-040 kiểm chéo NCKH-032: cài đặt độc lập THỨ BA (R=9, seed khác, 1007 case) hội tụ cùng đáp án. ĐẠT.
- NCKH-044 (pipeline dữ liệu): cân bằng lớp (n chẵn 50/50, n lẻ lệch 1), rò rỉ train→test (trùng 0 mọi R, đối chứng cùng seed trùng 200/200), seed cố định tái hiện bit-identical, chia tập đúng kích thước CLI. ĐẠT cả 4 điểm.
- NCKH-036 kiểm chéo NCKH-044: seed khác 777 trùng 0. ĐẠT.
- NCKH-001 kiểm chéo NCKH-008 (R=7 50k mẫu): seed khác vẫn đoán mò, σ=0.011 tính lại đúng. ĐẠT.
- NCKH-030 kiểm chéo NCKH-038 (R=8): mẫu độc lập seed 777 đoán mò, ước tính R=9 đứng vững. ĐẠT.

Chưa test / còn nợ:
- Trạng thái vector trong code (`TEST_KEY_WORDS` "chưa xác nhận") và `docs/research/06` chưa cập nhật thành "khớp Gohr deep_speck (k0=từ cuối)" dù đã có 3 cài đặt độc lập hội tụ (U2 của NCKH-032/040 — việc tài liệu, không phải test).
- Self-test micro-train không assert ngưỡng acc (chỉ kiểm 0<=acc<=1) — cố ý vì acc nhiễu, nhưng nghĩa là self-test không bắt được hồi quy chất lượng mô hình.
- Pipeline chỉ có train/test, chưa có tập validation (ghi nhận của NCKH-044).
- Chưa test tham số CLI lỗi (`--rounds` sai định dạng/ngoài [1,22] mới đọc code, chưa chạy).

### 8. firmware/hwtest (hwtest.ino + README) — build + đọc tĩnh kỹ, runtime = 0

Đã kiểm (không có self-test trên thiết bị; kiểm từ máy tính):
- NCKH-012: build sạch từ cache trống cả 2 chế độ — OTG 372633B flash/55680B RAM, HWCDC 302765B/22784B, khớp README, không error/warning. [KIEM-DINH] đạt.
- NCKH-003 (rà soát 154 dòng): descriptor đúng, không tràn `echoBuf` (clamp+pad), phát hiện chính race `echoPending`/`echoBuf` (mất echo/frame rách khi OUT dồn dập), `SendReport` false nuốt lặng, thiếu debounce BOOT.
- NCKH-009: parse descriptor độc lập khớp từng trường với tool.
- NCKH-016: đối chiếu firmware-tool khớp (cả hai đều bỏ qua report ID — nhất quán nhưng lỏng).
- NCKH-008 kiểm chéo (theo sổ 003): kiểm định đạt.
- Runbook nạp Windows (NCKH-015, kiểm chéo NCKH-023: KHÔNG ĐẠT lần 1 vì sai board/BOOT → duyệt lại ĐẠT) và Ubuntu (NCKH-021, kiểm chéo NCKH-013/033/041): mới đối chiếu tài liệu với script/board, chưa chạy thật.

Chưa test (toàn bộ runtime trên board thật — KHÔNG ai trong Viện có phần cứng trong phiên):
- Nạp thật + log Serial (chip/flash/PSRAM/USB mode/heartbeat) + nhấn BOOT + LED xanh lá/xanh dương — tiêu chí "Kết quả đạt" trong README chưa ai chạy.
- HID echo end-to-end (`hid_echo.py` main) trên cổng native.
- Race P1 của NCKH-003 (OUT dồn dập mất echo/frame rách) và `SendReport` false — mới phân tích tĩnh.
- `_onOutput` với report ID khác 1 / dài hơn 64 byte trên phần cứng thật.
- `scripts/flash_win.ps1` / `flash_linux.sh` chưa chạy lần nào (không board).
- `scripts/build_hwtest.ps1` chỉ build OTG (NCKH-005 ghi chú; muốn HWCDC phải sửa FQBN tay) và chưa ai chạy end-to-end qua chính script (NCKH-012 gọi arduino-cli trực tiếp); `build_hwtest.sh` chưa chạy trên Linux thật.

### 9. Bảng bao phủ tổng hợp

| Mục | Self-test | Kiểm độc lập (sổ cái) | Chưa test |
|---|---|---|---|
| fido_check | 5 khối, happy-path đầy | NCKH-004 (lỗi), NCKH-010 (fuzz 5639) | S1-S5 (timeout nối, CID, seq, rút TB, lỗi GetInfo), F5-F8, main trên key thật |
| hid_echo | 1 khối đóng gói | NCKH-016 (biên+mock), NCKH-009 (descriptor) | main với ESP32 thật, lọc VID/PID, report ID trả về, Linux |
| split_secret | 5 khối (GF+round-trip) | NCKH-022 (49 case), NCKH-026, NCKH-018 | lệnh qr, getpass, hồi quy P1-P4, N255/K255/1KB |
| mnemonic | 5 khối (BIP-39) | NCKH-024 (24 vector), NCKH-034 (27 case), NCKH-016 xcheck | lệnh qr, new+--out, hồi quy P1-P2 |
| vault | round-trip + từ chối | NCKH-030 (openssl/Node), NCKH-040 (két hỏng) | getpass tương tác, encrypt lỗi file, báo "két cụt", đo PBKDF2 |
| pqc | 5 bước trên liboqs | NCKH-001/006/043/035 | self-test tầng CLI, ghi OSError, chmod sk, chặn ../, FIPS assert |
| ml_distinguisher | vector+round-trip+micro | NCKH-002/032/040/044/036/001/030 | cập nhật trạng thái vector, ngưỡng acc, validation set, CLI lỗi |
| firmware hwtest | không có (kiểm từ PC) | NCKH-012 (build 2 chế độ), NCKH-003/009/016 (tĩnh) | toàn bộ runtime board thật, flash_*.sh/ps1, build script e2e |
| scripts/run_tests | chính nó là runner | NCKH-006 (ps1 PASS), NCKH-043 (đối chiếu nội dung) | run_tests.sh chưa chạy trên Linux thật |

### 10. Đối chiếu chéo: self-test có nói thật không

- pqc: NCKH-043 đối chiếu độc lập khớp 100% (5/5 self-test = 50 vòng + 12 ca lỗi + CLI). Self-test nói thật ở tầng lib.
- mnemonic: NCKH-024 chạy 24 vector chuẩn qua CLI thật, khớp 100%. Self-test + tool nói thật.
- vault: NCKH-030 khớp byte openssl/Node cả key lẫn ct lẫn tag. Self-test + thuật toán nói thật.
- split_secret: NCKH-022 round-trip mọi biên N/K đúng; NCKH-026 khớp vector AES. Tầng toán nói thật; tầng parse nói dối ở 4 điểm (P1-P4).
- fido_check: NCKH-004 xác nhận happy-path thật, đường lỗi thật nhưng self-test không bao; NCKH-010 chứng minh 30/5639 case crash sai loại. Self-test nói thật trong phạm vi hẹp của nó.
- hid_echo: NCKH-016 chứng minh self-test đúng nhưng mỏng; `python -O` làm self-test gốc fail. Nói thật khi chạy thường, im lặng khi `-O`.
- ml: NCKH-002 tái hiện bit-identical; 3 cài đặt Speck độc lập hội tụ. Nói thật.
- firmware: build số liệu khớp README (NCKH-012); descriptor khớp tool (NCKH-009). Phần tĩnh nói thật; phần runtime chưa ai nghe.

### 11. Unresolved của báo cáo này

- U1: Báo cáo tổng hợp từ đọc code + sổ cái, KHÔNG chạy lại self-test (NCKH-006/011 đã chạy 7/7 xanh cùng ngày; tránh trùng việc theo Hiến chương "một việc một chủ").
- U2: Toàn Viện chưa ai có board/key vật lý — mọi mục "chưa test" phần cứng dồn cho đợt có phần cứng.
- U3: Kanzo chập chờn — xem mục đồng bộ dưới; sổ cái file này là nguồn sự thật.
- Trạng thái: doing -> review (file; Kanzo xem mục đồng bộ dưới)

## 2026-11-21 03:15 — đồng bộ Kanzo (thẻ 199, opportunistic)
- GET board lần 1: OK, 61 thẻ, thấy `[kiemdinh] Báo cáo bao phủ kiểm thử (NCKH-048)` id 199 ở `todo`.
- MOVE todo->doing: OK ngay lần 1 (status=doing).
- COMMENT [BAO-CAO] (tóm tắt báo cáo + trỏ về sổ cái này): HỎNG 3/3 (lần đầu + 2 thử lại, cách 5s, timeout 30s) — HTTP 500 cả 3 lần.
- MOVE doing->review: HỎNG 3/3 — HTTP 500 cả 3 lần.
- VERIFY GET board sau đợt: HỎNG (500) — không đối chiếu được; theo Hiến chương §6, lỗi 500 không đồng nghĩa server chưa ghi nên comment/move có thể đã lọt một phần.
- Lưu ý: lần move đầu có 1 lỗi cú pháp client (`$i:` thiếu `{}`) chưa chạm server — không tính vào quota, đã sửa và thử lại thành công.
- Nhờ Viện trưởng khi Kanzo sống lại: đối chiếu thẻ 199 (trạng thái thật + số comment), vá giúp comment [BAO-CAO] (nội dung như lệnh đã thử) và move lên `review` nếu còn kẹt. Sổ cái file này là nguồn sự thật.
- Trạng thái bảng (xác nhận được): thẻ 199 ở `doing`; mục tiêu `review` còn treo do nghẽn SQLite.

## 2026-11-21 03:30 — kiểm chéo đợt 2C thẻ NCKH-055 (Hoàng Cường): ĐẠT

- Phạm vi: kiểm độc lập công việc "cài liboqs trên môi trường sạch" của NCKH-055
  (sổ `vien-nghien-cuu/so-cai/NCKH-055.md`). Luận điểm chính cần kiểm: pip OK
  nhưng import gãy vì thiếu DLL/native toolchain (thiếu cmake + MSVC).
- Phương pháp: ĐƯỜNG KHÁC — không chạy lại `import oqs` (đường của NCKH-055) mà
  xác nhận từng luận điểm bằng chứng cứ độc lập: (1) `Get-Command` toolchain,
  (2) đọc tĩnh mã nguồn `oqs/oqs.py` trong venv sạch, (3) đối chiếu `load_oqs`
  trong `tools/pqc.py` + `requirements-pqc.txt`.

### Xác minh độc lập (tự làm, shell pwsh)

1. Toolchain (lệnh `Get-Command cmake,cl,msbuild,git,ninja`):
   - `cmake`: KHÔNG có. `cl`: KHÔNG có. `msbuild`: KHÔNG có.
   - `git`: CÓ (`C:\Program Files\Git\cmd\git.exe`). `ninja`: CÓ
     (`Python313\Scripts\ninja.exe`). Khớp 100% sổ NCKH-055.
2. MSVC qua vswhere (đường dẫn cố định, vì `vswhere` không có trên PATH):
   - `vswhere -requires Microsoft.VisualStudio.Component.VC.Tools` → trả RỖNG
     (khớp sổ NCKH-055); không filter → `C:\Program Files\Microsoft Visual
     Studio\18\Community` (VS đã cài nhưng thiếu workload C++).
   - Điểm tinh tế phát hiện thêm: file `cl.exe` 14.44.35207 TỒN TẠI trên đĩa
     (`VC\Tools\MSVC\...`) nhưng không đăng ký component + không trên PATH nên
     cmake (kể cả nếu có) cũng không dò được compiler nếu không setup tay
     (vcvars/PATH). Kết luận thực tế của NCKH-055 ("có cmake thì build vẫn hỏng
     ở bước biên dịch C") vẫn ĐÚNG, chỉ cần hiểu chính xác là "compiler không
     dùng được" thay vì "file compiler vắng mặt".
3. Đọc tĩnh `oqs/oqs.py` trong venv sạch `$env:TEMP/nckh055-venv` (KHÔNG chạy import):
   - `_install_liboqs` (dòng 180): vòng lặp
     `(clone_cmd, configure_cmd, build_cmd, install_cmd)` (dòng 241),
     `configure_cmd[0] == "cmake"` (dòng 217-218) → clone xong rồi chết
     `FileNotFoundError` tại dòng 242 KHỚP ĐÚNG thiếu `cmake`. Suy luận nguyên
     nhân của NCKH-055 được chứng minh bằng code, không chỉ bằng log chạy.
   - `OQS_INSTALL_PATH` được tôn trọng (dòng 250-251) → cách sửa 2 có cơ sở code.
   - `pip show liboqs-python` trong venv: `0.16.0.2`, khớp sổ.
4. Đối chiếu `tools/pqc.py` + `requirements-pqc.txt`:
   - `load_oqs` (dòng 48-77) gom đúng 3 kiểu hỏng oqs (ImportError/RuntimeError/
     SystemExit) và thông điệp hướng dẫn khớp cả 2 cách sửa của NCKH-055
     (cài CMake + VS C++ để tự build vào `%USERPROFILE%\_oqs`, hoặc
     `OQS_INSTALL_PATH` trỏ DLL build sẵn). Docstring dòng 16-22 và comment
     trong `requirements-pqc.txt` cũng ghi cùng 2 cách. Cách sửa đề xuất là ĐỦ
     và nhất quán với tài liệu repo.
   - `$HOME/_oqs` chưa tồn tại, `.tooling/oqs/bin/oqs.dll` tồn tại → khớp sổ
     (build chết trước bước install; DLL cứu hộ có sẵn).
5. Không ai có phần cứng liên quan; không chạy build (đúng giới hạn).

### Kết luận kiểm chéo: ĐẠT

- Mọi luận điểm chính của NCKH-055 đều đứng vững trước xác minh độc lập bằng
  đường khác: pip OK (0.16.0.2), import gãy đúng vì thiếu cmake (chứng minh bằng
  code dòng 217-242), thiếu MSVC dùng được (vswhere rỗng), 2 cách sửa đủ và khớp
  tài liệu repo. Điểm tinh tế về cl.exe trên đĩa không đổi kết luận.
- Đánh giá cách sửa: ĐỦ. Cách 1 (CMake + VS Build Tools C++ rồi import một lần)
  sửa gốc; cách 2 (DLL sẵn + `OQS_INSTALL_PATH`) là đường tắt hợp lệ đã được
  NCKH-055 kiểm chứng (`oqs_version 0.16.0`, 38 KEM, ML-KEM-768 bật).

### Đồng bộ Kanzo (thẻ 209, chập chờn đúng như báo)

- GET board lần 1: OK (69 tasks). Thấy thẻ 209 `[PQC] Cài liboqs trên môi trường
  sạch (NCKH-055)` ở `todo` — mô tả ghi "Nguoi kiem cheo: NCKH-048 (khac nhom)"
  nên đây đúng là thẻ của mình kiểm. (NCKH-055 không thấy thẻ này lúc 03:20 vì
  thẻ mới tạo sau đó — `created_at 2026-11-20T20:24:39Z`.)
- Ghi chú: thẻ 201 `[ML] Benchmark CPU vs GPU (NCKH-050)` đã sang `review`
  (lúc NCKH-055 đọc còn ở `todo`); việc kiểm chéo thẻ 201 là của NCKH-055, không
  thuộc phạm vi lượt này nên KHÔNG chạm.
- COMMENT `[KIEM-DINH] ĐẠT + lý do` lên 209: đợt 1 HỎNG 3/3 (HTTP 500).
- MOVE 209 `todo->done` (thẻ chưa từng qua doing/review; verdict ĐẠT nên đích là
  `done`, đi thẳng 1 bước thay vì 2 bước giữa server chập chờn): OK ngay lần 1,
  VERIFY GET board OK, `status=done`, nhưng `comments=0` → comment đợt 1 rớt thật.
- COMMENT đợt 2 (server đã đáp lại): lần 1 HỎNG 500, lần 2 OK (comment id 122).
- Kết quả cuối (đã xác minh): thẻ 209 ở `done`, có comment kiểm định id 122.
- Mọi lệnh cách nhau 5s, timeout 30s, tối đa 2 thử lại/đợt; KHÔNG tự tạo thẻ.

### Unresolved của lượt kiểm chéo này

- U1: Không chạy lại `import oqs` thuần (cố ý — kiểm bằng đường khác; NCKH-055
  giữ venv tại `$env:TEMP/nckh055-venv` để ai cần chạy lại).
- U2: Không kiểm chứng thực tế cách sửa 1 (cài CMake + VS C++) vì vượt phạm vi
  kiểm chéo (cài phần mềm hệ thống); chỉ đánh giá đủ trên cơ sở code + tài liệu.
- U3: Thẻ 199 của chính mình (báo cáo bao phủ) vẫn kẹt mục tiêu `review` (xem
  mục trên) — nhờ Viện trưởng vá khi Kanzo ổn định.
