# Sổ cái NCKH-036 — Đỗ Bình (nhóm kiemdinh, đợt 2B)

## 2026-11-21 02:23 — nhận việc
- Nhiệm vụ (phan-cong.json): "Quét secret lọt repo" — Tìm mật khẩu/khóa/bí mật thật trong file, báo cáo hoặc xác nhận sạch.
- Phạm vi: toàn repo trừ `.git` và `.tooling`. Repo chỉ đọc, không git commit.
- Thẻ Kanzo: tìm ở bước đồng bộ cuối (GET board, lọc mã NCKH-036). Không tự tạo thẻ.
- Trạng thái: todo -> doing

## 2026-11-21 02:23 — báo cáo kiểm định: REPO SẠCH, không có bí mật thật
- Đã làm: liệt kê toàn bộ file text trong repo (trừ `.git`, `.tooling`), quét pattern
  `password|passwd|api-key|private key|secret key|token|secret|mnemonic|seed|ssid|wifi|totp|otp|webhook|smtp`,
  token cloud (`ghp_|gho_|xox-|sk-live|sk-test|AKIA|bearer|access-token`),
  khối `BEGIN ... PRIVATE KEY`, chuỗi base64/hex cứng (`["'][A-Za-z0-9+/=]{32,}["']`,
  hex 64+ ký tự), file nhạy cảm (`.env`, `*.pem`, `*.key`, `id_rsa*`, `*credential*`,
  `*.pfx`, `*.p12`, `*.asc`, `*.gpg`), PIN đi kèm số; đọc tay toàn bộ file nghi
  và toàn bộ `tools/*.py`, `scripts/*`, `firmware/hwtest/hwtest.ino`,
  `hardware/*`, `config/*`, `docs/06`, `docs/07`, `QGAC/ý tưởng.txt`.
- Tự kiểm: mọi hit đều là tên biến, tài liệu, hoặc giá trị mẫu công khai (chi tiết dưới).
  Không phát hiện mật khẩu, khóa API, seed, khóa bí mật hay token thật nào.
- Kết luận: [KIEM-DINH] SẠCH — không có secret thật lọt repo.
- Trạng thái: doing -> review

### Điểm nghi đã đọc tay và loại trừ (không phải secret thật)
1. `tools/vault.py` — `password`, `--password-file`: tên biến/tham số CLI; self-test
   dùng `os.urandom` ngẫu nhiên, không giá trị cứng.
2. `tools/mnemonic.py` — `abandon ... about`: test vector BIP-39 chính thức
   (entropy 16 byte 0), tài liệu công khai; `"TREZOR"` là passphrase của vector chuẩn.
3. `tools/fido_check.py:237-241` (`CANNED_GETINFO`) — hex CBOR GetInfo giả lập đóng hộp
   (versions/options/maxMsgSize), ghi chú rõ "Key giả trong RAM".
4. `tools/pqc.py`, `tools/split_secret.py` — `secret_key`/`shared_secret` là tên
   biến và tham số liboqs; self-test sinh ngẫu nhiên, không hardcode.
5. `tools/bip39_english.txt` — hai dòng `secret`, `token` là từ vựng trong bảng
   2048 từ BIP-39 chuẩn, không phải giá trị bí mật.
6. `scripts/flash_win.ps1`, `scripts/flash_linux.sh` — `15b848d...768e` là SHA commit
   git công khai của pico-fido tag v8.2; `COM3`/`/dev/ttyACM0` là cổng mẫu.
7. `firmware/hwtest/hwtest.ino:94` — chuỗi `"====="` trang trí log serial; file không
   có wifi/secret, MAC được ghi chú rõ "KHÔNG phải bí mật".
8. `hardware/keys.md` — bảng key còn trống, tuyên bố rõ "không chứa PIN hay mã khôi phục".
9. `vien-nghien-cuu/so-cai/NCKH-024.md` — các hex 64 ký tự là vector BIP-39 chuẩn của
   `trezor/python-mnemonic` (`vectors.json`, entropy toàn 0/7f/80/ff và vector mẫu),
   đã ghi rõ nguồn trong sổ NCKH-024.
10. `docs/*` — chỉ thuật ngữ giao thức (`navigator.credentials`, `hmac-secret`,
    "private key không rời chip", "secret 1 byte" trong gen_phan_cong là case test).
11. Không tồn tại file `.env`/`*.pem`/`*.key`/`id_rsa*`/`*credential*`; không có
    `ghp_|AKIA|sk-|bearer|BEGIN PRIVATE KEY` ở bất kỳ đâu.
12. `vien-nghien-cuu/so-cai/NCKH-023.md:84` — "WiFi Direct" là ghi chú sửa chính tả
    tài liệu, không phải credential wifi.

### Ngoài phạm vi / không quét nội dung
- `.git`, `.tooling`: loại trừ theo nhiệm vụ.
- `tools/__pycache__/*.pyc`: artifact biên dịch từ chính source đã quét, không đọc.
- `docs/assets/*.jpg`, `docs/reference/*.pdf`: file nhị phân, không quét nội dung.

## Đồng bộ Kanzo
- 2026-11-21 02:23 — GET `/api/board?project=esp32-securitykey` thành công (timeout 30s,
  thử 1 lần đã xong), bảng có 32 thẻ: 6 thẻ todo (id 167-172, gồm NCKH-022 và các thẻ
  FIX/DOC/OPS), 26 thẻ done gồm NCKH-001..021 và NCKH-024..028
  (NCKH-022 đang todo id 172; NCKH-023 không có trên bảng).
- Không thấy thẻ nào mang mã NCKH-036 (lọc theo title và description đều không trúng).
- Theo nhiệm vụ: KHÔNG tự tạo thẻ, không move/comment. Kết quả kiểm định nằm ở sổ này,
  chờ Viện trưởng đối chiếu và vá lên bảng.

## 2026-11-21 02:35 — kiểm chéo đợt 2B: rà công việc NCKH-044 Mai Bình (pipeline dữ liệu ML)
- Đối tượng: sổ `vien-nghien-cuu/so-cai/NCKH-044.md` (mục báo cáo 02:25) + `tools/ml_distinguisher.py` (331 dòng).
- Phạm vi kiểm: 4 điểm NCKH-044 đã kết luận (cân bằng lớp, rò rỉ train→test, seed cố định,
  chia tập đúng). Repo chỉ đọc, không sửa file repo, không git commit. Probe chỉ đọc chạy
  từ `$env:TEMP/nckh036_kc_probe.py` qua `sys.path.insert(0,'tools')`.
- Kết luận: [KIEM-DINH] ĐẠT — cả 4 điểm NCKH-044 báo ĐẠT đều đứng vững trước kiểm độc lập,
  không phát hiện lỗi sai sót hay điểm bỏ sót. Đề nghị move thẻ NCKH-044 review -> done
  (nếu có thẻ trên Kanzo).

### Kiểm tra độc lập bằng đường khác (seed và cách kiểm đều khác NCKH-044)
1. Cân bằng lớp — KHỚP. Seed 4242/4243 (NCKH-044 dùng 1337/1338/99): n=10 → 5/5;
   n=500 → 250/250; n=777 (lẻ, khác n=1001 của NCKH-044) → 389/388 (0.5006);
   n=1001 → 501/500. Đúng công thức `n_on = half + (n%2)`.
2. Trộn đều — KHỚP bằng cách khác: thay vì block 600 mẫu, kiểm nửa đầu/nửa sau
   (n=500): nửa đầu n1=119/250, nửa sau n1=131/250 → cả 2 lớp phân bố đều, trộn có hiệu lực.
3. Tái hiện — KHỚP. R=6, n=300: seed 4242 chạy 2 lần → X giống hệt True, y giống hệt True;
   seed 4243 → X khác. NCKH-044 kiểm ở R=5/seed 1337; kiểm chéo đổi cả R lẫn seed vẫn tái hiện.
4. Rò rỉ train→test — KHỚP. Seed gốc 777 (NCKH-044 dùng 1337/seed self-test 1-2):
   R=5 và R=7 theo đúng công thức `seed+r*1000` vs `+77` → trùng 0/300 cả hai.
5. Quét nguồn ngẫu nhiên — KHỚP, không chỗ nào quên seed. Grep toàn file:
   4/4 `np.random.default_rng(seed)` đều nhận seed truyền rõ (dòng 102, 146, 207, 251);
   5 hit `random.` chỉ là `np.random.Generator` (type hint dòng 95) + 4 `default_rng`;
   không có `import random`, `os.urandom`, `secrets`, `np.random.seed`, `np.random.rand`;
   import chỉ gồm `argparse/time/numpy`; `time.time()` chỉ đo thời gian in log (4 chỗ dòng
   268/272/286/293), không tham gia sinh dữ liệu. Chia tập sinh độc lập 2 seed riêng là
   hợp lệ với dữ liệu tổng hợp vô hạn; đặc trưng kiểm lại: shape (100,64), chỉ bit 0/1.
- Đối chiếu sổ NCKH-044: số liệu probe của Mai Bình (tỷ lệ 0.5000/0.5005, trùng 0,
  công thức dòng 103-104, sơ đồ seed `seed+r*1000/+77/seed+r`) đều khớp code dòng tương ứng
  mà kiểm chéo đọc lại trực tiếp. Hai lưu ý nhỏ của NCKH-044 (n lẻ lệch 1 mẫu; chưa có tập
  validation) là nhận xét đúng, không phải lỗi — kiểm chéo đồng ý, không nâng thành lỗi.

### Đồng bộ Kanzo (thẻ NCKH-044)
- GET `/api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s): lần 1 → 500,
  lần 2 → 500, lần 3 → trả về 1 đối tượng lạ (không phải bảng 35 thẻ như NCKH-044 thấy),
  lần 4 (soi cấu trúc) → lại 500. Kanzo chập chờn, không lấy được bảng dùng được.
- Không tìm thấy thẻ NCKH-044 (không có bảng hợp lệ để rà). Theo lệnh: KHÔNG tự tạo thẻ,
  không comment/move. Kết luận kiểm chéo nằm ở sổ này, chờ Viện trưởng đối chiếu và vá lên bảng.

### Unresolved
- Không có điểm nào chưa giải quyết về nội dung kiểm (4/4 điểm khớp).
- Kanzo chưa đồng bộ được (board 500 / phản hồi bất thường) — cần Viện trưởng hoặc lượt sau
  thử lại comment `[KIEM-DINH] đạt` + move thẻ NCKH-044 review -> done khi board ổn định.
