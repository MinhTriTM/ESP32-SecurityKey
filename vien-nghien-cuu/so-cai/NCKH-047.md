# Sổ cái NCKH-047 — Lâm Bình (nhóm tailieu, đợt 2C)

## 2026-11-21 03:10 — nhận việc
- Nhiệm vụ: Ghi chú tuân thủ giấy phép (loại t1-tay-chon)
- Mô tả: MIT repo mình vs AGPL pico-fido: được/không được làm gì.
- Phạm vi theo lệnh: đọc HIEN-CHUONG.md, mục NCKH-047 trong phan-cong.json, so-cai/README.md, LICENSE, docs/04-firmware.md (mục giấy phép); viết ghi chú tuân thủ giấy phép khi build/dùng/phân phối thành FILE MỚI duy nhất docs/tuan-thu-giay-phep.md; không git commit; shell bắt buộc pwsh.
- Nguồn đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-047: Lâm Bình, tailieu, thành viên, đợt 2, tiêu đề "Ghi chú tuân thủ giấy phép"), vien-nghien-cuu/so-cai/README.md, LICENSE (MIT, Copyright 2026 ESP32-SecurityKey contributors), docs/04-firmware.md dòng 18 (pico-fido AGPL-3.0 bản cộng đồng) + tag v8.2/commit 15b848d821b4995eb1b29a5c2a4c24c25d1a768e.
- Kiểm kê trước khi viết: docs/tuan-thu-giay-phep.md chưa tồn tại (sẽ tạo mới đúng 1 file này trong docs); sổ cái NCKH-047.md cũng chưa tồn tại nên tạo mới để ghi tiến độ TRƯỚC theo Hiến chương (file trước bảng sau) — sổ cái là nhật ký bắt buộc, không tính vào "1 file mới" deliverable.
- Kế hoạch: ghi sổ này TRƯỚC, tạo docs/tuan-thu-giay-phep.md, rồi cuối việc thử đồng bộ Kanzo (GET board, move+comment, cách 5s, timeout 30s, tối đa 2 thử lại; hỏng hoặc không thấy thẻ thì ghi sổ, KHÔNG tự tạo thẻ).
- Trạng thái: todo -> doing

## 2026-11-21 03:15 — báo cáo
- Đã làm: tạo đúng 1 file mới docs/tuan-thu-giay-phep.md (5791 bytes) — ghi chú tuân thủ giấy phép gồm: bảng 2 phần độc lập (repo MIT vs pico-fido AGPL-3.0 v8.2 + commit ghim), mục được làm (MIT: dùng/sửa/phân phối/bán kèm LICENSE; AGPL: tự build/dùng thoải mái, phân phối phải kèm Corresponding Source, lưu ý điều 13 mạng), mục không được làm (không phân phối binary thiếu source, không đóng source bản sửa, không xóa notice, không gắn thêm hạn chế, không nhúng code AGPL vào repo MIT, không tin tag mù), checklist build/dùng/phân phối, 1 điểm chưa chốt (Secure Boot + flash encryption vs Installation Information của User Product — cần ý kiến pháp lý), nguồn (LICENSE, docs/04-firmware.md, link release v8.2).
- Tự kiểm: Get-ChildItem docs/*.md xác nhận tuan-thu-giay-phep.md mới xuất hiện; các link trong file (../LICENSE, 04-firmware.md, 06-bao-mat.md) đều tồn tại; không git commit (git status chỉ đọc). Ghi chú: lúc tự kiểm thấy thêm docs/checklist-bring-up-board.md và docs/tom-tat-du-an.md không có ở lần kiểm kê trước — không phải do mình tạo (agent khác đang chạy song song), mình chỉ tạo đúng 1 file docs được giao.
- Trạng thái: doing -> review (chờ NCKH-052 kiểm chéo theo mô tả thẻ)

## 2026-11-21 03:15 — đồng bộ Kanzo (thẻ 198)
- GET board: lần 1+2 → "database is locked"; lần 3 OK 60 thẻ (script parse lỗi do `$_.id + ' | '`, đã sửa thành interpolation); GET quét lại OK 60 thẻ, tìm thấy thẻ 198 "[tailieu] Ghi chú tuân thủ giấy phép (NCKH-047)" ở todo. Mô tả thẻ: đợt 2C, người kiểm chéo NCKH-052.
- Move 198 todo -> doing: OK. Comment nhận việc id 110: OK (sau 5s).
- Move 198 doing -> review: lần 1 locked, thử lại 1 locked, thử lại 2 timeout 30s — nhưng GET đối chiếu sau đó xác nhận thẻ đã ở review (đúng cảnh báo Hiến chương: timeout client không đồng nghĩa server chưa ghi). Không move thêm.
- Comment báo cáo id 111: OK sau 1 thử lại (lần 1 locked).
- Kết quả cuối: thẻ 198 ở review, đủ 2 comment (nhận việc + báo cáo). Không tự tạo thẻ.
- Unresolved: (1) chờ NCKH-052 kiểm chéo review -> done; (2) điểm Secure Boot vs Installation Information trong ghi chú cần ý kiến pháp lý, chưa kết luận.

## 2026-11-21 — kiểm chéo đợt 2C: NCKH-054 Phạm Cường (cài lib trên venv sạch)
- Đối tượng: vien-nghien-cuu/so-cai/NCKH-054.md (mục báo cáo 03:19: 4 requirements OK, liboqs bỏ qua native; mục Kanzo 03:25: thẻ 205 ở review, chờ kiểm chéo).
- Phương pháp ĐƯỜNG KHÁC: venv sạch RIÊNG `$env:TEMP\nckh047-xcheck-venv` (Python 3.12.0, pip 23.2.1 — khác venv nckh054-venv của tác giả), cài độc lập cả 4 requirements + smoke test; KHÔNG import oqs; xác nhận nhận định liboqs native bằng 2 nguồn độc lập (source wrapper đã cài + tài liệu repo). REPO CHỈ ĐỌC (chỉ nối thêm file sổ này), shell pwsh, không git commit, không chạm .tooling/, không pip system.
- Cài đặt độc lập (4/4 OK, pip freeze KHỚP TỪNG PHIÊN BẢN với 054):
  - vault: cryptography 50.0.2 + cffi 2.1.1 + pycparser 3.12 — OK (exit 0).
  - qr: qrcode 8.2 + pillow 13.0.0 + colorama 0.4.6 — OK (exit 0).
  - pqc: liboqs-python 0.16.0.2 — OK pip install (exit 0), KHÔNG import.
  - base: hidapi 0.15.0 — OK (exit 0).
  - Smoke test: `import cryptography` 50.0.2 OK; `qrcode.make` ảnh 290x290 + PIL 13.0.0 OK; `import hid` OK (hid.cp312-win_amd64.pyd trong venv). Khớp 100% số liệu 054 đã ghi.
- Nhận định liboqs native của 054 là ĐÚNG, xác nhận bằng đường khác:
  1. Source wrapper vừa cài (`site-packages/oqs/oqs.py`): chỉ là ctypes (`ct.CDLL`, `LoadLibrary`) + lệnh `cmake --build/--install` tự build lần đầu import — pip install không hề build native.
  2. Tài liệu repo đồng thuận: docstring tools/pqc.py (18-22), tools/requirements-pqc.txt (4-6), docs/moi-truong-dev-windows.md (75-76, 184-185) đều nói lần đầu `import oqs` tự build vào `%USERPROFILE%\_oqs`, cần CMake + VS C++.
  3. Quan sát máy: sau pip install pqc, `Test-Path $env:USERPROFILE\_oqs` vẫn False (không build); `cmake` KHÔNG có trên PATH (VS 2022 có thư mục nhưng toolchain đầy đủ chưa kiểm) — quyết định bỏ qua import/build của 054 là đúng phạm vi venv-TEMP.
- Kết luận: ĐẠT. Quy trình tái hiện 100% trên venv sạch khác; số liệu khớp từng phiên bản; lý do bỏ qua liboqs native đúng và có cơ sở độc lập.

## 2026-11-21 — đồng bộ Kanzo kiểm chéo NCKH-054 (thẻ 205, file trước bảng sau)
- GET board: thử 1 OK nhưng parse sai key (`cards`, 0 thẻ) — cấu trúc thật là `tasks`; quét lại OK 140 tasks, tìm thấy thẻ 205 "[kiemdinh] Cài lib trên venv sạch (NCKH-054)" ở review. Mỗi thao tác cách 5s, timeout 30s, tối đa 2 thử lại.
- COMMENT `[KIEM-DINH] đạt...`: POST /api/tasks/205/comments OK ngay thử 1 (id 123).
- MOVE review -> done: PUT thử 1-3 đều 405 Method Not Allowed; chuyển sang PATCH: thử 1 timeout 30s, thử 2-3 lỗi 500 — nhưng GET đối chiếu sau đó xác nhận thẻ đã ở done (đúng cảnh báo Hiến chương: timeout/500 không đồng nghĩa server chưa ghi). Không move thêm.
- Kết quả cuối: thẻ 205 ở done, có comment kiểm định id 123. Không tự tạo thẻ.
- Unresolved kiểm chéo: (1) liboqs native vẫn chưa kiểm chứng trên máy này (ngoài phạm vi cả 054 lẫn lượt kiểm chéo này — cần nhiệm vụ riêng có quyền build + CMake/VS C++ đầy đủ); (2) venv kiểm chéo `$env:TEMP\nckh047-xcheck-venv` giữ nguyên để Viện trưởng đối chiếu, chưa xóa.
