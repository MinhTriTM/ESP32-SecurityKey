# Tóm tắt dự án ESP32-S3 Security Key (đọc 5 phút)

> Khóa bảo mật USB-C dùng thật, dựng trên board ESP32-S3 DevKit. Cắm cáp C-to-C là chạy trên Android, Linux/Ubuntu và Windows 11, không cần cài driver. Nguồn: [README](../README.md). Tác giả tóm tắt: Lê Cường (NCKH-053, nhóm tailieu, đợt 2C).

## Key là gì

- **Phần cứng:** board ESP32-S3 DevKit đời 2022, module ESP32-S3-WROOM-1-**N16R8** (flash 16 MB + PSRAM octal 8 MB; mã "N26R8" cũ là ghi nhầm). Chip có USB OTG native full-speed 12 Mbps (GPIO19 D-, GPIO20 D+) nên giả lập được thiết bị USB HID chuẩn — đó là lý do cắm là chạy. Nguồn: [BOM](../hardware/BOM.md), [03-phan-cung](03-phan-cung.md), [FAQ](FAQ.md).
- **Board có 2 cổng C khác vai trò:** cổng UART (chữ `COM`/`UART`) chỉ để nạp firmware; cổng native (chữ `USB`/`OTG`) mới chạy FIDO. Cắm nhầm cổng là nguyên nhân phổ biến nhất của lỗi "không thấy thiết bị". Nguồn: [FAQ](FAQ.md).
- **Firmware dùng thật:** pico-fido bản ESP32-S3, tag **v8.2** (2026-10-18, tag ký PGP), commit ghim `15b848d821b4995eb1b29a5c2a4c24c25d1a768e`, build bằng ESP-IDF **v5.5.1**. Ghim commit vì tag có thể bị dời; đã khảo sát, chưa build kiểm chứng trên máy này. Nguồn: [04-firmware](04-firmware.md).
- **Giao thức:** FIDO2 (CTAP2/WebAuthn) + U2F (CTAP1) cho dịch vụ cũ. Không tự viết CTAP2/crypto vì sai một byte là mất an toàn; code tự viết chỉ kiểm tra phần cứng và giao tiếp, không chạm private key. Nguồn: [README](../README.md).
- **Giấy phép:** code repo MIT; pico-fido AGPL-3.0 (tự build dùng cá nhân thoải mái, phân phối binary đã sửa phải công bố source). Nguồn: [04-firmware](04-firmware.md).
- **Mức an toàn:** chống lừa đảo và rò mật khẩu (private key không rời chip, credential gắn đúng domain), nhưng ESP32-S3 không có secure element đạt chứng nhận — đủ cho cá nhân nghiêm túc, bí mật cấp tổ chức nên mua key đạt chứng nhận FIDO. Nguồn: [06-bao-mat](06-bao-mat.md).

## Dùng thế nào

1. Cắm key bằng **cáp C-to-C có đủ dây dữ liệu** (cáp chỉ sạc làm board lên nguồn nhưng máy tính không thấy gì). Nguồn: [03-phan-cung](03-phan-cung.md).
2. **Windows 11:** nhận HID ngay, đăng ký bằng Edge/Chrome. **Linux/Ubuntu:** cài `config/70-u2f.rules` rồi chạy `tools/fido_check.py` (kiểm tra 3 tầng: HID, PING nối gói, CTAP2 GetInfo). **Android 9+:** Chrome + cáp OTG, bật OTG nếu máy tắt mặc định. Nguồn: [05-huong-dan-su-dung](05-huong-dan-su-dung.md).
3. Khi đèn báo chờ xác nhận thì **nhấn nút BOOT** trên board (LED RGB địa chỉ, thường là WS2812 trên GPIO38 hoặc GPIO48 tùy bản board). Nguồn: [03-phan-cung](03-phan-cung.md).
4. Quy tắc sống còn: **mỗi tài khoản quan trọng đăng ký ít nhất 2 key**, đặt tên từng key, in mã khôi phục ra giấy cất riêng, thử trên tài khoản phụ trước, không cập nhật cả hai key cùng lúc, đặt PIN FIDO (quên PIN nhiều lần là reset trắng key). Nguồn: [05-huong-dan-su-dung](05-huong-dan-su-dung.md), [06-bao-mat](06-bao-mat.md).

## Khôi phục ra sao (mất key thì làm gì)

Credential FIDO **không chép sang key mới được** theo thiết kế. Hệ thống xoay quanh một bí mật gốc **S duy nhất (32 byte / 256 bit)** với 3 đường khôi phục, đường nào cũng ra cùng S; hex của S chính là mật khẩu mở két `ket.bin` (AES-256-GCM, `tools/vault.py`) chứa mã khôi phục các dịch vụ. Nguồn: [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

1. **Key FIDO dự phòng đã đăng ký sẵn** — nhanh nhất: đăng nhập thẳng, gỡ tên key đã mất, đăng ký key mới.
2. **Share Shamir ngưỡng đa số** — cấu hình gợi ý **5 share cần 3** (PC, laptop, điện thoại, USB ở nhà, USB gửi người thân): gom ≥3 share về một máy tin cậy, `combine` ra S. Mất bất kỳ 2 nơi vẫn mở được; kẻ trộm lấy 2 nơi vẫn biết đúng 0 bit về S.
3. **Cụm 24 từ BIP-39** trên giấy (2 bản, 2 nơi) hoặc thép — đường cuối khi mất hết thiết bị: `to-entropy` ra S, checksum bắt lỗi gõ nhầm. 24 từ là tối đa của chuẩn cho 256 bit (không thể brute-force 2^256), giữ chuẩn để đọc được bằng mọi ví lạnh khác.

Dựng một lần: `mnemonic.py new --words 24` → ghi giấy NGAY → `split_secret.py split --shares 5 --threshold 3` → mã hóa mã khôi phục vào két → chuyển mỗi share sang đúng một thiết bị → **diễn tập ngay** (ghép thử, mở két thử) và lặp lại mỗi 6 tháng. Không bao giờ gom đủ share hay gõ 24 từ lên máy lạ. Nguồn: [07-sao-luu-va-khoi-phuc](07-sao-luu-va-khoi-phuc.md).

## Bắt đầu từ đâu (người mới)

1. Đọc [01-phan-tich-y-tuong](01-phan-tich-y-tuong.md) + [BOM](../hardware/BOM.md), tra cứu [FAQ](FAQ.md) khi kẹt.
2. Nạp sketch `firmware/hwtest/hwtest.ino` theo runbook (`docs/runbook-nap-hwtest-windows.md` hoặc `-ubuntu.md`) để kiểm tra USB, nút BOOT, LED, HID echo. Lưu ý: chọn đúng board `ESP32S3 Dev Module`, bật `USB CDC On Boot`, muốn HID echo thì dùng chế độ USB-OTG. Nguồn: [FAQ](FAQ.md).
3. Build + flash pico-fido theo [04-firmware](04-firmware.md), đối chiếu SHA commit sau checkout; bản dùng thật bật Flash Encryption + Secure Boot V2 và bịt cổng UART vật lý. Nguồn: [04-firmware](04-firmware.md), [06-bao-mat](06-bao-mat.md).
4. Kiểm tra toàn bộ bằng một lệnh `scripts/run_tests.ps1` (Windows) hoặc `scripts/run_tests.sh` (Linux) — chạy self-test cả 7 tool, không cần phần cứng. Nguồn: [README](../README.md).
5. Trạng thái dự án: đang phát triển — hwtest biên dịch sạch (arduino-cli 1.6.0, core ESP32 4.0.0), các tool đã qua self-test và thử CLI thật; phần cần board thật (nạp hwtest, flash pico-fido, INIT/PING với key) chưa thực hiện. Chi tiết: [README](../README.md).
