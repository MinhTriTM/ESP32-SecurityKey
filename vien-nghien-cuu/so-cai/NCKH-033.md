# Sổ cái NCKH-033 — Võ Bình (nhóm firmware, đợt 2B)

Nhiệm vụ (theo `vien-nghien-cuu/phan-cong.json`): **"Secure boot từ Arduino?"** — Nghiên cứu xem
Arduino-ESP32 có bật được secure boot/flash encryption không.

## 2026-11-21 02:15 +07:00 — nhận việc

- Đã đọc `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-033 trong `phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`.
- Phạm vi: Arduino-ESP32 core **4.0.0** trong `.tooling` + tài liệu web chính thức.
- Quy tắc: repo chỉ đọc, không git commit; ghi sổ TRƯỚC, đồng bộ Kanzo SAU.

## 2026-11-21 02:23 +07:00 — báo cáo nghiên cứu

### KẾT LUẬN (trả lời thẳng)

1. **Từ Arduino IDE / arduino-cli với core 4.0.0 nguyên bản: KHÔNG bật được** secure boot
   (Secure Boot V2) và flash encryption thật (mã hóa XTS-AES gắn eFuse). Không có menu, không có
   recipe, bootloader biên dịch sẵn đã tắt các tùy chọn này.
2. **Đường làm NẾU muốn có secure boot + flash encryption mà vẫn giữ code Arduino: CÓ** —
   chuyển sang mô hình **"Arduino as an ESP-IDF component"** (dự án ESP-IDF, Arduino là component),
   rồi bật `CONFIG_SECURE_BOOT` / `CONFIG_FLASH_ENCRYPTION_ENABLED` bằng menuconfig của IDF,
   tự build bootloader + ký ảnh + đốt eFuse bằng `espsecure`/`espefuse` (đã có sẵn trong
   `.tooling`, esptool 5.3.1).
3. Công cụ `bin_signing.py` kèm theo core **KHÔNG phải secure boot** — đó chỉ là ký RSA/ECDSA
   cho bản tin OTA ở tầng ứng dụng, ROM bootloader không kiểm tra chữ ký này.

### Bằng chứng trong core 4.0.0 (`.tooling`, tự tra)

Core: `.tooling/data/packages/esp32/hardware/esp32/4.0.0` (arduino release/v4.0.x 8f2cdd5bd),
libs S3: `.tooling/data/packages/esp32/tools/esp32s3-libs/4.0.0`, nền ESP-IDF **v6.1.1**
(`versions.txt`: `esp-idf: v6.1.1 051e4c4eb20`, `lib-builder: release/v6.1`).

1. `boards.txt`: grep `secure|encrypt|sign` (case-insensitive) → **0 kết quả** (chỉ dính 3 dòng
   "CPU Core Assignment" do chứa chữ "secu" trong... "Assignment"? không — do pattern `sign`
   khớp chữ "Assignment"). Danh sách `menu.*` đầy đủ: UploadSpeed, USBMode, CDCOnBoot, MSCOnBoot,
   DFUOnBoot, UploadMode, CPUFreq, FlashFreq, FlashMode, FlashSize, PartitionScheme, DebugLevel,
   PSRAM, LoopCore, EventsCore, MemoryType, EraseFlash, JTAGAdapter, ZigbeeMode, MatterNetwork,
   PinNumbers, ChipVariant, Revision, LORAWAN_*, LORA_*, SLOW_CLK_TPYE, einksize, NetworkLogLevel,
   DisplayModel, Language → **không có menu secure boot / flash encryption**.
2. `platform.txt`: grep `secure|encrypt|sign|efuse|bootloader` → chỉ thấy các recipe nạp
   **plain** `write-flash ... --flash-mode keep --flash-freq keep --flash-size keep` ở
   `tools.esptool_py.upload.pattern_args` (dòng ~369), `merge-bin` đóng gói 4 file
   (bootloader 0x1000, partitions 0x8000, boot_app0 0xe000, app 0x10000), và hook prebuild
   `elf2image` biến `bootloader_{build.boot}_{build.boot_freq}.elf` thành `.bin`.
   **Không có** `--encrypt`, không bước ký ảnh, không bước espefuse nào.
3. `tools/flasher.py`: grep `encrypt|secure|sign|efuse` → **0 kết quả** (chỉ là wrapper gọi
   esptool + đếm tiến trình).
4. `tools/bin_signing.py`: đọc toàn bộ 312 dòng — ký firmware bằng RSA-PSS/ECDSA rồi **nối thêm
   512 byte chữ ký vào cuối file .bin**, verify ở tầng app OTA. Không liên quan eFuse/ROM
   Secure Boot V2 (RSA-3072 digest trong eFuse BLOCK_KEY + REVOCATION). Đừng nhầm hai thứ này.
5. `sdkconfig` của `esp32s3-libs/4.0.0` (cấu hình lúc Espressif build sẵn libs + bootloader):
   - `# CONFIG_SECURE_BOOT is not set`
   - `# CONFIG_SECURE_FLASH_ENC_ENABLED is not set`
   - `# CONFIG_FLASH_ENCRYPTION_ENABLED is not set`
   - `# CONFIG_NVS_ENCRYPTION is not set`
   - `CONFIG_SECURE_BOOT_V2_RSA_SUPPORTED=y`, `CONFIG_SOC_SECURE_BOOT_SUPPORTED=y`,
     `CONFIG_SOC_FLASH_ENCRYPTION_XTS_AES=y` (chip S3 **hỗ trợ**, nhưng tính năng **tắt**),
   - `CONFIG_SECURE_ROM_DL_MODE_ENABLED=y` (download mode mở),
   - `CONFIG_SPI_FLASH_ENABLE_ENCRYPTED_READ_WRITE=y` (driver đọc/ghi mã hóa có mặt nhưng
     mã hóa chưa enable).
   Bootloader biên dịch sẵn: `bin/bootloader_{dio,qio,opi}_*.elf` (4 file) → build từ sdkconfig
   trên nên **không bật secure boot**, không thể "bật sau" bằng cờ Arduino vì Arduino không
   build lại bootloader từ source (chỉ `elf2image` file có sẵn). Muốn bootloader khác phải tự
   build bằng IDF rồi chép đè `bootloader.bin` vào sketch/variant (platform.txt có hook ưu tiên
   `bootloader.bin` trong sketch dir — dòng 139-140) — nhưng đó đã là đường vòng ra khỏi Arduino
   thuần.
6. `Kconfig.projbuild` của core: chỉ có các tùy chọn Arduino (variant, core chạy loop/event,
   log level, partition scheme, selective compilation...) → **không có** tùy chọn secure boot.
7. `firmware/hwtest/hwtest.ino`: grep chỉ dính `ESP.getEfuseMac()` (đọc MAC định danh, comment
   trong code đã ghi rõ "KHÔNG phải bí mật") → firmware hiện tại không dùng gì liên quan
   secure boot/flash encryption.
8. Điểm sáng duy nhất trong `.tooling`: gói `esptool_py/5.3.1` **có sẵn** `espefuse.exe` và
   `espsecure.exe` → đủ đồ nghề để đốt eFuse + ký/mã hóa ảnh **thủ công ngoài Arduino**.

### Bằng chứng web (nguồn chính thức Espressif)

- `esp-faq/docs/en/software-framework/security.rst` (repo espressif/esp-faq), mục
  "Secure Boot related":
  > "Can the secure boot function be enabled for ESP32 in Arduino development environment?
  > No. When developing in the Arduino environment, this function cannot be enabled via
  > simple configurations. If you are using the ESP32 Arduino Core, the only way to enable
  > secure boot is to use Arduino as an IDF component."
  → Khớp 100% với kết quả tra core ở trên.
- ESP-IDF Programming Guide (ổn định, mục Security Features): Secure Boot V2 = RSA-PSS-3072,
  digest khóa nằm trong eFuse (BLOCK_KEY0..2, tối đa 3 digest, revoke được); Flash Encryption =
  XTS-AES-128/256, key trong eFuse BLOCK_KEY (S3), bật bằng menuconfig rồi nạp lần đầu
  (device tự sinh key) hoặc pre-encrypted OTA. Tất cả đều là **luồng IDF**, không tồn tại trong
   Arduino IDE/CLI.
- Cộng đồng (PlatformIO forum "Secure Boot and Flash Encryption on ESP32S3", "Protect Arduino
  Sketch via flash encryption"): đồng thuận — framework Arduino không hỗ trợ; muốn có thì sang
  IDF (Arduino-as-component) hoặc tự ký/mã hóa thủ công sau build (không khuyến nghị cho sản phẩm).

### Đường làm NẾU dự án quyết bật (đề xuất cho Viện)

Điều kiện tiên quyết: chấp nhận **rời Arduino IDE thuần**, chuyển firmware sang dự án ESP-IDF
giữ nguyên code `.ino` dưới dạng component Arduino (Espressif hỗ trợ chính thức từ Arduino 2.x/3.x,
core 4.0.0 có `CMakeLists.txt` + `idf_component.yml` + `Kconfig.projbuild` sẵn để làm việc này).

1. Dựng dự án IDF v6.1 (khớp `versions.txt`), thêm `espressif/arduino-esp32` làm component,
   chuyển `hwtest.ino` thành `main.cpp` (giữ `setup()`/`loop()`, `AUTOSTART_ARDUINO=y`).
2. `idf.py menuconfig` → bật `Security features → Enable hardware Secure Boot in bootloader`
   (RSA-3072, S3 chỉ hỗ trợ V2) + `Enable flash encryption on boot` (XTS-AES-128, chế độ
   Release để khóa hoàn toàn).
3. `idf.py build` → IDF tự sinh khóa ký (`secure_boot_signing_key.pem`) + bootloader đã bật
   secure boot; `espsecure sign_data` ký app; nạp lần đầu `idf.py flash` (thiết bị tự sinh
   flash-encryption key trong eFuse ở lần boot đầu, sau đó flash bị mã hóa trong suốt).
4. Khóa máy: `espefuse.py --do-not-confirm burn_efuse DIS_DOWNLOAD_MANUAL_ENCRYPT`,
   vô hiệu hóa UART DL mode / JTAG theo `docs/06-bao-mat.md` của dự án; **cất kỹ**
   `secure_boot_signing_key.pem` (mất = không bao giờ update được nữa; lộ = mất secure boot).
5. Kiểm chứng: đọc flash raw bằng `esptool read-flash` → phải ra dữ liệu mã hóa (không thấy
   plaintext firmware); thử nạp firmware không ký → ROM từ chối boot.
6. Lưu ý riêng cho SecurityKey (khóa FIDO/PQC): secure boot + flash encryption **bảo vệ được**
   firmware/MAC Huber khỏi đọc trộm qua UART, nhưng **không thay thế** việc bảo vệ khóa người
   dùng trong NVS (cần bật thêm `NVS_ENCRYPTION` với key riêng, hoặc dùng eFuse BLOCK_KEY +
   Digital Signature peripheral của S3 cho khóa ký FIDO — để NCKH nhóm PQC/firmware đào sâu).

### Tự kiểm

- Lệnh đã chạy (pwsh, chỉ đọc, không sửa repo ngoài file sổ này):
  - `Get-ChildItem` cây `.tooling/.../esp32/{hardware,tools}` → xác định core 4.0.0, libs S3 4.0.0.
  - `Select-String boards.txt -Pattern '^menu\.'` → liệt kê toàn bộ menu (không có security).
  - `Select-String boards.txt -Pattern 'secure|encrypt|sign'` → 0 hit thực (3 hit giả "Assignment").
  - `Select-String platform.txt -Pattern 'secure|encrypt|sign|efuse|bootloader'` → chỉ recipe nạp plain.
  - `Select-String .../sdkconfig -Pattern 'SECURE|ENCRYPT|SIGN|EFUSE'` → 4 dòng `is not set` quyết định.
  - Đọc full `tools/bin_signing.py` (312 dòng) → xác định là OTA signing, không phải secure boot.
  - `Select-String tools/flasher.py -Pattern 'encrypt|secure|sign|efuse'` → 0 hit.
  - `Get-Content versions.txt` → IDF v6.1.1, arduino v4.0.x.
  - `Get-ChildItem esptool_py/5.3.1` → có `espefuse.exe`, `espsecure.exe`.
  - Web: esp-faq security.rst (trích dẫn nguyên văn ở trên), IDF Security Features, 2 thread PlatformIO.
- Peer review: chưa (chờ kiểm chéo).

### Unresolved / cần Viện quyết

- [ ] Dự án có chấp nhận rời Arduino IDE sang IDF + Arduino-as-component không? (Quyết định kiến
  trúc, ảnh hưởng toàn bộ nhóm firmware + runbook nạp của NCKH-015/021/039.)
- [ ] Chưa thực nghiệm đốt eFuse thật (one-time, không undo) — mọi bước đốt key chỉ làm trên
  board thử nghiệm rẻ tiền, KHÔNG làm trên board chính trước khi Viện duyệt.
- [ ] Khóa ký secure boot + quy trình cất giữ/ký release chưa có — cần 1 thẻ việc riêng cho nhóm PQC.
- [ ] NVS encryption + DS peripheral cho khóa FIDO: ngoài phạm vi thẻ này, đề nghị thẻ follow-up.

## Kanzo

- 2026-11-21 02:24 +07:00 — GET `/api/board?project=esp32-securitykey` (timeout 30s): **thành công**,
  bảng có 32 thẻ (id 138-172, gồm 5 thẻ todo + 27 thẻ done, mã cao nhất là NCKH-028).
- Tìm `NCKH-033|Võ Bình|Secure boot từ Arduino` trong toàn bộ title+description: **không thấy thẻ**.
- Theo quy định (không thấy thẻ thì ghi sổ và tiếp tục, KHÔNG tự tạo thẻ): **không move, không
  comment, không tạo thẻ**. Viện trưởng đối chiếu sổ này và vá bảng khi cần.

## 2026-11-21 — kiểm chéo đợt 2B: NCKH-041 Đinh Bình (`docs/moi-truong-dev-ubuntu.md`)

Vai: Võ Bình (NCKH-033), kiểm độc lập bằng ĐƯỜNG KHÁC (đối chiếu doc với
scripts/config/runbook hiện có, không đọc theo mạch của tác giả).

### Kết luận: ĐẠT (có 4 ghi nhận chữ nghĩa nhỏ, không ảnh hưởng tính đúng)

### Đối chiếu từng điểm (đều kiểm trực tiếp trên repo)

1. `python3` ≥ 3.10: ĐÚNG — `tools/requirements.txt` (comment dòng 1),
   `tools/fido_check.py:11` (`dict | None`), `tools/pqc.py:28` đều yêu cầu 3.10.
2. `pip install --target .tooling/pylibs` + 4 file requirements: ĐÚNG — cả 4 file
   tồn tại, nội dung khớp (hidapi / cryptography / qrcode+pillow / liboqs-python);
   quy ước `--target` khớp `tools/requirements-pqc.txt:3` và docstring `pqc.py:8`.
3. PEP 668 (`--break-system-packages`): ĐÚNG — khuyến nghị an toàn vì đích cài là
   `.tooling/pylibs` của repo, không động gói hệ thống.
4. `run_tests.sh`: ĐÚNG — đủ 7 tool đúng tên (`fido_check hid_echo split_secret
   mnemonic vault pqc ml_distinguisher`), `PYTHONPATH` + `OQS_INSTALL_PATH` khớp
   script từng biến, cơ chế `fail=1` khớp mô tả "1 tool hỏng là cả script báo hỏng".
5. liboqs native trên Ubuntu: ĐÚNG — `.tooling/oqs/bin` chỉ có `oqs.dll`
   (Windows) nên khẳng định "không dùng được trên Ubuntu" là chính xác; cơ chế tự
   build lần đầu `import oqs` + trỏ `OQS_INSTALL_PATH` tới thư mục chứa `.so` khớp
   docstring `pqc.py` và hành vi liboqs-python.
6. arduino-cli + core + FQBN: ĐÚNG — `build_hwtest.sh` gọi `arduino-cli` trên PATH
   và thoát lỗi nếu thiếu (khác đúng bản `.ps1` dùng `.tooling/arduino-cli.exe`);
   FQBN trong doc khớp từng ký tự với script
   (`esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default`); `core install esp32:esp32`
   và giải thích `USBMode=default`=HWCDC/HID TẮT khớp runbook Ubuntu mục 5.
7. dialout/udev: ĐÚNG — `usermod -aG dialout` + `id -nG` + đăng nhập lại khớp runbook
   mục 2; `cp config/70-u2f.rules` + reload/trigger khớp; VID `303a` + nhóm `plugdev`
   khớp file config; `brltty`/`ModemManager`, cấm `sudo chmod 666`/`sudo upload`
   đều khớp runbook.
8. Liên kết nội bộ: ĐÚNG 16/16 đích duy nhất (21 lượt trích dẫn) — Test-Path True toàn bộ:
   2 script `.sh`, 2 script `.ps1`, 4 requirements, `pqc.py`, `70-u2f.rules`,
   2 runbook, `03-phan-cung.md`, `04-firmware.md`, `hardware/wiring.md`, `hardware/BOM.md`.
9. Tham chiếu runbook: ĐÚNG ở mục 2–3, mục 4, mục 5 (đã đọc: mục 5 có đoạn FQBN
   `USBMode=otg`), Windows "bước 9" (đã đọc: mục 9 có đủ 4 bước giữ BOOT/RESET).
10. Chuỗi `self-test ok: đóng gói report HID echo đúng.` khớp từng chữ với
    `tools/hid_echo.py:39`.
11. Phạm vi 1 file mới, không đòi hỏi sửa file khác: HỢP LỆ.

### Ghi nhận nhỏ (đề nghị NCKH-041 sửa khi rảnh, không bắt buộc)

- G1. Doc viết "runbook (mục 3.2)" và "(runbook mục 4.2, 6.2)" nhưng runbook Ubuntu
  chỉ có `## 0–9`, không có mục con `###` — nên sửa thành "mục 3", "mục 4/mục 6".
- G2. Bảng lỗi dòng "`build_hwtest.sh` báo thiếu platform/core": script không tự in
  câu đó, lỗi do `arduino-cli` ném ra — nên sửa thành "`arduino-cli` báo thiếu
  platform/core".
- G3. Checklist đòi `id -nG` có `plugdev` nhưng doc (và cả runbook) không hướng dẫn
  `usermod -aG plugdev` — nên bổ sung 1 dòng lệnh hoặc bỏ "(và plugdev)".
- G4. Sổ NCKH-041 ghi "bảng 21 lỗi" nhưng đếm thực 19 dòng dữ liệu — lệch ở sổ,
  doc không tự ghi số nên doc không sai.

### Kanzo (board chập chờn, theo đúng nhịp lệnh: cách 5s, timeout 30s, tối đa 2 thử lại)

- Lần 1: GET `/api/board?project=esp32-securitykey` → 500 Internal Server Error.
- Lần 2 (sau 5s): thành công nhưng parse `cards` rỗng (count=0, cấu trúc không như
  kỳ vọng, chưa kịp xem raw).
- Lần 3 (sau 5s, thử lại cuối): 500 Internal Server Error.
- Hết số lần thử, KHÔNG xác định được thẻ NCKH-041 → không comment, không move,
  không tạo thẻ. Sổ cái này là bản chính, Viện trưởng vá bảng khi cần.

### Unresolved

- [ ] Kanzo chưa đồng bộ được (lỗi 500 / parse rỗng) — cần Viện trưởng kiểm tra board
  và move thẻ NCKH-041 review → done giúp (kiểm chéo: ĐẠT).
- [ ] G1–G4 chờ NCKH-041 sửa (không chặn done).
