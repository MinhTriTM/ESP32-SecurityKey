# Sổ cái NCKH-014 — Dương An, nhóm ML, Viện, đợt 2A

## 2026-11-21 01:50 — nhận việc
- Thẻ: [ML] Thử CNN 1D thay MLP (mã NCKH-014; id Kanzo tra cứu cuối việc qua GET board)
- Trạng thái: todo -> doing (đồng bộ Kanzo cuối việc; file trước bảng sau)
- Việc nhận (theo `vien-nghien-cuu/phan-cong.json`, NCKH-014 Dương An, nhóm ML, đợt 2):
  thử kiến trúc CNN 1D thay MLP cho `ml_distinguisher` trên cùng dữ liệu và ngân sách,
  so accuracy R=5/6/7 với baseline MLP 0.5970/0.5245/0.5070.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0),
  mục NCKH-014 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, `vien-nghien-cuu/NHIP-TIM.md`,
  toàn bộ `tools/ml_distinguisher.py`, sổ `vien-nghien-cuu/so-cai/NCKH-002.md`
  (baseline tái hiện khớp tuyệt đối).
- Baseline (NCKH-002, seed 1337, train 6000 / test 2000 / epochs 5 / batch 256):
  R=5 → 0.5970, R=6 → 0.5245, R=7 → 0.5070.
- Thiết kế CNN 1D (numpy thuần, cùng ngân sách dữ liệu/epochs/batch/seed):
  input 64 bit → Conv1 k=5, 1→32 (same) + ReLU → MaxPool 2 → Conv2 k=5, 32→64 (same)
  + ReLU → GlobalAvgPool → Dense 64→32 ReLU → Dense 32→1 sigmoid, Adam lr=0.002.
  Tổng tham số ~12.6k, tương đương MLP baseline (~16.6k: 64→128→64→1).
  Cùng seed sinh dữ liệu (`seed + R*1000` train, `+77` test) và seed khởi tạo (`seed + R`).
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; script thí nghiệm riêng trong `$env:TEMP`,
  mượn pipeline `make_dataset` của tool qua import (không sửa tool).
- Shell: mọi lệnh `muse.powershell` kèm `shell="pwsh"`. Không git commit.

## 2026-11-21 02:05 — báo cáo thí nghiệm
- Thẻ: [ML] Thử CNN 1D thay MLP (mã NCKH-014)
- Đã làm:
  1. Viết script riêng `$env:TEMP/NCKH-014-cnn1d.py` (numpy thuần, REPO CHỈ ĐỌC):
     mượn `make_dataset` của `tools/ml_distinguisher.py` qua import, không sửa tool.
     Biến thể A (AvgPool): Conv1 k=5, 1→32 + ReLU → MaxPool2 → Conv2 k=5, 32→64
     + ReLU → GlobalAvgPool → Dense 64→32 → 32→1. Tổng 12609 tham số
     (MLP baseline 16641: 64→128→64→1). Cùng seed dữ liệu/khởi tạo theo từng R
     (`seed+R*1000` train, `+77` test, `seed+R` init), Adam lr=0.002.
  2. Chạy thử nhanh (R=5, 400 mẫu, 1 epoch): chạy được, acc=0.5000, không lỗi.
  3. Chạy full cùng ngân sách baseline (train 6000 / test 2000 / epochs 5 /
     batch 256 / seed 1337), log `$env:TEMP/NCKH-014-full.log`:
     - CNN-AvgPool: R=5 → 0.5000 (22.9s), R=6 → 0.5000 (26.4s), R=7 → 0.5035 (22.6s).
     - Baseline MLP (NCKH-002): R=5 → 0.5970, R=6 → 0.5245, R=7 → 0.5070.
     - Nhận xét: mô hình đoán mò hoàn toàn, loss test kẹt ~0.69 (=ln2) cả 5 epoch.
  4. Nghi bug nên kiểm chứng bằng script `$env:TEMP/NCKH-014-debug.py`
     (log `$env:TEMP/NCKH-014-debug.log`):
     - Gradient check (finite-difference, batch 8): mọi weight khớp ~1e-9
       (w1 2.5e-9, w2 2.2e-9, w3 2.9e-8, w4 2.4e-11; b2/b3/b4 ~1e-9..1e-11);
       riêng b1 lệch 1.00 → cần xác minh thêm (xem bước 6).
     - Overfit test AvgPool (200 mẫu R=5, 30 epoch): train acc chỉ 0.605 —
       kiến trúc AvgPool gần như không biểu diễn nổi tập nhỏ.
  5. Viết biến thể B (Flatten, giữ thông tin vị trí) `$env:TEMP/NCKH-014-cnnflat.py`:
     Conv1 k=5, 1→8 → MaxPool2 → Conv2 k=5, 8→16 → Flatten 512 → Dense 512→32
     → 32→1. Tổng 17153 tham số ≈ MLP 16641 (công bằng tham số).
  6. Xác minh nghi ngờ b1/b2 bằng `$env:TEMP/NCKH-014-verify.py`
     (log `$env:TEMP/NCKH-014-verify.log`) + `$env:TEMP/NCKH-014-count0.py`:
     - Grad check batch 32 seed 3: mọi weight vẫn khớp (max ≤1.6e-4,
       median ~1e-9); chỉ bias conv lệch (b1 max 0.03..1.0, b2 max 0.12..0.2),
       còn bias dense khớp hoàn hảo (~1e-8).
     - Lệch KHÔNG ĐỔI khi đổi eps 1e-5 → 1e-7 (giống hệt 3 chữ số) → loại trừ
       nhiễu số; là hiệu ứng xác định.
     - Đếm activation: z1 có 39072/1048576 = 3.7% bằng 0 CHÍNH XÁC
       (khớp lý thuyết cửa sổ 5 bit toàn 0: 0.5^5 ≈ 3.1%), z2 có 256 điểm =0.
     - Kết luận: tại z=0 chính xác, mask `(z>0)` chọn subgradient 0 (chuẩn,
       giống hệt MLP gốc), còn finite-difference đo s/2 → numeric lệch là bản
       chất subgradient tại điểm gãy, KHÔNG PHẢI BUG. Bằng chứng quyết định:
       dw dùng cùng dz nhưng khớp hoàn hảo (input tại điểm gãy = 0 nên triệt
       tiêu sai lệch), và cùng dòng code db có lần khớp 4.7e-9.
     - Overfit test Flatten (200 mẫu, 30 epoch): train acc = 0.9950 → code conv
       HOÀN TOÀN ĐÚNG (dùng chung code với AvgPool); vấn đề của AvgPool là
       kiến trúc. Đối chứng MLP gốc cùng setting: test 0.5900 (khái quát ngay
       với 200 mẫu, Flatten chỉ test 0.50 — overfit thuần).
  7. Chạy full biến thể B cùng ngân sách, log `$env:TEMP/NCKH-014-flat-full.log`:
     - CNN-Flatten: R=5 → 0.5070, R=6 → 0.5100, R=7 → 0.4910 (~3.1s mỗi R).
- Bảng so sánh cuối (cùng dữ liệu + ngân sách, seed 1337):

  | Mô hình              | Tham số | R=5    | R=6    | R=7    |
  |----------------------|---------|--------|--------|--------|
  | MLP baseline         | 16641   | 0.5970 | 0.5245 | 0.5070 |
  | CNN 1D + AvgPool (A) | 12609   | 0.5000 | 0.5000 | 0.5035 |
  | CNN 1D + Flatten (B) | 17153   | 0.5070 | 0.5100 | 0.4910 |

- Kết luận: trong cùng dữ liệu và ngân sách, cả hai biến thể CNN 1D đều THUA
  MLP baseline, đặc biệt ở R=5 (0.500/0.507 so với 0.597). Nguyên nhân:
  tín hiệu phân biệt Speck phụ thuộc vị trí bit cụ thể; GlobalAvgPool xóa thông
  tin vị trí (biến thể A đoán mò); Flatten giữ vị trí nhưng inductive bias của
  conv (trọng số chia sẻ, cục bộ) kém hiệu quả hơn dense của MLP ở ngân sách
  nhỏ (học yếu, dễ overfit mà khó khái quát). Đây là negative result có giá trị:
  KHÔNG nên thay MLP bằng CNN 1D ở ngân sách này. Hướng tiếp theo (ngoài phạm vi
  thẻ này): thử kernel phủ toàn bộ cặp từ (k=16/32), bỏ pooling, hoặc tăng dữ
  liệu lên 50k (phối hợp NCKH-008) xem CNN có bắt kịp không.
- Tự kiểm (lệnh đã chạy + output chính, shell pwsh):
  - `python $env:TEMP/NCKH-014-cnn1d.py --rounds 5 --samples 400 ... --epochs 1`
    → chạy được, acc=0.5000, EXIT=0.
  - Full AvgPool R=5,6,7 → `Tom tat: R=5: 0.5000, R=6: 0.5000, R=7: 0.5035`, EXIT=0
    (log `$env:TEMP/NCKH-014-full.log`).
  - `python $env:TEMP/NCKH-014-debug.py` → grad check + overfit 0.605 + loss kẹt
    0.69, EXIT=0 (log `$env:TEMP/NCKH-014-debug.log`).
  - `python $env:TEMP/NCKH-014-cnnflat.py --grad-check-only` → weight khớp, EXIT=0.
  - `python $env:TEMP/NCKH-014-verify.py` → eps-không-đổi + overfit Flatten 0.9950
    + MLP đối chứng 0.59, EXIT=0 (log `$env:TEMP/NCKH-014-verify.log`).
  - `python $env:TEMP/NCKH-014-count0.py` → z1 3.7% bằng 0 chính xác, EXIT=0.
  - Full Flatten R=5,6,7 → `Tom tat: R=5: 0.5070, R=6: 0.5100, R=7: 0.4910`, EXIT=0
    (log `$env:TEMP/NCKH-014-flat-full.log`).
  - Repo: chỉ ghi file sổ cái này; `git status` không cần vì không commit;
    mọi script nằm trong `$env:TEMP`, tool gốc không bị sửa (chỉ import).
- Trạng thái: doing -> review (chờ kiểm chéo; peer review cần đường kiểm độc lập,
  không chạy lại đúng lệnh của tác giả).
- Kanzo: xem mục bên dưới (GET board + move + comment, cách nhau 5s, timeout 30s,
  tối đa 2 lần thử lại; hỏng thì nhờ Viện trưởng vá).

## 2026-11-21 02:10 — đồng bộ Kanzo (thẻ 154): THÀNH CÔNG (thiếu bước trung gian)
- GET board: OK, 23 thẻ. Thẻ của mình: id=154 `[ML] Thử CNN 1D thay MLP (NCKH-014)`,
  đang ở `todo`.
- `POST /api/tasks/154/move {"status":"doing"}`: 3/3 lần HTTP 500 (mỗi lần cách 5s,
  timeout 30s) → THẤT BẠI.
- `POST /api/tasks/154/move {"status":"review"}`: lần 1 timeout 30s, lần 2 HTTP 500,
  lần 3 OK → THÀNH CÔNG.
- `POST /api/tasks/154/comments` (báo cáo số liệu + kết luận + trỏ về sổ file):
  lần 1 OK → THÀNH CÔNG.
- Đối chiếu GET board sau ghi: thẻ 154 đã ở `[review]` → đúng trạng thái đích.
- Nhờ Viện trưởng (nhẹ): lịch sử thẻ thiếu bước trung gian `todo -> doing`
  (do move doing rớt 500 cả 3 lần); thẻ đã ở `review` đúng đích và comment báo cáo
  đã có, không cần vá gấp — chỉ ghi nhận nếu cần đối chiếu lịch sử.
- Unresolved: không còn việc tồn; thẻ chờ kiểm chéo ở `review`.

## 2026-11-21 02:07 (giờ máy) — kiểm chéo NCKH-022 (Lâm An, rà soát biên split_secret)

- Vai: Dương An (NCKH-014) làm lượt kiểm chéo đợt 2A, độc lập, REPO CHỈ ĐỌC
  (chỉ nối thêm chính file sổ cái này). Shell mọi lệnh `shell="pwsh"`. Không git commit.
- Tài liệu đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-022.md`
  (báo cáo biên + 5 phát hiện P1-P5 + mục đồng bộ Kanzo),
  toàn bộ `tools/split_secret.py` (308 dòng).
- Đường kiểm: KHÔNG dùng probe của tác giả; tự tái hiện bằng `python -c` trực tiếp.

### Tái hiện độc lập (lệnh đã chạy + output, shell pwsh, Python 3.12.0)

- P2 (index=-1 sai lặng): `python -c "import sys; sys.path.insert(0, '.');
  from tools.split_secret import split, combine; s=bytes.fromhex('12345678');
  sh=split(s,3,2); ... combine([(-1,sh[0][1]),(2,sh[1][1])])"`
  → exit 0, ra `922effc1` thay vì `12345678`, không báo lỗi. TÁI HIỆN ĐÚNG.
  (Rác khác số của tác giả `e6eb0501df57ea39` là đúng kỳ vọng vì đa thức ngẫu nhiên;
  điểm mấu chốt — sai lặng không lỗi — khớp.)
- P1 (thiếu key ném KeyError): `python -c "...parse_share(
  'SHAMIR-SHARE-V1 threshold=2 index=1 len=4\n12345678\n')"`
  → exit 1, `File tools/split_secret.py, line 146, in parse_share`
  `KeyError: 'shares'`. TÁI HIỆN ĐÚNG, trái docstring dòng 130 (`Ném ValueError`).
- P3 (index=300): `combine([(300,...),(2,...)])` → exit 1,
  `IndexError: list index out of range` tại `_gf_mul` (dòng 55) qua
  `_lagrange_at_zero` (dòng 100). TÁI HIỆN ĐÚNG.
- P4 (header không phải số): `parse_share('... shares=ba ...')` → exit 1,
  `ValueError: invalid literal for int() with base 10: 'ba'` tại dòng 139
  (`int()` không bọc). TÁI HIỆN ĐÚNG, thông điệp tiếng Anh đúng như báo cáo.
- P5 (lẫn 2 lần chia): split cùng secret 2 lần, ghép chéo 1 share mỗi lần
  → exit 0, ra `458b0399` thay vì `12345678`, không báo lỗi. TÁI HIỆN ĐÚNG;
  đồng ý đây là giới hạn thiết kế Shamir thuần (không tag xác thực), không phải bug code.
- Đối chiếu code: `cmd_combine` chỉ bắt `(OSError, ValueError)` (dòng 182) nên
  KeyError/IndexError crash traceback đúng như F3/F4; `combine` chỉ kiểm
  rỗng/trùng x/x=0/khác độ dài (dòng 107-116), không kiểm `1 <= x <= 255`
  đúng gốc P2/P3; `parse_share` không kiểm phạm vi, đúng F1.
- Self-test: `python tools/split_secret.py --self-test`
  → `self-test ok: GF(256) đúng vector AES...`, EXIT=0. Khớp báo cáo (F6 xanh).
- Phạm vi: tác giả đã đi hết việc giao (N=255, K=1, K=N, secret 1 byte/1KB,
  file hỏng/cụt/lẫn lộn, thông điệp lỗi), chỉ báo cáo không sửa code — đúng chỉ thị.

### Kết luận kiểm định: ĐẠT

- `[KIEM-DINH] dat — cả 5 phát hiện P1-P5 tái hiện đúng bằng đường độc lập
  (python -c trực tiếp, không dùng probe của tác giả); đối chiếu code khớp
  dòng lỗi nêu trong báo cáo; self-test xanh; phạm vi đủ, không sửa code
  đúng chỉ thị. Đề xuất review -> done.`
- Không phát hiện phóng đại hay thiếu sót trọng yếu. U1-U3 của tác giả
  (chưa đo N=255/K=255/1KB, ngoài phạm vi qr/getpass, chưa sửa code) là
  ghi nhận trung thực, không chặn kết luận đạt.

### Đồng bộ Kanzo (không thấy thẻ + server nghẽn, đã ghi sổ)

- GET board lần 1: OK — liệt kê đủ 27 thẻ, KHÔNG có thẻ nào mang mã NCKH-022
  trong tiêu đề (chỉ thấy NCKH-013..021, 024..028 + thẻ FIX + thẻ đợt 1).
- GET board lần 2: HTTP 500. Thử lại lần 3: HTTP 500. Lần 4: OK nhưng bộ lọc
  tiêu-đề/mô-tả chỉ trúng thẻ 154 (chính thẻ NCKH-014 của tôi, nhắc NCKH-022
  ở mục người kiểm chéo) — càng xác nhận không tồn tại thẻ NCKH-022.
- 3 lần GET tiếp theo (xác nhận theo tiêu đề, mỗi lần cách 5s, timeout 30s):
  cả 3 đều HTTP 500 → hết hạn mức thử lại, dừng theo luật.
- Kết quả: không comment/move được (không có id thẻ đích + server nghẽn).
  Đúng luật HIEN-CHUONG §6 + chỉ thị: hỏng hoặc không thấy thẻ thì ghi sổ
  và tiếp tục. Sổ cái này là nguồn chân lý.
- Nhờ Viện trưởng: tạo/vá thẻ NCKH-022 `[tooling] Rà soát split_secret biên`
  lên bảng khi Kanzo sống lại, dán comment `[KIEM-DINH] dat` ở trên và
  chuyển thẳng `review -> done` (tác giả làm xong ở doing, kiểm chéo đạt).

### Unresolved

- K1: thẻ NCKH-022 chưa tồn tại trên Kanzo + server hay 500 — nhờ Viện trưởng
  vá tay (nội dung comment và đích move đã ghi ở trên).


