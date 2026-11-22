# 05 — Hướng dẫn sử dụng trên Android, Linux, Ubuntu và Windows 11

## Nguyên tắc chung

Cắm key vào cổng USB-C native của board bằng cáp dữ liệu. Mở trình duyệt Chrome hoặc Edge rồi đăng ký key trong phần bảo mật của dịch vụ. Khi đèn báo chờ xác nhận thì nhấn nút BOOT trên board.

## Windows 11

Cắm key là Windows nhận HID, không cần driver. Vào Settings rồi Bluetooth và devices để xác nhận thiết bị HID mới xuất hiện. Đăng ký key trong tài khoản Google, GitHub hoặc Microsoft bằng Edge hoặc Chrome.

Nếu trình duyệt không thấy key thì đổi cổng USB, đổi cáp và kiểm tra Device Manager có thiết bị HID lạ báo lỗi không.

## Linux và Ubuntu

Cài file [udev rules](../config/70-u2f.rules) để trình duyệt có quyền mở thiết bị HID. Không có rules thì Chrome thường báo không tìm thấy authenticator.

Lệnh kiểm tra nhanh sau khi cắm: `lsusb` phải thấy Espressif, `dmesg` phải có dòng HID mới. Chạy [tool kiểm tra](../tools/fido_check.py) để xác nhận key trả lời INIT và PING.

Firefox cần bật WebAuthn và quyền USB trong about:config tùy bản. Chrome và Edge là đường ít lỗi nhất.

## Android

Dùng Chrome trên Android 9 trở lên. Cắm key qua cáp OTG C-to-C. Khi trang web gọi WebAuthn thì hệ thống hiện hộp thoại và key nháy đèn chờ nhấn nút.

Một số máy Android tắt OTG mặc định. Bật trong cài đặt rồi cắm lại. Nếu máy chỉ có cổng Micro-USB thì cần đầu chuyển OTG đúng chuẩn.

## Đăng ký dịch vụ

Luôn đăng ký ít nhất hai key cho mỗi tài khoản quan trọng. Đặt tên từng key để biết key nào đang cầm. In mã khôi phục của dịch vụ ra giấy và cất riêng.

Đăng ký thử trên tài khoản phụ trước. Chỉ đưa key vào tài khoản chính sau khi đăng nhập thử thành công vài lần.
