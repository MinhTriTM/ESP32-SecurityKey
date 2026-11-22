# hwtest — Sketch kiểm tra phần cứng

## Mục đích

Xác nhận board ESP32-S3 sống, USB CDC lên log, nút BOOT đọc được, LED RGB đổi màu và đường USB HID echo được. Nạp trước khi flash firmware FIDO chính.

## Nạp bằng Arduino IDE

1. Cài Arduino IDE và core ESP32 của Espressif.
2. Chọn board ESP32S3 Dev Module đúng với board đang cầm.
3. Trong menu Tools bật USB CDC On Boot là Enabled.
4. Trong menu Tools đặt USB Mode là USB-OTG (TinyUSB) để bật HID echo.
5. Chọn đúng cổng COM của cổng UART rồi nạp.
6. Mở Serial Monitor 115200 baud để xem log chip và nhấn nút BOOT thử.

## Nạp bằng PlatformIO

Tạo project với board esp32-s3-devkitc-1, chép file hwtest.ino thành src/main.cpp rồi thêm cờ build `-DARDUINO_USB_CDC_ON_BOOT=1`. Muốn HID echo thì project phải bật TinyUSB OTG trong sdkconfig. Nạp qua cổng UART như bình thường.

## Kiểm tra HID echo

Sau khi nạp bản OTG, cắm cổng USB native rồi chạy `python tools/hid_echo.py` trên máy tính. Tool gửi 60 byte ngẫu nhiên và đối chiếu từng byte trả về. Log serial đồng thời hiện dòng "HID echo: da gui lai 64 byte."

## Kết quả đạt

Log in đúng chip ESP32-S3, dung lượng flash và PSRAM. Nhấn BOOT thì log hiện nhấn và nhả. LED xanh lá khi chờ, xanh dương khi nhấn nút. Tool hid_echo báo 60 byte khớp. Thiếu bất kỳ điểm nào thì dừng lại kiểm tra board và cáp trước khi flash firmware chính.
