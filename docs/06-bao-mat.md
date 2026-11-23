# 06 — Bảo mật

## Mô hình đe dọa

Key này chống lừa đảo và rò mật khẩu vì private key không rời chip và mỗi credential gắn với đúng domain đã đăng ký. Trang giả mạo domain khác thì chữ ký không khớp.

Key không chống được máy tính đã nhiễm mã độc toàn quyền hoặc người khác cầm key vật lý cùng mã PIN. Bảo vệ key như chìa khóa nhà.

## Quy tắc dùng thật

- Bật Secure Boot V2 + Flash Encryption release cho bản firmware cuối, kèm cờ `encrypted` cho part0 (thiếu cờ là hỏng kho — xem [04-firmware](04-firmware.md)). Tự sinh khóa FE và cất offline.
- Đặt PIN FIDO và nhớ kỹ. Quên PIN nhiều lần là phải reset trắng key.
- Giữ ít nhất hai key cho mỗi tài khoản quan trọng.
- In mã khôi phục ra giấy, cất nơi khác với key.
- Không cập nhật cả hai key cùng lúc.
- Ghi MAC của từng board vào [sổ theo dõi key](../hardware/keys.md) ngay khi nạp hwtest.

## Định danh từng key bằng MAC

Mỗi chip ESP32-S3 có một MAC gốc ghi trong efuse, duy nhất từng con chip. Sketch hwtest in dòng `MAC: ...` ra log serial khi khởi động. Lấy chuỗi đó ghi vào sổ theo dõi cùng tên key, ngày flash và commit pico-fido.

MAC là định danh, không phải bí mật: ai cầm board cũng đọc được qua log serial hoặc esptool. Giá trị của nó là quản lý — biết key nào đang cầm, phát hiện board bị tráo, đối chiếu khi bảo hành. Không bao giờ dùng MAC làm PIN, mật khẩu hay vật liệu khóa.

## Tận dụng hai cổng USB-C để tăng bảo mật

Board DevKit có hai cổng C với vai trò khác nhau: cổng UART để nạp firmware, cổng OTG native để chạy FIDO hàng ngày. Cách tận dụng:

1. Chia vai trò dứt khoát. Chỉ flash qua cổng UART, chỉ dùng FIDO qua cổng OTG. Không bao giờ cắm cổng UART vào máy lạ vì đó là đường nạp code.
2. Flash bản cuối trên máy riêng, không phải máy dùng hàng ngày. Kiểm tra hash commit pico-fido trước khi build.
3. Bật Secure Boot V2 + Flash Encryption release cho bản cuối, kèm cờ `encrypted` cho part0. Mỗi chip dùng khóa FE tự sinh, cất offline + backup (mất khóa là mất đường nạp lại). Khi hai tính năng này bật, ESP-IDF tự chuyển cổng nạp sang Secure Download Mode: kẻ xấu không chạy được code lạ, chỉ còn vài lệnh nạp hạn chế. JTAG cũng tự tắt. Dữ liệu nghỉ có 2 lớp: flash encryption + mã hóa tầng app của pico (khóa chính trong OTP). KHÔNG bao giờ `--force` bản thô lên chip đã khóa (xem [nghiên cứu cứu hộ](research/11-cuu-key-01.md)).
4. Cân nhắc khóa hẳn ROM Download Mode sau khi flash bản cuối (tùy chọn `CONFIG_SECURE_UART_ROM_DL_MODE` hoặc hàm `esp_efuse_disable_rom_download_mode`). Đây là cầu dao một chiều: khóa rồi thì không flash lại qua UART nữa. Chỉ làm khi chắc chắn không cần cập nhật firmware qua cổng này.
5. Bịt cổng UART về mặt vật lý. Vỏ key chỉ chừa cổng OTG và lỗ nút BOOT, che kín cổng UART lại. Người mượn key không thể cắm vào cổng nạp để flash lén trong vài phút.
6. Không bật NVS encryption: pico-fido không dùng NVS mà lưu credential bằng object store mã hóa riêng.

Nguồn: tài liệu [Security của ESP-IDF cho ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/v5.1.2/esp32s3/security/security.html).

## Reset và mất key

Reset FIDO xóa toàn bộ credential trên key đó. Chỉ reset khi còn đăng nhập được bằng key dự phòng hoặc mã khôi phục. Mất một key thì vào từng dịch vụ gỡ key đó đi ngay. Quy trình khôi phục đầy đủ bằng két mã hóa và share Shamir nằm ở [tài liệu sao lưu](07-sao-luu-va-khoi-phuc.md).

## Giới hạn phải biết

ESP32-S3 không có secure element đạt chứng nhận như key thương mại. Kẻ có đủ thiết bị và thời gian cầm key vật lý vẫn có cửa tấn công kênh kề. Với người dùng cá nhân nghiêm túc thì mức này đủ, với bí mật cấp tổ chức thì nên mua key đạt chứng nhận FIDO.

Firmware pico-fido là nguồn mở do cộng đồng duy trì. Trước khi flash bản mới phải đọc changelog, kiểm tra hash và thử trên tài khoản phụ.

## Kiểm tra định kỳ

Mỗi vài tháng cắm từng key và đăng nhập thử một dịch vụ. Key để lâu không dùng có thể hết pin dự phòng suy nghĩ, quên PIN hoặc lỗi flash mới phát hiện. Phát hiện sớm thì còn key dự phòng để xoay.
