# FAQ dự án ESP32-S3 Security Key

> Gom các câu hỏi đã gặp thật trong quá trình làm dự án: từ tài liệu `docs/`,
> sổ cái các agent `vien-nghien-cuu/so-cai/NCKH-*.md` và `NHIP-TIM.log`.
> Mỗi câu trả lời đều ghi nguồn để đối chiếu.
> Tác giả: Phạm Bình (NCKH-029, nhóm tailieu, đợt 2B).

## Mục lục

1. [Dự án chung](#1-dự-án-chung)
2. [Phần cứng](#2-phần-cứng)
3. [Nạp hwtest và firmware](#3-nạp-hwtest-và-firmware)
4. [Dùng key trên Windows, Linux, Android](#4-dùng-key-trên-windows-linux-android)
5. [Bảo mật và vận hành key thật](#5-bảo-mật-và-vận-hành-key-thật)
6. [Sao lưu và khôi phục](#6-sao-lưu-và-khôi-phục)
7. [Tool Python và kiểm thử](#7-tool-python-và-kiểm-thử)
8. [Hậu lượng tử (PQC)](#8-hậu-lượng-tử-pqc)
9. [Thám mã bằng ML và Gohr 2019](#9-thám-mã-bằng-ml-và-gohr-2019)
10. [Quy trình làm việc của Viện](#10-quy-trình-làm-việc-của-viện)

---

## 1. Dự án chung

### Dự án này làm gì?

Làm một khóa bảo mật USB-C dùng thật, dựng trên board ESP32-S3 DevKit.
Cắm cáp C-to-C là chạy trên Android, Linux (kể cả Ubuntu) và Windows 11,
không cần cài driver. Nguồn: [README](../README.md),
[01-phan-tich-y-tuong](01-phan-tich-y-tuong.md).

### Vì sao chọn ESP32-S3 mà không phải ESP32 đời cũ?

ESP32-S3 có USB OTG native full-speed 12 Mbps (GPIO19 D-, GPIO20 D+),
chạy được stack TinyUSB nên giả lập thiết bị USB HID chuẩn.
ESP32 đời cũ không có USB native nên không làm được USB gadget.
Nguồn: [01-phan-tich-y-tuong](01-phan-tich-y-tuong.md),
[research/02-esp32s3-usb](research/02-esp32s3-usb.md).

### Vì sao cắm C-to-C là chạy, không cần driver?

Key hiện hình là USB HID chuẩn với usage page FIDO (0xF1D0).
Windows 11, Linux và Android đều có driver HID generic, còn Chrome và Edge
đều có WebAuthn. Không có tầng driver hay app độc quyền nào ở giữa.
Nguồn: [02-kien-truc](02-kien-truc.md) (mục "Vì sao cắm C-to-C là chạy").

### FIDO2, U2F, CTAP1, CTAP2, WebAuthn khác nhau thế nào?

U2F là thế hệ đầu (xác thực bước hai), CTAP1 là tên chuẩn hóa của U2F.
CTAP2 là thế hệ hai (đăng nhập không mật khẩu, quản lý credential).
WebAuthn là API phía trình duyệt gọi xuống key qua CTAP.
FIDO2 gồm CTAP2 + WebAuthn. Key dự án nói cả CTAP1 và CTAP2 nên dịch vụ
cũ và mới đều dùng được. Nguồn:
[research/01-giao-thuc-fido](research/01-giao-thuc-fido.md).

### Passkey và resident key là gì?

Resident key lưu credential trên key để đăng nhập không cần gõ tên tài khoản.
Passkey là cách gọi thân thiện của credential FIDO2 (gắn thiết bị hoặc đồng bộ).
Pico-fido hỗ trợ resident key nên dùng được luồng passkey cơ bản. Nguồn:
[research/01-giao-thuc-fido](research/01-giao-thuc-fido.md).

### Vì sao không tự viết CTAP2 và crypto từ đầu?

Giao thức chữ ký và quản lý credential sai một byte là mất an toàn, mà code
tự viết không ai audit. Mục tiêu là dùng thật nên repo dùng firmware pico-fido
đã kiểm chứng, ghim đúng phiên bản, kiểm tra SHA khi tải. Code tự viết chỉ làm
kiểm tra phần cứng và kiểm tra giao tiếp, không chạm vào private key. Nguồn:
[README](../README.md), [01-phan-tich-y-tuong](01-phan-tich-y-tuong.md),
[02-kien-truc](02-kien-truc.md) (mục "Ranh giới an toàn").

### Firmware chính là bản nào, vì sao ghim commit?

Pico-fido tag `v8.2` (2026-10-18, tag ký PGP), commit ghim
`15b848d821b4995eb1b29a5c2a4c24c25d1a768e`, build bằng ESP-IDF `v5.5.1`.
Ghim commit vì tag có thể bị dời; khi build phải đối chiếu SHA sau checkout.
Trạng thái: đã khảo sát từ nguồn chính thức, chưa build kiểm chứng trên máy này.
Nguồn: [04-firmware](04-firmware.md).

### Giấy phép pico-fido AGPL-3.0 có ảnh hưởng gì?

Tự build dùng cá nhân thì thoải mái. Nhưng phân phối binary đã sửa thì phải
công bố source theo giấy phép. Code trong repo này vẫn là MIT, hai phần độc lập.
Nguồn: [04-firmware](04-firmware.md).

### Key tự chế này an toàn cỡ nào, có bằng YubiKey không?

Chưa tương đương. ESP32-S3 không có secure element đạt chứng nhận như key
thương mại; kẻ có đủ thiết bị và thời gian cầm key vật lý vẫn có cửa tấn công
kênh kề. Mức này đủ cho người dùng cá nhân nghiêm túc; bí mật cấp tổ chức thì
nên mua key đạt chứng nhận FIDO. Nguồn:
[01-phan-tich-y-tuong](01-phan-tich-y-tuong.md), [06-bao-mat](06-bao-mat.md).

### Luồng một lần đăng nhập chạy qua những tầng nào?

Trình duyệt gọi WebAuthn → hệ điều hành gói thành message CTAPHID gửi qua
USB HID → firmware pico-fido xử lý, LED báo chờ, đợi chạm nút BOOT (User
Presence) → chip ký bằng private key trong flash (key không rời chip) →
trả response về. Sơ đồ chi tiết từng bước do NCKH-011 vẽ. Nguồn:
[02-kien-truc](02-kien-truc.md).

---

## 2. Phần cứng

### Board mục tiêu là gì? N26R8 hay N16R8?

ESP32-S3 DevKit đời 2022, module đúng là **N16R8** (flash 16 MB, PSRAM octal
8 MB). "N26R8" trong ý tưởng gốc là ghi nhầm: không có trong lineup Espressif
(flash 26 MB không phải cỡ JEDEC). Bằng chứng: ảnh `docs/assets/62256.jpg`
ghi dải N8R2/N8R8/N16R8, PDF DEVKITC-1-N16R8V tr.53 ghi 16 MB flash + 8 MB PSRAM.
Build pico-fido cần đúng dung lượng flash nên trước khi flash phải đọc chữ in
trên nắp shield kim loại và đối chiếu BOM. Nguồn:
[03-phan-cung](03-phan-cung.md), `hardware/BOM.md`, sổ NCKH-027, kiểm chéo NCKH-019.

### Board có hai cổng USB-C, dùng cổng nào?

Hai cổng khác vai trò hoàn toàn:

| Cổng | Chữ in trên lụa | Dùng để |
|---|---|---|
| Cổng UART (qua chip cầu nối) | `COM`, `UART` | Nạp firmware |
| Cổng USB native (thẳng GPIO19/GPIO20) | `USB`, `OTG` | Chạy FIDO, log CDC, HID echo |

Firmware FIDO bắt buộc dùng cổng native. Cắm nhầm cổng là nguồn gốc của một
loạt lỗi "không thấy thiết bị" bên dưới. Nguồn: [03-phan-cung](03-phan-cung.md),
runbook Windows mục 0.2, runbook Ubuntu mục 0.

### Nút BOOT và LED để làm gì?

Nút BOOT trên DevKit là nút xác nhận hiện diện người dùng (nhấn khi đèn báo chờ).
LED RGB địa chỉ (thường WS2812, GPIO38 hoặc GPIO48 tùy bản board) báo trạng thái:
xanh lá chờ, xanh dương khi nhấn nút. Không cần thêm linh kiện. Nguồn:
[03-phan-cung](03-phan-cung.md), [02-kien-truc](02-kien-truc.md).

### Cáp nào dùng được?

Cáp USB-C **có đủ dây dữ liệu**. Cáp chỉ sạc làm mất cả buổi debug vô ích:
board vẫn lên nguồn nhưng máy tính không thấy cổng nào mới. Nguồn:
[03-phan-cung](03-phan-cung.md), runbook Ubuntu mục 0,
[research/02-esp32s3-usb](research/02-esp32s3-usb.md).

### MAC in ra ở log hwtest là gì? Có phải bí mật không?

MAC là địa chỉ gốc của từng con chip, ghi trong eFuse, duy nhất từng board.
Hwtest in dòng `MAC: ...` để ghi vào sổ theo dõi key (`hardware/keys.md`).
MAC là **định danh, không phải bí mật**: ai cầm board cũng đọc được.
Giá trị của nó là quản lý (biết key nào đang cầm, phát hiện board bị tráo).
Không bao giờ dùng MAC làm PIN hay vật liệu khóa. Nguồn: [06-bao-mat](06-bao-mat.md).

### Board trần có dùng thật được không?

Không. Bản DevKit trần chỉ hợp thử nghiệm. Bản dùng thật nên in vỏ 3D che mạch,
chừa lỗ nút BOOT và LED, cố định cáp để chân USB-C không chịu lực uốn.
Không để mạch trần trong túi cùng chìa khóa kim loại. Nguồn:
[03-phan-cung](03-phan-cung.md).

---

## 3. Nạp hwtest và firmware

### Hwtest là gì? Vì sao phải nạp hwtest trước?

Hwtest là sketch Arduino tối giản (`firmware/hwtest/hwtest.ino`) để xác nhận
board sống: USB CDC lên log, nút BOOT, LED và HID echo. Nạp tầng này trước để
chắc phần cứng và cổng USB native đều tốt, rồi mới flash firmware FIDO chính.
Nguồn: [04-firmware](04-firmware.md), runbook Windows/Ubuntu.

### "USB CDC On Boot = Enabled" để làm gì? Quên bật thì sao?

Để đối tượng `Serial` trong sketch nối ra cổng USB. Quên bật (để Disabled)
thì nạp thành công nhưng Serial Monitor trắng trơn. Nguồn: runbook Windows
bước 6, runbook Ubuntu mục 4.

### "USB Mode = USB-OTG (TinyUSB)" để làm gì? Chữ "HID echo: TAT" nghĩa là gì?

Chế độ này bật HID echo (log in `USB mode: 0`). Nếu để HWCDC thì sketch vẫn
chạy nhưng log in `HID echo: TAT (can USB Mode = USB-OTG)` và tool
`hid_echo.py` không thấy thiết bị. Thấy `USB mode: 1` hay `HID echo: TAT`
thì nạp lại bản OTG. Nguồn: runbook Windows bước 7, runbook Ubuntu mục 4.

### Nạp kẹt ở "Connecting..." rồi "Failed to connect"?

Giữ nút BOOT → nhấn-nhả nút RESET (vẫn giữ BOOT) → thả BOOT khi IDE bắt đầu
ghi (`Writing at...`). Board vào chế độ download; lần nạp sau thường tự vào được.
Nguồn: runbook Windows bước 9.

### Serial Monitor trắng trơn hoặc chữ rác?

Trắng trơn: kiểm tra USB CDC On Boot đã Enabled, đúng cổng COM, đúng 115200 baud,
nhấn RESET xem lại. Chữ rác (ký tự lạ): sai baud, chỉnh lại 115200. Nguồn:
runbook Windows bước 10.

### Tool báo "Không thấy HID echo (usage page 0xFF00)"?

Ba nguyên nhân hay gặp: đang cắm nhầm cổng UART (phải cắm cổng native),
bản đã nạp là HWCDC (nạp lại bản OTG), hoặc thiếu quyền hidraw trên Linux
(xem mục udev). Nguồn: runbook Windows mục 12, runbook Ubuntu mục 7 và 9.

### Tool báo "Thiết bị không trả lời"?

Rút ra cắm lại cổng native, chạy lại tool. Nếu vẫn lỗi, có thể chạm race
`echoPending` trong firmware (xem câu tiếp). Nguồn: runbook Ubuntu mục 9,
sổ NCKH-003.

### Race `echoPending` trong hwtest là gì?

Phát hiện chính của NCKH-003: `_onOutput()` (ngữ cảnh USB) và `loop()` cùng
đọc/ghi cờ `echoPending` và bộ đệm `echoBuf` mà không có khóa. Host gửi OUT
dồn dập có thể làm mất echo (tool timeout, báo "câm" giả) hoặc frame rách +
gửi trùng. Với test đơn 60 byte hiện tại thì không sao, nhưng không được coi
echo này là kênh truyền tin cậy. Sửa đề xuất: vùng cấm ngắt/`portMUX` hoặc
hàng đợi 2 ngăn (chưa vá, chờ thẻ follow-up nhóm firmware). Nguồn: sổ NCKH-003
(mục P1), runbook Ubuntu mục 7, sổ NCKH-016 (phát hiện 9).

### Dùng PlatformIO thì cần cờ gì?

Tạo project board `esp32-s3-devkitc-1`, chép `hwtest.ino` thành `src/main.cpp`,
thêm cờ build `-DARDUINO_USB_CDC_ON_BOOT=1`. Muốn HID echo thì bật TinyUSB OTG
trong sdkconfig (tương đương `ARDUINO_USB_MODE=0`); thiếu cờ này thì nhánh HID
bị biên dịch loại và log chỉ in `HID echo: TAT`. Nguồn: runbook Windows mục 14,
runbook Ubuntu mục 5, sổ NCKH-003 (mục P3).

### Sai board trong Arduino IDE thì sao?

Đây là lỗi hay gặp nhất: nạp cho board khác có thể "thành công giả" rồi log rác
hoặc không chạy. Phải chọn `ESP32S3 Dev Module` và đối chiếu chữ in trên shield
với BOM nếu chưa chắc. Nguồn: runbook Windows bước 5.

### Sai cổng COM/TTY khi nạp thì sao?

Flash nhầm thiết bị khác. Luôn kiểm tra kỹ: cổng phải xuất hiện khi cắm board
và biến mất khi rút. Nguồn: runbook Windows bước 8, runbook Ubuntu mục 1,
[04-firmware](04-firmware.md).

---

## 4. Dùng key trên Windows, Linux, Android

### Windows có cần cài driver cho key FIDO không?

Không. Cắm key là Windows nhận HID. Vào Settings → Bluetooth & devices để xác
nhận thiết bị mới, rồi đăng ký bằng Edge hoặc Chrome. Nguồn:
[05-huong-dan-su-dung](05-huong-dan-su-dung.md).

### Device Manager có dấu chấm than vàng ở cổng COM?

Thiếu driver chip cầu nối (CP210x hoặc CH340 tùy board). Tải driver từ trang chủ
hãng chip, cài xong rút ra cắm lại. Nguồn: runbook Windows bước 2.

### Linux báo "Permission denied" khi mở cổng serial?

Người dùng chưa vào nhóm `dialout`. Chạy `sudo usermod -aG dialout "$USER"`
rồi **đăng xuất đăng nhập lại** (nhóm mới mới có hiệu lực). Tuyệt đối không
`sudo chmod 666` hay chạy Arduino IDE bằng `sudo` để "cho nhanh". Nguồn:
runbook Ubuntu mục 2.

### File udev rules để làm gì?

`config/70-u2f.rules` cho phép trình duyệt mở thiết bị HID mà không cần root.
Không có rules thì Chrome thường báo không tìm thấy authenticator. Nguồn:
[05-huong-dan-su-dung](05-huong-dan-su-dung.md), runbook Ubuntu mục 3.

### Cổng ACM vừa cắm đã bận trên Ubuntu?

Do `brltty` (trình đọc màn hình chữ nổi) chiếm `ttyACM0` trên Ubuntu 22.04+.
Kiểm tra `sudo dmesg | grep -i brltty`, nếu có thì `sudo apt remove -y brltty`.
Tương tự, tắt `ModemManager` nếu nó thăm dò làm cổng chập chờn:
`sudo systemctl disable --now ModemManager`. Nguồn: runbook Ubuntu mục 3 và 9.

### Chrome trên Linux kiểm tra key thế nào sau khi cắm?

`lsusb` phải thấy Espressif (VID `303a`, hoặc `10c4` nếu qua chip CP210x),
`dmesg` phải có dòng HID mới, rồi chạy `tools/fido_check.py` để xác nhận key
trả lời INIT và PING. Nguồn: [05-huong-dan-su-dung](05-huong-dan-su-dung.md),
runbook Ubuntu mục 1.

### Firefox dùng được không?

Tùy bản, cần bật WebAuthn và quyền USB trong `about:config`. Chrome và Edge là
đường ít lỗi nhất. Nguồn: [05-huong-dan-su-dung](05-huong-dan-su-dung.md).

### Android cần gì để dùng key?

Chrome trên Android 9 trở lên, cáp OTG C-to-C đúng chuẩn. Một số máy tắt OTG
mặc định thì bật trong cài đặt rồi cắm lại. Máy chỉ có Micro-USB thì cần đầu
chuyển OTG đúng chuẩn. Nguồn: [05-huong-dan-su-dung](05-huong-dan-su-dung.md),
[03-phan-cung](03-phan-cung.md).

---

## 5. Bảo mật và vận hành key thật

### Vì sao phải đăng ký ít nhất hai key cho mỗi tài khoản quan trọng?

Mỗi key vật lý là một bản sao duy nhất: credential FIDO không xuất ra được
theo thiết kế. Mất key duy nhất mà không có key dự phòng thì chỉ còn đường mã
khôi phục. Đặt tên từng key để biết key nào đang cầm. Nguồn:
[05-huong-dan-su-dung](05-huong-dan-su-dung.md), [06-bao-mat](06-bao-mat.md),
[07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Quên PIN FIDO thì sao?

Quên PIN nhiều lần là phải reset trắng key (xóa toàn bộ credential trên key đó).
Chỉ reset khi còn đăng nhập được bằng key dự phòng hoặc mã khôi phục. Nguồn:
[06-bao-mat](06-bao-mat.md).

### Mất một key thì xử lý thế nào?

Vào từng dịch vụ, dùng key dự phòng (hoặc mã khôi phục) đăng nhập rồi gỡ đúng
tên key đã mất ngay. Quy trình đầy đủ nằm ở tài liệu sao lưu. Nguồn:
[06-bao-mat](06-bao-mat.md), [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Vì sao không cập nhật cả hai key cùng lúc?

Để luôn còn một key đang chạy ổn. Chỉ flash bản build từ commit đã ghim và đã
kiểm tra SHA; giữ bản cũ tới khi bản mới vượt qua đăng nhập thử; thử trên tài
khoản phụ trước. Nguồn: [04-firmware](04-firmware.md), [06-bao-mat](06-bao-mat.md).

### Flash Encryption và Secure Boot để làm gì?

Khóa việc đọc trộm firmware từ flash và chặn firmware không ký. Khi bật ở chế
độ release, cổng nạp tự chuyển sang Secure Download Mode (kẻ xấu không chạy
được code lạ) và JTAG tự tắt. Điều kiện bắt buộc: part0 phải có cờ `encrypted`
(thiếu là kho FIDO hỏng, CTAP trả `0x21` — bài học key-01), và phải tự sinh +
giữ khóa FE offline (mất khóa là mất đường nạp lại). Pico-fido còn hỗ trợ
Secure Lock và lưu khóa mã hóa chính trong vùng OTP. Nguồn:
[04-firmware](04-firmware.md), [06-bao-mat](06-bao-mat.md).

### Bật bảo mật phần cứng có nguy cơ khóa luôn board không?

Có. Các thao tác eFuse là một chiều: sai cấu hình có thể khóa luôn board.
Riêng khóa hẳn ROM Download Mode là "cầu dao một chiều": khóa rồi thì không
flash lại qua UART nữa, chỉ làm khi chắc chắn không cần cập nhật qua cổng này.
Đọc kỹ tài liệu ESP-IDF trước. Nguồn: [04-firmware](04-firmware.md),
[06-bao-mat](06-bao-mat.md).

### Vì sao tài liệu dặn bịt cổng UART về mặt vật lý?

Board có hai cổng: UART để nạp, OTG để dùng FIDO hàng ngày. Vỏ key chỉ chừa
cổng OTG và lỗ nút BOOT, che kín cổng UART lại thì người mượn key không thể
cắm vào cổng nạp để flash lén trong vài phút. Không bao giờ cắm cổng UART vào
máy lạ. Nguồn: [06-bao-mat](06-bao-mat.md).

### Key có chống được máy tính nhiễm mã độc không?

Không. Key chống lừa đảo và rò mật khẩu (private key không rời chip, credential
gắn đúng domain), nhưng không chống được máy đã bị chiếm toàn quyền hoặc người
khác cầm key vật lý cùng mã PIN. Nguồn: [06-bao-mat](06-bao-mat.md).

### Bao lâu kiểm tra key một lần?

Mỗi vài tháng cắm từng key và đăng nhập thử một dịch vụ. Key để lâu có thể quên
PIN, quên cách dùng hoặc lỗi flash mới phát hiện. Phát hiện sớm thì còn key dự
phòng để xoay. Nguồn: [06-bao-mat](06-bao-mat.md).

---

## 6. Sao lưu và khôi phục

### Vì sao không làm kiểu "ESP chỉ chạy khi cắm đúng USB có serial X"?

Ba lý do, theo [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md):

1. Cổng C thứ hai chỉ là UART qua chip cầu nối, ESP không thấy USB để đọc serial.
2. ESP32-S3 chỉ có một controller USB OTG: đang làm thiết bị cắm vào PC thì không
   thể đồng thời làm chủ để đọc thêm ổ USB khác.
3. Serial/MAC đọc được trong một phút và giả mạo được; khóa theo serial mà không
   mã hóa thì kẻ trộm flash lại firmware là qua.

### Credential FIDO có chép sang ESP mới được không?

Không. Credential không xuất ra được theo thiết kế. "Khôi phục" đúng nghĩa của
FIDO là: key dự phòng đã đăng ký sẵn + mã khôi phục của dịch vụ. Nguồn:
[07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Bí mật gốc S là gì? Ba đường khôi phục là gì?

S là 32 byte ngẫu nhiên (256 bit), gốc duy nhất của toàn hệ thống sao lưu.
Ba hình thức tương đương, đường nào cũng ra cùng S:

1. Key FIDO dự phòng đã đăng ký sẵn (nhanh nhất, không cần S).
2. Share Shamir trên các thiết bị (cần đủ ngưỡng đa số, gợi ý 3/5, rồi `combine`).
3. Cụm 24 từ trên giấy/thép (đường cuối, `to-entropy` ra S, checksum bắt lỗi gõ).

Hex của S chính là mật khẩu mở két mã hóa `ket.bin` chứa mã khôi phục các dịch vụ.
Sơ đồ do NCKH-017 vẽ, NCKH-025 kiểm chéo đạt. Nguồn:
[07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md), sổ NCKH-017, NCKH-025.

### Ngưỡng Shamir "K lớn hơn nửa N" nghĩa là gì? Vì sao 5 share cần 3?

Kẻ xấu gom dưới một nửa thì biết đúng 0 bit về S (tính chất toán học của Shamir),
còn bạn mất dưới một nửa thiết bị thì vẫn đủ share để mở. Cấu hình gợi ý: 5 share
(PC bàn, laptop, điện thoại, USB ở nhà, USB gửi nhà người thân), cần 3.
Mất bất kỳ 2 nơi nào vẫn mở được; kẻ trộm lấy 2 nơi vẫn không mở được. Nguồn:
[07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Vì sao cụm từ là 24 từ mà không phải 32?

Chuẩn BIP-39 tối đa 24 từ cho 256 bit, và 256 bit đã không thể brute-force
(2^256 phép thử). Thêm từ không vừa công thức checksum của chuẩn, cũng không an
toàn hơn mà chỉ dễ ghi nhầm hơn. Giữ đúng chuẩn còn đọc được bằng mọi ví lạnh
và tool BIP-39 khác. Nguồn: [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Share và giấy 24 từ phải giữ thế nào?

Không để K share trở lên trên cùng một máy, một tài khoản cloud hay một chùm
sao lưu tự động. Điện thoại giữ share phải có khóa màn hình và mã hóa máy.
Giấy 24 từ không chụp ảnh, không lưu app ghi chú có đồng bộ cloud.
Nghi lộ thì đổi bí mật gốc và làm lại toàn bộ. Mỗi sáu tháng diễn tập ghép thử
một lần. Nguồn: [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Mất điện thoại giữ share thì sao?

Coi như mất một share, còn 4 share vẫn đủ ngưỡng 3/5. Nhưng nếu nghi điện thoại
lọt vào tay kẻ xấu kết hợp với các nơi khác thì đổi bí mật gốc và làm lại toàn bộ.
Nguồn: [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### "Diễn tập" là gì, làm khi nào?

Gom 3 share bất kỳ về một máy, chạy `combine`, đối chiếu hex với `to-entropy`,
mở két thử rồi xóa dấu vết. Làm ngay sau khi dựng xong, và mỗi sáu tháng một lần.
Diễn tập thất bại bây giờ còn hơn thất bại lúc mất key thật. Không bao giờ gom
đủ K share hay gõ cụm từ lên máy lạ hoặc máy nhiễm độc. Nguồn:
[07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

### Vì sao không tự chế thuật toán mã hóa mới?

Thuật toán tự chế hầu như luôn có lỗ hổng mà chỉ lộ khi bị tấn công thật.
Hệ thống chỉ dùng phép toán chuẩn đã phân tích công khai hàng chục năm:
Shamir (1979), BIP-39, SHA-256, PBKDF2. Phần riêng — và cũng là phần kẻ tấn công
không biết — là quy trình vận hành: thiết bị nào giữ gì, ngưỡng bao nhiêu, két ở
đâu. An toàn nằm ở bí mật S, không nằm ở giấu quy trình. Nguồn:
[07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md),
[research/05-qgac-danh-gia](research/05-qgac-danh-gia.md).

---

## 7. Tool Python và kiểm thử

### Chạy kiểm tra toàn bộ repo bằng gì?

`scripts/run_tests.ps1` (Windows) hoặc `scripts/run_tests.sh` (Linux): một lệnh
chạy self-test của cả 7 tool. Nguồn: [README](../README.md).

### `--self-test` là gì?

Mỗi tool có chế độ tự kiểm nhanh không cần phần cứng: ví dụ `fido_check` kiểm
framing INIT/PING, `hid_echo` kiểm đóng gói report, `split_secret` kiểm vector
nhân AES và round-trip mọi ngưỡng. Chạy self-test trước khi nghi tool hỏng.
Nguồn: [README](../README.md), các sổ NCKH-002/004/010/016/022/024.

### `fido_check.py` kiểm tra mấy tầng?

Ba tầng: HID (liệt kê thiết bị), PING nối gói (CTAPHID INIT/PING), và CTAP2
GetInfo (hỏi khả năng key). Có self-test key giả trong RAM để kiểm không cần board.
Nguồn: [README](../README.md), [04-firmware](04-firmware.md), sổ NCKH-004.

### Fuzz `cbor_decode` phát hiện gì? (NCKH-010)

5639 case, 30 case (~0,53%) crash sai loại kỳ vọng (kỳ vọng mọi lỗi đều là
ValueError): `TypeError: unhashable type: 'list'` khi map dùng mảng làm khóa,
`RecursionError` khi lồng sâu, và thân cụt (khai 5 byte, thực 2 byte) bị nuốt im
không báo lỗi. NCKH-003 đã tái hiện độc lập cả 3 bằng one-liner, đường khác.
Kết luận kiểm định: báo cáo đạt, lỗi thuộc về `fido_check.py`, cần thẻ follow-up
siết `cbor_decode`. Nguồn: sổ NCKH-010, kiểm chéo NCKH-003.

### Fuzz `parse_share` phát hiện gì? (NCKH-028)

5066 case: 4870 ValueError đúng, 154 case ném `KeyError` ('shares'/'threshold'/
'index') khi header thiếu key — vi phạm hợp đồng "chỉ ValueError". Nguyên nhân:
`tools/split_secret.py` dòng 146 truy cập dict trực tiếp. NCKH-020 tái hiện độc
lập 3/3. Nguồn: sổ NCKH-028, kiểm chéo NCKH-020.

### Lỗi nguy hiểm nhất ở `split_secret` là gì? (NCKH-022)

`index=-1` cho bí mật **sai lặng**: parse chấp nhận, combine không từ chối,
trả ra rác mà không báo lỗi — người dùng tưởng đã khôi phục đúng. Cùng gốc thiếu
kiểm phạm vi còn gây `IndexError` với index=300. Đề xuất: kiểm tra `1 <= x <= 255`
ở cả parse và combine. Lẫn 2 lần chia khác nhau cũng cho rác mà rc=0, nhưng đó là
giới hạn thiết kế của Shamir thuần (không tag xác thực), không phải bug. Nguồn:
sổ NCKH-022 (P1-P5), kiểm chéo NCKH-014.

### `hid_echo.py` có thể bắt nhầm thiết bị không? (NCKH-016)

Có. Tool lọc thiết bị chỉ theo `usage_page == 0xFF00`, không lọc usage/VID/PID;
trên máy test có 2 thiết bị hệ thống (HIDI2C, Alienware AW-ELC) cùng usage page
nên tool có thể gửi nhầm 65 byte lạ vào driver hệ thống. Đề xuất lọc thêm usage,
thêm cờ `--vid/--pid`. Cùng đợt còn phát hiện: `assert` kiểm độ dài biến mất
dưới `python -O` (nên `raise ValueError`), và tool không kiểm tra report ID trả về.
Nguồn: sổ NCKH-016.

### Tool mnemonic kiểm định BIP-39 thế nào? (NCKH-024)

Chạy 24 vector chuẩn của `trezor/python-mnemonic` (8 vector 12 từ, 8 vector 18 từ,
8 vector 24 từ), mỗi vector kiểm cả 3 chiều from-entropy/to-entropy/seed: 24/24
khớp. NCKH-016 kiểm chéo độc lập 4/24 vector (tự tải vectors.json, tự gõ CLI),
khớp 100%. Nguồn: sổ NCKH-024, kiểm chéo NCKH-016.

### Chưa có board thật thì kiểm thử kiểu gì?

Dùng `--self-test` của từng tool, mock/fake device trong RAM (như FakeDevice của
NCKH-004, mock module hid của NCKH-016), và probe biên bằng script riêng trong
`$env:TEMP` (không viết file tạm vào repo). Nhiều agent đã khai "chưa có board"
trong Unresolved và vẫn hoàn thành phần kiểm tĩnh. Nguồn: sổ
NCKH-004/010/014/016/022/028.

---

## 8. Hậu lượng tử (PQC)

### PQC là gì? Vì sao dự án quan tâm?

PQC (mật mã hậu lượng tử) là các thuật toán chống được máy tính lượng tử tương lai.
Dự án quan tâm ở hai chỗ: thử nghiệm trao đổi khóa ML-KEM-768 trên máy tính
(`tools/pqc.py`) và đặc tả két lai X25519+ML-KEM (NCKH-013), bọc bản sao S bằng
ML-KEM (NCKH-025). Nguồn: [README](../README.md), sổ NCKH-001/007/013/019/025.

### ML-KEM-768 là gì? Vì sao chọn 768 mà không phải 512/1024?

ML-KEM là chuẩn FIPS 203 cho bao gói khóa hậu lượng tử (tên cũ Kyber).
NCKH-007 đo cả 3 mức trên máy này: 768 là điểm cân bằng (an toàn NIST level 3,
kích thước vừa: pk 1184 B, sk 2400 B, ct 1088 B, ss 32 B) nên được khuyến nghị
cho két. Nguồn: sổ NCKH-007, kiểm chéo NCKH-012 (khớp FIPS 203 từng ô).

### Vì sao không đưa ML-KEM vào firmware ESP32-S3?

Kết luận của NCKH-019: **kỹ thuật được, sản phẩm chưa**.

- Kỹ thuật được: mlkem-native tốn ~11,3 KB flash, ~24 KB stack, ~10 ms/op —
  không đáng kể so với ngân sách S3.
- Sản phẩm chưa: (1) firmware dùng thật là pico-fido, chuẩn CTAP 2.x không có
  chỗ cho KEM (PIN protocol dùng ECDH P-256) — nhúng vào là fork sâu, không
  RP/browser nào hiểu; (2) chưa có đặc tả dùng ML-KEM vào việc gì trong key;
  (3) thư viện chính chủ esp-pqc còn ghi "evaluation only".

NCKH-027 kiểm chéo đạt, bổ sung: WebAuthn L3 (2026-08) vẫn chưa có PQC, FIDO mới
ở mức nhóm nghiên cứu. Hướng đúng đợt này: giữ PQC ở tầng tool máy tính. Nguồn:
sổ NCKH-019, kiểm chéo NCKH-027.

### Két lai X25519 + ML-KEM là gì? (NCKH-013)

Đặc tả két (bản 0.1, chưa code) kết hợp hai vế: X25519 cổ điển và ML-KEM hậu
lượng tử. Vế nào gãy về mật mã thì vế còn lại vẫn giữ két; gãy vận hành (mất một
khóa bí mật) thì có quy trình mở khẩn. Còn 5 unresolved (U1-U5) chờ hội đồng,
trong đó có câu hỏi có cho phép phong bì dự phòng mật khẩu hay cấm hẳn. Nguồn:
sổ NCKH-013, kiểm chéo NCKH-021 (đạt).

### Vì sao bọc S phải hybrid KEM+DEM mà không "mã hóa S bằng ML-KEM" trực tiếp?

ML-KEM là KEM: `encap` chỉ tạo shared secret 32 byte chung, không nhận plaintext
tùy ý. Muốn bọc S (32 byte) phải dùng cấu trúc hybrid chuẩn: KEM tạo ss →
HKDF-SHA256 ra khóa Ke → AES-256-GCM mã hóa S. Gói PQC-WRAP-V1 (1218 byte) lưu
được trên cloud; khóa bí mật sk (2400 byte) chia Shamir 5/3, không bao giờ lên
cloud. Nguồn: sổ NCKH-025 (mục 2-5), kiểm chéo NCKH-017 (đạt).

### Share khóa ML-KEM (2400 byte) chuyển sang thiết bị khác bằng gì?

Bằng file (Bluetooth/Quick Share/cáp/USB), **không** dùng QR: ~4800 ký tự hex
vượt sức chứa thực tế của QR, dễ quét lỗi. Xong thì xóa file tạm và ảnh QR trên
máy gửi. Nguồn: sổ NCKH-025 (mục 3).

### Chạy tool PQC báo thiếu liboqs / DLL?

`scripts/run_tests.*` đã tự đặt `OQS_INSTALL_PATH` tới `.tooling/oqs` chứa DLL
liboqs. Quy ước mã thoát: thiếu lib là exit 2 (khớp `hid_echo.py`).
Lưu ý mâu thuẫn tài liệu đang mở: docstring `pqc.py` nói liboqs build vào `_oqs`
trong home, trong khi run_tests và README nói `.tooling/oqs` — cần chủ repo chốt.
Nguồn: [README](../README.md), sổ NCKH-001 (mục 5), NCKH-006.

### File khóa bí mật `.sk` cần khóa quyền không?

Có. NCKH-001 phát hiện `pqc.py` ghi `.sk` bằng `write_bytes` với umask mặc định,
trên Linux file có thể world-readable. Đề xuất `chmod 0o600` sau khi ghi
(đặc tả NCKH-025 đã đưa vào yêu cầu cho bản code sau). Nguồn: sổ NCKH-001 (mục 3),
sổ NCKH-025.

---

## 9. Thám mã bằng ML và Gohr 2019

### `ml_distinguisher.py` làm gì? Kết quả ra sao?

Thí nghiệm học tập: huấn luyện MLP nhỏ (64→128→64→1, numpy thuần, CPU ~2 giây)
phân biệt đầu ra mã toy Speck32/64 rút gọn với dữ liệu ngẫu nhiên. Kết quả
(seed 1337, NCKH-002 tái hiện khớp tuyệt đối): R=5 → 0.5970 (phân biệt rõ),
R=6 → 0.5245 (tín hiệu yếu), R=7 → 0.5070 (gần đoán mò). Chỉ để học và minh họa,
không dùng vào khóa thật. Nguồn: [research/06-ml-distinguisher](research/06-ml-distinguisher.md),
sổ NCKH-002.

### Distinguisher là gì? (Giải thích cho người mới)

Hãy tưởng tượng hai hộp đen: hộp A trả số hoàn toàn ngẫu nhiên, hộp B chạy thuật
toán mã hóa rồi trả kết quả. Distinguisher là bất kỳ thủ tục nào cố trả lời
"mẫu tôi đang cầm đến từ hộp nào?". Nếu đoán đúng rõ trên 50% (ví dụ 60%), mã đó
rò rỉ cấu trúc. Đây là bài kiểm tra tối thiểu: trượt thì chắc chắn yếu, nhưng đỗ
không có nghĩa là an toàn (xem câu tiếp). Nguồn:
[research/07-giai-thich-distinguisher](research/07-giai-thich-distinguisher.md).

### Vì sao "mã chống được distinguisher" không phải bằng chứng an toàn?

Bốn lý do (NCKH-026): (1) kết quả âm tính chỉ nói về đúng một mạng, một ngân sách —
đổi mạng/dữ liệu/chênh lệch là kết quả có thể đổi; (2) kẻ tấn công thật không bị
giới hạn ngân sách của ta; (3) "an toàn" là khẳng định phổ quát ("không tồn tại"
đòn tấn công), một thí nghiệm chỉ kiểm tra một điểm — nó chỉ có thể bác bỏ, không
thể chứng minh; (4) chuẩn mực an toàn thực sự là phép toán chuẩn + nhiều năm bị
cộng đồng thám mã "đánh" mà vẫn đứng vững. Nguồn:
[research/07-giai-thich-distinguisher](research/07-giai-thich-distinguisher.md),
[research/05-qgac-danh-gia](research/05-qgac-danh-gia.md).

### Bài Gohr 2019 là gì? Thí nghiệm của ta khác gì?

Gohr (CRYPTO 2019) huấn luyện mạng residual sâu làm distinguisher vi sai-thần kinh
cho Speck32/64, rồi đi tới tấn công khôi phục khóa 9/11 vòng. Ta là "Gohr thu nhỏ":
đúng chênh lệch (0x0040, 0x0000), đúng đặc trưng 64 bit, nhưng khác 3 điểm lớn —
nhãn 0 của Gohr là mã hóa cặp ngẫu nhiên (khó, đúng nghĩa vi sai), của ta là bit
ngẫu nhiên thuần (dễ hơn); Gohr dùng ResNet sâu + BatchNorm, ta dùng MLP; Gohr
10 triệu mẫu + GPU, ta 6000 mẫu + CPU 2 giây. Vì vậy accuracy ta thấp hơn Gohr ở
cùng R là bình thường, không phải lỗi code. Nguồn: sổ NCKH-020, kiểm chéo NCKH-028.

### Thử CNN 1D thay MLP thì sao? (NCKH-014)

Thua baseline. Cùng dữ liệu và ngân sách: MLP 0.5970/0.5245/0.5070, CNN+AvgPool
0.5000/0.5000/0.5035, CNN+Flatten 0.5070/0.5100/0.4910. Nguyên nhân: tín hiệu
phân biệt Speck phụ thuộc vị trí bit cụ thể; AvgPool xóa thông tin vị trí, còn
conv (trọng số chia sẻ) kém hiệu quả hơn dense ở ngân sách nhỏ. Code conv đã
được chứng minh đúng (gradient check khớp ~1e-9, overfit 200 mẫu đạt 0.995) nên
đây là negative result có giá trị: không nên thay MLP bằng CNN 1D ở ngân sách này.
Nguồn: sổ NCKH-014, kiểm chéo NCKH-022 (đạt).

### Tăng mẫu lên 50k ở R=7 có cải thiện không? (NCKH-008)

Không. 50k mẫu, R=7, seed 1337 cho accuracy 0.4970 — vẫn đoán mò, kết quả âm tính
trung thực. NCKH-001 kiểm chéo độc lập (seed 99/1234, 10k mẫu) cho 0.4970/0.4965,
tính lại độ lệch chuẩn ~0.011 với test 2000 mẫu: tất cả nằm gọn trong nhiễu.
Nguồn: sổ NCKH-008, kiểm chéo NCKH-001.

### Test vector Speck32/64 thứ tự khóa thế nào?

k0 là **từ cuối**: key (0x1918,0x1110,0x0908,0x0100) thì k0=0x0100, pt
(0x6574,0x694c) → ct (0xa868,0x42f2). NCKH-020 xác nhận độc lập từ code chính chủ
`deep_speck/speck.py` của Gohr (`ks[0] = k[-1]`), khớp cách hiểu của tool ta mà
tài liệu 06 đang để "chưa xác nhận". NCKH-032 sẽ đối chiếu chéo. Nguồn: sổ NCKH-020,
[research/06-ml-distinguisher](research/06-ml-distinguisher.md).

### QGAC là gì? Kết luận đánh giá ra sao? (NCKH-005 nhóm)

QGAC (Quantum Generative Adversarial Cryptography) là ý tưởng trong thư mục `QGAC/`:
AI tự sinh và tự tấn công thuật toán mã hóa. Kết luận: đề tài nghiên cứu, không phải
hướng xây mật mã dùng thật — GAN chỉ chứng minh chống được đúng con AI trong lab,
mô phỏng 50+ qubit không chứng minh kháng lượng tử thật, QKD mô phỏng vẫn là mô
phỏng (thiếu phần cứng lượng tử). Hướng làm thật rút ra: PQC chuẩn NIST qua liboqs,
Rust cho thành phần nhạy cảm, ML toy để học. Nguồn:
[research/05-qgac-danh-gia](research/05-qgac-danh-gia.md).

---

## 10. Quy trình làm việc của Viện

### Tên tôi là gì khi lệnh giao việc và `phan-cong.json` lệch nhau?

Lấy tên trong `phan-cong.json` làm chuẩn, Viện trưởng chốt khi có lệch.
Nhiều agent đợt 1 đã gặp (NCKH-002 Trần An, NCKH-003 Lê An, NCKH-004 Phạm An,
NCKH-005 Hoàng An...) và đều được đính chính theo file phân công, mã giữ nguyên.
Nguồn: sổ NCKH-002/003/004/005/007/008/009/010/011, Hiến chương §1.

### `HIEN-CHUONG.md`, `phan-cong.json` nằm ở đâu?

Dưới `vien-nghien-cuu/` (`vien-nghien-cuu/HIEN-CHUONG.md`,
`vien-nghien-cuu/phan-cong.json`, `vien-nghien-cuu/so-cai/README.md`),
**không** ở gốc repo như một số lệnh giao việc ghi. Đã có agent mất công tìm
(NCKH-023, NCKH-027). Nguồn: sổ NCKH-023/027.

### Shell báo `program not found`?

Thiếu tham số `shell='pwsh'` trong lệnh gọi shell — thêm vào là chạy được
(NCKH-002 đã gặp đúng lỗi này). Trường hợp khác: shell hỏng cục bộ theo phiên
(NCKH-001: mọi lệnh đều hỏng, phiên sau lại sống) — khi đó chỉ đọc tĩnh, ghi sổ,
và nhờ agent có shell chạy kiểm chứng. Nguồn: sổ NCKH-001/002.

### Kanzo báo 500 `database is locked`?

Máy chủ Kanzo dùng SQLite, khóa database khi ghi/đọc dồn dập — bệnh đã biết,
hầu hết agent các đợt đều gặp. Luật ghi: file trước bảng sau, thao tác cách nhau
ít nhất 1-5 giây, lỗi thì chờ rồi thử lại (tối đa 2-3 lần), vẫn hỏng thì ghi sổ
file và nhờ Viện trưởng vá, **không** thử tiếp để tránh ghi dồn dập thêm. Nguồn:
Hiến chương §6, `vien-nghien-cuu/NHIP-TIM.md`, `NHIP-TIM.log`, sổ NCKH-001..028.

### Timeout client có nghĩa server chưa ghi?

Không. Timeout client không đồng nghĩa server chưa ghi — phải đối chiếu lại bảng
sau mỗi đợt (đã kiểm chứng thực tế). Khi vá tay, nhớ kiểm tra trùng comment.
Nguồn: Hiến chương §6, sổ NCKH-003 (lượt kiểm thẻ 143), NCKH-028 (thẻ 160).

### GET board OK nhưng không thấy thẻ của mình?

Bảng có thể chưa được tạo thẻ cho bạn (đợt 2A: bảng mới có thẻ đến NCKH-021,
thiếu NCKH-022..030). Ghi sổ và nhờ Viện trưởng tạo giúp, **không tự tạo thẻ**
(tránh trùng), không chạm vào thẻ người khác kể cả khi thẻ đó ghi bạn là người
kiểm chéo mà chưa tới lượt. Nguồn: sổ NCKH-023/027/028.

### Không dám move/comment vì chưa chắc id thẻ?

Đúng — không đoán id. NCKH-020 thấy output board bị cắt, đoán id 160 nhưng không
dám gọi theo id đoán vì có thể chạm nhầm thẻ người khác; ghi sổ nhờ Viện trưởng
vá. Một việc một chủ. Nguồn: sổ NCKH-020, Hiến chương §4.

### Kiểm chéo là gì? Vì sao phải "kiểm bằng đường khác"?

Người khác nhóm kiểm độc lập thẻ ở `review`: đạt thì `review → done`, không đạt
thì về `doing` kèm yêu cầu sửa. "Đường khác" nghĩa là không chạy lại đúng lệnh
của tác giả mà kiểm bằng cách khác: seed khác (NCKH-001), parser thủ công
(NCKH-002), one-liner thay script fuzz (NCKH-003, NCKH-020), tự tải vector
(NCKH-016), đọc code thay vì chạy (NCKH-028). Comment `[KIEM-DINH] đạt/không đạt
+ lý do`. Nguồn: Hiến chương §2, sổ NCKH-001/002/003/016/020/028.

### Sổ cái file để làm gì? Khi nào ghi?

Là kênh dự phòng khi Kanzo sập, và là nguồn sự thật khi bảng chưa đồng bộ.
Luật: **ghi sổ TRƯỚC, đồng bộ Kanzo SAU**. Chỉ nối thêm mục mới, không sửa mục
cũ (sai thì viết mục đính chính — NCKH-027 đã làm mẫu). Nguồn:
`vien-nghien-cuu/so-cai/README.md`, Hiến chương §6, `NHIP-TIM.md`, sổ NCKH-027.

### Nhịp tim 2 phút làm gì?

Cron mỗi 2 phút: đọc bảng (Kanzo sập thì đọc sổ file thay), thẻ `doing` quá
30 phút hoặc `review` quá 20 phút thì gọi agent phụ trách, agent rảnh được giao
việc theo thứ tự ưu tiên. Nhịp không có gì làm thì ghi một dòng log rồi nghỉ,
không bịa việc. Thẻ kẹt do lỗi Kanzo (không phải việc khó) thì ghi rõ trong sổ
để nhịp tim không gọi oan. Nguồn: Hiến chương §4, `NHIP-TIM.md`, `NHIP-TIM.log`.

### Repo chưa có commit nào, `git status` toàn `??` — đếm file sửa thế nào?

Không đếm bằng git được. Tự liệt kê thao tác edit/write mình đã gọi trong phiên
(NCKH-027 đã đính chính đúng kiểu này). Nguồn: sổ NCKH-027, kiểm chéo NCKH-019.

### Số dòng trích dẫn trong báo cáo bị lệch?

Repo có nhiều agent sửa đồng thời (NCKH-023: file 07 tăng 126→182 dòng, BOM tăng
21→30 dòng trong lúc quét). Khi đối chiếu, tra theo cụm chữ thay vì số dòng.
Nguồn: sổ NCKH-023 (mục CẢNH BÁO NHIỄU ĐỒNG THỜI).

### Tài liệu và code lệch nhau thì tin ai?

Đối chiếu cả hai và ghi nhận lệch. Ví dụ thật: runbook Windows ghi
`pip install -r requirements.txt` nhưng file thật ở `tools/requirements.txt`
(NCKH-023 B44); docstring `pqc.py` nói DLL ở `_oqs` trong home nhưng run_tests
nói `.tooling/oqs` (NCKH-001 mục 5, chờ chủ repo chốt); `docs/03` vẫn viết
"khả năng cao N16R8 bị ghi nhầm" trong khi BOM đã chốt N16R8 (NCKH-023 B43).
Nguồn: sổ NCKH-001/023.

---

## Câu hỏi chưa có lời đáp (Unresolved gom từ sổ cái)

| # | Câu hỏi | Nguồn |
|---|---|---|
| 1 | Chữ in vật lý trên nắp shield là gì (chưa ai có board trong tay)? | NCKH-027, NCKH-019 |
| 2 | Vị trí DLL liboqs chuẩn là `.tooling/oqs` hay `_oqs` trong home? | NCKH-001, NCKH-006 |
| 3 | Wrapper oqs ném `ValueError` hay `RuntimeError` cho input ngắn? | NCKH-001 |
| 4 | Có cho phép phong bì dự phòng mật khẩu cho két lai, hay cấm hẳn? | NCKH-013 (U1) |
| 5 | Tên file CLI `pqc_wrap.py` + trường header `kind`, chốt với nhóm tooling? | NCKH-025 |
| 6 | Chu kỳ rotation khóa bọc bao lâu (đề xuất 2 năm)? | NCKH-025 |
| 7 | FIDO đã có draft PQC nào cho CTAP/WebAuthn chưa? (tính đến 09/2026: chưa) | NCKH-019 (U2), NCKH-027 |
| 8 | Số trang PDF tr.51/53 trong BOM đã đúng chưa (chưa kiểm độc lập)? | NCKH-019 |
| 9 | Số accuracy từng bảng trong PDF Gohr (mới dùng số thứ cấp)? | NCKH-020 |
| 10 | Race `echoPending` xác nhận trên board thật + bản vá portMUX? | NCKH-003, NCKH-008 |
| 11 | `hid_echo` đọc 64 hay 65 byte trên Linux thật? | NCKH-016 (U2) |
| 12 | Sửa P1-P4 `split_secret` + fuzz lại sau sửa? | NCKH-022, NCKH-028 |
| 13 | Siết `cbor_decode` (key hash, giới hạn sâu, báo cụt thân)? | NCKH-010, NCKH-003 |
| 14 | CNN kernel k=16/32 hoặc dữ liệu 50k có bắt kịp MLP không? | NCKH-014 |
| 15 | Thẻ Kanzo NCKH-022..030 + comment/move tồn khi Kanzo sống lại? | NCKH-023/027/028, NHIP-TIM.log |
