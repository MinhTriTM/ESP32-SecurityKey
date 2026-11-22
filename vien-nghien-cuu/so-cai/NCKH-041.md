# Sổ cái NCKH-041 — Đinh Bình (nhóm tailieu, đợt 2B)

Nhiệm vụ theo `vien-nghien-cuu/phan-cong.json`: "Hướng dẫn môi trường dev Ubuntu — Tương tự bản Windows."
Phạm vi 1 file mới duy nhất: `docs/moi-truong-dev-ubuntu.md`.

## 2026-11-21 02:21 — nhận việc
- Thẻ: [tailieu] Hướng dẫn môi trường dev Ubuntu (Kanzo, chưa rõ id — đối chiếu cuối việc)
- Trạng thái: todo -> doing (ghi sổ trước, đồng bộ Kanzo sau theo HIEN-CHUONG §6 + NHIP-TIM)
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-041 trong phan-cong.json,
  vien-nghien-cuu/so-cai/README.md, scripts/run_tests.sh, scripts/build_hwtest.sh.
- Đọc thêm để viết đúng kỹ thuật: docs/runbook-nap-hwtest-windows.md (NCKH-015),
  docs/runbook-nap-hwtest-ubuntu.md (NCKH-021), scripts/run_tests.ps1,
  scripts/build_hwtest.ps1, tools/requirements*.txt, tools/pqc.py (docstring),
  config/70-u2f.rules, firmware/hwtest/README.md.
- Ghi nhận: bản Windows của NCKH-035 chưa có trong repo
  (không thấy docs/moi-truong-dev-windows.md, chưa có so-cai/NCKH-035.md),
  nên bài Ubuntu này tự thiết kế cấu trúc song song: từ máy trắng đến chạy được
  run_tests và build (python3, arduino-cli, core ESP32, lib, udev, lỗi thường gặp).

## 2026-11-21 02:30 — báo cáo
- Đã làm: tạo MỚI duy nhất `docs/moi-truong-dev-ubuntu.md` (9 mục: lấy repo,
  gói hệ thống, pip --target .tooling/pylibs + PEP 668, run_tests.sh + liboqs
  native trên Ubuntu, arduino-cli + core esp32 + build_hwtest.sh, dialout/udev
  + config/70-u2f.rules, checklist 7 điểm, bảng 21 lỗi thường gặp, đọc tiếp).
  Không sửa bất kỳ file nào khác.
- Tự kiểm: Test-Path 2 file True; kiểm 16/16 liên kết nội bộ trong bài mới
  đều trỏ tới file có thật (không GAY); git status chỉ đọc (repo untracked
  toàn bộ từ trước, không commit theo lệnh).
- Trạng thái: doing -> review (ghi sổ trước, đồng bộ Kanzo sau).
- Unresolved: bản Windows NCKH-035 chưa có nên chưa đối chiếu song song được;
  nội dung Ubuntu viết từ kỹ thuật thực tế trong scripts/tools/runbook.

## 2026-11-21 02:35 — đồng bộ Kanzo
- GET /api/board?project=esp32-securitykey timeout 30s: lần 1 hỏng (500
  Internal Server Error), chờ 5s thử lại lần 2 thành công: 32 thẻ,
  KHÔNG thấy thẻ nào chứa NCKH-041 / dev Ubuntu.
- Theo lệnh: không tự tạo thẻ, dừng đồng bộ ở đây, Viện trưởng đối chiếu
  sổ này vá lên bảng khi cần.
- Trạng thái thẻ Kanzo: không đổi được (không có thẻ) — sổ cái là bản chính.

## 2026-11-21 02:32 +07:00 — kiểm chéo NCKH-033 (Võ Bình) đợt 2B

Vai trò: Đinh Bình (NCKH-041) kiểm độc lập kết luận của NCKH-033:
"Arduino KHÔNG bật được secure boot; đường làm là Arduino-as-IDF-component".
Repo chỉ đọc, không git commit. Đã đọc toàn bộ `so-cai/NCKH-033.md`.

### Xác minh độc lập (đường khác, tự grep lại từ .tooling)

1. `boards.txt`: `Select-String 'secure|encrypt'` → **0 hit**; `^menu\..*(secure|secur|encrypt|crypto|efuse)` → **0 hit**; liệt kê toàn bộ menu được **33 menu** (UploadSpeed, USBMode, CPUFreq, FlashMode, PartitionScheme, PSRAM, ...), **không menu bảo mật nào**. Khớp sổ 033.
2. `platform.txt`: recipe `tools.esptool_py.upload.pattern_args` (dòng 369) là **nạp plain** `write-flash ... --flash-mode keep --flash-freq keep --flash-size keep` 4 địa chỉ (bootloader/partitions/boot_app0/app); grep `--encrypt|secure|efuse|sign_data|espsecure` → **0 hit**. Khớp sổ 033.
3. `sdkconfig` esp32s3-libs 4.0.0: `# CONFIG_SECURE_BOOT is not set`, `# CONFIG_SECURE_FLASH_ENC_ENABLED is not set`, `# CONFIG_FLASH_ENCRYPTION_ENABLED is not set`, `# CONFIG_NVS_ENCRYPTION is not set`; ngược lại `CONFIG_SOC_*_SUPPORTED=y` (chip hỗ trợ, tính năng tắt) và `CONFIG_SECURE_ROM_DL_MODE_ENABLED=y` (download mode mở). Khớp từng dòng sổ 033.
4. `tools/bin_signing.py`: 312 dòng, docstring "OTA Update Signing Tool for ESP32 Arduino", các hàm generate/extract/sign/verify RSA-ECDSA cho OTA; grep `efuse|secure.?boot|BLOCK_KEY|REVOCATION` → **0 hit**. Xác nhận: chỉ là ký OTA tầng app, KHÔNG phải secure boot. Khớp sổ 033.
5. `tools/flasher.py`: grep `encrypt|secure|sign|efuse` → **0 hit** (wrapper esptool thuần). Khớp sổ 033.
6. `esptool_py/5.3.1`: có `espefuse.exe` + `espsecure.exe` → đủ đồ nghề đốt eFuse/ký ảnh thủ công ngoài Arduino. Khớp sổ 033 (điểm sáng duy nhất).

### Kết luận kiểm định: [KIEM-DINH] ĐẠT

- Mọi bằng chứng độc lập đều tái hiện đúng số liệu của NCKH-033 (0 hit / 4 dòng not set / 312 dòng OTA / recipe plain).
- Kết luận "Arduino thuần KHÔNG bật được secure boot; muốn có thì sang Arduino-as-IDF-component" là **đúng và đủ bằng chứng**.
- Đề xuất đường làm 6 bước trong sổ 033 hợp lý, có cảnh báo one-time eFuse và cất khóa ký — không yêu cầu sửa.

### Đồng bộ Kanzo (thẻ NCKH-033)

- Lần 1 GET `/api/board?project=esp32-securitykey` (timeout 30s): thành công, parse **không thấy thẻ** chứa NCKH-033.
- Chờ 5s, lần 2: **500 Internal Server Error**.
- Chờ 5s, lần 3 (thử lại cuối): thành công, parse **HIT-033 = 0** (không thấy thẻ).
- Theo lệnh (hỏng hoặc không thấy thẻ thì ghi sổ và tiếp tục, KHÔNG tự tạo thẻ): **không comment, không move, không tạo thẻ**. Viện trưởng đối chiếu sổ này vá bảng khi cần.

### Unresolved

- [ ] Không move được thẻ NCKH-033 review->done trên Kanzo vì không tìm thấy thẻ (dù kết luận kiểm định là ĐẠT) — Viện trưởng xử lý.
- [ ] Các unresolved gốc của NCKH-033 (quyết kiến trúc rời Arduino IDE, cấm đốt eFuse board chính khi chưa duyệt, khóa ký + NVS encryption follow-up) vẫn nguyên — thuộc thẩm quyền Viện, kiểm chéo không đóng thay.
