# Sổ cái NCKH-005 — Hoàng An (nhóm tailieu, nhóm trưởng, đợt 1)

## 2026-11-21 01:20 — nhận việc
- Thẻ: [TAILIEU] Rà soát liên kết gãy docs (Kanzo id 142)
- Việc nhận: quét mọi liên kết nội bộ trong docs/ (.md), liệt kê liên kết gãy
  và chỗ dẫn sai. CHỈ BÁO CÁO, không sửa file. REPO CHỈ ĐỌC.
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md,
  mục NCKH-005 trong vien-nghien-cuu/phan-cong.json
  (tên chính thức: Hoàng An, nhóm tailieu, nhóm trưởng, đợt 1),
  vien-nghien-cuu/so-cai/README.md.
- Trạng thái: todo -> doing (sẽ đồng bộ Kanzo opportunistic sau khi ghi sổ)

## 2026-11-21 01:32 — báo cáo
- Đã làm: đọc toàn bộ 13 file .md trong docs/ (7 file gốc + 6 file
  docs/research/), trích mọi liên kết markdown bằng grep đối chứng
  (`Select-String -Pattern '\]\([^)]+\)'`), mở và đọc từng file đích để xác
  nhận tồn tại + đúng nội dung. Kiểm tra thêm: ảnh `![`, neo `](#`,
  link kiểu tham chiếu `[ref]:`, đường dẫn trong backtick.
- Tự kiểm:
  - `Get-ChildItem docs; docs/research; docs/reference; docs/assets; hardware`
    -> docs 7 md + 1 txt, research 6 md, reference đúng 3 PDF,
    assets 3 jpg, hardware đủ BOM.md/keys.md/wiring.md.
  - `Select-String -Pattern '\]\([^)]+\)'` trên 13 file -> 17 link nội bộ
    + 29 link ngoài (http/https, ngoài phạm vi, không kiểm tra).
  - Tìm `![`, `](#`, `^[ref]:` trong docs/ -> không có kết quả nào.
  - Đọc đầu file mọi đích: BOM.md, wiring.md, keys.md, hwtest.ino,
    fido_check.py, 70-u2f.rules, vault.py, mnemonic.py, split_secret.py,
    pqc.py, ml_distinguisher.py, QGAC/y-tuong.txt -> nội dung khớp chữ link.
- Kết quả: 17/17 liên kết nội bộ SỐNG và DẪN ĐÚNG. Không có gì để sửa.
- Trạng thái: doing -> review (đồng bộ Kanzo opportunistic, xem dưới)

### Bảng 17 liên kết nội bộ (tất cả ĐẠT)

| # | File nguồn:dòng | Chữ link | Đích giải | Kết quả |
|---|-----------------|----------|-----------|---------|
| 1 | 01-phan-tich-y-tuong.md:34 | tài liệu kiến trúc | docs/02-kien-truc.md | SỐNG, đúng kiến trúc |
| 2 | 03-phan-cung.md:7 | BOM | hardware/BOM.md | SỐNG, đúng BOM |
| 3 | 03-phan-cung.md:19 | sơ đồ đấu nối | hardware/wiring.md | SỐNG, tiêu đề "Sơ đồ đấu nối" khớp |
| 4 | 04-firmware.md:41 | BOM | hardware/BOM.md | SỐNG |
| 5 | 04-firmware.md:50 | hwtest | firmware/hwtest/hwtest.ino | SỐNG, đúng sketch hwtest |
| 6 | 04-firmware.md:62 | tool kiểm tra | tools/fido_check.py | SỐNG, đúng INIT/PING/GetInfo |
| 7 | 04-firmware.md:65 | scripts | scripts/ | SỐNG, thư mục có build/flash/run_tests |
| 8 | 04-firmware.md:75 | tài liệu bảo mật | docs/06-bao-mat.md | SỐNG |
| 9 | 05-huong-dan-su-dung.md:15 | udev rules | config/70-u2f.rules | SỐNG, đúng rules FIDO |
| 10 | 05-huong-dan-su-dung.md:17 | tool kiểm tra | tools/fido_check.py | SỐNG |
| 11 | 06-bao-mat.md:16 | sổ theo dõi key | hardware/keys.md | SỐNG, tiêu đề "Sổ theo dõi key" khớp |
| 12 | 06-bao-mat.md:39 | tài liệu sao lưu | docs/07-sao-luu-va-khoi-phuc.md | SỐNG |
| 13 | 07-sao-luu-va-khoi-phuc.md:25 | tài liệu bảo mật | docs/06-bao-mat.md | SỐNG |
| 14 | 07-sao-luu-va-khoi-phuc.md:125 | nghiên cứu distinguisher ML | docs/research/06-ml-distinguisher.md | SỐNG, đúng file |
| 15 | research/02-esp32s3-usb.md:7 | đúng cổng USB | docs/03-phan-cung.md | SỐNG, đúng mục cổng USB |
| 16 | research/04-tai-lieu-tham-khao.md:31 | docs/reference | docs/reference/ | SỐNG, đúng 3 PDF như ghi |
| 17 | research/04-tai-lieu-tham-khao.md:32 | docs/assets | docs/assets/ | SỐNG, 3 ảnh jpg board |

### Danh sách gãy: KHÔNG CÓ (0/17)

### Chỗ dẫn sai: KHÔNG CÓ (0/17)

### Ghi chú thêm (ngoài phạm vi link, không tính là lỗi)
- 29 link ngoài http/https trong docs/ + research/ không kiểm tra (nhiệm vụ
  chỉ yêu cầu link nội bộ).
- Đường dẫn trong backtick (`tools/*.py`, `scripts/run_tests.*`,
  `QGAC/ý tưởng.txt`, `workflows/autobuild.sh`) không phải link markdown;
  kiểm tra thêm thì tất cả file tương ứng đều tồn tại.
- Từng nghi `hardware/wiring.md` vắng mặt do kết quả search bị cắt bởi giới
  hạn matches; đã đọc trực tiếp file và `Get-ChildItem hardware` xác nhận
  file TỒN TẠI. Bài học: không kết luận gãy khi chưa đọc trực tiếp.
- Tên gọi: lệnh giao việc ghi "Hoàng Em", Viện trưởng đã đính chính tên
  chính thức theo phan-cong.json là Hoàng An. Từ mục này dùng Hoàng An.

### Đồng bộ Kanzo (opportunistic, API nghẽn)
- move 142 -> doing: 3/3 lần lỗi `database is locked` (cách nhau 5s). BỎ QUA.
- GET board đối chứng: thẻ 142 tồn tại, vẫn ở `todo`.
- move 142 -> review: lần 1 `database is locked`; lần 2 client timeout 30s
  nhưng GET board đối chứng sau đó cho thấy thẻ ĐÃ ở `review` (đúng như
  Hiến chương cảnh báo: timeout client không đồng nghĩa server chưa ghi).
- POST comment [BAO-CAO]: THÀNH CÔNG ngay lần 1 (comment id 10).
- Kết quả cuối: thẻ 142 ở `review` + có comment báo cáo. Đủ điều kiện
  chờ kiểm chéo theo Hiến chương mục 2.

## 2026-11-21 01:42 — kiểm chéo thẻ 150 của NCKH-012 (lượt kiểm chéo đợt 1)
- Thẻ: [KIEMDINH] Build sạch hai chế độ (Kanzo id 150, tác giả Hồ An NCKH-012)
- Phương pháp (đường khác, Hiến chương mục 2): KHÔNG chạy lại đúng lệnh của
  tác giả (không xóa cache toàn cục); thay vào đó: (1) build lại 1 chế độ
  HWCDC với --clean + --build-path riêng; (2) đối chiếu số liệu với README.md;
  (3) kiểm version cli/core; (4) kiểm FQBN với boards.txt + cờ compile --help.
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-012.md (toàn bộ),
  README.md (mục trạng thái), scripts/build_hwtest.ps1,
  firmware/hwtest/README.md.
- Đối chiếu số liệu:
  - README.md dòng 41: OTG 372 KB, HWCDC 302 KB. Tác giả báo OTG 372633B
    flash / 55680B RAM (28%/16%), HWCDC 302765B flash / 22784B RAM (23%/6%),
    bin 372784B / 302912B. 372633B≈372KB, 302765B≈302KB thập phân → KHỚP.
  - Tự tính: 372633/1310720=28.43%→28% ✓; 302765/1310720=23.10%→23% ✓;
    55680+272000=327680 ✓; 22784+304896=327680 ✓. Bin lớn hơn sketch
    ~150B (header) cả hai chế độ → hợp lý.
  - Lịch sử: không còn số liệu build hwtest nào khác trong repo
    (grep 372633|302765 chỉ trúng README.md + sổ NCKH-012) → README là
    mốc duy nhất, đã khớp.
- Version: `arduino-cli version` → 1.6.0; `core list` → esp32:esp32 4.0.0
  (installed=latest) → KHỚP với sổ tác giả và README.
- Cú pháp: `compile --help` có --clean ("cleanup the build folder and do not
  use any cached build") và --build-path → cờ tác giả dùng HỢP LỆ.
  boards.txt core 4.0.0: esp32s3 USBMode hwcdc (usb_mode=1) / default
  (usb_mode=0), CDCOnBoot cdc → đúng 2 FQBN tác giả báo.
  - Lưu ý nhỏ: scripts/build_hwtest.ps1 hiện CHỈ build OTG, không có sẵn
    --clean/--build-path (tác giả chạy thủ công, cú pháp đúng). Không ảnh
    hưởng kết luận; đề nghị Viện trưởng xem có nên bổ sung script 2 chế độ.
- Build đối chứng HWCDC (build-path riêng %TEMP%/hwtest-kc005-hwcdc, --clean,
  không ghi repo): exit 0, "Sketch uses 302765 bytes (23%)",
  "Global variables use 22784 bytes (6%), leaving 304896 bytes",
  hwtest.ino.bin 302912 bytes → TÁI HIỆN CHÍNH XÁC 100% số tác giả báo.
- Kết luận: [KIEM-DINH] ĐẠT — build sạch tái hiện được, số liệu khớp README
  và kiểm chứng độc lập. Đề nghị review -> done.
- Đồng bộ Kanzo (opportunistic, API nghẽn nặng — cả đọc cũng 500):
  - GET board: 2/2 HTTP 500 (không đọc được trạng thái thẻ 150).
  - POST comment [KIEM-DINH]: 2/2 HTTP 500.
  - POST move 150 -> done: 2/2 HTTP 500.
  - Mỗi lệnh cách nhau 5s, timeout 30s, đúng giới hạn 2 lần thử. DỪNG theo
    lệnh, nhờ Viện trưởng vá tay: gắn comment đạt + chuyển thẻ 150 -> done.
