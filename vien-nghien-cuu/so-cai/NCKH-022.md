# Sổ cái NCKH-022 — Lâm An, nhóm tooling, thành viên Viện, đợt 2A

## 2026-11-21 01:52 — nhận việc

- Thẻ: [tooling] Rà soát split_secret biên (tìm id trên Kanzo sau, bảng trước)
- Trạng thái: todo -> doing (thử opportunistic sau khi ghi sổ; Kanzo hay nghẽn)
- Việc nhận: rà soát biên `tools/split_secret.py`: N=255, K=1, K=N,
  secret 1 byte và 1KB, file share hỏng/cụt/lẫn lộn; probe riêng trong
  `$env:TEMP`; đối chiếu thông điệp lỗi có rõ không. CHỈ BÁO CÁO,
  không sửa code. REPO CHỈ ĐỌC.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0),
  mục NCKH-022 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, toàn bộ `tools/split_secret.py`
  (308 dòng: GF(256) dòng 23-71, split/combine 76-120,
  format/parse 125-146, CLI 151-206 + qr 288-304, self-test 211-261).
- Môi trường: Windows, Python 3.12.0 (`python --version`).
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; file tạm chỉ trong
  `$env:TEMP` (`C:\Users\user\AppData\Local\Temp`).

## 2026-11-21 01:59 — báo cáo rà soát biên split_secret

### Đã làm

- Viết 2 probe trong `$env:TEMP` (import tool từ repo, không sửa repo):
  `probe_split_NCKH022.py` (49 case nhóm A-E),
  `probe_split_NCKH022_F.py` (nhóm F đào sâu) + 1 lệnh kiểm x âm.
- Chạy toàn bộ biên: N=255 (K=1/2/255), K=1 (N=1/5/255), K=N (5/255),
  secret 1 byte / 1KB / rỗng, tham số sai (K=0, N=0/256, K>N, K âm),
  combine lỗi (rỗng/trùng x/x=0/khác độ dài/x=300), parse_share 19 case
  hỏng/cụt, CLI lẫn lộn 2 lần chia / header khác nhau / thiếu share /
  file mất / split --from-file + combine --out, self-test.

### Tự kiểm (lệnh đã chạy + output)

- `python C:\Users\user\AppData\Local\Temp\probe_split_NCKH022.py`
  -> exit 0, `TONG: 45/49 đạt`.
- `python C:\Users\user\AppData\Local\Temp\probe_split_NCKH022_F.py`
  -> exit 0; F3/F4 có `Traceback`, F6 self-test `rc=0 ... self-test ok`.
- `python -c "...combine([(-1,...),(2,...)]...)"`
  -> ra rác `e6eb0501df57ea39` thay vì `12345678`, không báo lỗi.
- Kết quả JSON: `C:\Users\user\AppData\Local\Temp\probe_shamir_NCKH022\ketqua.json`.

### Bảng biên

| # | Biên | Kết quả | Ghi chú |
|---|------|---------|---------|
| A1 | secret 1 byte, N=3 K=2 | ĐẠT | round-trip đúng |
| A2 | secret 1KB, N=5 K=3 | ĐẠT | split 0,004s, combine 0,003s |
| A3 | N=255 K=2 | ĐẠT | round-trip đúng |
| A4 | N=255 K=255 (K=N max) | ĐẠT | split 0,008s, combine 0,014s (secret 1 byte) |
| A5 | K=1, N=5 | ĐẠT | round-trip đúng |
| A6 | K=1 N=1 tối thiểu | ĐẠT | round-trip đúng |
| A7 | K=1 N=255 | ĐẠT | round-trip đúng |
| A8 | N=255 K=2 secret 1KB | ĐẠT | split 0,092s, combine 0,002s |
| A9 | K=N=5 | ĐẠT | round-trip đúng |
| A10 | K=1: mỗi share đơn lẻ đều mở được | ĐẠT | đúng ngữ nghĩa ngưỡng 1 |
| A11 | K=N thiếu 1 share cho kết quả khác | ĐẠT | đúng kỳ vọng Shamir |
| B1-B7 | split N/K sai (K=0, N=0, N=256, K>N, K âm) | ĐẠT | ValueError tiếng Việt rõ: `cần 1 <= threshold <= shares <= 255, nhận k=.. n=..` |
| B8 | secret rỗng | ĐẠT | ValueError: `bí mật rỗng, không có gì để chia` |
| C1-C4 | combine rỗng / trùng x / x=0 / khác độ dài | ĐẠT | ValueError tiếng Việt rõ ràng |
| C5 | combine x=300 | GHI NHẬN | IndexError `list index out of range` — khó hiểu (xem P3) |
| D1 | file chuẩn, rác, rỗng, thiếu dòng hex, thừa dòng, sai magic, hex sai, hex cụt lẻ, hex rỗng, len sai, thiếu len, header lạ, dòng trống giữa (13 case) | ĐẠT | ValueError rõ; hex HOA vẫn chấp nhận (khoan dung hợp lý); trailing space cuối file được strip nên vẫn chấp nhận (chấp nhận được) |
| D2 | thiếu shares/threshold/index | RỚT | KeyError thô, không phải ValueError (xem P1) |
| D3 | shares=ba (không phải số) | GHI NHẬN | ValueError nhưng thông điệp tiếng Anh của int(): `invalid literal for int()...` (xem P4) |
| E1 | lẫn lộn 2 lần chia cùng N/K/len | GHI NHẬN | rc=0, in bí mật rác hex, không cảnh báo (xem P5) |
| E2 | header khác nhau (threshold khác) | ĐẠT | từ chối rõ: `Các share không cùng một lần chia...` |
| E3 | thiếu share | ĐẠT | báo rõ: `Thiếu share: cần ít nhất 2 trong 3, mới đưa 1.` |
| E4 | file không tồn tại | ĐẠT | báo rõ kèm OSError gốc |
| E5 | CLI split --from-file + combine --out, 1KB | ĐẠT | rc1=0 rc2=0, khôi phục khớp byte |
| E6 | CLI split N=300 | ĐẠT | `Sai tham số: cần 1 <= ...` |
| F1 | parse index=0/300/-1, shares=0/999, threshold=0/9>3 | GHI NHẬN | tất cả parse OK, không kiểm phạm vi (nguồn của P2/P3) |
| F6 | --self-test | ĐẠT | xanh: `self-test ok: GF(256) đúng vector AES...` |

### Phát hiện (5, xếp theo mức nguy hiểm)

- **P1 — parse_share ném KeyError khi thiếu key, CLI crash traceback.**
  File thiếu `shares`/`threshold`/`index` ném `KeyError: 'shares'`...
  thay vì ValueError như docstring dòng 130 hứa
  (`Ném ValueError nếu file sai định dạng`). `cmd_combine` chỉ bắt
  `(OSError, ValueError)` (dòng 182) nên người dùng thấy cả đống
  Traceback (F3: rc=1, `có traceback? True`). Đề xuất: kiểm tra đủ 4 key
  trong parse_share, ném ValueError tiếng Việt.
- **P2 — index=-1 cho bí mật SAI LẶNG (nguy hiểm nhất).**
  parse chấp nhận `index=-1` (F1), combine không từ chối số âm, kết quả
  là rác (`e6eb0501df57ea39` thay vì `12345678`) mà không báo lỗi —
  người dùng tưởng đã khôi phục đúng. Nguyên nhân: chỉ số âm trong Python
  truy cập bảng GF từ cuối thay vì vượt biên. Đề xuất: parse_share và
  combine cùng kiểm tra `1 <= x <= 255`.
- **P3 — index=300 gây IndexError khó hiểu + CLI traceback.**
  combine ném `IndexError: list index out of range` (F2), CLI traceback
  (F4) vì IndexError không được bắt. Cùng gốc với P2: thiếu kiểm phạm vi.
- **P4 — thông điệp lỗi tiếng Anh khó hiểu khi header không phải số.**
  `shares=ba` cho `invalid literal for int() with base 10: 'ba'` (F5) —
  người Việt không rành khó hiểu. Đề xuất bọc `int()` trong try/except,
  ném ValueError tiếng Việt kiểu `header sai: shares='ba' không phải số`.
- **P5 — lẫn lộn 2 lần chia cùng N/K/len cho rác mà rc=0 (hạn chế thiết kế).**
  E1: ghép 1 share lần chia A + 1 share lần chia B vẫn `rc=0`, in hex rác,
  không cảnh báo. Đây là giới hạn của Shamir thuần (không xác thực),
  không phải bug code. Đề xuất cho bản sau: thêm checksum toàn vẹn
  (ví dụ CRC/SHA vào header, format V2) để phát hiện share lẫn lộn.

### Điểm tốt ghi nhận

- Mọi biên N/K/kích thước secret đều round-trip đúng, kể cả N=255 K=255;
  hiệu năng tốt (combine K=255 chỉ 0,014s/byte).
- Thông điệp lỗi tiếng Việt ở các đường chính rõ ràng, nêu đúng số
  (thiếu share, sai tham số, khác độ dài có gợi ý `lẫn lộn hai lần chia?`).
- Khoan dung hợp lý: hex chữ HOA, khoảng trắng cuối file.
- self-test xanh.

### Unresolved

- U1: chưa đo N=255 K=255 với secret 1KB (ước ~14s, không cần thiết;
  ai cần thì chạy, không chặn kết luận).
- U2: chưa rà `qr` (vẽ QR) và đường nhập tay `getpass` — ngoài phạm vi
  việc giao (biên split/combine/parse).
- U3: P1-P4 là báo cáo, chưa sửa code (đúng phạm vi: chỉ rà soát).
  Đề xuất Viện giao thẻ sửa cho nhóm tooling đợt sau.
- Trạng thái Kanzo: xem mục đồng bộ dưới (ghi sau khi thử API).

## 2026-11-21 02:05 — đồng bộ Kanzo (thất bại, đã ghi sổ)

- GET `http://100.101.100.100:4242/api/board?project=esp32-securitykey`
  (timeout 30s): cả 3 lần (1 chính + 2 thử lại, cách nhau 5s) đều
  `500 Internal Server Error`. Không đọc được board nên không tìm được
  id thẻ NCKH-022, không move/comment được.
- Đúng luật HIEN-CHUONG §6 + chỉ thị: hỏng thì ghi sổ và tiếp tục.
  Sổ cái này là nguồn chân lý; nhờ Viện trưởng đối chiếu và vá lên bảng
  khi Kanzo sống lại. Nội dung comment dự kiến: báo cáo rà soát biên
  split_secret (45/49 probe đạt, 5 phát hiện P1-P5, xem mục báo cáo trên),
  đề xuất doing -> review.

## 2026-11-21 02:20 — kiểm chéo NCKH-014 (Dương An: CNN 1D thay MLP)

- Vai: Lâm An (NCKH-022), lượt kiểm chéo đợt 2A, REPO CHỈ ĐỌC (trừ sổ này),
  shell `pwsh`, không git commit.
- Đối tượng: `vien-nghien-cuu/so-cai/NCKH-014.md` — thử CNN 1D thay MLP,
  cả hai biến thể thua MLP, gradient check khớp 1e-9.
- Đã đọc: toàn bộ sổ NCKH-014, toàn bộ `tools/ml_distinguisher.py`,
  2 script của tác giả trong `$env:TEMP` (`NCKH-014-cnn1d.py`,
  `NCKH-014-cnnflat.py`, chỉ đọc để đánh giá, KHÔNG chạy lại lệnh tác giả).

### Đường kiểm độc lập (khác tác giả)

1. Tự triển khai CNN-Flatten từ đầu trong
   `$env:TEMP/NCKH-022-xcheck-014.py` (conv bằng `stride_tricks` +
   `tensordot`, khác đường với vòng lặp `k` của tác giả; cùng toán học
   cross-correlation + same-pad), cùng kiến trúc tham số tương đương MLP
   (17153 vs 16641, khớp con số tác giả báo).
2. Seed MỚI 777 (tác giả 1337), R=5 (nơi chênh lệch lớn nhất, phân biệt
   rõ nhất), cùng ngân sách 6000/2000/5/256; đối chứng MLP bằng
   `train_mlp` của tool gốc trên cùng dữ liệu seed mới.
3. Thí nghiệm kiến trúc riêng: đo độ nhạy vị trí của GAP so với Flatten
   bằng dịch vòng 16 bit trên 200 mẫu thật (không train, conv ngẫu nhiên
   cố định) — kiểm trực tiếp lập luận "AvgPool xóa vị trí".
4. Gradient check nội bộ cho CNN tự viết (batch 32, seed 11, eps 1e-5).

### Số liệu độc lập (log `$env:TEMP/NCKH-022-xcheck-014.log`, EXIT=0)

- Seed 777, R=5: MLP (tool gốc) = 0.5840, CNN-Flat (tự viết) = 0.5215,
  chênh +0.0625 nghiêng về MLP. Tác giả (seed 1337): 0.5970 vs 0.5070,
  chênh +0.090. Cùng hướng, cùng thứ tự độ lớn → CNN thua KHÔNG phải
  do may rủi seed. (CNN seed mới nhích lên 0.5215 nhưng vẫn thua xa.)
- GAP-vs-vị trí: dịch vòng 16 bit làm GAP đổi 0.0671 (tương đối) so với
  Flatten đổi 0.7849 → GAP kém nhạy vị trí gần 12x (tỉ lệ 11.69x).
  Xác nhận trực tiếp: GlobalAvgPool xóa thông tin vị trí tuyệt đối.
- Grad check CNN tự viết: mọi weight khớp (w1 max 1.5e-9, w2/w3 median
  ~9e-10, w4 ~1e-10, b2/b3/b4 ~1e-8..1e-11); riêng b1 lệch (max 0.16) —
  TÁI HIỆN ĐỘC LẬP đúng hiện tượng tác giả mô tả bằng code viết khác
  hẳn, ủng hộ mạnh giải thích subgradient ReLU tại z=0 (không phải bug).

### Đánh giá lập luận kiến trúc của tác giả

- "AvgPool xóa vị trí → đoán mò": VỮNG. Được cả 3 nguồn ủng hộ: (a) lý
  thuyết (trung bình toàn cục bất biến hoán vị vị trí), (b) overfit test
  của tác giả (AvgPool 0.605 vs Flatten 0.9950 trên 200 mẫu — cùng code
  conv, chỉ khác đầu ra), (c) thí nghiệm dịch-vòng độc lập của tôi
  (GAP kém nhạy vị trí 11.69x).
- "Conv chia sẻ trọng số + cục bộ kém hơn dense ở ngân sách nhỏ": VỮNG
  Ở MỨC ĐỦ cho negative result. Flatten giữ vị trí mà vẫn thua
  (0.507/0.5215 so với 0.584/0.597) trên 2 seed độc lập; overfit 0.9950
  kèm test 0.50 của tác giả cho thấy học vẹt thay vì khái quát. Đây là
  kết luận thực nghiệm có đối chứng công bằng tham số, không phải suy
  đoán suông. (Giải thích sâu hơn về inductive bias vẫn là giả thuyết
  hợp lý, không cần chứng minh thêm cho phạm vi thẻ.)
- "Lệch bias conv là subgradient, không phải bug": VỮNG. Chuỗi bằng
  chứng của tác giả đầy đủ (eps-không-đổi, đếm 3.7% z=0 khớp lý thuyết
  0.5^5, dw khớp trong khi db lệch, overfit Flatten 0.9950 chứng minh
  code đúng), và grad check độc lập của tôi tái hiện cùng mẫu hình
  (weight khớp, b1 lệch) trên code khác hẳn.
- Công bằng so sánh: ĐẠT. Cùng dữ liệu/seed theo R, cùng epochs/batch,
  tham số tương đương (A 12609 < MLP; B 17153 ≈ MLP — B thua dù tham số
  nhỉnh hơn, càng thuyết phục).

### Kết luận kiểm chéo: ĐẠT

- Số liệu chính tái hiện được ở seed mới (CNN thua MLP rõ rệt).
- Lập luận kiến trúc vững, có 2 thí nghiệm độc lập mới ủng hộ.
- Gradient check 1e-9 và giải thích subgradient được tái hiện độc lập.
- Không phát hiện bug, số liệu ảo, hay kết luận quá đà. Hướng tiếp theo
  tác giả đề xuất (k=16/32, bỏ pooling, 50k mẫu) nằm ngoài phạm vi, hợp lý.
- Đề xuất Kanzo: thẻ NCKH-014 review -> done + comment `[KIEM-DINH]`.

### Unresolved

- U-X1: chỉ kiểm 1 cấu hình (R=5, seed 777) theo đúng yêu cầu; R=6/7 ở
  seed mới chưa chạy (không cần thiết: R=5 đã phân biệt rõ, chênh 6 điểm).
- U-X2: chưa kiểm biến thể A (AvgPool) ở seed mới vì B là biến thể mạnh
  hơn mà còn thua; A đoán mò 0.50 trên seed cũ khó đảo ngược.
- U-X3: Kanzo: xem mục đồng bộ dưới (thất bại, đã ghi sổ).

## 2026-11-21 02:25 — đồng bộ Kanzo kiểm chéo NCKH-014 (thất bại, đã ghi sổ)

- GET board: thử 1 lỗi 500, thử 2 OK (27 thẻ). Thẻ NCKH-014: id=154
  `[ML] Thử CNN 1D thay MLP`, đang ở `[review]` — khớp sổ tác giả.
- POST `/api/tasks/154/comments` (`[KIEM-DINH] ĐẠT` + lý do + trỏ về sổ):
  cả 3 thử đều HTTP 500 (cách nhau 5s, timeout 30s) → THẤT BẠI.
- POST `/api/tasks/154/move {"status":"done"}`: cả 3 thử đều HTTP 500
  (cách nhau 5s, timeout 30s) → THẤT BẠI.
- Đối chiếu GET board sau ghi: thẻ 154 vẫn ở `[review]`.
- Đúng luật HIEN-CHUONG §6 + chỉ thị: hỏng thì ghi sổ và tiếp tục.
  Kết luận kiểm chéo (ĐẠT) nằm ở sổ cái này; nhờ Viện trưởng vá giúp:
  comment `[KIEM-DINH] ĐẠT` (nội dung như lệnh đã thử) và move thẻ 154
  review -> done khi Kanzo sống lại.
