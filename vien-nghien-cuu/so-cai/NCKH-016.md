# Sổ cái NCKH-016 — Đinh An (nhóm tooling, đợt 2A)

## 2026-11-21 01:40 — nhận việc
- Thẻ: [tooling] Rà soát hid_echo hai nền tảng (mã NCKH-016)
- Nhiệm vụ (phan-cong.json): Report ID có/không, thiết bị câm, payload biên 0/64 byte.
- Mở rộng theo giao việc: thêm payload biên 60 byte, đối chiếu firmware hwtest.ino,
  chạy self-test và probe biên bằng script riêng trong $env:TEMP.
- Ràng buộc: REPO CHỈ ĐỌC (không sửa tools/firmware), không git commit, shell pwsh.
- Trạng thái: todo -> doing

## 2026-11-21 01:54 — báo cáo rà soát tools/hid_echo.py
- Đã làm:
  - Đọc tools/hid_echo.py (88 dòng), firmware/hwtest/hwtest.ino,
    firmware/hwtest/README.md, tools/requirements.txt.
  - Chạy self_test() gốc + probe biên build_report với payload 0/1/59/60/63/64
    (đúng hết, report luôn 65 byte, pad 0) và 65/100 (bị từ chối đúng).
  - Probe main() bằng thiết bị giả (mock module hid): echo 65 byte kèm report ID,
    echo 64 byte không report ID, thiết bị câm, echo sai, độ dài lạ 32 byte,
    report ID trả về sai (=2).
  - Quét HID thật trên máy: có 2 thiết bị lạ cùng usage_page 0xFF00.
  - Chạy lại self-test dưới `python -O` để kiểm tra assert.
- Tự kiểm:
  - `python "$env:TEMP\nckh016_selftest.py"` -> self_test rc=0, 6/6 biên đóng gói OK,
    65/100 byte bị AssertionError đúng.
  - `python "$env:TEMP\nckh016_probe.py"` -> 6/6 case DAT (2 đường report ID OK,
    câm rc=1 đúng, echo sai rc=1 đúng, dài lạ rc=1 đúng, ID=2 vẫn rc=0).
  - Quét hid thật -> `so thiet bi 0xFF00: 2` (Microsoft HIDI2C Device usage 1,
    Alienware AW-ELC usage 1), không có ESP32.
  - `python -O selftest` -> self_test GỐC fail: `AssertionError: đáng lẽ phải từ
    chối payload quá dài` (assert bị lược bỏ).
- Phát hiện:
  1. [NẶNG] Lọc thiết bị chỉ theo usage_page==0xFF00 (hid_echo.py:51), không lọc
     usage/VID/PID. Trên máy này tool sẽ bắt nhầm HIDI2C hoặc AW-ELC và gửi 65
     byte lạ vào driver hệ thống. Đề xuất: lọc thêm usage==1, thêm cờ --vid/--pid,
     hoặc liệt kê ứng viên cho người dùng chọn.
  2. [VỪA] build_report kiểm tra độ dài bằng assert (dòng 25) -> biến mất dưới
     python -O, đã chứng minh self-test gốc fail. Đề xuất: raise ValueError.
  3. [VỪA] Không kiểm tra report ID trả về (dòng 72 chỉ bóc byte0): echo với ID=2
     vẫn được chấp nhận (probe DAT). Đề xuất: khi len==65 thì yêu cầu echo[0]==1.
  4. [NHẸ] Xử lý hai nền tảng report ID có/không (dòng 72) ĐÚNG: cả echo 65 byte
     (Windows/hidapi) và 64 byte (một số backend Linux) đều pass. Giữ nguyên.
  5. [NHẸ] Thiết bị câm (read rỗng sau 2s) xử lý ĐÚNG: in "Thiết bị không trả
     lời.", rc=1. Giữ nguyên.
  6. [NHẸ] Độ dài lạ (ví dụ 32 byte) báo "Echo sai" đúng nhưng không in độ dài
     thực -> khó debug. Đề xuất: in thêm len(echo).
  7. [ĐỐI CHIẾU FIRMWARE] Descriptor trong hwtest.ino khớp tool: Usage Page
     0xFF00, Report ID 1, Report Count 64 IN/OUT, 8-bit. _onOutput chép tối đa
     64 byte + pad 0, loop() SendReport(1, echoBuf, 64) -> khớp write 65/read 65
     của tool. Hai bên đều bỏ qua report ID (firmware `(void)report_id`, tool
     không kiểm tra byte0) -> nhất quán nhưng lỏng.
  8. [GỢI Ý] PAYLOAD_LEN=60 để lại 4 byte cuối luôn 0 và không kiểm tra -> hỏng
     đúng 4 byte cuối thì tool không phát hiện. Đề xuất: gửi/kiểm tra đủ 64 byte
     ngẫu nhiên.
  9. [LIÊN QUAN NCKH-003] echoPending clear rồi mới SendReport: report mới đến
     giữa hai bước sẽ mất 1 echo -> client thấy "câm" giả. Hiếm với tool gửi
     1 lần, fuzz dồn dập có thể gặp.
- Unresolved:
  - U1: Chưa có board ESP32-S3 thật -> main() end-to-end chưa chạy, mọi kiểm tra
    main() đều qua mock. Cần hardware hoặc phối hợp NCKH-003/NCKH-015.
  - U2: Chưa kiểm chứng trên Linux (read trả 64 hay 65 byte thực tế, enumerate
    usage_page trên hidraw). Mock chỉ chứng minh logic bóc đúng cả hai.
  - U3: Hành vi _onOutput khi host gửi report ID khác 1 hoặc dài hơn 64 byte trên
    phần cứng thật (code clamp 64 nhưng chưa đo).
- Trạng thái: doing -> review

## 2026-11-21 01:57 — đồng bộ Kanzo (thẻ 156)
- GET board OK: tìm thẻ `[tooling] Rà soát hid_echo hai nền tảng (NCKH-016)`, id 156.
- move todo->doing: 500 lần 1, OK lần 2.
- comment nhận việc: 500 cả 3 lần (hết 2 thử lại) -> THIẾU trên bảng.
- move doing->review: 500 lần 1-2, OK lần 3.
- comment báo cáo: OK lần 1.
- Đối chiếu sau đợt: thẻ 156 status=review, comments=1. Đúng cột, đủ báo cáo,
  thiếu comment nhận việc do lỗi 500 phía server (ghi nhận, không thử thêm để
  tránh ghi dồn dập).
- Người kiểm chéo: NCKH-024 (theo mô tả thẻ).

## 2026-11-21 02:06 — kiểm chéo NCKH-024 (Đinh An xét Tạ An, đợt 2A) — ĐẠT
- Đối tượng: sổ NCKH-024 mục 01:57 (24 vector BIP-39, 24/24 KHỚP cả 3 chiều)
  + log `$env:TEMP/nckh024_vectors.log` (pass=24 fail=0) + script `nckh024_vectors.ps1`.
- Phương pháp (đường khác, độc lập, tự gõ tay — không chạy lại script của 024):
  - Tự tải `vectors.json` từ `trezor/python-mnemonic` master bằng `curl.exe` về
    `$env:TEMP/nckh016_vectors.json` (152400 byte, ngày 2026-11-21).
  - File nguồn của 024 (session `01a1f9c2-.../tool-outputs/.../call_...-web_fetch-page.txt`,
    152399 byte) vẫn tồn tại; parse JSON đối chiếu với file tôi tự tải: 24/24 mục
    `english`, số mục khác = 0 (lệch 1 byte thô là newline cuối file).
  - Tự gõ 12 lệnh CLI (4 vector × 3 chiều `from-entropy`/`to-entropy`/`seed
    --passphrase TREZOR`); ghi file entropy bằng `python` + `pathlib` (khác cách
    .NET của 024); mnemonic gõ tay từng từ. Kỳ vọng lấy từ file tôi tự tải.
- Kết quả chạy lại (Python 3.12.0, `python tools/mnemonic.py --self-test` OK trước giờ kiểm):
  - VEC-01 (12 từ, `0000...0000`): from→`abandon×11 about` KHỚP;
    to→`00000000000000000000000000000000` KHỚP; seed→`c55257c3...e7463b04` KHỚP.
  - VEC-12 (24 từ, `ffff...ffff`): from→`zoo×23 vote` KHỚP; to→`fff...(64 ký tự)` KHỚP;
    seed→`dd48c104...a69890ad` KHỚP.
  - VEC-20 (18 từ, `8197a4a4...ceacc0`): from→`light rule ... proud access` KHỚP;
    to→đúng entropy KHỚP; seed→`4cbdff1c...a37b93eda02` KHỚP.
  - VEC-24 (24 từ, `f585c11a...989d8f`): from→`void come ... involve unfold` KHỚP;
    to→đúng entropy KHỚP; seed→`01f5bced...49a5d0998` KHỚP.
  - Mnemonic/entropy của 4 vector trong sổ 024 trùng 100% file tôi tự tải.
- Kết luận: ĐẠT — mẫu kiểm 4/24 vector (gồm 2 vector 24 từ, phủ cả 3 nhóm
  12/18/24 từ) khớp 100% cả 3 chiều; nguồn vector của 024 trùng nguồn trezor hiện tại.
- Đồng bộ Kanzo (thất bại đúng quy trình, đã ghi sổ): GET
  `http://100.101.100.100:4242/api/board?project=esp32-securitykey` (timeout 30s,
  cách nhau 5s): lần 1 → 500, lần 2 → 500, lần 3 → 500 (hết 2 thử lại). Không đọc
  được board nên không tìm được thẻ NCKH-024, không comment/move được. Dừng đúng
  quy trình, không thử thêm.
- Unresolved:
  - U-X1: Chưa đồng bộ Kanzo (server 500 cả 3 lần). Nhờ Viện trưởng: khi board khỏe,
    tìm/tạo thẻ NCKH-024, gắn comment `[KIEM-DINH] đạt — Đinh An kiểm chéo 4/24
    vector (VEC-01/12/20/24) khớp cả 3 chiều, nguồn trezor trùng khớp` và move
    review→done (kết quả gốc của 024 đang ở trạng thái review-chờ-thẻ).
  - U-X2: Chỉ kiểm mẫu 4/24 vector, không chạy lại toàn bộ 24 (đúng yêu cầu kiểm
    chéo đợt 2A: 3-4 vector, gồm ít nhất 1 vector 24 từ).
- Vệ sinh: đã xóa 4 file entropy tạm `nckh016_e*.bin`; giữ `nckh016_vectors.json`
  làm bằng chứng nguồn. Không sửa file repo nào ngoài sổ này, không git commit.
