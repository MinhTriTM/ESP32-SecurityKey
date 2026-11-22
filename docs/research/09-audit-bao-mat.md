# 09 — Kiểm toán bảo mật code tự viết và bản vá (2026-11-22)

> Phạm vi: mọi code tự viết trong repo (không audit pico-fido, ESP-IDF,
> Arduino core, thư viện pip). Phương pháp: đọc toàn bộ từng file, quét mẫu
> nguy hiểm (`assert` kiểm validation, `except:` trần, `shell=True`, `pickle`,
> `eval`, `innerHTML`, `random` không-crypto), dựng proof-of-concept cho lỗi
> nghiêm trọng, vá kèm test hồi quy, chạy lại toàn bộ self-test.

## 1. Bảng phát hiện

Mức: C = nghiêm trọng · H = cao · M = trung bình. Trạng thái: VÁ hoặc SẠCH
(không lỗi) hoặc GHI NHẬN (thiết kế, đã ghi tài liệu).

| ID | Mức | File | Vấn đề | Trạng thái |
|----|-----|------|--------|-----------|
| S1 | C | `tools/split_secret.py` | `index=-1` cho bí mật SAI LẶNG; thiếu param văng KeyError; `index=300` văng IndexError (U032 P1–P3) | VÁ |
| F1 | H | `tools/fido_check.py` | CBOR key không băm được văng TypeError (U024) | VÁ |
| F2 | H | `tools/fido_check.py` | CBOR đệ quy không giới hạn → RecursionError (U025) | VÁ |
| F3 | H | `tools/fido_check.py` | CBOR bytes/text cụt im lặng, rác đuôi bị bỏ qua (U026) | VÁ |
| Q2 | H | `tools/pqc.py` | `--prefix ../` ghi file ra ngoài thư mục (U029) | VÁ |
| M7 | H | `tools/mnemonic.py` | Cụm từ qua argv lộ vào shell history/process list | VÁ |
| WEB1 | H | `web/index.html` | Tải esptool-js từ CDN không kiểm toàn vẹn | VÁ |
| WEB0 | H | `web/index.html` | Đoạn JS thừa sau `</html>` hiện rác trên trang | VÁ |
| F4 | M | `tools/fido_check.py`, `tools/hid_echo.py` | `assert` kiểm validation, mất tác dụng dưới `python -O` (U028) | VÁ |
| F5 | M | `tools/fido_check.py` | Không kiểm CID kỳ vọng, không giới hạn cỡ message (U027) | VÁ |
| F6 | M | `tools/fido_check.py` | `fragment` cho message tới 64KB, vượt 7609 chuẩn CTAPHID | VÁ |
| F9 | M | `tools/fido_check.py` | Text CBOR sai UTF-8 văng UnicodeDecodeError | VÁ |
| F12 | M | `tools/fido_check.py` | `--index` âm lách qua list index | VÁ |
| H1 | M | `tools/hid_echo.py` | Bắt nhầm thiết bị 0xFF00 lạ đầu tiên thấy (U030) | VÁ |
| H2 | M | `tools/hid_echo.py` | Không kiểm report ID trả về (U030) | VÁ |
| S3/V2/Q1/M6 | M | split/mnemonic/vault/pqc | File bí mật ghi world-readable (U029) | VÁ |
| S7/M5/Q3 | M | split/mnemonic/pqc | Thiếu mkdir cha + OSError traceback ở lệnh `qr`/ghi file (U034) | VÁ |
| V1 | M | `tools/vault.py` | Gộp két rỗng/cụt/sai pass; bắt `Exception` trần (U033) | VÁ |
| M1/M2 | M | `tools/mnemonic.py` | `seed` văng traceback khi cụm hỏng; input rỗng đếm "nhận 1" (U031) | VÁ |
| HW1 | M | `firmware/hwtest/hwtest.ino` | Đua buffer HID echo + nuốt lỗi gửi (FIX-177, U013) | VÁ |
| U014 | M | `firmware/hwtest/hwtest.ino` | Chưa chặn biên dịch nhầm board không phải S3 | VÁ |
| REQ | M | `tools/requirements*.txt` | Chưa ghim phiên bản, lib trôi theo thời gian (U088) | VÁ |
| F8/F11 | thấp | `tools/fido_check.py` | `not cmd & 0x80` khó đọc; FakeDevice kẹp biên | VÁ |
| S4 | — | `tools/split_secret.py` | In bí mật ra stdout (thiết kế, đã có `--out`) | GHI NHẬN |
| V3 | — | `tools/vault.py` | `--password-file` đọc nguyên byte | GHI NHẬN |
| KANZO | — | `tools/kanzo.py` | HTTP trên tailnet nội bộ, có timeout + retry đúng | SẠCH |
| DASH | — | `dashboard/template.html` | Mọi dữ liệu agent qua `esc()` trước `innerHTML` | SẠCH |
| ML | — | `tools/ml_distinguisher.py` | Nghiên cứu thuần, không pickle/mạng/file lạ | SẠCH |
| KEYS | — | toàn repo | Không có khóa riêng tư/secret nào bị commit | SẠCH |

## 2. Bản vá theo file

- `tools/secureio.py` (mới): ghi nguyên tử + tự tạo thư mục cha + chmod 0600
  trên POSIX cho file bí mật, chặn tên lách thư mục, đọc giới hạn 64 MB.
  Mọi tool ghi file bí mật chuyển qua module này (S3/V2/Q1/M6, S7/M5/Q3).
- `tools/split_secret.py`: `_check_coords` chặn x ngoài 1..255 và k/n sai ở
  cả `parse_share` lẫn `combine`; header thiếu/trùng/không-số bị từ chối
  sạch; share ghi 0600; `qr` tự tạo thư mục cha và bọc OSError/Unicode (S1).
- `tools/mnemonic.py`: input rỗng đếm đúng 0 từ; `seed` cảnh báo khi cụm
  hỏng; cụm từ nhận qua `--from-file`/stdin, đối số còn lại nhưng cảnh báo
  lộ history; entropy ghi 0600; `qr` bọc OSError (M1/M2/M7).
- `tools/vault.py`: tách két rỗng / két cụt / sai mật khẩu; chỉ bắt
  InvalidTag cho lỗi xác thực; két giải mã ghi 0600; đọc giới hạn cỡ (V1).
- `tools/fido_check.py`: CBOR giới hạn sâu 32, chặn key không băm được,
  bytes/text cụt, UTF-8 sai, rác đuôi GetInfo; `assert` thành ValueError;
  `recv_msg` kiểm CID kỳ vọng + giới hạn 7609 byte; `fragment` chặn vượt
  chuẩn; `--index` âm bị từ chối (F1–F6, F9, F12, F4, F8, F11).
- `tools/hid_echo.py`: `select_device` lọc VID/PID + `--index`, liệt kê mọi
  ứng viên; kiểm report ID và độ dài echo (H1/H2, F4).
- `tools/pqc.py`: chặn tiền tố lách thư mục; `.sk`/shared secret ghi 0600;
  đường ghi tự tạo thư mục cha; self-test thêm vòng CLI keygen→encap→decap
  trong thư mục tạm (Q2, Q1, Q3).
- `tools/cborx.py` (mới): codec CBOR dùng chung cho CTAP2 (giải + mã),
  `fido_check` chuyển sang dùng; fuzz 3000 ca gieo seed trong self-test.
- `tools/keymgr.py` (mới, U036): `list/status/attest/provision/reset/doctor`
  dùng chung framing `fido_check`; reset cần `--yes` + `--confirm RESET` +
  rút cắm lại; provision ghi sổ an toàn (không ghi đè MAC); self-test
  offline bằng key giả.
- `tools/web_firmware.py`: thêm `--check` đối chiếu bin với manifest, nối
  vào `run_tests` và `keymgr doctor`.
- `firmware/hwtest/hwtest.ino`: critical section cho buffer echo hai chiều,
  log rõ khi gửi thất bại, chặn biên dịch nhầm board (đặt sau `#include`
  vì macro CONFIG_* chỉ có khi sdkconfig đã nạp). Build sạch cả OTG
  (372853 byte) và HWCDC (302765 byte).
- `web/index.html`: xóa đoạn JS thừa sau `</html>`; esptool-js tải về kiểm
  SHA-384 ghim sẵn rồi mới import qua blob URL (hai CDN cùng một bản
  179662 byte) (WEB0, WEB1).
- `tools/requirements*.txt`: ghim `==` đúng bản đã kiểm + bổ sung numpy
  (REQ, U088).

## 3. Rủi ro còn lại (không vá trong đợt này)

- Chưa nạp và chạy thật trên board: HID/FIDO end-to-end (U037), HID echo
  thật, monitor serial thật. Mọi test mới đều qua key giả và kiểm tra logic.
- `combine` in bí mật ra stdout theo thiết kế (có `--out` để tránh).
- `vault --password-file` đọc nguyên byte: file thừa xuống dòng cuối là sai
  mật khẩu — đã ghi rõ trong code và help.
- `kanzo` dùng HTTP trên tailnet nội bộ: chấp nhận được cho tool nội bộ,
  không dùng cho dữ liệu bí mật.
- Web nạp cần mạng lần đầu để tải esptool-js (đã có kiểm SHA-384).
- pico-fido, ESP-IDF, Arduino core và thư viện pip nằm ngoài phạm vi audit.

## 4. Đối chiếu U-list

Đóng hoàn toàn: U029 (trừ CLI self-test đã thêm), U030, U031, U032, U033,
U034, U036, U079. Đóng một phần: U088 (đã ghim, còn vé bump), U010/U011
(liên quan OTA/reset, còn việc firmware), U049 (threat model cập nhật một
phần qua file này). Mở: U037 (cần board thật).

## 5. Kiểm chứng (2026-11-22, máy này)

- `scripts/run_tests.ps1`: PASS toàn bộ 13 self-test
  (`secureio`, `cborx`, `fido_check`, `hid_echo`, `split_secret`, `mnemonic`,
  `vault`, `pqc`, `keymgr`, `ml_distinguisher`, `kanzo`, `vien_nhip_tim`,
  `vien_cong`) + `web_firmware --check` (2/2 bin SHA-256 khớp), exit 0.
- Mỗi lỗi S1/F1–F3/Q2/M7/M1/M2/V1/H1/H2 đều có vector hồi quy trong
  self-test của đúng file đó (chạy `python tools/<file>.py --self-test`).
- `arduino-cli` biên dịch sạch hwtest sau vá cả 2 biến thể OTG/HWCDC;
  bin gộp chứa chuỗi log mới (`gui that bai`), chứng tỏ đúng bản đã vá.
- Web nạp: JS qua `node --check`, 30/30 id giao diện khớp code, `</html>`
  duy nhất, SHA-384 CDN ghim từ bản tải thật (2 CDN cùng hash).
- Quy mô code (không tính `.tooling`, build, sổ Viện, dashboard sinh):
  xem `CHANGELOG.md` đợt này; đo bằng quét `*.py/*.ino/*.ps1/*.sh/*.md/
  *.html/*.json/*.rs/*.toml` trừ thư mục loại.

## 6. Đợt mở rộng 2 (cùng ngày, sau khi bản vá đã PASS)

- `tools/lintsec.py` (mới): quét AST — except trần, assert ngoài test,
  shell=True, os.system, eval/exec, pickle, random không-crypto (lỗi);
  open() thiếu encoding và hằng secret (cảnh báo). Self-test gồm 17 mẫu
  luật + tự quét `tools/` phải sạch lỗi. Để luật `assert` nghiêm, đã đổi
  4 assert còn lại ngoài test thành ValueError (`split_secret._build_tables`,
  `vien_dashboard.main` ×3, cùng điều kiện nên không đổi hành vi).
- `keymgr pin-retries`: đọc số lần thử PIN còn lại qua CTAP2 clientPIN
  getRetries (mã hóa tham số bằng `cborx`), kèm test trên key giả (U004).
- `keymgr backup-check`: kiểm tra bộ sao lưu không cần mở bí mật — share
  cùng lần chia + đủ ngưỡng, két đúng định dạng, cụm từ checksum đúng;
  kèm test đủ/thiếu/hỏng/trống (U054/U057).
- `vault rekey`: đổi mật khẩu két + test (mật khẩu mới mở được, cũ hết
  tác dụng, sai mật khẩu cũ thì hỏng) (U043).
- `run_tests` chạy thêm `lintsec` (14 self-test + manifest check).
