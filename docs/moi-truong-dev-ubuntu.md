# Hướng dẫn dựng môi trường dev trên Ubuntu

> Tác giả: Đinh Bình (NCKH-041, nhóm tailieu, đợt 2B).
> Phạm vi: từ máy Ubuntu trắng đến khi chạy được `./scripts/run_tests.sh`
> và `./scripts/build_hwtest.sh` trong repo này.
> Bài song sinh Windows do Bùi Bình (NCKH-035) phụ trách — cùng cấu trúc:
> Python → thư viện → arduino-cli + core ESP32 → udev → kiểm tra → lỗi thường gặp.
> Nguồn kỹ thuật đối chiếu: [scripts/run_tests.sh](../scripts/run_tests.sh),
> [scripts/build_hwtest.sh](../scripts/build_hwtest.sh),
> [scripts/run_tests.ps1](../scripts/run_tests.ps1),
> [scripts/build_hwtest.ps1](../scripts/build_hwtest.ps1),
> [tools/requirements.txt](../tools/requirements.txt),
> [tools/requirements-pqc.txt](../tools/requirements-pqc.txt),
> [tools/requirements-qr.txt](../tools/requirements-qr.txt),
> [tools/requirements-vault.txt](../tools/requirements-vault.txt),
> [tools/pqc.py](../tools/pqc.py) (docstring cài đặt),
> [config/70-u2f.rules](../config/70-u2f.rules),
> [runbook nạp hwtest Ubuntu](runbook-nap-hwtest-ubuntu.md),
> [runbook nạp hwtest Windows](runbook-nap-hwtest-windows.md).

Đã kiểm chứng tư tưởng trên Ubuntu 22.04 và 24.04 (x86_64).
Mọi lệnh dưới đây chạy trong Terminal, tại thư mục gốc repo sau bước 2.

## 0. Lấy repo về máy

1. Cài git nếu máy trắng chưa có:
   ```
   sudo apt update
   sudo apt install -y git
   ```
2. Clone repo rồi vào thư mục gốc:
   ```
   git clone <URL-REPO> ESP32-SecurityKey
   cd ESP32-SecurityKey
   ```
   Từ đây, mọi đường dẫn tương đối (`tools/...`, `scripts/...`) đều tính từ thư mục này.

## 1. Cài gói hệ thống (làm 1 lần cho mỗi máy)

1. Cài Python 3, pip, curl và công cụ build:
   ```
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv curl git \
     build-essential cmake ninja-build pkg-config \
     libhidapi-hidraw0 libudev-dev
   ```
   - `python3` ≥ 3.10 là bắt buộc (`tools/fido_check.py` dùng cú pháp `dict | None`).
   - `build-essential` + `cmake` + `ninja-build`: để lần đầu `import oqs`
     tự biên dịch thư viện native liboqs (xem mục 3.3).
   - `libhidapi-hidraw0`: backend cho gói Python `hidapi`
     (`tools/hid_echo.py`, `tools/fido_check.py`).
2. Kiểm tra phiên bản:
   ```
   python3 --version   # phải in 3.10 trở lên
   pip3 --version
   cmake --version
   gcc --version
   ```
   Điểm nhìn đạt: `python3 --version` in `Python 3.10.x` trở lên.
   Ubuntu 22.04 kèm Python 3.10, Ubuntu 24.04 kèm Python 3.12 — đều đạt.

## 2. Cài thư viện Python vào `.tooling/pylibs` (không cài system-wide)

Repo không cài thư viện vào hệ thống. Mọi tool Python chạy với
`PYTHONPATH` trỏ vào `.tooling/pylibs` (xem `scripts/run_tests.sh`).
Cài đúng 4 nhóm requirements:

```
python3 -m pip install --target .tooling/pylibs -r tools/requirements.txt
python3 -m pip install --target .tooling/pylibs -r tools/requirements-vault.txt
python3 -m pip install --target .tooling/pylibs -r tools/requirements-qr.txt
python3 -m pip install --target .tooling/pylibs -r tools/requirements-pqc.txt
```

Ghi chú:

- `--target .tooling/pylibs` là quy ước của repo (ghi trong
  `tools/requirements-pqc.txt` và docstring `tools/pqc.py`). Không dùng
  `sudo pip install`, không cài vào `/usr/lib/python3*/`.
- Trên Ubuntu 23.04+ (kể cả 24.04), pip ngoài venv có thể chặn với lỗi
  `externally-managed-environment` (PEP 668). Cách xử lý đúng cho repo này:
  thêm cờ `--break-system-packages` vào 4 lệnh trên (an toàn vì đích cài là
  thư mục `.tooling/pylibs` của repo, không động vào gói hệ thống).
- Nhóm `requirements.txt` (`hidapi`) cần `libhidapi-hidraw0` đã cài ở mục 1;
  thiếu là `pip install` vẫn xong nhưng `import hid` hỏng lúc chạy.
- Nhóm `requirements-pqc.txt` (`liboqs-python`) chỉ là wrapper ctypes;
  thư viện native liboqs được xử lý ở mục 3.3.

## 3. Chạy `run_tests.sh` (7 self-test Python)

### 3.1. Lệnh chuẩn

```
./scripts/run_tests.sh
```

Script này làm 3 việc (đọc `scripts/run_tests.sh` để đối chiếu):

1. `export PYTHONPATH="$ROOT/.tooling/pylibs"` — để Python thấy thư viện ở mục 2.
2. `export OQS_INSTALL_PATH="$ROOT/.tooling/oqs"` — gợi ý chỗ tìm liboqs native.
3. Chạy lần lượt `--self-test` của 7 tool:
   `fido_check`, `hid_echo`, `split_secret`, `mnemonic`, `vault`, `pqc`,
   `ml_distinguisher`. Bất kỳ tool nào hỏng thì script thoát mã khác 0.

Điểm nhìn đạt: 7 khối `=== <tên-tool> ===` đều in `self-test ok` / `ok`
tương ứng, lệnh thoát mã 0 (`echo $?` in `0`).

### 3.2. Chạy lẻ từng tool để debug

```
export PYTHONPATH="$PWD/.tooling/pylibs"
export OQS_INSTALL_PATH="$PWD/.tooling/oqs"
python3 tools/<ten-tool>.py --self-test
```

Ví dụ kiểm nhanh không cần board:

```
python3 tools/hid_echo.py --self-test
# phải in: self-test ok: đóng gói report HID echo đúng.
```

### 3.3. Riêng `pqc`: thư viện native liboqs trên Ubuntu

`tools/pqc.py` cần 2 lớp: gói Python `oqs` (đã cài ở mục 2) + thư viện
native liboqs (file `.so` trên Ubuntu, khác `.dll` trên Windows — thư mục
`.tooling/oqs` kèm sẵn trong repo là bản build cho Windows, **không dùng
được trên Ubuntu**).

Lần đầu `import oqs`, liboqs-python sẽ **tự clone + biên dịch liboqs**
vào thư mục `_oqs` trong home của bạn. Để việc này thành công cần
`cmake` + `gcc` đã cài ở mục 1 và máy có mạng (tải source liboqs).
Lần chạy `--self-test` đầu tiên của `pqc` vì vậy có thể mất vài phút —
bình thường, không phải treo.

Nếu đã tự build liboqs tay vào chỗ khác, trỏ biến môi trường tới đó
trước khi chạy (cách này hơn là để tự build mỗi máy mỗi khác):

```
export OQS_INSTALL_PATH=/duong/toi/thu-muc-liboqs-tu-build
./scripts/run_tests.sh
```

(oqs tìm thư viện `.so` trong thư mục `lib` bên dưới `OQS_INSTALL_PATH`.)

## 4. Cài arduino-cli + core ESP32 (để build firmware)

Khác bản Windows (dùng `arduino-cli.exe` bỏ sẵn trong `.tooling`,
xem `scripts/build_hwtest.ps1`), bản Ubuntu dùng `arduino-cli` cài trên
hệ thống: `scripts/build_hwtest.sh` gọi `arduino-cli` trên `PATH`
và thoát lỗi ngay nếu không thấy.

1. Cài `arduino-cli` theo hướng dẫn chính thức:
   ```
   curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
   sudo mv bin/arduino-cli /usr/local/bin/
   arduino-cli version
   ```
   Điểm nhìn đạt: `arduino-cli version` in số phiên bản, không báo
   `command not found` (nếu còn báo, mở Terminal mới cho `PATH` ăn).
2. Cập nhật chỉ mục board rồi cài core ESP32 của Espressif:
   ```
   arduino-cli core update-index
   arduino-cli core install esp32:esp32
   ```
   Lệnh này tải toolchain vài trăm MB, cần mạng ổn định.
   Kiểm tra:
   ```
   arduino-cli core list
   ```
   Điểm nhìn đạt: danh sách có dòng `esp32:esp32`.
3. Biên dịch sketch hwtest đúng FQBN của repo:
   ```
   ./scripts/build_hwtest.sh
   ```
   Lệnh này chạy `arduino-cli compile --fqbn
   'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default' firmware/hwtest`.
   Điểm nhìn đạt: log biên dịch chạy hết, không báo lỗi, cuối có dòng
   tóm tắt dung lượng (kiểu `Sketch uses ... bytes ... of program storage`).
   - `CDCOnBoot=cdc`: bật USB CDC để `Serial` lên log.
   - `USBMode=default` là HWCDC nên **HID echo TẮT**; muốn echo thì đổi
     thành FQBN có `USBMode=otg` (chi tiết ở runbook nạp hwtest Ubuntu, mục 5).
4. Ai quen Arduino IDE thì vẫn dùng IDE được: cài IDE + core ESP32 trong
   Board Manager như runbook (mục 4), nhưng **build chuẩn của repo để đối
   chiếu vẫn là `./scripts/build_hwtest.sh`** — số nào báo cáo kiểm định
   thì lấy từ lệnh này.

## 5. Phân quyền serial + quy tắc udev (làm 1 lần, cần trước khi nạp)

Mục này tóm tắt để dựng máy mới không sót; hướng dẫn từng lệnh ở
[runbook nạp hwtest Ubuntu](runbook-nap-hwtest-ubuntu.md) (mục 2–3).

1. Thêm user vào nhóm `dialout`, rồi **đăng xuất/nhập lại**:
   ```
   sudo usermod -aG dialout "$USER"
   ```
   Kiểm tra sau khi đăng nhập lại: `id -nG` phải in ra `dialout`.
   Thiếu bước này thì nạp báo `Permission denied` / `Failed to open port`.
2. Quy tắc udev cho board tự build: chép file có sẵn của repo:
   ```
   sudo cp config/70-u2f.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```
   File này mở quyền `hidraw` cho VID Espressif `303a` (board tự build
   thành FIDO key) và các key thương mại, nhóm `plugdev`.
   Nếu cổng UART dùng chip CP210x và cần tên/quyền ổn định cho cả cổng
   nạp, thêm dòng cho VID `10c4` theo mẫu trong runbook (mục 3.2).
   Xong thì **rút cáp ra cắm lại** cho quy tắc ăn.
3. Gỡ xung đột hay gặp trên Ubuntu 22.04+:
   ```
   sudo apt remove -y brltty                        # chiếm ttyACM0
   sudo systemctl disable --now ModemManager        # thăm dò cổng (nếu máy có cài)
   ```
4. Tuyệt đối không `sudo chmod 666 /dev/ttyUSB0`, không chạy Arduino IDE
   hay `arduino-cli upload` bằng `sudo` để "cho nhanh" — vừa mất an toàn
   vừa đẻ file cấu hình thuộc root gây lỗi về sau.

## 6. Kiểm tra cuối (checklist chốt máy dev mới)

Chạy từ thư mục gốc repo, ghi lại output để đối chiếu khi báo lỗi:

- [ ] `python3 --version` → 3.10 trở lên.
- [ ] `ls .tooling/pylibs` → thấy các gói `hid`, `cryptography`, `oqs`,
      `qrcode`, `PIL` (tên thư mục có thể kèm phiên bản).
- [ ] `./scripts/run_tests.sh` → 7/7 self-test xanh, `echo $?` in `0`.
- [ ] `arduino-cli core list` → có `esp32:esp32`.
- [ ] `./scripts/build_hwtest.sh` → biên dịch xong, không lỗi.
- [ ] `id -nG` → có `dialout` (và `plugdev`).
- [ ] Cắm board cổng UART → `ls -l /dev/ttyUSB* /dev/ttyACM*` thấy cổng mới,
      thuộc nhóm `dialout`; cổng native → `lsusb | grep -i espressif`
      thấy VID `303a`.

Đạt cả 7 điểm thì máy sẵn sàng: nạp hwtest theo
[runbook nạp hwtest Ubuntu](runbook-nap-hwtest-ubuntu.md),
viết code tool Python rồi kiểm bằng `run_tests.sh`.

## 7. Lỗi thường gặp

| Triệu chứng | Nguyên nhân hay gặp | Cách xử lý |
|---|---|---|
| `pip install` báo `externally-managed-environment` | PEP 668 trên Ubuntu 23.04+ chặn pip ngoài venv | Thêm `--break-system-packages` (đích cài vẫn là `.tooling/pylibs` của repo, mục 2) |
| `ModuleNotFoundError: hid / oqs / cryptography / qrcode` | Chưa cài requirements, hoặc chạy `python3 tools/...` mà quên `PYTHONPATH` | Cài đủ 4 file requirements (mục 2); chạy qua `./scripts/run_tests.sh`, hoặc `export PYTHONPATH="$PWD/.tooling/pylibs"` trước (mục 3.2) |
| `import hid` hỏng dù đã pip | Thiếu backend hệ thống | `sudo apt install -y libhidapi-hidraw0` rồi chạy lại (mục 1) |
| `pqc --self-test` treo vài phút lần đầu | `import oqs` đang tự build liboqs | Bình thường — chờ xong; cần `cmake` + `gcc` + mạng (mục 3.3) |
| `pqc` báo thiếu liboqs / `OqsMissingError` | Chưa `pip install -r tools/requirements-pqc.txt`, hoặc tự build thất bại (thiếu cmake/gcc), hoặc `OQS_INSTALL_PATH` trỏ nhầm chỗ (bản `.dll` Windows kèm repo không dùng được) | Cài đủ mục 1–2; chạy lại cho tự build; nếu build tay thì `export OQS_INSTALL_PATH` tới thư mục chứa `.so` (mục 3.3) |
| `run_tests.sh` dừng ở 1 tool, `echo $?` khác 0 | Đúng thiết kế: 1 tool hỏng là cả script báo hỏng | Chạy lẻ tool đó theo mục 3.2 để lấy lỗi chi tiết, tra bảng này |
| `arduino-cli: command not found` | Chưa cài, hoặc `PATH` chưa ăn | Mục 4.1; mở Terminal mới rồi thử lại |
| `arduino-cli core install esp32:esp32` lỗi mạng / dở dang | Mất mạng giữa chừng (toolchain nặng vài trăm MB) | Chạy lại `core update-index` rồi `core install`; kiểm tra bằng `arduino-cli core list` |
| `build_hwtest.sh` báo `Chưa có arduino-cli` | Thiếu bước 4.1 | Cài arduino-cli (mục 4.1) — script không tự cài |
| `build_hwtest.sh` báo thiếu platform/core | Chưa cài core ESP32 | `arduino-cli core install esp32:esp32` (mục 4.2) |
| `Permission denied` / `Failed to open port` khi nạp | Chưa vào nhóm `dialout`, hoặc chưa đăng nhập lại | `sudo usermod -aG dialout "$USER"`, đăng xuất/nhập lại, kiểm tra `id -nG` (mục 5.1) |
| Cổng ACM vừa cắm đã bận | `brltty` chiếm `ttyACM0` | `sudo apt remove -y brltty`, cắm lại (mục 5.3) |
| Cổng chập chờn, tự reset khi mở | `ModemManager` thăm dò cổng | `sudo systemctl disable --now ModemManager` (mục 5.3) |
| Không thấy cổng mới khi cắm | Cáp chỉ sạc, sai cổng, udev chưa ăn | Đổi cáp dữ liệu; cắm cổng UART để nạp; `dmesg \| tail`, `lsusb` (runbook mục 1); nạp lại udev (mục 5.2) |
| `HID echo: TAT` sau khi build bằng script | `build_hwtest.sh` dùng `USBMode=default` (HWCDC) | Muốn echo thì build lại với FQBN `USBMode=otg` (mục 4.3, runbook mục 5) |
| Tool HID báo `Không thấy HID echo` / `Không mở được thiết bị` | Nạp bản HWCDC, cắm nhầm cổng UART, hoặc thiếu quyền `hidraw` | Nạp bản OTG + cắm cổng native + kiểm tra udev `config/70-u2f.rules` đã chép (mục 5.2) |
| Monitor trắng trơn sau nạp | Xem nhầm cổng, hoặc CDC chưa bật | Cắm sang cổng native; kiểm tra `USB CDC On Boot: Enabled` (runbook mục 4.2, 6.2) |
| Chữ rác trên Serial Monitor | Sai baud | Chỉnh lại 115200 |
| Kẹt `Connecting...` rồi `Failed to connect` | Board chưa vào download mode | Giữ BOOT → nhấn-nhả RESET → thả BOOT khi bắt đầu ghi (runbook Windows bước 9) |

## 8. Đọc tiếp

- Nạp và kiểm hwtest từng bước: [runbook nạp hwtest Ubuntu](runbook-nap-hwtest-ubuntu.md)
  (bản Windows: [runbook nạp hwtest Windows](runbook-nap-hwtest-windows.md)).
- Phần cứng (board, đấu nối, BOM): [03-phan-cung.md](03-phan-cung.md),
  [../hardware/wiring.md](../hardware/wiring.md), [../hardware/BOM.md](../hardware/BOM.md).
- Firmware chính: [04-firmware.md](04-firmware.md).
- Quy tắc udev FIDO: [../config/70-u2f.rules](../config/70-u2f.rules).
