# Runbook provision key mới (từ chip virgin tới key dùng thật)

Quy trình chuẩn cho mọi board mới (key-02 trở đi), đúc từ bài học key-01
(xem [research/11](../docs/research/11-cuu-key-01.md)). Thứ tự các bước là
bắt buộc: đốt khóa FE trước lần boot mã hóa đầu tiên, nếu không chip tự
sinh khóa rồi giấu luôn và mất đường nạp lại.

Quy ước cổng: **COM** = cổng UART (nạp, đọc eFuse, log boot), **USB/OTG** =
cổng native (dùng FIDO). Cáp phải là cáp dữ liệu, cắm thẳng vào máy. Tốc độ
nạp 115200 cho chắc (cáp nhóm này hay rớt ở tốc độ cao).

## 0. Sinh và backup khóa (trên máy, chưa đụng board)

1. Khóa ký Secure Boot: đã có `keys/secure-boot-signing.key` (dùng chung
   mọi key). Không tạo mới.
2. Sinh khóa FE riêng cho board mới, mỗi board một chiếc:
   ```
   python tools/gen_fe_key.py --name key-02
   ```
   ra file `keys/fe-key-02.bin` (32 byte). Ghi lại vân tay SHA-256 nó in ra.
3. Backup NGAY cả hai khóa bằng vault + Shamir theo `keys/README.md`
   (in giấy, cất riêng). Mất khóa FE = mất đường nạp lại sau khi khóa chip.

## 1. Kiểm tra chip virgin

Cắm cáp COM, đọc tóm tắt eFuse (chỉ đọc, an toàn):

```
espefuse.py --port COM10 --chip esp32s3 summary
```

Kiểm tra: các `BLOCK_KEY` chưa đốt (purpose = 0), `SPI_BOOT_CRYPT_CNT = 0`,
Secure Boot chưa bật. Chip đã khóa (như key-01) thì dừng — không provision
đè lên chip cũ.

## 2. Nạp hwtest, lấy MAC, ghi sổ

1. Nạp sketch hwtest theo runbook hệ mình
   (`docs/runbook-nap-hwtest-windows.md` hoặc `-ubuntu.md`).
2. Đọc dòng `MAC: ...` trong log serial.
3. Ghi sổ:
   ```
   python tools/keymgr.py provision --name key-02 --mac <MAC> --commit 15b848d821b4995eb1b29a5c2a4c24c25d1a768e
   ```

## 3. Đốt khóa FE vào eFuse (một chiều, đọc kỹ rồi làm)

Điều kiện: vừa xong bước 2, chip vẫn virgin, file `keys/fe-key-02.bin` đã
backup. Dùng `BLOCK_KEY1` (giữ `BLOCK_KEY0` cho Secure Boot digest mà lần
boot đầu sẽ tự đốt):

```
idf.py --port COM10 efuse-burn-key BLOCK_KEY1 keys/fe-key-02.bin XTS_AES_128_KEY
```

Lệnh hỏi xác nhận 2 lần — đó là chốt an toàn, đọc kỹ tên block rồi mới gõ.
Đốt xong đọc lại `summary`: `KEY_PURPOSE_1 = XTS_AES_128_KEY`, block bị
khóa đọc/ghi. Từ đây KHÔNG cho board boot bản FE khi chưa nạp ảnh đúng.

Nguồn lệnh: `flash-encryption.rst` mục "Using Host Generated Key" trong
ESP-IDF v5.5.1 (xem `.tooling`), keysize AES-128 là default của Kconfig.

## 4. Nạp ảnh hardened, boot mã hóa lần đầu

1. Nạp file gộp đã ký ở địa chỉ `0x0` (bản thô — đúng, lần đầu nạp thô):
   - Cách dễ: siêu web nạp, gói `pico-fido-v8.2-hardened`.
   - Tay: `esptool.py --chip ESP32-S3 -p COM10 -b 115200 write_flash
     --flash_mode dio --flash_freq 80m 0x0
     web/firmware/pico-fido-v8.2/pico_fido_esp32-s3-hardened.bin`
2. Nhấn RST (hoặc rút cắm lại). Lần boot đầu bootloader tự: dùng khóa FE đã
   đốt (bỏ qua tự sinh), mã hóa tại chỗ bootloader + app + part0 có cờ
   (mất tới ~1 phút, đèn có thể đứng yên), đốt digest Secure Boot, tắt
   JTAG, bật Secure Download Mode.
3. **Tuyệt đối không rút điện giữa lần boot đầu.** Hỏng giữa chừng là phải
   làm lại từ ảnh pre-encrypt (mục 7).

## 5. Kiểm chứng (cáp USB/OTG)

1. Đổi sang cổng USB, đợi máy nhận HID FIDO.
2. Chạy kiểm tra 3 tầng, phải PASS cả 3:
   ```
   python tools/fido_check.py
   ```
3. Đăng ký + đăng nhập thử trên webauthn.io (tài khoản phụ), đặt PIN FIDO.
4. Chỉ khi cả 3 đạt mới sang bước tiếp theo.

## 6. Khóa vật lý và đưa vào dùng thật

1. Bịt cổng COM về mặt vật lý (vỏ chỉ chừa cổng OTG + lỗ nút BOOT).
2. KHÔNG đốt `DIS_DOWNLOAD_MODE`: giữ cổng nạp cho đường cứu hộ (kẻ xấu
   cầm board cũng không nạp được gì vì secure download + ảnh phải ký +
   phải mã hóa đúng khóa FE).
3. Đăng ký key vào dịch vụ thật (mỗi tài khoản quan trọng đủ 2 key),
   cập nhật cột dịch vụ trong `hardware/keys.md`.

## 7. Nạp lại sau này (update / cứu hộ)

Chip đã khóa chỉ nhận ảnh **vừa ký đúng khóa RSA vừa mã hóa đúng khóa FE**.
Không bao giờ `--force` bản thô (bài học key-01: gạch boot vĩnh viễn).
Quy trình:

```
powershell -ExecutionPolicy Bypass -File scripts/preencrypt_rescue.ps1 -FeKey keys/fe-key-02.bin
```

Script mã hóa trước ảnh hardened bằng khóa FE rồi in đúng lệnh `write_flash`
(`--force --no-stub`) để chạy. Chi tiết trong đầu file script.
