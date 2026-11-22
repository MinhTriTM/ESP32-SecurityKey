# Sổ cái NCKH-034 — Đặng Bình (nhóm tooling, đợt 2B)

Nhiệm vụ (theo `vien-nghien-cuu/phan-cong.json`): **Rà soát mnemonic input lạ** —
chữ hoa, khoảng trắng thừa, từ gần đúng, thiếu/thừa từ (loại `t1-tay-chon`).
Phạm vi đọc: `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-034 trong `phan-cong.json`,
`vien-nghien-cuu/so-cai/README.md`, mục tiêu rà soát `tools/mnemonic.py`.
Nguyên tắc: REPO CHỈ ĐỌC (không sửa code, không commit), probe riêng trong `$env:TEMP`.

## 2026-11-21 02:15 — nhận việc

- Thẻ: [tooling] Rà soát mnemonic input lạ (Kanzo `esp32-securitykey`, tìm theo mã NCKH-034)
- Trạng thái: todo -> doing
- Kế hoạch: probe API `mnemonic_to_entropy` / `normalize_mnemonic` / `mnemonic_to_seed`
  và CLI `to-entropy` / `seed` / `new` / `--self-test` với input lạ; đối chiếu thông điệp lỗi.

## 2026-11-21 02:22 — báo cáo

### Đã làm

- Đọc `tools/mnemonic.py` (225 dòng) và `tools/bip39_english.txt` (2048 từ).
- Viết probe riêng `C:\Users\user\AppData\Local\Temp\nckh034_probe.py` (không chạm repo),
  chạy 7 nhóm input lạ + 8 case CLI. Vector chuẩn dùng xuyên suốt:
  `abandon × 11 + about` (= entropy 16 byte 0, hợp lệ BIP-39).

### Bảng input lạ (kết quả probe)

| # | Nhóm | Input lạ | Kết quả | Thông điệp lỗi (nguyên văn) | NX |
|---|------|----------|---------|------------------------------|----|
| 1 | Chữ hoa | `ABANDON ×11 + ABOUT` | OK, entropy đúng | (không lỗi) | Đạt, đúng BIP-39 |
| 2 | Chữ hoa | `Abandon ×11 + About` | OK, entropy đúng | (không lỗi) | Đạt |
| 3 | Chữ hoa | `aBaNdOn…` lộn xộn | OK, entropy đúng | (không lỗi) | Đạt |
| 4 | Khoảng trắng | Thừa space đầu/giữa/cuối | OK, entropy đúng | (không lỗi) | Đạt |
| 5 | Khoảng trắng | Tab + `\n` xen kẽ | OK, entropy đúng | (không lỗi) | Đạt |
| 6 | Khoảng trắng | Xuống dòng CRLF mỗi từ | OK, entropy đúng | (không lỗi) | Đạt |
| 7 | Khoảng trắng | NBSP (U+00A0) | OK, entropy đúng | (không lỗi) | Đạt |
| 8 | Gần đúng 1kt | `abandox` (sai chữ cuối) | Từ chối | `từ lạ không có trong bảng BIP-39: abandox` | Đạt, rõ + đúng CT |
| 9 | Gần đúng 1kt | `abanbon` (sai giữa) | Từ chối | `từ lạ không có trong bảng BIP-39: abanbon` | Đạt |
| 10 | Gần đúng 1kt | `abando` (thiếu 1kt) | Từ chối | `từ lạ không có trong bảng BIP-39: abando` | Đạt |
| 11 | Gần đúng 1kt | `abandonn` (thừa 1kt) | Từ chối | `từ lạ không có trong bảng BIP-39: abandonn` | Đạt |
| 12 | Gần đúng | `aban` (tiền tố 4kt) | Từ chối | `từ lạ không có trong bảng BIP-39: aban` | Đạt |
| 13 | Đúng bảng, sai checksum | `ability + abandon×10 + about` | Từ chối | `sai checksum: gõ nhầm từ hoặc sai thứ tự` | Đạt |
| 14 | Thiếu từ | 11 từ | Từ chối | `số từ phải là [12, 15, 18, 21, 24], nhận 11` | Đạt |
| 15 | Thiếu từ | 2 từ / 10 từ | Từ chối | `số từ …, nhận 2` / `nhận 10` | Đạt |
| 16 | Thừa từ | 13 từ / 25 từ | Từ chối | `số từ …, nhận 13` / `nhận 25` | Đạt |
| 17 | Rỗng | `""` và chỉ space/tab/`\n` | Từ chối **nhưng đếm sai** | `số từ phải là […], nhận 1` (thực tế 0 từ) | **Lỗi đếm (P1)** |
| 18 | Ngoài bảng | `xin chào…` (TV có dấu) | Từ chối | `từ lạ không có trong bảng BIP-39: xin` | Đạt (chỉ báo từ lạ đầu tiên) |
| 19 | Ngoài bảng | `bitcoin …` | Từ chối | `từ lạ không có trong bảng BIP-39: bitcoin` | Đạt |
| 20 | Ngoài bảng | `hello world …` | Từ chối checksum | `sai checksum: gõ nhầm từ hoặc sai thứ tự` | Đạt — `hello`/`world` CÓ trong bảng (dòng 855/2030), máy báo vậy là đúng |
| 21 | Ngoài bảng | `từ-lạ`, `abandon123` | Từ chối | `từ lạ …: từ-lạ` / `abandon123` | Đạt |
| 22 | Sai thứ tự | Đảo 2 từ cuối | Từ chối | `sai checksum: gõ nhầm từ hoặc sai thứ tự` | Đạt |
| 23 | Checksum | `abandon × 12` | Từ chối | `sai checksum: gõ nhầm từ hoặc sai thứ tự` | Đạt |
| 24 | `seed()` | Từ rác / rỗng / sai checksum | **Không từ chối, trả seed 64B, exit 0** | (không lỗi, im lặng) | **Rủi ro UX (P2)** |
| 25 | CLI `to-entropy` | Chữ hoa, từ lạ, thiếu từ, sai checksum | exit 0/1 đúng | `Cụm từ sai: …` + chi tiết | Đạt, rõ + đúng CT |
| 26 | CLI `new --words 13` | Số từ không hợp lệ | exit 1 | `--words phải là một trong [12, 15, 18, 21, 24]` | Đạt |
| 27 | CLI `--self-test` | Tự kiểm gốc | exit 0 | `self-test ok: bảng BIP-39 nguyên vẹn, vector chuẩn đúng, checksum bắt lỗi.` | Đạt |

### Đối chiếu chính tả thông điệp lỗi

- Đã đọc toàn bộ chuỗi lỗi trong `mnemonic.py`: `Cụm từ sai:`, `từ lạ không có trong
  bảng BIP-39:`, `sai checksum: gõ nhầm từ hoặc sai thứ tự`, `số từ phải là`,
  `Bảng từ lỗi:`, `Thiếu thư viện QR. Chạy: pip install -r requirements-qr.txt`,
  `--words phải là một trong`, `Entropy (… byte):`, `self-test ok: …` —
  **không phát hiện lỗi chính tả**, câu chữ rõ, nêu đúng nguyên nhân + giá trị nhận được.
- Ghi nhận nhỏ (không phải lỗi): `cmd_new` in `(xóa sau khi chia share!)` — từ `share`
  nửa Anh nửa Việt; gợi ý `chia sẻ (Shamir share)` cho thống nhất. Không sửa vì repo chỉ đọc.

### Phát hiện chính

- **P1 — Đếm sai input rỗng** (`mnemonic.py:56`): `normalize_mnemonic(mnemonic).split(" ")`
  với chuỗi rỗng cho `['']` nên báo `nhận 1` dù thực tế 0 từ (đã chứng minh:
  `python -c "print(''.split(' '), len(''.split(' ')))"` → `[''] 1`). Sửa gợi ý: dùng
  `.split()` thay vì `.split(" ")`. Không sửa trong đợt này (repo chỉ đọc).
- **P2 — `seed` im lặng với input hỏng**: `cmd_seed` và `mnemonic_to_seed` không gọi
  `mnemonic_to_entropy` nên cụm từ gõ sai vẫn cho seed 64 byte, exit 0. Về chuẩn BIP-39
  thì suy ra seed không bắt buộc checksum, nhưng tool nên cảnh báo để người dùng không
  lưu nhầm seed từ cụm từ sai chính tả. Kiến nghị: thêm cảnh báo hoặc flag `--no-check`.
- Không có gợi ý sửa từ gần đúng (`did you mean?`): đúng chuẩn nhưng kém thân thiện;
  ghi nhận để nhóm tooling cân nhắc, không tính là lỗi.

### Tự kiểm

- Lệnh: `python C:\Users\user\AppData\Local\Temp\nckh034_probe.py`
  -> output: 27 case như bảng trên, `PROBE-XONG`, exit 0.
- Lệnh: `python -c "print(''.split(' '), len(''.split(' ')))"`
  -> output: `[''] 1` (chứng minh lỗi đếm P1).
- Lệnh: `Select-String -Path tools/bip39_english.txt -Pattern '^(hello|world|bitcoin)$'`
  -> output: `hello` (dòng 855), `world` (dòng 2030) có trong bảng; `bitcoin` không có.
- Không sửa file repo nào ngoài sổ cái này; `git status` không có thay đổi code.

### Unresolved (chưa giải quyết, cần người khác)

1. P1 đếm `nhận 1` với input rỗng — chờ nhóm tooling sửa `.split(" ")` → `.split()`.
2. P2 `seed` im lặng với input hỏng — chờ quyết định UX (cảnh báo hay giữ nguyên theo BIP-39).
3. Không gợi ý từ gần đúng — chờ quyết định có làm `did you mean?` không.

- Trạng thái: doing -> review (file; Kanzo không có thẻ để chuyển)
- Kanzo: GET board OK (2026-11-21 02:23, timeout 30s, 1 lần là được), 32 thẻ
  (26 done + 6 todo), KHÔNG thấy thẻ mang mã NCKH-034 / Đặng Bình.
  Thẻ gần nhất là id 162 `[kiemdinh] Vector BIP-39 bổ sung (NCKH-024)` (chỉ trùng
  từ khóa `mnemonic`, không phải thẻ của mình). Theo luật: ghi sổ và tiếp tục,
  KHÔNG tự tạo thẻ. Không thực hiện move/comment.

## 2026-11-21 02:33 — kiểm chéo NCKH-042 Trịnh Bình (kiểm .gitignore, đợt 2B)

- Đối tượng: báo cáo 02:25 của NCKH-042 trong `vien-nghien-cuu/so-cai/NCKH-042.md`
  + `.gitignore` (21 dòng) + file thực tế trên đĩa. Repo CHỈ ĐỌC (không sửa,
  không commit); probe mô phỏng đặt trong `$env:TEMP\nckh034_xcheck042`.
- Đường kiểm ĐỘC LẬP (không chạy lại đúng lệnh tác giả): (1) lọc toàn bộ
  `git status --untracked-files=all` theo đuôi đáng ngờ thay vì `Get-ChildItem`
  toàn cây; (2) dựng repo git mới trong TEMP, chép `.gitignore` + 8 dòng đề xuất
  của tác giả rồi chạy `git check-ignore` mô phỏng từng đề xuất và từng rủi ro
  loại nhầm (`NHIP-TIM.log`, `docs/assets`).

### Xác minh độc lập (đều khớp báo cáo tác giả)

1. Vùng đã loại: `git status --ignored` chỉ còn đúng 2 mục `!! .tooling/`,
   `!! tools/__pycache__/`; `git ls-files` rỗng (0 commit); `git check-ignore -v`
   khớp `.tooling/`, `__pycache__/`, `build/` — khớp.
2. Đường lọt hiện tại: `tools/qr.png`, `*.temp`, `*.bak`, `*.swp`, `*.swo`,
   `*~`, `*.log` đều KHÔNG khớp luật nào (check-ignore in rỗng) — khớp luận
   điểm "thiếu luật" của tác giả.
3. File lọt THẬT: lọc 106 entry untracked theo đuôi
   `png|log|temp|bak|swp|swo|tmp|~` chỉ trúng đúng 1 file:
   `vien-nghien-cuu/so-cai/NHIP-TIM.log` (sổ nhịp tim có chủ đích, PHẢI giữ).
   Không có `*.png`/`*.temp`/`*.bak`/`*.swp`/`*.swo`/`*.tmp` nào lọt thật — khớp
   (tác giả đếm 88 entry lúc 02:25, tôi đếm 106 lúc 02:33 do các sổ
   NCKH-035..044 ghi thêm sau đó — toàn file `.md` hợp lệ, không phải sai lệch).
4. Đề xuất 1 `tools/*.png` (mô phỏng TEMP): loại `tools/qr.png`, KHÔNG chạm
   `docs/assets/future.png` (`::` không khớp) lẫn 3 ảnh `.jpg` chủ đích trong
   `docs/assets/` (62256/62257/65436.jpg) — phạm vi hẹp đúng như tác giả luận.
5. Đề xuất 2 (`*.temp`, `*.bak`, `*.swp`, `*.swo`, `*~`): cả 5 đuôi đều khớp
   trong mô phỏng — đạt.
6. Đề xuất 3 (`*.log` + `!vien-nghien-cuu/so-cai/NHIP-TIM.log`): `debug.log`
   bị loại, còn `NHIP-TIM.log` KHÔNG bị loại (`git check-ignore` thường in rỗng,
   exit False) — ngoại lệ có hiệu lực, file chủ đích an toàn.

### Ghi nhận nhỏ (không tính lỗi, không chặn đạt)

- `tools/*.png` không phủ thư mục con (`tools/sub/qr.png` vẫn lọt trong mô phỏng
  vì `*` không qua `/`). Ngoài phạm vi mô tả nhiệm vụ ("ảnh QR trong tools/"),
  chỉ nêu để nhóm tooling biết khi duyệt luật.

### Kết luận kiểm chéo: ĐẠT

- `[KIEM-DINH] đạt — Đặng Bình (NCKH-034) xác minh độc lập: 2 vùng ignore đúng,
  7 đường lọt đúng là thiếu luật, 0 file lọt thật (ngoài NHIP-TIM.log chủ đích),
  mô phỏng TEMP chứng minh cả 3 đề xuất có hiệu lực và không loại nhầm
  NHIP-TIM.log hay docs/assets.`
- Đề nghị: thẻ NCKH-042 `review` -> `done`; 3 đề xuất dòng ignore chờ
  Viện trưởng/nhóm tooling duyệt và áp vào `.gitignore`.

### Đồng bộ Kanzo (thẻ NCKH-042, opportunistic): HỎNG, đã ghi sổ

- GET board lần 1: HỎNG — `database error: database is locked` (đúng bệnh SQLite).
- Sau 5s, lần 2: HỎNG — HTTP 500 Internal Server Error.
- Sau 5s, lần 3 (hết 2 lần thử lại): HỎNG — HTTP 500.
- Không đọc được bảng nên không tìm được thẻ NCKH-042 (tác giả cũng báo không có
  thẻ này trên bảng lúc 02:28), KHÔNG comment/move được, KHÔNG tự tạo thẻ.
- Nhờ Viện trưởng khi Kanzo sống lại: dán comment `[KIEM-DINH] đạt` ở trên và
  move thẻ NCKH-042 `review` -> `done` (nếu thẻ tồn tại).

### Unresolved

1. Comment kiểm định + move `review` -> `done` chưa lên được Kanzo do sập 500
   (xem nhờ Viện trưởng ở trên); sổ cái này là nguồn sự thật.
2. 3 dòng ignore đề xuất chưa được áp vào `.gitignore` (ngoài quyền đợt chỉ đọc)
   — chờ Viện trưởng/nhóm tooling duyệt.
