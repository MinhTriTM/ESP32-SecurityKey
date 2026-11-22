# Changelog

Mọi thay đổi đáng chú ý của dự án ESP32-S3 Security Key.
Quy ước mã thoát: 0 xong · 1 lỗi chạy · 2 sai cách dùng (bảng NCKH-052).

## 2026-11-22 — Build pico-fido v8.2 kiểm chứng (U001, U002, U053)

- Build thành công từ commit đã ghim bằng ESP-IDF v5.5.1 trong `.tooling`:
  bản thử (799200 byte) và bản chốt ký RSA-3072 + Flash Encryption release
  (856064 byte). Chữ ký V2 hợp lệ cho cả app và bootloader
  (`espsecure verify_signature`). Hai bản đều có trong web nạp + manifest.
- `tools/gen_sign_key.py` sinh khóa ký ngoại tuyến (RSA-3072, `keys/`, không
  commit); `config/sdkconfig.hardened` chốt cấu hình bản phát hành.
- `scripts/build_pico_fido.*` build lặp lại được cả 2 bản (kèm workaround
  CMake backslash Windows); `scripts/lockdown_key.*` là danh mục khóa chip
  có hướng dẫn, chỉ đọc eFuse, không tự đốt fuse nào.
- Ghi nhận khi build: USB VID/PID `0x2E8A:0x10FE`, flash config 4 MB trên
  board 16 MB, bảng phân vùng bản ký dời lên `0x10000` (chi tiết ở
  `docs/04-firmware.md`).

## 2026-11-22 — Đợt kiểm toán bảo mật và mở rộng

### Vá bảo mật (mỗi lỗi kèm test hồi quy trong self-test)

- S1 (nghiêm trọng): `split_secret` chặn chỉ số share ngoài 1..255 và
  thiếu/sai tham số header — trước đây `index=-1` cho ra bí mật SAI LẶNG,
  thiếu param văng KeyError, `index=300` văng IndexError (U032 P1–P3).
- F1/F2/F3: `fido_check` cứng hóa CBOR — key không băm được, lồng sâu quá 32
  tầng, bytes/text cụt, text sai UTF-8 và rác đuôi GetInfo đều bị từ chối
  sạch bằng ValueError (U024–U026).
- F4: thay `assert` kiểm validation bằng ValueError trong `fido_check` và
  `hid_echo` (assert mất tác dụng dưới `python -O`) (U028).
- F5/F6/F7: `recv_msg` kiểm CID kỳ vọng, giới hạn message 7609 byte chuẩn
  CTAPHID; `fragment` chặn message vượt chuẩn (U027).
- F9/F12: `--index` âm bị từ chối; FakeDevice kẹp biên gói nối.
- H1/H2: `hid_echo` liệt kê mọi thiết bị 0xFF00, chọn bằng `--index` và lọc
  `--vid`/`--pid`, kiểm report ID trả về (U030).
- Q2: `pqc keygen` chặn tiền tố lách thư mục (`../`, phân cách) (U029).
- M7: `mnemonic` nhận cụm từ qua `--from-file`/stdin, đối số còn lại nhưng
  cảnh báo lộ vào shell history.
- M1/M2: `seed` cảnh báo khi cụm hỏng thay vì văng traceback; input rỗng đếm
  đúng 0 từ (U031).
- V1: `vault` tách thông điệp két rỗng / két cụt / sai mật khẩu, chỉ bắt
  InvalidTag cho lỗi xác thực (U033).
- S3/V2/Q1/M6: file bí mật (share, entropy, két giải mã, khóa PQC, shared
  secret) ghi nguyên tử + chmod 0600 trên POSIX, qua module `secureio` mới.
- S7/M5/Q3: lệnh `qr` và đường ghi file tự tạo thư mục cha, bọc OSError
  sạch (U034).
- HW1: `hwtest` khóa critical section cho buffer HID echo, log rõ khi gửi
  thất bại (hết nuốt lỗi), chặn biên dịch nhầm board không phải S3
  (FIX-177, U013, U014).
- WEB0: xóa đoạn JS thừa sau `</html>` trong web nạp (trình duyệt hiện rác).

### Thêm mới

- `tools/secureio.py`: ghi file nguyên tử + 0600, chặn tên lách thư mục,
  đọc giới hạn cỡ, kèm self-test. Mọi tool ghi file bí mật đều dùng chung.
- `tools/cborx.py`: codec CBOR dùng chung (giải + mã), `fido_check` chuyển
  sang dùng; self-test gồm round-trip, từ chối sạch và fuzz 3000 ca seed.
- `tools/lintsec.py`: máy quét tĩnh cho `tools/*.py` (except trần, assert
  ngoài test, shell=True, eval/exec, pickle, random không-crypto) + tự quét
  toàn cây; nối vào `run_tests`.
- `keymgr` thêm `pin-retries` (số lần thử PIN còn lại qua clientPIN) và
  `backup-check` (đồng bộ share, định dạng két, checksum cụm từ).
- `vault rekey`: đổi mật khẩu két (mở bằng cũ, mã hóa lại bằng mới).
- `tools/keymgr.py` (U036): quản lý key hợp nhất — `list`, `status`,
  `attest`, `provision` (ghi sổ `hardware/keys.md`), `reset` có 2 lớp xác
  nhận, `doctor` kiểm tra môi trường. Self-test offline bằng key giả.
- `tools/web_firmware.py --check`: đối chiếu bin trên đĩa với manifest
  (tồn tại + cỡ + SHA-256), đã nối vào `run_tests`.
- File CHANGELOG này (U079).

### Thay đổi

- Ghim phiên bản thư viện đúng bản đã kiểm (vé bump U088): hidapi 0.15.0,
  numpy 2.5.4, liboqs-python 0.16.0.2, cryptography 50.0.2, qrcode 8.2,
  pillow 13.0.0. `requirements.txt` bổ sung numpy cho `ml_distinguisher`.
- `run_tests` chạy thêm `secureio`, `cborx`, `keymgr` và `web_firmware --check`.
- `vault --password-file` đọc nguyên byte (kể cả xuống dòng cuối), đã ghi rõ.

### Không lỗi sau khi rà soát

- `dashboard/template.html`: mọi dữ liệu agent đều qua `esc()` trước khi
  `innerHTML` — không XSS.
- `tools/kanzo.py`, `tools/ml_distinguisher.py`: không phát hiện lỗi bảo mật.
- Quét toàn repo: không có khóa riêng tư hay secret nào bị commit.
