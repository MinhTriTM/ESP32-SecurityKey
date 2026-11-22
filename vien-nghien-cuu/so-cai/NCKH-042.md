# Sổ cái NCKH-042 — Trịnh Bình (nhóm kiemdinh, đợt 2B)

## 2026-11-21 02:22 — nhận việc
- Nhiệm vụ: Kiểm .gitignore (loại t1-tay-chon)
- Mô tả: Xác nhận .tooling/build/__pycache__/ảnh QR đều bị loại.
- Nguồn đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-042), vien-nghien-cuu/so-cai/README.md, .gitignore
- Kế hoạch: repo CHỈ ĐỌC (không sửa file repo, không git commit); kiểm bằng git status/check-ignore + liệt kê file thực tế; ghi sổ cái này TRƯỚC rồi mới đồng bộ Kanzo.
- Trạng thái: todo -> doing

## 2026-11-21 02:25 — báo cáo
- Đã làm: kiểm .gitignore (21 dòng) bằng `git status`, `git check-ignore -v` (đường thật + đường giả định) và liệt kê file thực tế trên đĩa.
- Bối cảnh: repo chưa có commit nào (`git ls-files` rỗng, 88 entry untracked); `.tooling/` và `tools/__pycache__/` KHÔNG xuất hiện trong `git status` → đã bị loại. `git status --ignored` chỉ còn đúng 2 mục: `!! .tooling/`, `!! tools/__pycache__/`.
- Kết quả check-ignore (ĐẠT = bị loại):
  - ĐẠT: `.tooling/` (+ toàn bộ bên trong, kể cả `.tooling/arduino-cli.zip`), `build/` (gốc và lồng như `firmware/hwtest/build/`), `__pycache__/` (kể cả `tools/__pycache__/*.pyc`), `dist/`, `.pio/`, `.venv/`, `venv/`, `*.tmp`, `Thumbs.db`, `.DS_Store`, `.vscode/`, `*.bin`, `*.elf`, `*.map`.
  - LỌT (check-ignore không khớp, file giả định sẽ hiện lên git status): `tools/*.png` (ảnh QR), `*.temp`, `*.bak`, `*.swp`, `*.swo`, `*~`, `*.log`.
- File thực tế trên đĩa:
  - `.tooling/`: rất nhiều file (arduino-cli, data/packages, oqs, pylibs...) — tất cả đã bị loại, không lọt mục nào.
  - `tools/__pycache__/`: 7 file .pyc thực (fido_check, hid_echo x2, ml_distinguisher, pqc, split_secret, vault) — đã bị loại.
  - `__pycache__` khác: 19 thư mục, toàn bộ nằm trong `.tooling/pylibs` — đã bị loại theo `.tooling/`.
  - `*.png`: chưa có file nào trên đĩa (chưa lọt thực tế, nhưng thiếu luật nên file QR tương lai sẽ lọt).
  - `build/`, `dist/`, `.pio/`, `*.bin`, `*.elf`, `*.map` (ngoài .tooling): chưa tồn tại.
  - File tạm/log: chỉ có `vien-nghien-cuu/so-cai/NHIP-TIM.log` — đây là sổ cái nhịp tim có chủ đích, PHẢI được commit, không được loại.
  - Không có code hiện tại ghi `.png` (grep `\.png|save\(|qrcode\.make|to_file` trong tools/, scripts/ không trúng) — luật `tools/*.png` là phòng ngừa theo đúng mô tả nhiệm vụ.
- Chỗ lọt + đề xuất dòng ignore (chỉ đề xuất, KHÔNG tự sửa .gitignore vì repo chỉ đọc):
  1. Ảnh QR trong tools/ → thêm `tools/*.png` (phạm vi hẹp, tránh blanket `*.png` vì docs/assets/ chứa ảnh tài liệu có chủ đích như 62256.jpg).
  2. File tạm biến thể → thêm `*.temp`, `*.bak`, `*.swp`, `*.swo`, `*~` (hiện chỉ có `*.tmp`).
  3. File log → thêm `*.log` KÈM `!vien-nghien-cuu/so-cai/NHIP-TIM.log` (giữ lại sổ cái nhịp tim có chủ đích).
- Tự kiểm: `git status --porcelain --untracked-files=all` (88 entry, không có artifact); `git check-ignore -v` 2 đợt (đường thật + 20 đường giả định); `Get-ChildItem -Recurse` tìm build/__pycache__/*.png/*.tmp/*.log; `muse.search` tìm code ghi png. Lệnh chỉ đọc, không sửa repo, không commit.
- Trạng thái: doing -> review (chờ peer review; đề xuất ignore chờ Viện trưởng/nhóm tooling duyệt)

## 2026-11-21 02:28 — đồng bộ Kanzo (opportunistic)
- GET board lần 1: OK, 32 thẻ; không có thẻ nào nhắc NCKH-042 (rà title+description).
- Đối chiếu full-JSON lần 2: HỎNG — Kanzo báo `database error: database is locked` (đúng cảnh báo chập chờn).
- GET lại lần 3 (sau 5s, timeout 30s): OK, 32 thẻ; rà full JSON vẫn XÁC NHẬN không có thẻ NCKH-042.
- Move/comment: KHÔNG thực hiện — không có thẻ của mình để di chuyển; KHÔNG tự tạo thẻ theo lệnh.
- Ghi chú cho Viện trưởng: việc "Kiểm .gitignore" của NCKH-042 chưa có thẻ Kanzo riêng; sổ cái file này là nguồn chính. Kết quả kiểm + 3 đề xuất dòng ignore nằm ở mục báo cáo phía trên.

## 2026-11-21 02:34 — kiểm chéo NCKH-034 (Đặng Bình, mnemonic input lạ, đợt 2B)
- Vai: Trịnh Bình (NCKH-042) làm lượt kiểm chéo độc lập; repo CHỈ ĐỌC, không commit.
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-034.md` (bảng 27 case, P1/P2), `tools/mnemonic.py` (225 dòng).
- Đường kiểm khác tác giả: KHÔNG dùng probe của tác giả; chạy CLI `tools/mnemonic.py` trực tiếp + đọc code xác nhận nguyên nhân.
- Tái hiện P1 (input rỗng báo sai số):
  - `python tools/mnemonic.py to-entropy ""` → `Cụm từ sai: số từ phải là [12, 15, 18, 21, 24], nhận 1`, exit 1. KHỚP bảng tác giả (case 17).
  - `python tools/mnemonic.py to-entropy "   "` (chỉ khoảng trắng) → cùng thông điệp `nhận 1`, exit 1. KHỚP.
  - `python -c "print(repr(''.split(' ')), len(''.split(' ')))"` → `[''] 1`. KHỚP chứng minh của tác giả.
  - Đọc code: `mnemonic.py:56` `cleaned = normalize_mnemonic(mnemonic).split(" ")` — `normalize_mnemonic("")` trả `""`, `"".split(" ")` cho `['']` nên `len(cleaned)=1`. Nguyên nhân tác giả nêu ĐÚNG.
- Tái hiện P2 (seed im lặng):
  - `python tools/mnemonic.py seed abandox xyzzy` → in 128 ký tự hex (seed 64B), exit 0, không cảnh báo. KHỚP bảng tác giả (case 24).
  - `python tools/mnemonic.py seed ""` → in 128 ký tự hex khác, exit 0, không cảnh báo. KHỚP.
  - Đọc code: `cmd_seed` (dòng 119-121) gọi thẳng `mnemonic_to_seed`, không qua `mnemonic_to_entropy` nên không kiểm tra từ/checksum. Nguyên nhân tác giả nêu ĐÚNG.
- Case đối chứng thêm (đường CLI trực tiếp):
  - Vector chuẩn `abandon ×11 + about` → `Entropy (16 byte): 0000...0000`, exit 0. KHỚP.
  - Vector CHỮ HOA `ABANDON ×11 + ABOUT` → cùng entropy đúng, exit 0. KHỚP case 1-3 (chuẩn hóa chữ hoa).
  - `abandon ×12` → `Cụm từ sai: sai checksum: gõ nhầm từ hoặc sai thứ tự`, exit 1. KHỚP case 23.
- Kết luận kiểm chéo: **ĐẠT** — P1, P2 và 3 case đối chứng đều tái hiện khớp 100% (thông điệp nguyên văn + exit code); nguyên nhân `.split(" ")` và `cmd_seed` không kiểm tra đã xác minh trực tiếp trong code. Không phát hiện case nào sai lệch.
- Kanzo (http://100.101.100.100:4242/api, cách 5s, timeout 30s):
  - GET board: thấy thẻ id 182 `[tooling] Rà soát mnemonic input lạ (NCKH-034)`, status lúc tìm thấy là `todo` (tác giả trước đó không thấy thẻ; nay thẻ đã tồn tại).
  - POST comment `[KIEM-DINH] đạt + lý do`: lần 1 lỗi 500, thử lại lần 2 OK.
  - PATCH status todo → done (kết luận đạt): lần 1 lỗi 500, thử lại lần 2 OK.
  - GET xác minh cuối: `id=182 status=done comments=1`. (1 lần GET giữa chừng cũng lỗi 500 rồi OK ở lần thử lại — đúng cảnh báo chập chờn.)
- Lưu ý: thẻ ở `todo` chứ không phải `review` như lệnh dự kiến, nhưng vì kết luận đạt và công việc tác giả đã xong + đã kiểm định, đã chuyển thẳng sang `done` và ghi rõ trong comment.
- Unresolved (kế thừa từ tác giả, ngoài phạm vi kiểm chéo): P1 chờ sửa `.split(" ")` → `.split()`; P2 chờ quyết định UX cảnh báo/`--no-check`; gợi ý `did you mean?` chờ quyết định.
