# Sổ cái NCKH-009 — Đặng An (nhóm firmware, thành viên Viện, đợt 1)

> Viện trưởng đính chính: tên chính thức là Đặng An (giao việc ban đầu ghi nhầm
> "Đặng Hùng"). Mã NCKH-009 giữ nguyên.

## 2026-11-21 01:29 — nhận việc
- Thẻ: kiểm descriptor HID độc lập (Kanzo id 148)
- Trạng thái: todo -> doing
- Đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-009 trong
  `vien-nghien-cuu/phan-cong.json`, `vien-nghien-cuu/so-cai/README.md`,
  `firmware/hwtest/hwtest.ino`, `tools/hid_echo.py`.
- Repo chỉ đọc; script riêng đặt trong `$env:TEMP`, không commit.

## 2026-11-21 01:30 — báo cáo
- Đã làm: tự viết script riêng `C:\Users\user\AppData\Local\Temp\nckh009_hid_parse.py`
  (không dùng lại code repo) — đọc `firmware/hwtest/hwtest.ino`, trích mảng
  `echo_report_descriptor`, parse từng byte theo HID (prefix tag/type/size),
  đối chiếu report ID / usage page / độ dài IN-OUT với code `.ino` và
  `tools/hid_echo.py`.
- Tự kiểm:
  - `python $env:TEMP\nckh009_hid_parse.py` -> exit 0, "KET LUAN: TAT CA KHOP"
    (descriptor 36 byte; Usage Page 0xFF00; Report ID 1; 1 Input + 1 Output,
    mỗi chiều Report Size 8 x Report Count 64 = 64 byte; khớp `echoBuf[64]`,
    `SendReport(1, echoBuf, sizeof(echoBuf))`, comment dòng 13-14 và chuỗi
    Serial dòng 122; khớp `hid_echo.py`: ECHO_USAGE_PAGE=0xFF00, REPORT_ID=1,
    REPORT_LEN=64, PAYLOAD_LEN=60 <= 64, `build_report` 1+64 byte,
    `device.read(REPORT_LEN + 1)`).
  - `python tools/hid_echo.py --self-test` -> exit 0,
    "self-test ok: đóng gói report HID echo đúng."
- Kết luận: KHỚP toàn bộ — descriptor, firmware và tool thống nhất
  (vendor page 0xFF00, report ID 1, 64 byte IN/OUT). Không phát hiện lệch.
- Ghi chú `_onOutput` bỏ qua `report_id` (`(void)report_id`): chấp nhận được vì
  descriptor chỉ định nghĩa đúng 1 Report ID.
- Trạng thái: doing -> review (mục tiêu; Kanzo chưa nhận, xem dưới)
- Kanzo: xem mục đồng bộ bên dưới (API nghẽn, opportunistic).

## 2026-11-21 01:35 — đồng bộ Kanzo (opportunistic, thẻ id 148)
- `POST /api/tasks/148/move {"status":"doing"}` -> OK (status doing).
- `POST /api/tasks/148/move {"status":"review"}` -> timeout 30s (lần 1), rồi
  `database is locked` (lần 2 và 3 = hết 2 lần thử lại). Dừng theo luật.
- `POST /api/tasks/148/comments` (báo cáo) -> `database is locked`. Dừng.
- Mỗi lệnh cách nhau 5s, shell pwsh. Thẻ hiện ở `doing` trên server
  (chưa xác minh lại được vì Kanzo nghẽn). Viện trưởng đối chiếu và vá khi
  Kanzo sống lại: cần move 148 doing -> review + comment báo cáo ở trên.
- Unresolved: đồng bộ Kanzo chưa xong; nội dung báo cáo đầy đủ nằm ở sổ này.

## 2026-11-21 01:41 — kiểm chéo thẻ 141 của NCKH-004 Phạm An (người kiểm: NCKH-009 Đặng An)

- Vai trò lượt này: Đặng An (NCKH-009), nhóm firmware, KIỂM CHÉO đợt 1
  (khác nhóm với tác giả tooling). REPO CHỈ ĐỌC, không git commit.
- Đối tượng kiểm: thẻ [tooling] Rà soát fido_check đường lỗi (Kanzo id 141),
  báo cáo trong `vien-nghien-cuu/so-cai/NCKH-004.md` mục 01:32 (F1 CID,
  F2 ERROR giữa chừng, F3 seq wrap, F5 nhãn sai, F6 nuốt lỗi, F8 assert).
- Đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-004.md`, toàn bộ
  `tools/fido_check.py` (463 dòng, để chọn đường kiểm khác).
- Phương pháp: ĐƯỜNG KHÁC — tự viết probe riêng
  `C:\Users\user\AppData\Local\Temp\nckh009_kiemcheo_141.py` (class `HangGia`
  tự chế, input tự chọn, không mở/chạy probe của tác giả — tác giả cũng chỉ
  công bố output chứ không nộp script). Shell bắt buộc `shell='pwsh'`,
  chạy `python -B` (không ghi repo, không sinh `__pycache__`).

### Kết quả từng phát hiện (input độc lập trong ngoặc)

1. F1 (CID gói ĐẦU không kiểm) — XÁC NHẬN.
   - `ctap2_get_info(dev, cid_req=0x0A0B0C0D)` vẫn trả ok khi key đáp bằng
     `cid_rep=0xDEADBEEF` (sai CID vẫn chấp nhận, `versions` đúng).
   - Đối chiếu tĩnh: cả 3 caller (`main` nhánh INIT/PING dòng 416/429/437,
     `ctap2_get_info` dòng 213) đều dùng `_` bỏ CID `recv_msg` trả về.
2. F2 (ERROR/init giữa chừng báo nhầm thứ tự) — XÁC NHẬN (2 biến thể mới).
   - F2a: gói INIT PING mới (`0x81`=129) giữa chừng (tác giả dùng ERROR 191)
     -> `ValueError: gói nối sai thứ tự (muốn 0, thấy 129)`.
   - F2b: ERROR `CHANNEL_BUSY (0x06)` ở seq=1 sau 1 gói nối đúng (tác giả thử
     ở seq=0) -> `ValueError: ... (muốn 1, thấy 191)`, mất `CtapHidError 0x06`.
   - Cùng gốc rễ: `recv_msg` dòng 140-143 không tách gói INIT (`bit 0x80`)
     trước khi so CID/seq.
3. F3 (seq không wrap modulo 128) — XÁC NHẬN.
   - Payload `b'\x5A'`*7700 byte (khác tác giả), 130 gói nối đúng chuẩn
     (seq `% 128`) -> `ValueError: gói nối sai thứ tự (muốn 128, thấy 0)`.
4. F5 (nhãn CTAP2 sai) — TỪ CHỐI MỘT PHẦN, phải hiệu chỉnh trước khi sửa code.
   - `0x0A='cần mở khóa'` của tool thực ra ĐÚNG (= `CTAP1_ERR_LOCK_REQUIRED`,
     đối chiếu RIOT-OS `ctap.h`: `LOCK_REQUIRED 0x0A`); tác giả nói phải là
     `CBOR_UNEXPECTED_TYPE` là SAI (`CBOR_UNEXPECTED_TYPE` là `0x11`).
   - `0x27='lệnh chưa hỗ trợ'` SAI thật, nhưng đáp án đúng là
     `OPERATION_DENIED` (thao tác bị từ chối), KHÔNG phải `PIN_NOT_SET`
     (`PIN_NOT_SET` là `0x35`). Tác giả sai đáp án.
   - Chỉ đúng ở điểm bảng thiếu nhiều mã chuẩn (hiện 9 mục, thiếu `0x0B`,
     `0x10`-`0x16`...). Khi sửa code F5 phải dùng mapping đã hiệu chỉnh ở
     đây, tuyệt đối không đổi `0x0A` thành `CBOR_UNEXPECTED_TYPE`.
   - Ghi nhận trung thực: tác giả đã tự gắn cờ U2 (F5 dựa vào trí nhớ spec,
     cần nhóm tài liệu xác nhận) — kiểm chéo này chính là xác nhận đó.
5. F6 (nuốt lỗi CBOR) — XÁC NHẬN cả 2 vế bằng input mới.
   - Rác đuôi `b"\x18\x2A"` (CBOR uint 42, tác giả dùng `b"XYZ"`):
     `cbor_decode` trả `rest=182a` non-empty nhưng `ctap2_get_info` vẫn ok.
   - `bytes(5)` khai 5 nhưng chỉ 3 byte thực `b"\x45\x01\x02\x03"` (tác giả
     dùng `text(3)`/2 byte) -> trả 3 byte im lặng, không báo lỗi.
6. F8 (assert lọt ra traceback) — XÁC NHẬN.
   - `build_ping_packet(cid, bytes(100))` (tác giả dùng 58),
     `build_init_packet(bytes(7))`, `fragment(..., bytes(70000))` đều
     `AssertionError`; tuple `except` của `main` không chứa `AssertionError`
     (kiểm bằng đọc source + mô phỏng đúng tuple -> lọt ra ngoài).

### Lệnh đã chạy + output (rút gọn, exit 0)

- `python -B $env:TEMP\nckh009_kiemcheo_141.py` -> 17 dòng:
  `F1-CTAP2-saiCID-chapnhan: ... 0x0a0b0c0d ... 0xdeadbeef van_ok`,
  `F2a ... (muốn 0, thấy 129)`, `F2b ... (muốn 1, thấy 191)`,
  `F3-wrap: ... (muốn 128, thấy 0)`,
  `F5 ... 0x0A=CTAP1_ERR_LOCK_REQUIRED 0x11=CBOR_UNEXPECTED_TYPE 0x27=OPERATION_DENIED 0x35=PIN_NOT_SET`,
  `F6a ... rest=182a ... van_ok`, `F6b-bytes-cut: tra_ve=b'\x01\x02\x03'`,
  `F8-PING100/NONCE7/FRAG70K: AssertionError`,
  `F8-mo-phong-main: AssertionError LOT ra ngoai -> traceback (xac nhan)`.
- Đối chiếu spec F5: RIOT-OS `sys/include/fido2/ctap.h` (bản dựng tài liệu
  từ spec FIDO CTAP2) — `CTAP1_ERR_LOCK_REQUIRED 0x0A`,
  `CTAP2_ERR_CBOR_UNEXPECTED_TYPE 0x11`, `CTAP2_ERR_OPERATION_DENIED 0x27`,
  `CTAP2_ERR_PIN_NOT_SET 0x35`.

### Kết luận kiểm định

- [KIEM-DINH] ĐẠT (có hiệu chỉnh bắt buộc F5): 5/6 phát hiện (F1, F2, F3, F6,
  F8) tái hiện độc lập toàn phần bằng input tự chọn; báo cáo trung thực
  (tác giả tự gắn cờ U2 cho đúng điểm còn ngờ là F5). Thẻ 141 đủ điều kiện
  review -> done; khi mở thẻ sửa code theo F5 phải dùng mapping đã hiệu
  chỉnh ở mục 4, không dùng đáp án cũ trong báo cáo NCKH-004.
- Trạng thái thẻ: review -> done (đẩy opportunistic; xem mục Kanzo dưới).
- Unresolved lượt kiểm chéo: (1) chưa có key vật lý nên F1/F2 mới ở mức
  probe RAM, cùng giới hạn U1 của tác giả; (2) đối chiếu spec F5 qua tài
  liệu dựng từ spec (RIOT-OS `ctap.h`), chưa đọc bản PDF spec gốc của FIDO.
- Kanzo: xem mục đồng bộ bên dưới (API nghẽn, opportunistic).

## 2026-11-21 01:45 — đồng bộ Kanzo (opportunistic, thẻ id 141)

- `POST /api/tasks/141/comments` (nội dung [KIEM-DINH] ở mục trên) -> HTTP 500
  cả 3 lần thử (lần đầu + 2 lần thử lại, mỗi lệnh cách 5s, timeout 30s,
  shell pwsh). Dừng theo luật. Thẻ hiện có `comments: 1` (comment cũ của
  tác giả), comment kiểm định CHƯA lên được.
- `POST /api/tasks/141/move {"status":"done"}` -> HTTP 500 (lần 1), OK ở
  lần thử lại thứ nhất: server trả `status: done`, `comments: 1`.
- Viện trưởng vá giúp khi Kanzo sống lại: paste comment `[KIEM-DINH] ĐẠT
  (có hiệu chỉnh bắt buộc F5)` (nội dung đầy đủ ở mục kiểm chéo trên,
  bản không dấu đã dùng ở lần thử 1) vào thẻ 141. Trạng thái thẻ đã `done`.
- Unresolved: comment kiểm định chưa đồng bộ lên Kanzo; nguồn sự thật đầy
  đủ là sổ này.
