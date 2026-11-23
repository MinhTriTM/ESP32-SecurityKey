# 11 — Cứu key-01: nghiên cứu sửa chữa board Secure Boot + FE không boot

> Ngày: 2026-11-23. Loại: nghiên cứu sửa chữa, chạy thí nghiệm thật trên board.
> Câu hỏi gốc: key-01 (SB V2 + Flash Encryption release + Secure Download)
> sau khi nạp `--force` bản thô thì không boot (không LED RGB, OTG chỉ hiện
> ROM 303A:1001) — còn đường nào cứu, hay đã chết hẳn?

## 1. Hiện trạng (chỉ ghi điều đã đo)

- eFuse: SB V2 bật (key0, key1/2 revoked), FE bật (`SPI_BOOT_CRYPT_CNT 0x7`,
  release), JTAG tắt vĩnh viễn, download mode qua UART vẫn sống
  (`get_security_info` đọc được ngày 2026-11-23).
- Ảnh FE gốc (build từ commit đã ghim, chưa có cờ `encrypted` cho part0):
  **đã từng boot** — HID/PING sống, chỉ GetInfo trả CTAP `0x21`.
- Đã thử: `erase_flash`/`erase_region` (bị chặn), ghi trắng 16 MB `--force`
  (dừng giữa chừng), nạp 2 lần ảnh ký mới (SB+FE+cờ `encrypted` part0,
  `Wrote 856064 bytes`, verify chữ ký RSA đạt trước khi nạp).
- Sau 2 lần nạp: board không boot — RGB tối, OTG hiện `303A:1001` (ROM),
  không có HID FIDO. Cổng CDC qua OTG đọc lỗi.
- Chưa đọc: log boot UART (cần cáp COM), vì vậy chưa phân biệt được H1/H2.

## 2. Giả thuyết

- **H1 — ROM không mã hóa khi ghi (nghi ngờ chính).** Ở Secure Download
  Mode, stub bị cấm nên không có ai mã hóa bản thô lúc ghi; flash giữ bản
  thô, lúc boot MMU giải mã ra rác → Secure Boot rớt → boot loop. Muốn nạp
  đúng phải mã hóa trước bằng khóa FE của đúng con chip — khóa nằm trong
  eFuse, không đọc ra được (JTAG chết, đọc flash bị chặn). Nếu H1 đúng,
  mọi lần nạp lại đều chết như nhau và key-01 không cứu được.
- **H2 — Cờ `encrypted` của part0 làm kẹt bootloader.** Ảnh mới khác ảnh gốc
  ở đúng cờ này (+ rebuild). Nếu bootloader xử lý cờ lạ (crypt_cnt đã lẻ)
  thì boot chết dù flash ghi đúng. Nếu H2 đúng, nạp lại ảnh gốc sẽ sống
  (về lại HID + `0x21`) và phải tìm cách sửa kho khác.
- Đã loại trừ: lỗi đường truyền (nạp 2 lần giống hệt nhau), ảnh ký sai
  (verify RSA đạt), part0 bẩn (không giải thích được mất boot + mất LED).

## 3. Ma trận thí nghiệm

| TN | Việc | Cần | H1 đúng | H2 đúng |
|----|------|-----|---------|---------|
| E1 | Đọc log boot UART 115200, nhấn RST | Cáp COM | ROM báo secure-boot/image fail + loop | Boot qua ROM, kẹt ở bootloader/app |
| E2 | Nạp lại ảnh FE gốc lấy từ git (`543c1d0`, đúng byte đã từng boot) | Cáp COM + OTG | Vẫn chết | HID sống lại (kèm `0x21`) |
| E3 | Nếu E2 sống: build lại ảnh cờ-fix từ sạch, nạp, đối chiếu | Như E2 | — | Chết lại = cờ có tội; sống = lần build trước lỗi |

E2 không cần build lại: ảnh gốc còn nguyên trong lịch sử git, chỉ trích ra
(origin: `web/firmware/pico-fido-v8.2/pico_fido_esp32-s3-hardened.bin` ở
`543c1d0`, 856064 byte, byte đầu `0xE9`).

## 4. Ranh giới không thể (đã đối chiếu, không thử mù)

- Đọc khóa FE từ eFuse: không (block bị khóa đọc, JTAG chết, secure
  download chặn mọi lệnh đọc). Đây là bảo đảm an ninh của chip, không phải bug.
- Tắt FE / downgrade crypt_cnt: một chiều, không có đường về.
- Bật lại JTAG / stub: eFuse đã đốt vĩnh viễn.
- OTA: pico-fido không có OTA (xem `docs/04-firmware.md`).
- Glitch điện áp / fault injection qua mặt bảo mật: có tiền lệ học thuật
  trên họ ESP32 nhưng ngoài tầm tay và tầm giá dự án — ghi nhận, không làm.

## 5. Nhật ký chạy

- **E1 (2026-11-23, xong): H1 ĐÚNG.** Log UART sau reset là vòng lặp vô tận
  `invalid header: 0xbb83c7af` (114 KB/10 s). ROM đọc header bootloader qua
  lớp giải mã FE, gặp bản thô mới nạp nên ra rác cố định — từ chối ngay
  trước cả bước xác thực Secure Boot. Chứng minh: ROM **không** mã hóa khi
  ghi ở Secure Download Mode; bản nạp `--force` nằm thô trên flash.
- **E2 (hủy, không cần chạy):** với H1 đã đúng, nạp lại ảnh gốc cũng cho bản
  thô → cùng một cái chết. Không tốn thêm chu kỳ flash vô ích.
- **Kết luận:** key-01 chết vĩnh viễn. Muốn boot lại phải nạp ảnh mã hóa
  trước bằng đúng khóa FE của chip — khóa nằm trong eFuse, không đọc ra
  được. Board còn dùng được làm chặn giấy / mẫu trưng bày.

## 6. Bài học cho key-02 (quan trọng hơn cả cuộc cứu hộ)

- **Tự sinh khóa FE và GIỮ LẠI.** Mặc định chip tự sinh khóa rồi giấu luôn;
  thay vào đó ta sinh khóa trên máy (`espsecure.py generate_flash_encryption_key`),
  đốt vào eFuse lúc provision, cất offline + backup Shamir cùng khóa ký RSA.
  Có khóa FE trong tay thì luôn mã hóa trước được ảnh mới → giữ đường cứu hộ
  UART ngay cả khi FE bật.
- Cấu hình sản xuất giữ nguyên SB+FE+cờ `encrypted` part0 (mạch lạc về lý
  thuyết, chờ chứng minh trên chip mới): lần nạp đầu trên chip virgin vẫn
  nạp bản thô, lần boot đầu chip tự mã hóa toàn bộ gồm cả part0 có cờ.
- Không bao giờ `--force` bản thô lên chip FE đã khóa khi chưa giữ khóa FE.

## 7. Đào sâu lần cuối: còn khe nào không? (2026-11-23, kết luận: không)

- **Mặt lệnh còn mở:** tài liệu ESP-IDF v5.5.1 (`flash-encryption.rst`)
  ghi rõ Secure Download Mode chỉ cho đúng 4 việc: đổi cấu hình SPI,
  đổi baud, **ghi flash thô**, và `get_security_info`. Không đọc, không
  xóa, không stub, không đốt eFuse. Quan sát thực tế khớp 100%: `chip_id`
  lỗi, `erase_*` bị chặn, `read_flash`/đọc eFuse bị chặn, chỉ `write_flash`
  và `get_security_info` chạy được.
- **Lỗ hổng công khai:** mọi tấn công fault-injection lấy khóa
  (CVE-2019-15894, CVE-2019-17391, CVE-2023-35818/AR2023-005) đều nhắm
  ESP32 đời đầu; Espressif đã cứng hóa từ S2 trở đi. Khuyến cáo duy nhất
  cho S3 (AR2026-005) chỉ lấy được khóa của **AES ngoại vi thường**, không
  phải khóa XTS của flash encryption. Tổng hợp công khai (10/2026): chưa
  có bypass Secure Boot/FE nào cho ESP32-S3.
- **eFuse:** block khóa FE đã khóa đọc + khóa ghi, `KEY_PURPOSE` khóa ghi,
  `SPI_BOOT_CRYPT_CNT = 0x7` (3 bit đốt hết, không còn gì để đốt). Mẹo
  parity-counter trên mạng chỉ cứu được chip development-mode còn bit trống.
- **Malleability XTS / cấy flash ngoài:** bản mã gốc đã bị ghi đè 3 lần,
  trên tay không còn ciphertext nào; chữ ký RSA-3072 không dung thứ cho
  sửa đổi mù. Gỡ flash ra đọc cũng chỉ lấy lại byte ảnh mà git đã có.
- **Kết luận cuối:** key-01 không cứu được bằng bất kỳ con đường nào đã
  biết — phần mềm, phần cứng phòng lab bình dân, hay khai thác công khai.
  Đây là chip bảo mật làm đúng việc của nó; thiệt hại là 1 board vài đô
  và toàn bộ bài học đã đưa vào runbook key-02.

## 8. Bài học chuỗi cung ứng (dù kết quả ra sao)

- Ảnh đã từng boot trên chip khóa là tài sản: giữ nguyên byte trong git
  (đã làm) và không bao giờ ghi đè flash chip khóa khi chưa trích được log.
