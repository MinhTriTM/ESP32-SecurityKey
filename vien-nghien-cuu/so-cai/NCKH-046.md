# Sổ cái NCKH-046 — Hứa Bình (nhóm tooling, đợt 2C)

## 2026-11-21 03:10 — nhận việc
- Nhiệm vụ: Rà soát lệnh qr hai tool (loại t1-tay-chon)
- Mô tả: File không tồn tại, thiếu lib (thử bằng cách đổi tên lib tạm thời).
- Phạm vi theo lệnh: lệnh `qr` của tools/split_secret.py và tools/mnemonic.py — file share/mnemonic không tồn tại, file hỏng, thiếu lib qrcode/pillow (mô phỏng bằng cách đổi tên lib tạm thời trong PYTHONPATH riêng rồi phục hồi, KHÔNG xóa lib thật).
- Nguồn đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-046), vien-nghien-cuu/so-cai/README.md, tools/split_secret.py (308 dòng), tools/mnemonic.py (225 dòng), tools/requirements-qr.txt.
- Kế hoạch: repo CHỈ ĐỌC (không sửa file repo, không git commit, không đụng lib thật trong site-packages); mọi file thử nằm ở $env:TEMP/nckh046-qr; ghi sổ cái này TRƯỚC rồi mới đồng bộ Kanzo.
- Trạng thái: todo -> doing

## 2026-11-21 03:14 — báo cáo
- Đã làm: đọc toàn bộ 2 tool (đặc biệt cmd_qr split_secret.py dòng 288-304, cmd_qr mnemonic.py dòng 206-221) và chạy 17 ca thử có đối chứng, gồm happy path, file thiếu/hỏng, lib thiếu (mô phỏng), thư mục --out thiếu, wordlist thiếu.
- Kết luận chung: lệnh `qr` xử lý ĐẠT các ca file thiếu/hỏng và thiếu qrcode; PHÁT HIỆN 2 lỗi xử lý ngoại lệ (thiếu pillow riêng lẻ và --out vào thư mục không tồn tại đều văng traceback thay vì thông điệp thân thiện, cả 2 tool cùng mắc).

### 1. split_secret.py qr — file share thiếu/hỏng — ĐẠT
- Code: cmd_qr đọc file + parse_share trong try/except (OSError, ValueError) → in "File share lỗi: ..." return 1 (dòng 295-300).
- Chuẩn bị: `python tools/split_secret.py split --shares 3 --threshold 2 --from-file $TEMP/nckh046-qr/secret.txt --out .../shares` → exit 0, 3 share (share-1-of-3.txt 83 byte).
- CA0 happy path: `qr shares/share-1-of-3.txt --out share1.png` → "Đã vẽ QR ra ... share1.png. Quét xong thì xóa file ảnh." exit 0, PNG 1154 byte, mở bằng PIL: PNG (450, 450) mode 1.
- CA1 file không tồn tại: `qr khong-co.txt` → "File share lỗi: [Errno 2] No such file or directory: ..." exit 1.
- CA2 file rác ("rac hoan toan"): → "File share lỗi: file không phải share Shamir của tool này" exit 1.
- CA3 header thiếu tham số + hex sai: → "File share lỗi: phần dữ liệu không phải hex hợp lệ" exit 1.
- CA4 len mismatch (len=14 sửa thành 13): → "File share lỗi: độ dài dữ liệu không khớp header" exit 1.
- CA5 hex CHỮ HOA: parse_share chấp nhận (đúng — code so `y.hex() != lines[1].lower()`, dòng 144). Probe t_upper.py → (3,2,1) upper-ok, exit 0.
- CA6 mặc định --out (không truyền --out): vẽ ra cùng tên đuôi .png (def-test.png 1162 byte), exit 0.
- CA7 file rỗng: → "File share lỗi: file không phải share Shamir của tool này" exit 1.
- CA8 truyền thư mục thay vì file: → "File share lỗi: [Errno 13] Permission denied: ..." exit 1 (bắt được; message hơi khó hiểu trên Windows nhưng chấp nhận được).
- Đối chứng QR đúng nội dung: tái tạo `qrcode.make(text.strip(), M).save(det.png)` cho byte GIỐNG HỆT file tool vẽ (1154 == 1154 byte, giong nhau: True) → QR mã hóa đúng nội dung share đã strip.

### 2. mnemonic.py qr — cụm từ sai — ĐẠT
- Code: cmd_qr chuẩn hóa rồi mnemonic_to_entropy trong try/except ValueError → "Cụm từ sai: ..." return 1 (dòng 213-218).
- MN1 happy path (vector BIP-39 chuẩn 11xabandon+about): → "Đã vẽ QR ra ... mn1.png..." exit 0, PNG 1303 byte.
- MN2 checksum sai (12xabandon): → "Cụm từ sai: sai checksum: gõ nhầm từ hoặc sai thứ tự" exit 1.
- MN3 từ lạ (tu-la): → "Cụm từ sai: từ lạ không có trong bảng BIP-39: tu-la" exit 1 (message hiện từ sau chuẩn hóa lowercase).
- MN4 sai số từ (2 từ): → "Cụm từ sai: số từ phải là [12, 15, 18, 21, 24], nhận 2" exit 1.
- MN5 không truyền từ nào: argparse báo `error: the following arguments are required: words`, exit 2 (ghi chú: trùng mã 2 với ca thiếu-lib nhưng khác kênh — argparse ra stderr kèm usage; xem lưu ý ở mục 4).
- MN6 chữ HOA (ABANDON...ABOUT): chuẩn hóa NFKD+lower nên vẫn vẽ thành công, exit 0.
- MN8 wordlist thiếu: chạy bản sao mnemonic.py ở $TEMP không kèm bip39_english.txt (repo không đụng) → "Bảng từ lỗi: [Errno 2] No such file or directory: ...bip39_english.txt" exit 1 (bắt ở main, áp dụng mọi lệnh kể cả qr).

### 3. Thiếu lib qrcode/pillow — MỘT ĐẠT, MỘT LỖI (cả 2 tool)
- Phương pháp (đúng lệnh, lib thật không đụng): sao chép `qrcode` + `PIL` từ site-packages vào $TEMP/nckh046-qr/fakelibs làm PYTHONPATH riêng; đổi tên bên trong fakelibs để mô phỏng thiếu; chạy `python -S` (bỏ site-packages thật) với PYTHONPATH trỏ fakelibs; xong đổi tên lại (phục hồi) và chạy lại chứng minh hồi phục.
- LIB1 thiếu cả qrcode+PIL (đổi tên cả 2 thành qrcode_AN/PIL_AN): split `qr` → "Thiếu thư viện QR. Chạy: pip install -r requirements-qr.txt" exit 2. ĐẠT.
- LIB1b tương tự với mnemonic `qr` → cùng thông điệp, exit 2. ĐẠT.
- LIB2 CHỈ thiếu pillow (qrcode phục hồi tên, PIL vẫn ẩn): split `qr` → TRACEBACK `ModuleNotFoundError: No module named 'PIL'` (qrcode/image/pil.py dòng 2, gọi từ main.py:364 make_image ← cmd_qr dòng 302), exit 1. LỖI — không thân thiện.
- LIB2b tương tự với mnemonic `qr` → TRACEBACK y hệt (mnemonic.py dòng 219), exit 1. LỖI.
- Nguyên nhân gốc: try/except ImportError chỉ bọc 2 dòng `import qrcode` đầu hàm; còn PIL được qrcode import LƯỜI bên trong make_image lúc vẽ, nằm ngoài khối try — nên thiếu-pillow lọt ra ngoài thành traceback.
- PHỤC HỒI: đổi PIL_AN về PIL trong fakelibs → chạy lại `python -S` cả 2 tool đều exit 0 (restored1.png 1154 byte, restored2.png 1303 byte). Lib thật kiểm tra sau cùng vẫn nguyên vẹn: qrcode + PIL còn đủ trong site-packages, `import` bình thường.

### 4. Lỗi thứ hai: --out vào thư mục không tồn tại — LỖI (cả 2 tool)
- CA9 split `qr share-1-of-3.txt --out nodir/x.png` → TRACEBACK `FileNotFoundError` (PIL/Image.py save ← qrcode pil.py:54 ← cmd_qr dòng 302), exit 1. Không có thông điệp thân thiện.
- MN7 mnemonic tương tự → TRACEBACK y hệt (mnemonic.py dòng 219), exit 1.
- Nguyên nhân gốc: `.save(out)` nằm ngoài mọi try/except OSError; khác với cmd_split (tự mkdir parents) — cmd_qr không tạo thư mục cha.

### 5. Bảng ca lỗi (tóm tắt)
| # | Tool | Ca | Kết quả | Exit | Ghi chú |
|---|------|----|---------|------|---------|
| CA0 | split | happy path | Vẽ PNG 1154B | 0 | ĐẠT |
| CA1 | split | file không tồn tại | Thông điệp thân thiện | 1 | ĐẠT |
| CA2 | split | file rác | Từ chối đúng | 1 | ĐẠT |
| CA3 | split | header thiếu/hex sai | Từ chối đúng | 1 | ĐẠT |
| CA4 | split | len mismatch | Từ chối đúng | 1 | ĐẠT |
| CA5 | split | hex chữ hoa | Chấp nhận (đúng) | 0 | ĐẠT |
| CA6 | split | mặc định --out | Cùng tên .png | 0 | ĐẠT |
| CA7 | split | file rỗng | Từ chối đúng | 1 | ĐẠT |
| CA8 | split | truyền thư mục | Bắt OSError | 1 | ĐẠT (message khó hiểu nhẹ) |
| CA9 | split | --out thư mục thiếu | TRACEBACK FileNotFound | 1 | LỖI |
| LIB1 | split | thiếu qrcode | Thông điệp + hướng dẫn pip | 2 | ĐẠT |
| LIB2 | split | chỉ thiếu pillow | TRACEBACK ModuleNotFound PIL | 1 | LỖI |
| MN1 | mnemonic | happy path | Vẽ PNG 1303B | 0 | ĐẠT |
| MN2 | mnemonic | checksum sai | Từ chối đúng | 1 | ĐẠT |
| MN3 | mnemonic | từ lạ | Từ chối đúng | 1 | ĐẠT |
| MN4 | mnemonic | sai số từ | Từ chối đúng | 1 | ĐẠT |
| MN5 | mnemonic | thiếu tham số words | argparse usage | 2 | Lưu ý: trùng mã 2 với thiếu-lib |
| MN6 | mnemonic | chữ hoa | Chuẩn hóa, vẽ được | 0 | ĐẠT |
| MN7 | mnemonic | --out thư mục thiếu | TRACEBACK FileNotFound | 1 | LỖI |
| MN8 | mnemonic | wordlist thiếu | Thông điệp thân thiện | 1 | ĐẠT |
| LIB1b | mnemonic | thiếu qrcode | Thông điệp + hướng dẫn pip | 2 | ĐẠT |
| LIB2b | mnemonic | chỉ thiếu pillow | TRACEBACK ModuleNotFound PIL | 1 | LỖI |

### 6. Kiến nghị sửa (không tự sửa — repo chỉ đọc, nhiệm vụ chỉ rà soát)
1. Bọc cả khối `qrcode.make(...).save(...)` trong try/except ImportError → in cùng thông điệp "Thiếu thư viện QR..." return 2 (bắt PIL import lười). Áp dụng cả 2 tool.
2. Bọc `.save()` trong try/except OSError → thông điệp thân thiện kiểu "Không ghi được file ảnh: ..." return 1. Áp dụng cả 2 tool.
3. (Tùy chọn) Ghi tài liệu rằng exit 2 vừa là thiếu-lib vừa là lỗi tham số argparse, hoặc chuyển thiếu-lib sang mã riêng.

### Tự kiểm bổ sung
- Lệnh chỉ đọc/không sửa repo: mọi file thử ở $env:TEMP/nckh046-qr (shares, *.png, bad*.txt, fakelibs, toolscopy, t_*.py); không git commit; lib thật trong site-packages kiểm tra còn nguyên sau khi thử.
- Môi trường: Python 3.12.0, qrcode 8.2, pillow 12.3.0, Windows.
- Trạng thái: doing -> review (chờ peer review nhóm khác kiểm độc lập)

## 2026-11-21 03:16 — đồng bộ Kanzo (opportunistic)
- GET board lần 1: OK, 63 thẻ; rà title không có thẻ nào nhắc NCKH-046.
- GET lại lần 2 (sau 5s, timeout 30s): OK, 63 thẻ; rà full JSON (title+description): XÁC NHẬN không có "NCKH-046"/"Hứa Bình"/"lệnh qr".
- Move/comment: KHÔNG thực hiện — không có thẻ của mình để di chuyển; KHÔNG tự tạo thẻ theo lệnh.
- Ghi chú cho Viện trưởng: việc "Rà soát lệnh qr hai tool" của NCKH-046 chưa có thẻ Kanzo riêng; sổ cái file này là nguồn chính. Kết quả rà soát (2 lỗi traceback cần sửa ở cả 2 tool) nằm ở mục báo cáo phía trên.

## Unresolved
- U1: Chưa giải mã ngược ảnh QR bằng bộ giải mã độc lập (pyzbar chưa cài, không cài thêm để tránh thay đổi máy) — đã đối chứng thay thế bằng tái tạo xác định (byte giống hệt).
- U2: Chưa có thẻ Kanzo cho NCKH-046 để chuyển review — chờ Viện trưởng tạo thẻ hoặc chấp nhận sổ file.
- U3: Hai lỗi traceback (LIB2/LIB2b thiếu pillow, CA9/MN7 --out thư mục thiếu) mới ở mức kiến nghị — chưa sửa vì repo chỉ đọc; cần 1 thẻ FIX-tooling và peer review xác nhận.

## 2026-11-21 — kiểm chéo NCKH-053 Lê Cường (tóm tắt dự án 1 trang, đợt 2C)
- Vai: Hứa Bình (NCKH-046) kiểm độc lập bằng ĐƯỜNG KHÁC. Đã đọc: vien-nghien-cuu/so-cai/NCKH-053.md, docs/tom-tat-du-an.md (37 dòng, đúng 1 file mới, không git commit — khớp báo cáo của tác giả).
- Đủ 4 phần yêu cầu: `## Key là gì` (dòng 5), `## Dùng thế nào` (dòng 14), `## Khôi phục ra sao` (dòng 21), `## Bắt đầu từ đâu` (dòng 31). Mỗi đoạn đều ghi nguồn như tác giả tự nhận.
- Mẫu đối chiếu ngẫu nhiên 8 khẳng định với nguồn (grep trực tiếp nguồn, không qua bản tóm tắt):
  1. pico-fido v8.2 / 2026-10-18 / commit 15b848d8… / ESP-IDF v5.5.1 → KHỚP docs/04-firmware.md dòng 11-13, 46 (tag + commit + IDF).
  2. N16R8 = flash 16 MB + PSRAM 8 MB Octal, "N26R8" ghi nhầm → KHỚP hardware/BOM.md dòng 5, 21-25.
  3. USB OTG native full-speed 12 Mbps, GPIO19 D-/GPIO20 D+ → KHỚP docs/FAQ.md dòng 34.
  4. Android 9+ Chrome + cáp OTG, bật OTG nếu tắt mặc định → KHỚP docs/05-huong-dan-su-dung.md dòng 23-25.
  5. Bí mật gốc S 32 byte/256 bit, hex S mở két ket.bin (vault.py, AES-256-GCM) → KHỚP docs/07-sao-luu-va-khoi-phuc.md dòng 32-33, 40, 93.
  6. Shamir 5 share cần 3, mất bất kỳ 2 vẫn mở, dưới nửa biết đúng 0 bit → KHỚP 07 dòng 102-103, 113, 133.
  7. LED "thường là WS2812, GPIO38 hoặc GPIO48 tùy bản" → KHỚP NGUYÊN VĂN docs/03-phan-cung.md dòng 19 (câu tác giả đã sửa đúng).
  8. run_tests.ps1/.sh self-test 7 tool, không cần phần cứng → KHỚP scripts/run_tests.ps1 dòng 8 (liệt kê đúng 7 tool: fido_check, hid_echo, split_secret, mnemonic, vault, pqc, ml_distinguisher) + tools/*.py đúng 7 file. Lưu ý nhỏ: con số "7" không nằm trong README mà nằm ở FAQ + script — trích dẫn README hơi lệch nhưng số liệu đúng, không trừ điểm.
- Kiểm thêm (không tính vào mẫu): arduino-cli 1.6.0 + core ESP32 4.0.0 khớp README dòng 35; "không chép credential FIDO" + "đăng ký 2 key" khớp 05/06/07; lệnh dựng tóm tắt (new --words 24, split --shares 5 --threshold 3) khớp 07 dòng 130-133 (bản tóm tắt lược bớt --out/--from-file — chấp nhận được cho tóm tắt 1 trang).
- Không phát hiện số liệu sai, không thiếu phần, không vi phạm phạm vi (đúng 1 file mới).
- KẾT LUẬN: [KIEM-DINH] ĐẠT — 8/8 mẫu khớp nguồn, đủ 4 phần, trích nguồn đầy đủ.
- Đồng bộ Kanzo: GET /api/board?project=esp32-securitykey, timeout 30s, 3 lần cách nhau 5s — cả 3 lần lỗi 500 Internal Server Error (giống NCKH-053 gặp). Không đọc được bảng, không tìm được thẻ NCKH-053 → KHÔNG comment/move, KHÔNG tự tạo thẻ theo lệnh.
- Unresolved (kiểm chéo): U-KC1: comment/move Kanzo cho thẻ NCKH-053 (review->done) chưa thực hiện được vì Kanzo 500 — chờ Viện trưởng vá rồi đồng bộ bù.
