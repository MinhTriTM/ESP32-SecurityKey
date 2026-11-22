# Sổ cái NCKH-044 — Mai Bình (nhóm ML, đợt 2B)

## 2026-11-21 02:24 — nhận việc
- Nhiệm vụ: Rà soát pipeline dữ liệu (loại t1-tay-chon)
- Mô tả: Kiểm cân bằng lớp, rò rỉ tập test, seed ngẫu nhiên có cố định không.
- Phạm vi theo lệnh: tools/ml_distinguisher.py — cân bằng lớp 0/1, rò rỉ train→test, seed cố định/tái hiện, chia tập đúng không; chạy thử chứng minh từng điểm.
- Nguồn đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-044), vien-nghien-cuu/so-cai/README.md, tools/ml_distinguisher.py (331 dòng).
- Kế hoạch: repo CHỈ ĐỌC (không sửa file repo, không git commit); probe chỉ đọc chạy từ $env:TEMP qua `sys.path.insert(0,'tools')`; ghi sổ cái này TRƯỚC rồi mới đồng bộ Kanzo.
- Trạng thái: todo -> doing

## 2026-11-21 02:25 — báo cáo
- Đã làm: đọc toàn bộ tools/ml_distinguisher.py (đặc biệt make_dataset dòng 100-124, train_mlp 204-219, run_experiment 281-294, self_test 261-278) và chạy 3 probe + self-test chính thức.
- Kết luận chung: pipeline dữ liệu ĐẠT cả 4 điểm, không phát hiện lỗi.

### 1. Cân bằng lớp 0/1 — ĐẠT
- Code: `half = n//2; n_on = half + (n%2)` (dòng 103-104) → n chẵn chia 50/50 tuyệt đối, n lẻ thừa đúng 1 mẫu nhãn 1; trộn đều bằng `rng.permutation` (dòng 123).
- Chứng minh (probe 1):
  - n=6000 → n1=3000 n0=3000 (tỷ lệ 0.5000); n=2000 → 1000/1000; n=400 → 200/200; n=200 → 100/100
  - n=1001 → n1=501 n0=500 (0.5005); n=2 → 1/1; n=1 → 1/0 (trường hợp biên, đúng công thức)
  - Sau trộn, 10 nhãn đầu `[0,1,1,0,0,1,0,0,0,1]` và mọi block 600 mẫu đều chứa cả 2 lớp → trộn có hiệu lực.
- Lưu ý nhỏ (không phải lỗi): n lẻ lệch 1 mẫu về nhãn 1; cấu hình mặc định dùng n chẵn nên không ảnh hưởng.

### 2. Rò rỉ train→test — KHÔNG PHÁT HIỆN
- Code: train/test sinh độc lập bằng 2 seed khác nhau — run_experiment: `seed+r*1000` vs `+77` (dòng 287-288); self-test: seed 1 vs 2 (dòng 269-270).
- Chứng minh (probe 2, so trùng mẫu chính xác từng bit trên vector 64 bit):
  - R=5: train 6000 (seed 6337) vs test 2000 (seed 6414) → trùng 0
  - R=6: seed 7337 vs 7414 → trùng 0; R=7: seed 8337 vs 8414 → trùng 0
  - self-test: train 400 (seed 1) vs test 200 (seed 2) → trùng 0
  - Trùng nội bộ: 6000/6000 unique (dup 0); các R khác nhau (seed cách nhau 1000) → trùng 0/1000
  - Đối chứng hiệu lực: cùng seed 99 cho cả 2 tập → trùng 200/200; seed 99 vs 176 (offset 77) → trùng 0/200 → offset seed có tác dụng thật, phương pháp kiểm bắt được trùng nếu có.
- Mỗi mẫu thật dùng khóa ngẫu nhiên độc lập (random_key từ rng đã seed), bản rõ ngẫu nhiên độc lập → không có kênh rò rỉ qua khóa/bản rõ.

### 3. Seed cố định và tái hiện — ĐẠT
- Quét nguồn ngẫu nhiên: cả 4 điểm đều `np.random.default_rng(seed)` với seed được truyền rõ ràng — make_dataset:102, MLP init:146, train shuffle:207, check_roundtrip:251. `time.time()` chỉ dùng đo thời gian in log, không tham gia sinh dữ liệu. Không có `random`/`os.urandom`/`secrets` hay seed mặc định.
- Chứng minh (probe 1+3):
  - Cùng seed 1337 chạy 2 lần → X giống hệt True, y giống hệt True; khác seed 1337 vs 1338 → X khác nhau.
  - Train đầu-cuối 2 lần cùng seed (400 mẫu, 1 epoch, seed 3) → acc 0.505000 == 0.505000.
- Sơ đồ seed run_experiment: data-train `seed+r*1000`, data-test `+77`, MLP/shuffle `seed+r` → 3 luồng độc lập, không lẫn vào nhau.

### 4. Chia tập đúng không — ĐẠT
- Thiết kế: không tách từ một pool chung mà sinh 2 tập độc lập với seed riêng — hợp lệ vì dữ liệu là tổng hợp vô hạn, không lấy từ nguồn hữu hạn.
- Chứng minh (probe 2): R=5,6,7 đều train shape (6000,64) n1=3000 + test shape (2000,64) n1=1000 — đúng kích thước CLI mặc định (`--samples 6000 --test-samples 2000`), cả 2 tập cân bằng.
- Đặc trưng hợp lệ (probe 3): X chỉ gồm bit 0/1, đúng 64 chiều = nối cặp bản mã (c0,c1).
- Lưu ý nhỏ (không phải lỗi): pipeline chỉ có train/test, chưa có tập validation riêng.

### Tự kiểm bổ sung
- `python tools/ml_distinguisher.py --self-test` → PASS: vector KHOP (k0=tu-cuoi), round-trip PASS (200 mẫu x R=5,22), micro-train acc=0.505.
- Lệnh chỉ đọc, không sửa repo, không commit. Probe lưu ở $env:TEMP (nckh044_probe1/2/3.py), không đưa vào repo.
- Trạng thái: doing -> review (chờ peer review nhóm khác kiểm độc lập)

## 2026-11-21 02:26 — đồng bộ Kanzo (opportunistic)
- GET board lần 1: OK, 35 thẻ; rà title không có thẻ nào nhắc NCKH-044.
- Rà full JSON (title+description): XÁC NHẬN không có "NCKH-044"/"Mai Bình"; cũng không có thẻ ML pipeline/dữ liệu nào khác.
- GET lại lần 2 (sau 5s, timeout 30s): OK, 35 thẻ; vẫn XÁC NHẬN không có thẻ NCKH-044.
- Move/comment: KHÔNG thực hiện — không có thẻ của mình để di chuyển; KHÔNG tự tạo thẻ theo lệnh.
- Ghi chú cho Viện trưởng: việc "Rà soát pipeline dữ liệu" của NCKH-044 chưa có thẻ Kanzo riêng; sổ cái file này là nguồn chính. Kết quả rà soát (ĐẠT cả 4 điểm, không phát hiện lỗi) nằm ở mục báo cáo phía trên.

## 2026-11-21 — kiểm chéo NCKH-036 (Đỗ Bình, quét secret, kết luận SẠCH)
- Vai: Mai Bình kiểm độc lập bằng ĐƯỜNG KHÁC tác giả. Đã đọc toàn bộ vien-nghien-cuu/so-cai/NCKH-036.md (12 điểm loại trừ + ngoài phạm vi). Repo chỉ đọc, không git commit.
- Kết luận kiểm chéo: [KIEM-DINH] ĐẠT — đồng ý repo SẠCH, kết luận của NCKH-036 vững.

### Quét độc lập (5 pattern riêng, khác tác giả)
- K1 TODO/FIXME/HACK/XXX/HARDCODE/CHANGE-ME/REPLACE-ME: 2 hit, cả 2 đều là placeholder mẫu `NCKH-XXX.md` trong vien-nghien-cuu/NHIP-TIM.md:22 và vien-nghien-cuu/so-cai/README.md:3. Không có TODO giấu key. Sạch.
- K2 gán giá trị dài `[:=]\s*["']?[A-Za-z0-9_\-/+]{20,}` toàn repo: ~60 hit đã xem hết, toàn bộ là đường dẫn ($PWD\.tooling, $env:TEMP), cổng mẫu, phép tính byte trong sổ, SHA commit pico-fido công khai, vector kiểm thử đã biết (entropy NCKH-024, mật khẩu kiểm thử NCKH-030 — xem dưới). Không có credential thật.
- K3 file lạ đuôi nhạy cảm mở rộng (.pem/.key/.env/.ppk/.jks/.keystore/.p12/.pfx/.asc/.gpg/.secret/.token/*credential*/*password*/*private*/*.ovpn/id_rsa*): 0 file.
- K4 URI nhúng credential + khối khóa (-----BEGIN, ://user:pass@, api_key=, mongodb/postgres/mysql URI): 0 hit.
- K5 chuỗi quoted 24+ ký tự trong scripts/config/firmware/hardware/tools/QGAC: 6 hit, khớp đúng các điểm tác giả đã loại trừ (SHA 15b848d...768e công khai, "=====" trang trí hwtest.ino:94, "maxCredentialCountInList", hex CANNED_GETINFO) + 1 đường dẫn .tooling/arduino-cli. Không phát hiện điểm nghi mới.
- Kiểm kê đuôi file toàn repo (trừ .git/.tooling): chỉ có .md/.py/.ps1/.sh/.txt/.json/.ino/.rules/.jpg/.pdf/.pyc/.log/LICENSE/.gitignore — không đuôi lạ. File không đuôi = LICENSE, file .log = NHIP-TIM.log (log nhịp tim Kanzo, đã đọc, không secret).

### Đọc tay 4 file nhạy cảm nhất
- scripts/flash_win.ps1, scripts/flash_linux.sh: chỉ có SHA commit công khai + cổng mẫu COM3//dev/ttyACM0 + lệnh git/esptool công khai. Sạch.
- config/70-u2f.rules: chỉ vendor ID USB công khai (1050/096e/1a86/303a) + MODE/GROUP. Sạch.
- scripts/run_tests.ps1: chỉ đường dẫn .tooling + vòng lặp self-test. Sạch.

### Điểm bổ sung ngoài 12 điểm của tác giả (đều đã xác minh không phải secret thật)
- NCKH-030.md: `mat-khau-kiem-dinh-NCKH-030` là mật khẩu kiểm thử do chính researcher đặt, salt/nonce tăng dần 000102..., key/tag/ct là output suy ra từ vector — tài liệu kiểm thử, không phải bí mật thật.
- NCKH-025.md: `info="ESP32-[REDACTED]"` là tên domain KDF trong tài liệu thiết kế, không phải giá trị bí mật.
- NCKH-024.md:126 entropy hex là vector BIP-39 chuẩn đã ghi nguồn (tác giả đã loại trừ ở điểm 9).
- Không phát hiện secret thật nào mà tác giả bỏ sót.

### Đồng bộ Kanzo (kiểm chéo NCKH-036)
- GET /api/board?project=esp32-securitykey (timeout 30s, cách nhau 5s): lần 1 → 500, lần 2 → 500, lần 3 → trả về nhưng parse rỗng (TOTAL=1, id/status/title trống, cấu trúc không như kỳ vọng), lần raw → lại 500. Kanzo chập chờn, không đọc được bảng ổn định.
- Kết quả: không tìm được thẻ NCKH-036 → KHÔNG comment, KHÔNG move, KHÔNG tự tạo thẻ. Viện trưởng đối chiếu và vá bảng khi Kanzo sống lại.
- Unresolved: (1) thẻ NCKH-036 review->done còn chờ Kanzo; (2) file nhị phân docs/assets/*.jpg, docs/reference/*.pdf và .tooling/.git ngoài phạm vi quét như tác giả đã nêu.
