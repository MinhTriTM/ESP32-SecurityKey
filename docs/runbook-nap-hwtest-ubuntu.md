# Runbook nạp hwtest trên Ubuntu

> Đối xứng với bản Windows của NCKH-015: từng bước từ cắm cáp đến thấy log.
> Phần riêng của Ubuntu là mục 2 (phân quyền serial) và mục 3 (quy tắc udev).
> Nguồn đối chiếu: `firmware/hwtest/README.md`, `firmware/hwtest/hwtest.ino`,
> `tools/hid_echo.py`, `scripts/build_hwtest.sh`, `docs/03-phan-cung.md`,
> `docs/04-firmware.md`, `docs/research/02-esp32s3-usb.md`.

## 0. Chuẩn bị

- Board ESP32-S3 DevKit, cáp USB-C **có dây dữ liệu** (cáp sạc thuần làm mất cả buổi
  debug vô ích — xem `docs/research/02-esp32s3-usb.md`).
- Phân biệt 2 cổng USB trên board (xem `docs/03-phan-cung.md`):
  - Cổng ghi **COM/UART** (qua chip cầu nối): dùng để **nạp** firmware.
  - Cổng ghi **USB/OTG** (nối thẳng GPIO19 D-, GPIO20 D+): cổng native, dùng cho
    **log CDC, nút/LED và HID echo**. Firmware FIDO bắt buộc dùng cổng này.
- Máy Ubuntu đã cài Arduino IDE + core ESP32 của Espressif (bản 22.04/24.04 đều được).
  Muốn nạp bằng dòng lệnh thì cài `arduino-cli` + core thay cho IDE (mục 5).

## 1. Cắm cáp lần đầu, xác định cổng

1. Cắm cáp vào **cổng UART/COM** của board, đầu kia vào máy Ubuntu.
2. Mở Terminal, xem kernel nhận thiết bị:
   ```
   dmesg | tail -n 20
   ```
   Điểm nhìn đạt: có dòng kiểu `cp210x converter now attached to ttyUSB0`
   (chip cầu nối CP210x) hoặc `cdc_acm ... ttyACM0` (USB Serial/JTAG của S3).
3. Liệt kê cổng chắc chắn thuộc về board:
   ```
   ls -l /dev/ttyUSB* /dev/ttyACM*
   ls -l /dev/serial/by-id/
   ```
   Điểm nhìn đạt: thấy 1 cổng mới xuất hiện sau khi cắm, biến mất khi rút.
   Ghi lại tên cổng (ví dụ `/dev/ttyUSB0`) — mọi lệnh nạp sau này dùng đúng tên này.
   Sai cổng là flash nhầm thiết bị, không đoán mù.
4. Kiểm tra USB ở mức bus:
   ```
   lsusb | grep -i -E 'espressif|cp210|silicon|303a'
   ```
   Điểm nhìn đạt: thấy 1 dòng thiết bị mới, VID thường là `303a` (Espressif, cổng
   native/JTAG) hoặc `10c4` (CP210x, cổng UART).

## 2. Phân quyền serial (riêng Ubuntu, làm 1 lần cho mỗi user)

Không có bước này thì Arduino IDE báo `Permission denied` hoặc `Failed to open
port` dù cổng vẫn hiện trong menu.

1. Xem user hiện tại thuộc nhóm nào:
   ```
   id -nG
   ```
2. Thêm user vào nhóm `dialout` (nhóm sở hữu cổng serial trên Ubuntu):
   ```
   sudo usermod -aG dialout "$USER"
   ```
3. **Đăng xuất rồi đăng nhập lại** (hoặc reboot) để nhóm mới có hiệu lực.
   Kiểm tra sau khi đăng nhập lại: `id -nG` phải in ra `dialout`.
4. Kiểm tra quyền trên cổng (thay bằng cổng đã ghi ở mục 1):
   ```
   ls -l /dev/ttyUSB0
   ```
   Điểm nhìn đạt: dòng kiểu `crw-rw---- 1 root dialout ... /dev/ttyUSB0` và user
   đã ở nhóm `dialout` thì mở cổng không cần `sudo`. Tuyệt đối không `sudo chmod 666`
   hay chạy Arduino IDE bằng `sudo` để "cho nhanh" — vừa mất an toàn vừa đẻ file
   cấu hình thuộc root gây lỗi về sau.

## 3. Quy tắc udev cho ESP32-S3 (riêng Ubuntu, làm 1 lần cho mỗi máy)

udev gán quyền + tên ổn định cho board mỗi lần cắm, và cho phép tool HID
(`tools/hid_echo.py`) mở thiết bị mà không cần root.

1. Tìm VID:PID của board khi cắm **cổng native** (cổng USB/OTG):
   ```
   lsusb | grep -i espressif
   ```
   Điểm nhìn đạt: dòng kiểu `Bus 001 Device 012: ID 303a:1001 Espressif ...`.
   Ghi lại cặp số sau `ID` (ví dụ `303a:1001`; board khác có thể là `303a:0002`
   hoặc PID khác — dùng đúng số máy mình in ra).
2. Tạo file quy tắc (thay VID/PID bằng số vừa ghi):
   ```
   sudo tee /etc/udev/rules.d/99-esp32s3.rules > /dev/null <<'EOF'
   # ESP32-S3 Security Key: serial + HID echo cho hwtest
   SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", MODE="0660", GROUP="dialout"
   SUBSYSTEM=="hidraw", ATTRS{idVendor}=="303a", MODE="0660", GROUP="plugdev"
   SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", MODE="0660", GROUP="plugdev"
   EOF
   ```
   Nếu cổng UART dùng chip CP210x (`10c4:ea60`) thì thêm 1 dòng tương tự cho VID đó:
   ```
   SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0660", GROUP="dialout"
   ```
3. Nạp lại quy tắc và cắm lại board:
   ```
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```
   Rút cáp ra, cắm lại, rồi kiểm tra quyền đã ăn:
   ```
   ls -l /dev/ttyUSB* /dev/ttyACM* /dev/hidraw*
   ```
   Điểm nhìn đạt: cổng serial thuộc nhóm `dialout`, `hidraw` thuộc nhóm `plugdev`
   (user Ubuntu mặc định đã ở nhóm `plugdev`; kiểm tra bằng `id -nG`).
4. Gỡ xung đột với `brltty` (trình đọc màn hình chữ nổi chiếm `ttyACM0` trên
   Ubuntu 22.04+): nếu cổng ACM vừa cắm đã bị chiếm, Arduino báo cổng bận.
   Kiểm tra: `sudo dmesg | grep -i brltty`. Nếu có, gỡ:
   ```
   sudo apt remove -y brltty
   ```
   Tương tự, tắt `ModemManager` chiếm cổng nếu máy có cài:
   ```
   sudo systemctl disable --now ModemManager
   ```

## 4. Cài đặt board trong Arduino IDE

1. Mở Arduino IDE, vào **Tools > Board**, chọn **ESP32S3 Dev Module** đúng board đang cầm.
2. **Tools > USB CDC On Boot**: chọn **Enabled** (không bật thì `Serial` không lên log).
3. **Tools > USB Mode**: chọn **USB-OTG (TinyUSB)** để bật HID echo
   (bản HWCDC `USBMode=hwcdc` vẫn nạp và xem log được, nhưng sketch sẽ in
   `HID echo: TAT (can USB Mode = USB-OTG)` và tool echo không thấy thiết bị).
   BẮT BUỘC với module N16R8: **Tools > Flash Mode → DIO 80MHz** và
   **Tools > PSRAM → OPI PSRAM** (flash QIO/OPI là boot-loop watchdog).
4. **Tools > Port**: chọn cổng đã ghi ở mục 1 (dạng `/dev/ttyUSB0` hoặc `/dev/ttyACM0`).
   Nếu menu Port mờ: quay lại mục 2–3 (thiếu nhóm `dialout` hoặc udev chưa ăn).
5. Mở file `firmware/hwtest/hwtest.ino`, nhấn **Upload** khi board đang cắm **cổng UART**.
   Điểm nhìn đạt: log nạp chạy hết 100%, không báo `Permission denied`.

## 5. Nạp bằng dòng lệnh (thay cho mục 4 nếu không dùng IDE)

1. Cài `arduino-cli` theo hướng dẫn chính thức, rồi cài core ESP32:
   ```
   arduino-cli core install esp32:esp32
   ```
2. Biên dịch đúng FQBN của repo (lệnh trong `scripts/build_hwtest.sh`):
   ```
   ./scripts/build_hwtest.sh
   ```
   Lệnh này chạy `arduino-cli compile --fqbn
   'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default,FlashMode=dio,PSRAM=opi' firmware/hwtest`.
   Lưu ý: `USBMode=default` chính là USB-OTG (có echo); HWCDC là `USBMode=hwcdc`.
   `FlashMode=dio,PSRAM=opi` là bắt buộc với module N16R8 (flash QIO/OPI là boot-loop).
3. Nạp qua cổng UART (thay bằng cổng đã ghi ở mục 1):
   ```
   arduino-cli upload -p /dev/ttyUSB0 --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default,FlashMode=dio,PSRAM=opi' firmware/hwtest
   ```
4. Người dùng PlatformIO: tạo project board `esp32-s3-devkitc-1`, chép
   `hwtest.ino` thành `src/main.cpp`, thêm cờ build `-DARDUINO_USB_CDC_ON_BOOT=1`;
   muốn HID echo phải bật TinyUSB OTG trong sdkconfig (tương đương
   `ARDUINO_USB_MODE=0` — thiếu cờ này thì nhánh HID bị biên dịch loại, xem ghi nhận
   của NCKH-003 trong sổ cái). Nạp qua cổng UART như bình thường.

## 6. Xem log, thử nút BOOT và LED

1. Sau khi nạp xong, **rút cáp khỏi cổng UART, cắm sang cổng USB/OTG native**
   (log CDC và HID echo đều đi đường native).
2. Mở Serial Monitor 115200 baud (trong Arduino IDE: **Tools > Port** chọn lại cổng
   native mới hiện, rồi **Tools > Serial Monitor**, đặt 115200).
   Không dùng IDE thì dùng `tio`/`screen`: `tio /dev/ttyACM0 -b 115200`.
3. Điểm nhìn đạt — log in đúng chip (theo `printChipInfo()` trong `hwtest.ino`):
   ```
   === ESP32-S3 Security Key: hwtest ===
   Chip: ESP32-S3 rev ...
   MAC: ...
   CPU: ... MHz, cores: 2
   Flash: ... bytes
   PSRAM: ... bytes
   SDK: ...
   USB mode: 0 (0 la OTG co HID echo, 1 la HWCDC)
   Nhan nut BOOT de test. LED RGB se doi mau.
   ======================================
   HID echo: san sang (vendor page 0xFF00, 64 byte, khong report ID).
   ```
   (Bản HWCDC thì dòng cuối là `HID echo: TAT (can USB Mode = USB-OTG)` — bình thường
   nếu cố ý nạp bản đó, nhưng không kiểm HID được.)
4. Nhấn rồi nhả nút **BOOT**: log hiện `BOOT: nhan` khi nhấn, `BOOT: nha` khi nhả.
   LED **xanh lá** khi chờ, chuyển **xanh dương** khi nhấn nút.
5. Cứ 5 giây có 1 dòng `Heartbeat: uptime ... s, heap ...` — board sống ổn định.

## 7. Kiểm tra HID echo

Chỉ làm sau khi mục 6 đạt và board đang ở bản USB-OTG + cắm cổng native.

1. Cài thư viện HID cho Python (theo `tools/requirements.txt`, cần Python ≥ 3.10):
   ```
   pip install -r tools/requirements.txt
   ```
   Trên Ubuntu nếu `pip` báo thiếu backend, cài thêm gói hệ thống:
   `sudo apt install -y libhidapi-hidraw0` rồi cài lại `hidapi`.
2. Chạy tool echo từ thư mục repo:
   ```
   python3 tools/hid_echo.py
   ```
   Tool gửi 60 byte ngẫu nhiên, đối chiếu từng byte trả về.
3. Điểm nhìn đạt:
   - Terminal in: `HID echo ok: 60 byte đi về khớp từng byte. Đường USB HID sống.`
   - Log serial đồng thời hiện: `HID echo: da gui lai 64 byte.`
4. Kiểm nhanh không cần board: `python3 tools/hid_echo.py --self-test` phải in
   `self-test ok: đóng gói report HID echo đúng.`
5. Lưu ý đã biết (phát hiện của NCKH-003): echo có race `echoPending` khi host gửi
   OUT dồn dập — frame giữa có thể mất lặng. Với test đơn 60 byte này thì không sao;
   không dùng echo hiện tại làm kênh truyền tin cậy.

## 8. Kết quả đạt (checklist chốt)

- [ ] Log in đúng chip ESP32-S3, dung lượng flash và PSRAM.
- [ ] Nhấn BOOT thì log hiện nhấn/nhả, LED xanh lá chờ / xanh dương khi nhấn.
- [ ] Tool `hid_echo.py` báo 60 byte khớp (bản OTG).
- [ ] Heartbeat 5 s đều, không treo, không reset lạ.
- Thiếu bất kỳ điểm nào thì dừng lại kiểm tra board và cáp trước khi flash
  firmware FIDO chính (xem `docs/04-firmware.md`).

## 9. Xử lý sự cố

| Triệu chứng | Nguyên nhân hay gặp | Cách xử lý |
|---|---|---|
| `Permission denied` / `Failed to open port` | Chưa vào nhóm `dialout`, hoặc chưa đăng nhập lại | Mục 2: `usermod -aG dialout`, đăng xuất/nhập lại, kiểm tra `id -nG` |
| Cổng ACM vừa cắm đã bận | `brltty` chiếm `ttyACM0` | `sudo apt remove -y brltty`, cắm lại (mục 3.4) |
| Cổng chập chờn, tự reset khi mở | `ModemManager` thăm dò cổng | `sudo systemctl disable --now ModemManager` |
| Không thấy cổng mới khi cắm | Cáp sạc, sai cổng, udev chưa ăn | Đổi cáp dữ liệu, cắm cổng UART để nạp, `dmesg` + `lsusb` (mục 1), nạp lại udev (mục 3.3) |
| Menu Port trong IDE mờ | Quyền serial / udev | Quay lại mục 2–3, không chạy IDE bằng `sudo` |
| Không có log serial sau nạp | Xem nhầm cổng, hoặc CDC chưa bật | Cắm sang cổng native, kiểm tra `USB CDC On Boot: Enabled` (mục 4.2, 6.2) |
| `HID echo: TAT` | Nạp bản HWCDC / sai USB Mode | Nạp lại bản USB-OTG (mục 4.3); PIO thêm `ARDUINO_USB_MODE=0` (mục 5.4) |
| Boot-loop `TG0WDT`/`RTCWDT`, USB chập chờn | Flash Mode QIO/OPI trên flash Boya | Build/nạp lại với Flash Mode DIO 80MHz + PSRAM OPI (mục 4.3, 5.2) |
| `Không thấy HID echo (usage page 0xFF00)` | Chưa nạp OTG, cắm nhầm cổng UART, hoặc thiếu quyền hidraw | Nạp OTG + cắm cổng native + kiểm tra udev `hidraw` nhóm `plugdev` (mục 3, 7) |
| `Không mở được thiết bị` (HID) | Quyền `hidraw` | Kiểm tra `ls -l /dev/hidraw*`, udev mục 3.2–3.3 |
| `Thiết bị không trả lời` | Race echo / OUT dồn dập | Chạy lại test đơn; nếu vẫn lỗi, xem phân tích race của NCKH-003 |
| Thiếu thư viện `hid` | Chưa `pip install` | `pip install -r tools/requirements.txt` (+ `libhidapi-hidraw0` nếu cần) |
