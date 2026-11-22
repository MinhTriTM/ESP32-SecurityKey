# Sổ cái — NCKH-028 Lê Bình (nhóm tooling, đợt 2A)

## 2026-11-21 01:55 — nhận việc
- Thẻ: [tooling] Fuzz parse_share (tìm id trên Kanzo sau — file trước bảng sau)
- Nhiệm vụ (phan-cong.json): "Input rác chỉ được ném ValueError, không crash loại khác."
- Phạm vi: hàm `parse_share` trong `tools/split_secret.py`. CHỈ BÁO CÁO, không sửa code.
- Trạng thái: todo -> doing

## 2026-11-21 01:57 — báo cáo fuzz parse_share
- Đã làm:
  - Đọc `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-028 trong `phan-cong.json`,
    `vien-nghien-cuu/so-cai/README.md`, và toàn bộ `tools/split_secret.py` (chỉ đọc).
  - Viết script fuzz `fuzz_parse_share_NCKH028.py` trong `$env:TEMP` (ngoài repo),
    chạy 5066 case str: 66 corpus có chủ đích (thiếu key, value không phải số,
    hex sai, len sai, unicode, số âm/khổng lồ, nhiều/ít dòng...) + 5000 random
    seed 28 (1500 rác hoàn toàn, 2500 đột biến trên share hợp lệ, 1000 header ghép).
  - Phân loại mỗi case: ok / ValueError có thông điệp / ValueError rỗng / ngoại lệ khác.
- Tự kiểm: `python $env:TEMP\fuzz_parse_share_NCKH028.py` -> exit 0, xem thống kê dưới.
- Kết quả thống kê (5066 case):
  - ok (parse được): 42
  - ValueError có thông điệp: 4870
  - ValueError rỗng: 0
  - NGOẠI LỆ KHÁC: 154 — toàn bộ là `KeyError`
- Ngoại lệ khác (vi phạm yêu cầu "chỉ ValueError"):
  - Loại duy nhất: `KeyError`, msg một trong `'shares'`, `'threshold'`, `'index'`.
  - Nguyên nhân gốc (đọc code, dòng 146): `return params["shares"], params["threshold"],
    params["index"], y` truy cập dict trực tiếp. Điều kiện kích hoạt: dòng 2 là hex
    hợp lệ + `len` khớp + header thiếu ≥1 trong 3 key shares/threshold/index
    (kể cả gõ sai tên key, vd `threshol=2`, `Shares=3`).
  - Ví dụ tối thiểu (3/3 key đều tái hiện):
    - `SHAMIR-SHARE-V1 threshold=2 index=1 len=8\n6162636465666768` -> KeyError 'shares'
    - `SHAMIR-SHARE-V1 shares=3 index=1 len=8\n6162636465666768` -> KeyError 'threshold'
    - `SHAMIR-SHARE-V1 shares=3 threshold=2 len=8\n6162636465666768` -> KeyError 'index'
  - Ghi chú: `len` thiếu không gây KeyError (dùng `params.get("len", -1)` -> ValueError
    "độ dài dữ liệu không khớp header"). Value không phải số (vd `shares=abc`) vẫn ra
    ValueError (từ `int()`) nên đạt.
- Ngoài hợp đồng `text: str` (ghi chú, không tính vi phạm chính):
  - `None`/`123`/`['x']` -> AttributeError (không có `.strip`); `bytes` -> TypeError
    ở `startswith`. Caller `cmd_combine`/`cmd_qr` chỉ bắt `(OSError, ValueError)` nên
    các ngoại lệ trên (kể cả KeyError) đều thoát ra ngoài thành traceback.
- Không sửa code theo yêu cầu (CHỈ BÁO CÁO).
- Trạng thái: doing -> review (đồng bộ Kanzo sau mục này; nếu Kanzo hỏng sẽ ghi thêm mục dưới)

## 2026-11-21 01:58 — đồng bộ Kanzo (không có thẻ)
- GET `/api/board?project=esp32-securitykey` thành công (timeout 30s), bảng có 21 thẻ.
- Không có thẻ nào của NCKH-028 (bảng mới có thẻ đến NCKH-021; các thẻ NCKH-022..030
  đợt 2A, gồm việc của tôi, chưa được tạo). Thẻ duy nhất nhắc NCKH-028 là id 160
  `[ML] Tóm tắt Gohr 2019 (NCKH-020)`, đang `todo`, ghi tôi là người kiểm chéo —
  chưa đến lượt kiểm (chỉ kiểm khi thẻ sang `review`) nên không động vào.
- Không tự tạo thẻ mới (ngoài nhiệm vụ được giao; tránh trùng với Viện trưởng).
- Kết luận: bỏ qua move+comment, sổ cái này là kênh báo cáo duy nhất. Không thử lại
  (không phải lỗi mạng, thử lại không thay đổi kết quả).

## 2026-11-21 02:07 — kiểm chéo NCKH-020 Đoàn An (đợt 2A)
- Vai trò: Lê Bình (NCKH-028), nhóm tooling, kiểm độc lập: tóm tắt Gohr 2019 +
  bảng khác biệt + phát hiện nhãn-0. (Giao việc ghi "7 tiêu chí" nhưng bảng thực
  có 13 hàng — đầy đủ hơn mô tả, coi là điểm cộng.)
- Tài liệu đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-020.md`, toàn bộ
  `tools/ml_distinguisher.py` (331 dòng), `docs/research/06-ml-distinguisher.md`,
  `vien-nghien-cuu/HIEN-CHUONG.md` (§6 API Kanzo).
- Phương pháp: kiểm bằng ĐƯỜNG KHÁC — đọc trực tiếp code nguồn để xác nhận các
  khẳng định cột "Ta" trong bảng (không chạy lại lệnh tác giả; tác giả cũng chỉ
  đọc, không chạy).
- Spot-check 1 — "Mẫu nhãn 0" (Ta = 64 bit ngẫu nhiên trực tiếp, không qua mã
  hóa): KHỚP. Code dòng 118-121 `X[idx] = rng.integers(0, 2, size=64)`; nhãn 1
  dòng 109-116 (cặp bản rõ lệch FIXED_DX/DY, cùng khóa); FIXED_DX=0x0040,
  FIXED_DY=0x0000 dòng 31-32.
- Spot-check 2 — "Kiến trúc" (MLP 64->128->64->1, ReLU+sigmoid, không
  conv/residual/BN): KHỚP. Docstring dòng 143; w1(64,128)/w2(128,64)/w3(64,1)
  dòng 148-153; forward ReLU-ReLU-sigmoid dòng 164-173; không BN/conv/residual.
  Phụ: Adam lr 0.002 (dòng 145), BCE (dòng 176), defaults 6000/2000/5 epoch/
  batch 256/seed 1337 (dòng 300-306) đều khớp bảng; đặc trưng 64 bit nối 4 từ
  (dòng 115) khớp; accuracy 0.597/0.525/0.507 nhất quán với `docs/research/06`.
- Đánh giá phát hiện "bài toán của ta dễ hơn": LOGIC ĐÚNG. Nhãn 0 ngẫu nhiên
  thuần cho phép mạng học mọi bias của mã rút gọn so với phân phối đều; Gohr
  nhãn 0 = mã hóa cặp ngẫu nhiên nên hai lớp cùng phân phối mã, mạng buộc học
  tín hiệu gắn chênh lệch cố định (đúng nghĩa distinguisher vi sai, khó hơn).
  Không mâu thuẫn với accuracy ta thấp hơn Gohr cùng R: mạng yếu hơn (MLP vs
  ResNet) + dữ liệu ít hơn ~1600 lần (6k vs 10M) — tác giả đã giải thích đúng
  ở Bài học 1.
- Điểm trừ nhỏ (không ảnh hưởng đạt): số accuracy Gohr (~0.93/0.79/0.62/0.51)
  từ nguồn thứ cấp, chưa đối chiếu PDF — nhưng tác giả đã khai minh bạch và dặn
  không trích dẫn số tuyệt đối. Giới hạn kiểm: phía Gohr trong bảng (ResNet,
  MSE, 10M mẫu, Bayes, 70GB/300 CPU-ngày) tôi KHÔNG xác minh độc lập trong lượt
  này, tin theo 2 URL truy xuất của tác giả.
- KẾT LUẬN: ĐẠT.
- Kanzo thẻ id 160 `[ML] Tóm tắt Gohr 2019 (NCKH-020)` (mỗi lệnh cách 5s,
  timeout 30s, `shell="pwsh"`):
  - GET board: lần 1 HTTP 500; lần 2 OK (27 thẻ, id 160 đang `todo`; mô tả thẻ
    xác nhận người kiểm chéo là NCKH-028).
  - POST comment `[KIEM-DINH] đạt + lý do`: OK ngay lần đầu (comment id 30).
  - Move todo->doing: lần 1 500, retry 1 OK (đưa thẻ về đúng cột vì tác giả kẹt
    500 không move được).
  - Move doing->review: cả 3 attempt 500 → hết quota.
  - GET đối chiếu: cả 3 attempt 500 → không xác minh được trạng thái thực
    (vẫn doing, hoặc đã review nếu server ghi dù báo lỗi).
  - Chưa move được review->done. Nhờ Viện trưởng khi Kanzo hồi phục: đối chiếu
    thẻ 160, nếu đang doing/review thì đưa về done (kiểm đã đạt, comment id 30
    đã dán) + dán giúp comment báo cáo của NCKH-020 (mục 01:55 trong sổ 020).
- Trạng thái thật: NỘI DUNG ĐẠT, chờ Kanzo hồi phục để đóng thẻ.
- Unresolved: (1) thẻ 160 chưa về done do Kanzo nghẽn SQLite; (2) phía Gohr
  trong bảng chưa được kiểm độc lập (giới hạn đã nêu).
- Tự kiểm: repo chỉ đọc (chỉ đọc 4 file + nối thêm chính sổ này); không git
  commit; mọi lệnh shell kèm `shell="pwsh"`.
