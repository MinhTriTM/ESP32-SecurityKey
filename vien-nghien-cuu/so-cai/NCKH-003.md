# Sổ cái NCKH-003 (nhóm firmware, nhóm trưởng, đợt 1)

> Tên theo `phan-cong.json`: Lê An. Objective gọi "Lê Cường" — lệch tên, cần Viện trưởng chốt
> (xem mục unresolved). Dưới đây ký theo mã NCKH-003.

## 2026-11-21 01:30 — nhận việc

- Thẻ: [firmware] Rà soát hwtest.ino (Kanzo id 140)
- Việc nhận (theo `phan-cong.json` + objective): đọc toàn bộ `firmware/hwtest/hwtest.ino`,
  kiểm logic nút BOOT / LED / HID echo, race condition `echoPending`, tràn bộ đệm,
  đối chiếu descriptor HID với `tools/hid_echo.py`.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`,
  mục NCKH-003 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, `vien-nghien-cuu/NHIP-TIM.md`,
  `firmware/hwtest/hwtest.ino` (154 dòng, toàn bộ),
  `firmware/hwtest/README.md`, `tools/hid_echo.py` (đối chiếu).
- Chế độ: REPO CHỈ ĐỌC — không sửa firmware, chỉ ghi sổ cái này.
- Trạng thái: todo -> doing (Kanzo nghẽn, xem mục "đồng bộ Kanzo").

## 2026-11-21 01:35 — báo cáo rà soát hwtest.ino

### Kết luận nhanh

- Descriptor HID: ĐÚNG, khớp `tools/hid_echo.py` (vendor page 0xFF00, report ID 1,
  64 byte IN + 64 byte OUT).
- Tràn bộ đệm `echoBuf`: KHÔNG THẤY — code đã clamp `min(len, 64)` + zero-pad.
- Race condition `echoPending`/`echoBuf`: CÓ, là phát hiện chính (mất echo hoặc
  frame rách khi host gửi OUT dồn dập).
- Lỗi nuốt lặng: `SendReport()` thất bại thì mất echo không dấu vết.
- Nút/LED/heartbeat: đúng về cơ bản, thiếu debounce tường minh.

### P1 — Race giữa `_onOutput()` (ngữ cảnh USB) và `loop()` (dòng 53-61, 146-151)

```cpp
// USB context:
memcpy(echoBuf, buffer, n); ... echoPending = true;
// loop():
if (echoPending && HID.ready()) { echoPending = false; HID.SendReport(1, echoBuf, 64); }
```

- `volatile bool` chỉ ngăn cache compiler, KHÔNG làm chuỗi
  check-then-clear thành nguyên tử, và không rào chắn bộ nhớ giữa 2 core ESP32-S3.
- Kịch bản A (mất echo): OUT mới đến xen giữa lúc `loop()` đọc `echoPending==true`
  và lúc gán `false` → cờ của frame mới bị xóa, frame mới không bao giờ được gửi
  cho tới OUT kế tiếp. Tool `hid_echo.py` timeout 2s sẽ báo "Thiết bị không trả lời".
- Kịch bản B (frame rách + gửi trùng): OUT mới đến sau khi xóa cờ nhưng trước/during
  `SendReport()` → `SendReport` đọc `echoBuf` đang bị `memcpy` ghi dở (xé frame),
  đồng thời cờ còn `true` nên vòng sau gửi trùng frame mới.
- Coalescing: nhiều OUT trước khi `loop()` kịp ăn (chu kỳ 20ms) thì chỉ frame cuối
  sống sót, các frame giữa mất lặng. Với test đơn 60 byte hiện tại thì không sao,
  nhưng phải ghi rõ vào tài liệu, không được coi là echo đáng tin cậy.
- Sửa đề xuất (không sửa trong nhiệm vụ chỉ đọc này): vùng cấm ngắt / `portMUX`
  quanh cặp (copy `echoBuf` ra bản cục bộ + xóa cờ), rồi `SendReport` từ bản cục bộ;
  hoặc hàng đợi 2 ngăn (double-buffer). Đồng thời log khi ghi đè frame chưa kịp gửi.

### P1 — `SendReport()` thất bại bị nuốt lặng (dòng 146-151)

- `echoPending` đã xóa TRƯỚC khi gửi; nếu `SendReport()` trả `false` thì frame mất,
  không log, không thử lại, host chỉ thấy timeout.
- Sửa đề xuất: nếu `SendReport()` false thì đặt lại `echoPending = true` (thử lại
  vòng sau) và `Serial.println` cảnh báo. Hiện nhánh else trống.

### P2 — `_onOutput()` bỏ qua `report_id` (dòng 53-54)

- `(void)report_id;` chấp nhận mọi report ID. Hiện tại descriptor chỉ định nghĩa
  ID 1 nên vô hại, nhưng nếu sau này thêm Feature report (FIDO cần) thì echo nhầm.
- Sửa đề xuất: `if (report_id != 1) return;`.

### P2 — Nút BOOT không debounce tường minh (dòng 129-138)

- Phát hiện cạnh `pressed && !lastPressed` đúng, `INPUT_PULLUP` + nhấn mức LOW đúng,
  nhưng chống dội chỉ nhờ `delay(20)` một cách tình cờ. Bounce dài vẫn gây log
  "nhan/nha" trùng.
- Sửa đề xuất: yêu cầu trạng thái ổn định ~30-50ms mới chốt cạnh.

### P2 — `_onGetDescriptor()` memcpy không kiểm tra đích (dòng 48-51)

- `memcpy(buffer, echo_report_descriptor, 36)` giả định framework luôn cấp buffer
  ≥ 36 byte. Theo API Arduino-ESP32 thì đúng trong thực tế, nhưng nếu host xin
  descriptor rút gọn (wLength nhỏ) thì có nguy cơ ghi quá. Rủi ro thấp, ghi nhận
  để NCKH-009 (kiểm descriptor độc lập) đối chiếu thêm.

### P3 — Góp ý nhỏ

- LED không phản hồi HID echo: chỉ có log serial. Nên chớp LED mỗi lần echo để
  debug không cần Serial Monitor.
- `Serial.printf("...heap %d\n", ESP.getFreeHeap())` (dòng 142): `%d` cho `uint32_t`,
  nên dùng `%u` (thực tế heap < 2GB nên chưa sai).
- Constructor `EchoHIDDevice` dùng `static bool initialized` chống add 2 lần:
  instance thứ hai (nếu có) lặng lẽ không hoạt động. Hiện chỉ 1 instance nên ổn.
- PlatformIO: `ARDUINO_USB_MODE` có thể undefined → HID bị biên dịch loại, chỉ in
  "HID echo: TAT". `firmware/hwtest/README.md` chưa cho cờ tương đương
  `ARDUINO_USB_MODE=0` cho PlatformIO — người dùng PIO dễ tưởng echo hỏng.
  (Thuộc runbook NCKH-015/NCKH-021, ghi ở đây để khỏi rơi.)

### Đối chiếu descriptor từng byte — KẾT LUẬN ĐÚNG

| Byte | Ý nghĩa | Nhận xét |
|---|---|---|
| `06 00 FF` | Usage Page vendor 0xFF00 | đúng, little-endian |
| `09 01`, `A1 01` | Usage 0x01, Collection Application | đúng |
| `85 01` | Report ID 1 | khớp `REPORT_ID = 1` trong hid_echo.py |
| `09 02`, `15 00`, `26 FF 00` | Usage IN, Logical 0..255 | đúng |
| `75 08`, `95 40` | Report Size 8, Count 64 | = 64 byte, khớp `REPORT_LEN = 64` |
| `81 02` | Input (Data,Var,Abs) | đúng |
| `09 03` ... `91 02` | Usage OUT, 64 byte Output | đúng, đối xứng IN |
| `C0` | End Collection | đúng, tổng 36 byte |

- IN và OUT chung Report ID 1 là hợp lệ với HID; host Windows/Linux/macOS chấp nhận.
- `hid_echo.py` gửi 60 byte ngẫu nhiên + pad 0 lên 64 (`build_report`), firmware
  zero-pad OUT ngắn lên 64 rồi echo đủ 64, tool so 60 byte đầu → nhất quán cả hai đầu.
- OUT dài hơn 64 (trái descriptor) bị cắt an toàn, không tràn.

### Đối chiếu logic nút/LED/heartbeat

- BOOT (GPIO0, `INPUT_PULLUP`, nhấn = LOW): đúng với DevKit; log "nhan/nha" theo cạnh.
- LED: `RGB_BUILTIN` → `neopixelWrite` (không cần `pinMode`, đúng S3-GPIO48);
  ngược lại `LED_BUILTIN` → digital; đều có `pinMode OUTPUT` đúng nhánh. Màu:
  xanh lá chờ (0,32,0), xanh dương khi nhấn (0,0,64) — khớp README.
- Heartbeat `millis() - lastPrint > 5000`: an toàn tràn `millis()` (số học unsigned).
- `while (!Serial && ... < 3000)`: chờ CDC tối đa 3s, không treo khi không có host. Đúng.
- Thứ tự `HID.addDevice` (global init) → `HID.begin()` → `USB.begin()`: đúng mẫu Arduino.
- `delay(20)`: độ trễ echo ≤ ~20ms, trong timeout 2000ms của tool. Ổn.

### Tự kiểm (repo chỉ đọc, không build)

- Đọc toàn bộ 154 dòng `hwtest.ino` + `hid_echo.py` + README: đã xong.
- Parse descriptor thủ công từng byte, đối chiếu `REPORT_ID`/`REPORT_LEN`/`PAYLOAD_LEN`:
  khớp, xem bảng trên.
- Không chạy build Arduino (ngoài phạm vi chỉ đọc + không có toolchain yêu cầu);
  không sửa file nguồn nào. Cần kiểm định viên biên dịch 2 chế độ OTG/HWCDC
  (việc của NCKH-012) để xác nhận `#if ARDUINO_USB_MODE` hai nhánh đều qua.

### Trạng thái

- doing -> review (Kanzo nghẽn, xem mục "đồng bộ Kanzo").

## Đồng bộ Kanzo (opportunistic, thẻ id 140)

- Công cụ shell (`muse.powershell`) của agent này báo lỗi `program not found` ở cả
  2 lần thử (liệt kê thư mục + probe `Write-Output`, đã dừng đúng giới hạn 2 lần
  thử lại), nên không gọi được `Invoke-RestMethod` tới
  `http://100.101.100.100:4242/api` từ phiên này.
- Đã tuân thủ "file trước bảng sau": toàn bộ nhật ký nằm ở file này.
- Nhờ Viện trưởng / nhịp tim đối chiếu giúp: thẻ 140 todo -> doing -> review kèm
  nội dung báo cáo trên. Thẻ kẹt do lỗi công cụ, không phải do việc khó —
  xin đừng gọi oan theo luật NHIP-TIM.md mục 5.

## Unresolved

1. Lệch tên: objective ghi "Lê Cường", `phan-cong.json` ghi NCKH-003 = "Lê An".
   Cần Viện trưởng chốt tên duy nhất theo Hiến chương §1.
2. Kanzo chưa đồng bộ được từ phiên này (shell hỏng, xem trên). Cần Viện trưởng vá bảng.
3. Race `echoPending` và các sửa P1/P2: mới ở mức đề xuất, chưa có bản vá
   (ngoài phạm vi nhiệm vụ chỉ đọc). Đề nghị mở thẻ follow-up cho nhóm firmware.
4. Chưa kiểm chứng runtime trên board thật (không có phần cứng trong phiên này);
   kịch bản A/B mới là phân tích tĩnh, cần NCKH-012/NCKH-016 bắn OUT dồn dập để xác nhận.

## 2026-11-21 01:39 — kiểm chéo thẻ 143 của NCKH-010 (người kiểm: NCKH-003 Lê An)

- Thẻ: [tooling] Fuzz cbor_decode (Kanzo id 143), tác giả Bùi An (NCKH-010).
- Phạm vi: kiểm độc lập báo cáo fuzz 5639 case (TypeError unhashable,
  RecursionError, cụt thân nuốt im). REPO CHỈ ĐỌC, không git commit.
- Tài liệu đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-010.md` (mục nhận việc,
  báo cáo fuzz, đồng bộ Kanzo), `tools/fido_check.py` (đối chiếu dòng code).
- Phương pháp: ĐƯỜNG KHÁC — one-liner `python -c` trực tiếp, không dùng lại
  script fuzz/verify của tác giả (`fuzz_cbor_NCKH010.py`, `verify_cbor_NCKH010.py`
  không hề mở/chạy). Shell bắt buộc `shell='pwsh'`.

### Repro độc lập (lệnh đã chạy + output)

1. TypeError khóa mảng (lỗi 1/3) — ĐẠT (tái hiện):
   - `python -c "import sys; sys.path.insert(0, 'tools'); from fido_check import
     cbor_decode; cbor_decode(bytes.fromhex('a18000'))"`
     -> exit 1, `TypeError: unhashable type: 'list'` tại `fido_check.py` dòng 199
     (`mapping[key] = value`). Trùng gốc rễ tác giả nêu (nhánh major 5).
   - Biến thể độc lập (tác giả không liệt kê hex này):
     `bytes.fromhex('a1810100')` (map khóa mảng `[1]`)
     -> exit 1, `TypeError: unhashable type: 'list'` cùng dòng 199.
2. RecursionError lồng sâu (lỗi 2/3) — ĐẠT (tái hiện):
   - `python -c "...cbor_decode(b'\x81'*1200 + b'\x00')"` (độ sâu 1200,
     khác 2000/1500 của tác giả) -> exit 1,
     `RecursionError: maximum recursion depth exceeded` tại dòng 191
     (nhánh major 4 đệ quy). Khớp nhận định "ngưỡng gãy giữa 500-2000".
3. Cụt thân nuốt im (lỗi 3/3) — ĐẠT (tái hiện, cả 2 kiểu):
   - `cbor_decode(bytes.fromhex('456162'))` (bstr khai 5, thực 2)
     -> exit 0, `(b'ab', b'')`, không báo lỗi. Đúng hành vi dòng 184-185.
   - Biến thể text độc lập: `bytes.fromhex('655859')` (text khai 5, thực "XY")
     -> exit 0, `('XY', b'')`, cũng nuốt im (dòng 187).
4. UnicodeDecodeError là con của ValueError — ĐẠT (xác nhận):
   - `python -c "print(issubclass(UnicodeDecodeError, ValueError))"`
     -> `True` (Python 3.12.0, trùng môi trường tác giả).
   - Repro độc lập: `cbor_decode(bytes.fromhex('61ff'))` (text chứa 0xFF)
     -> exit 1, `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff...`
     tại dòng 187. Vì là lớp con ValueError nên `main()` dòng 447 bắt được —
     đồng ý với tác giả coi nhóm này là ĐẠT về loại.
   - (Ghi nhận thao tác thừa: lần đầu gõ nhầm `41ff` là bstr nên exit 0 không
     lỗi; sửa thành `61ff` text mới đúng. Không ảnh hưởng kết luận.)

### Đối chiếu tĩnh

- Dòng code tác giả dẫn đều đúng: `cbor_decode` 176-207, `_cbor_arg` 164-173,
  `mapping[key] = value` dòng 199, `main()` bắt
  `(CtapHidError, Ctap2Error, ValueError, TimeoutError)` dòng 447 — quả thật
  không bắt `TypeError`/`RecursionError` nên 2 nhóm crash sẽ đổ stack trace.
- Kỳ vọng "mọi crash đều là ValueError": tác giả kết luận KHÔNG ĐẠT cho code
  (30/5639 ≈ 0,53%) là trung thực; nhiệm vụ CHỈ BÁO CÁO nên đây là kết quả đúng,
  không phải lỗi của tác giả. Lỗi thuộc về `fido_check.py`, cần thẻ follow-up.

### Kết luận kiểm định

- [KIEM-DINH] đạt — báo cáo fuzz trung thực, đầy đủ bằng chứng; cả 3 phát hiện
  (TypeError, RecursionError, cụt thân) và quan hệ UnicodeDecodeError-ValueError
  đều tái hiện độc lập bằng đường khác. Đề nghị review -> done; mở thẻ follow-up
  siết `cbor_decode` (kiểm tra key hash được, giới hạn độ sâu, báo lỗi khi thân
  cụt) cho nhóm tooling.
- Trạng thái thẻ 143: review -> done (sau khi thử đồng bộ Kanzo bên dưới).

### Đồng bộ Kanzo (opportunistic, thẻ id 143) — HỎNG, Kanzo nghẽn

- Lần 1 (blind, log bị nuốt do lỗi script `Write-Output` trong function bị
  thu vào giá trị trả về, chỉ còn `KETQUA comment=System.Object[]
  move=System.Object[]`): POST comment `[KIEM-DINH] đạt...` + POST move
  `review->done`, mỗi lệnh timeout 30s, thử lại tối đa 2 lần, cách nhau 5s.
  Kết quả từng lần thử KHÔNG xác định được — lỗi của người kiểm, đã rút kinh
  nghiệm dùng `Write-Host` cho các lần sau.
- Lần 2 (xác minh, log hiển thị): `GET /api/board?project=esp32-securitykey`
  -> HỎNG `500 Internal Server Error`; `GET /api/tasks/143` -> HỎNG 500.
  Không đối chiếu được bảng, cũng không xác nhận được lần 1 có ghi lọt không.
- Lần 3 (ghi lại, mỗi lệnh 1 lần thử, cách nhau 5s, timeout 30s):
  POST comment -> HỎNG 500; POST move `done` -> HỎNG 500.
- Kết luận: Kanzo nghẽn toàn phần lúc 01:39-01:45 (đọc và ghi đều 500).
  Dừng đúng giới hạn, không thử tiếp. Khả năng trùng comment nếu lần 1 lọt
  qua là thấp (mọi request sau đều 500) nhưng không loại trừ tuyệt đối —
  nhờ Viện trưởng khi vá bảng kiểm tra trùng và xóa bản dư nếu có.
- Đã tuân thủ "file trước bảng sau": toàn bộ kiểm định nằm ở mục này.
  Nhờ Viện trưởng vá giúp: comment `[KIEM-DINH] đạt` (nội dung ở mục kết luận
  trên) + chuyển thẻ 143 review -> done.
