# Sổ cái NCKH-002 — Trần An, nhóm ML, nhóm trưởng Viện, đợt 1

> Ghi chú tên: lệnh giao việc ban đầu ghi "Trần Bình (NCKH-002)" nhưng
> `vien-nghien-cuu/phan-cong.json` ghi NCKH-002 = "Trần An" (còn "Trần Bình" là
> NCKH-027). Viện trưởng đã đính chính: tên chính thức là Trần An, mã NCKH-002
> giữ nguyên. Từ đây dùng đúng tên Trần An.

## 2026-11-21 01:29 — nhận việc
- Thẻ: [ML] Tái hiện ml_distinguisher (Kanzo id 139)
- Trạng thái: todo -> doing (thử opportunistic sau; Kanzo đang nghẽn)
- Việc nhận: chạy full `tools/ml_distinguisher.py --rounds 5,6,7`, ghi accuracy từng R,
  đối chiếu với `docs/research/06-ml-distinguisher.md`.
- Tài liệu đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0),
  mục NCKH-002 trong `vien-nghien-cuu/phan-cong.json`,
  `vien-nghien-cuu/so-cai/README.md`, `docs/research/06-ml-distinguisher.md`,
  toàn bộ `tools/ml_distinguisher.py`.
- Số liệu trong tài liệu (seed 1337, CPU): R=5 → 0.5970, R=6 → 0.5245, R=7 → 0.5070
  (test 2000 mẫu, train 6000 mẫu, 5 epoch, ~2 giây cho cả 3 R).
- Môi trường: Windows, Python 3.12.0, numpy 2.5.4 (kiểm bằng `python -c "import numpy"`).
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; file tạm chỉ trong `$env:TEMP`.

## 2026-11-21 01:30 — báo cáo
- Thẻ: [ML] Tái hiện ml_distinguisher (Kanzo id 139)
- Đã làm:
  1. Self-test: PASS (vector KHOP k0=tu-cuoi, round-trip PASS 200 mẫu x R=5,22,
     micro-train R=5 acc=0.505).
  2. Full run `python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000 --epochs 5`
     (seed mặc định 1337):
     - R=5 → accuracy=0.5970 (0.6s)
     - R=6 → accuracy=0.5245 (0.6s)
     - R=7 → accuracy=0.5070 (0.5s)
  3. Chạy lặp lần 2 cùng lệnh: R=5 → 0.5970, R=6 → 0.5245, R=7 → 0.5070 (giống hệt).
- Đối chiếu `docs/research/06-ml-distinguisher.md`: KHỚP TUYỆT ĐỐI cả 3 R
  (tài liệu: 0.5970 / 0.5245 / 0.5070; quan sát: 0.5970 / 0.5245 / 0.5070).
  Nhận xét trong tài liệu đứng vững: R=5 phân biệt rõ, R=6 tín hiệu yếu,
  R=7 gần đoán mò. Tổng thời gian ~1.6s cả 3 R, phù hợp "~2 giây" trong tài liệu.
- Tự kiểm (lệnh đã chạy + output chính):
  - `python tools/ml_distinguisher.py --self-test` → PASS, EXIT=0
    (log: `$env:TEMP/NCKH-002-selftest.log`)
  - `python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000 --epochs 5` →
    `Tom tat: R=5: 0.5970, R=6: 0.5245, R=7: 0.5070`, EXIT=0
    (log: `$env:TEMP/NCKH-002-full.log`)
  - Chạy lặp cùng lệnh → số giống hệt, EXIT=0
    (log: `$env:TEMP/NCKH-002-repeat.log`)
- Kết luận: tái hiện THÀNH CÔNG, số liệu tài liệu đáng tin ở seed 1337 trên máy này.
- Trạng thái: doing -> review (chờ kiểm chéo; peer review cần đường kiểm độc lập,
  không chạy lại đúng lệnh của tác giả).
- Kanzo: xem mục bên dưới (thử opportunistic, cách nhau 5s, timeout 30s, tối đa 2 lần thử lại).

## 2026-11-21 01:35 — đồng bộ Kanzo (thẻ 139): THẤT BẠI, chờ Viện trưởng vá
- Lệnh 1 `POST /api/tasks/139/move {"status":"doing"}`: 3/3 lần HTTP 500
  (Internal Server Error), mỗi lần thử cách nhau 5s, timeout 30s.
- Lệnh 2 `POST /api/tasks/139/move {"status":"review"}`: 3/3 lần HTTP 500.
- Lệnh 3 `POST /api/tasks/139/comments` (báo cáo tái hiện khớp tuyệt đối):
  3/3 lần HTTP 500.
- Mỗi lệnh cách nhau ≥5s (Start-Sleep 5 + độ trễ giữa các lượt gọi).
- Nhận xét: server phản hồi 500 (không phải timeout), đúng triệu chứng SQLite
  khóa DB khi ghi dồn dập đã ghi trong Hiến chương §6. Không rõ server có ghi
  mà vẫn trả 500 hay không — nhờ Viện trưởng đối chiếu bảng khi Kanzo hồi phục
  và vá giúp: thẻ 139 todo -> doing -> review + comment báo cáo trong mục trên.
- Trạng thái thật của việc: ĐÃ XONG, chờ kiểm chéo (review), dù thẻ Kanzo chưa
  di chuyển được.
- Ghi chú shell: 1 lệnh đầu quên `shell="pwsh"` nên lỗi `program not found`,
  đã chạy lại thành công với `shell="pwsh"` (Viện trưởng nhắc — đã tuân thủ,
  mọi lệnh shell sau đó đều kèm tham số này).

## 2026-11-21 01:38 — kiểm chéo thẻ 148 của NCKH-009 (kiểm định viên)
- Vai trò: Trần An (NCKH-002), nhóm ML, lượt KIỂM CHÉO đợt 1.
- Đối tượng: thẻ Kanzo id 148 của NCKH-009 Đặng An — parser độc lập xác nhận
  descriptor HID khớp toàn bộ. Đã đọc `vien-nghien-cuu/so-cai/NCKH-009.md`.
- Đường kiểm ĐỘC LẬP (khác parser prefix tag/type/size của tác giả):
  1. Trích byte bằng PowerShell regex sau khi lọc comment `//` từng dòng
     (lần đầu quên lọc nên đếm nhầm 38 do dính hex trong comment — đã sửa).
     Kết quả: COUNT=36:
     `06 00 FF | 09 01 | A1 01 | 85 01 | 09 02 | 15 00 | 26 FF 00 | 75 08 |
     95 40 | 81 02 | 09 03 | 15 00 | 26 FF 00 | 75 08 | 95 40 | 91 02 | C0`.
  2. Nhóm item HID THỦ CÔNG (theo format item HID, không dùng parser generic):
     Usage Page (3B, LE 0xFF00 vendor) + Usage (2B) + Collection App (2B) +
     Report ID 1 (2B) + Usage IN (2B) + LogMin 0 (2B) + LogMax 255 (3B) +
     Report Size 8 (2B) + Report Count 64 (2B) + Input (2B) + Usage OUT (2B) +
     LogMin 0 (2B) + LogMax 255 (3B) + Report Size 8 (2B) +
     Report Count 64 (2B) + Output (2B) + End Collection (1B)
     = 3+2+2+2+2+2+3+2+2+2+2+2+3+2+2+2+1 = 36 byte. KHỚP COUNT=36.
     Collection mở/đóng cân bằng (1 A1 ... 1 C0), đúng 1 Report ID.
  3. Ngữ nghĩa rút ra: Usage Page 0xFF00; Report ID 1 duy nhất;
     Input 8 bit x 64 = 64 byte; Output 8 bit x 64 = 64 byte.
- Đối chiếu `tools/hid_echo.py`: ECHO_USAGE_PAGE=0xFF00 ✓, REPORT_ID=1 ✓,
  REPORT_LEN=64 ✓ (= 64 byte mỗi chiều), PAYLOAD_LEN=60 ≤ 64 ✓,
  `build_report` = 1+64 byte ✓, `device.read(REPORT_LEN + 1)` = 65 byte ✓.
- Đối chiếu firmware: `echoBuf[64]` ✓, `SendReport(1, echoBuf, sizeof)` ✓,
  comment dòng 13-14 ✓, chuỗi Serial dòng 122 ✓.
- Tự chạy `python tools/hid_echo.py --self-test` → PASS, EXIT=0
  ("self-test ok: đóng gói report HID echo đúng.").
- Ghi chú `_onOutput` bỏ qua `report_id`: ĐỒNG Ý với tác giả — chấp nhận được
  vì descriptor chỉ định nghĩa đúng 1 Report ID.
- Kết luận kiểm chéo: ĐẠT — mọi khẳng định của NCKH-009 (36 byte, 0xFF00,
  Report ID 1, 1 IN + 1 OUT 64 byte, khớp firmware và tool) đều được tái xác
  nhận bằng đường kiểm khác. Không phát hiện lệch.
- Kanzo (opportunistic, mỗi lệnh cách 5s, timeout 30s, tối đa 2 lần thử lại,
  shell pwsh): THẤT BẠI toàn bộ.
  - `POST /api/tasks/148/comments` (nội dung `[KIEM-DINH] DAT` + lý do):
    lần 1 HTTP 500, lần 2 HTTP 500, lần 3 HTTP 400.
  - `POST /api/tasks/148/move {"status":"done"}`: 3/3 lần HTTP 500.
  - Nhờ Viện trưởng vá khi Kanzo hồi phục: comment `[KIEM-DINH] DAT` của
    NCKH-002 lên thẻ 148 + move thẻ về done (lưu ý thẻ hiện ở doing trên
    server theo sổ NCKH-009 vì move doing -> review của tác giả cũng rớt).
- Unresolved: đồng bộ Kanzo chưa xong; nội dung kiểm định đầy đủ nằm ở mục này.
