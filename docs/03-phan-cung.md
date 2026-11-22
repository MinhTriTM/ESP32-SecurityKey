# 03 — Phần cứng

## Board mục tiêu

ESP32-S3 DevKit đời 2022, module được ghi là N26R8. Tên này lạ vì mã module Espressif thường là N8R2 hoặc N16R8. Khả năng cao là N16R8 (flash 16 MB, PSRAM octal 8 MB) bị ghi nhầm.

Việc cần làm trước khi flash: đọc chữ in trên nắp shield kim loại của module và đối chiếu với [BOM](../hardware/BOM.md). Build pico-fido cần đúng dung lượng flash nên không được đoán.

## Yêu cầu cổng USB

Board phải có cổng USB-C nối thẳng vào USB OTG native của ESP32-S3 (GPIO19 D-, GPIO20 D+). Nhiều board DevKit có hai cổng C: một cổng UART qua chip cầu nối, một cổng USB native. Firmware FIDO bắt buộc dùng cổng native.

Cách nhận biết: cổng native thường ghi USB hoặc OTG trên lụa. Cổng UART thường ghi COM hoặc UART.

## Nút xác nhận và LED

Nút BOOT trên DevKit đóng vai trò nút xác nhận hiện diện người dùng. Mạch DevKit đã có sẵn nên không cần thêm linh kiện.

LED RGB địa chỉ (thường là WS2812 trên GPIO38 hoặc GPIO48 tùy bản board) dùng báo trạng thái: chờ xác nhận, đang xử lý, thành công, lỗi. Đúng chân LED theo [sơ đồ đấu nối](../hardware/wiring.md).

## Nguồn và cáp

Key ăn nguồn 5 V từ USB host, dòng tiêu thụ nhỏ nên mọi cổng USB đều đủ. Dùng cáp C-to-C có đủ dây dữ liệu, không dùng cáp chỉ sạc.

Trên Android nếu máy không cấp host mode thì key không lên. Đổi cáp OTG hoặc bật OTG trong cài đặt.

## Vỏ và hoàn thiện

Bản DevKit trần chỉ hợp thử nghiệm. Bản dùng thật nên in vỏ 3D che mạch, chừa lỗ nút BOOT và LED, cố định cáp để chân USB-C không chịu lực uốn. Không để mạch trần trong túi quần áo cùng chìa khóa kim loại.
