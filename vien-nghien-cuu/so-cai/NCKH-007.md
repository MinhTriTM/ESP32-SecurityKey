# Sổ cái NCKH-007 — Vũ An, nhóm PQC, thành viên, đợt 1

> Ghi chú tên (đã chốt 01:35): lệnh giao việc ban đầu ghi "Vũ Giang
> (NCKH-007)" nhưng Viện trưởng đính chính tên chính thức theo
> phan-cong.json là "Vũ An". Từ đây dùng đúng tên Vũ An.

## 2026-11-21 01:24 — nhận việc

- Thẻ: [PQC] So sánh ML-KEM-512/768/1024 (Kanzo id 145)
- Việc nhận: đo kích thước pk/sk/ct/ss và tốc độ keygen/encap/decap của
  ML-KEM-512/768/1024 bằng liboqs có sẵn (.tooling/pylibs +
  OQS_INSTALL_PATH=.tooling/oqs) trên máy này; khuyến nghị một bản cho vault.
- Trạng thái: todo -> doing (sẽ thử opportunistic sau khi ghi sổ xong,
  vì Kanzo đang nghẽn)
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-007 trong
  vien-nghien-cuu/phan-cong.json, vien-nghien-cuu/so-cai/README.md,
  tools/pqc.py (để biết đúng cách nạp liboqs).

## 2026-11-21 01:30 — báo cáo

- Đã làm: benchmark 3 bản ML-KEM bằng liboqs-python + oqs.dll có sẵn trong
  repo, script đo đặt tại `$env:TEMP\mlkem_bench_007.py` (ngoài repo, đúng
  quy định REPO CHỈ ĐỌC). Mỗi op đo 200 vòng (lần 1) và 500 vòng (lần 2),
  có warmup, có kiểm round-trip encap/decap khớp từng byte trước khi đo.
- Môi trường: Windows, CPU 13th Gen Intel i7-13620H, Python 3.12.0,
  liboqs 0.16.0, liboqs-python 0.16.0.2, oqs.dll tại .tooling/oqs/bin.
- Lệnh chạy (lần 2, bản chốt):
  `$env:OQS_INSTALL_PATH='D:\Download\ESP32-SecurityKey\.tooling\oqs';`
  `$env:PYTHONPATH='D:\Download\ESP32-SecurityKey\.tooling\pylibs';`
  `python "$env:TEMP\mlkem_bench_007.py"`

### Bảng 1 — Kích thước (byte, đọc từ kem.details, cả 2 lần chạy giống nhau)

| Bản        | pk   | sk   | ct   | ss | NIST level |
|------------|------|------|------|----|------------|
| ML-KEM-512 | 800  | 1632 | 768  | 32 | 1          |
| ML-KEM-768 | 1184 | 2400 | 1088 | 32 | 3          |
| ML-KEM-1024| 1568 | 3168 | 1568 | 32 | 5          |

Đối chiếu: khớp chuẩn FIPS 203 và khớp docstring tools/pqc.py
(pk=1184, sk=2400, ct=1088, ss=32 cho ML-KEM-768).

### Bảng 2 — Tốc độ keygen/encap/decap (micro-giây/op, số nhỏ = nhanh)

| Bản        | keygen L1 | keygen L2 | encap L1 | encap L2 | decap L1 | decap L2 |
|------------|-----------|-----------|----------|----------|----------|----------|
| ML-KEM-512 | 88,9      | 160,8     | 104,6    | 196,6    | 26,5     | 59,2     |
| ML-KEM-768 | 105,2     | 174,8     | 193,2    | 259,4    | 107,4    | 88,7     |
| ML-KEM-1024| 218,8     | 228,6     | 125,0    | 197,2    | 87,2     | 107,1    |

(L1 = 200 vòng, L2 = 500 vòng, bản script 2 với đúng cặp sk/ct.)

Nhận xét trung thực: trị tuyệt đối dao động mạnh giữa 2 lần chạy
(máy đang bận, nhiều agent chạy cùng lúc), nên số trên chỉ có ý nghĩa
tương đối. Điểm nhất quán qua cả 2 lần: ML-KEM-512 nhanh nhất ở cả 3 op;
ML-KEM-768 và 1024 cùng bậc (chênh lệch < 2x, không ổn định chiều).
Quan trọng: cả 3 bản đều dưới ~260 us/op — với vault (mỗi lần mở két chỉ
encap/decap 1 lần) thì chênh lệch ~100 us là không đáng kể. Tốc độ KHÔNG
phải yếu tố quyết định; kích thước và mức an toàn mới là.

### Khuyến nghị cho vault: ML-KEM-768

Lý do:

1. NIST level 3 (tương đương AES-192), đủ biên an toàn cho két bí mật
   dài hạn; ML-KEM-512 chỉ level 1 (tương đương AES-128), biên mỏng cho
   dữ liệu "thu hôm nay, giải mã sau" khi máy lượng tử mạnh lên.
2. Nhỏ hơn ML-KEM-1024 đáng kể: pk -384 byte, sk -768 byte, ct -480 byte;
   trong khi 1024 (level 5) cho thêm an toàn mà vault không cần tới.
3. Khớp hạ tầng sẵn có: tools/pqc.py đã chốt ML-KEM-768, chọn bản khác
   đồng nghĩa sửa tool + self-test + tài liệu mà không có lợi ích rõ ràng.

- Tự kiểm:
  - Round-trip encap→decap khớp từng byte cho cả 3 bản, cả 2 lần chạy.
  - Kích thước khớp FIPS 203 và tools/pqc.py.
  - Không ghi/sửa gì trong repo ngoài file sổ này (script đo nằm ở
    $env:TEMP, đã kiểm bằng mắt: chỉ 1 file sổ mới).
  - Không git commit (đúng lệnh).
- Peer review: chờ agent khác nhóm kiểm chéo.
- Trạng thái: doing -> review (sẽ thử opportunistic; nếu Kanzo hỏng thì
  thẻ ở lại bảng cũ, Viện trưởng đối chiếu sổ này sau).

## 2026-11-21 01:38 — đồng bộ Kanzo id 145 (opportunistic, Kanzo nghẽn)

- move -> doing: THÀNH CÔNG ở lần thử 3 (lần 1: 500, lần 2: timeout 30s).
- comment báo cáo (id 8): THÀNH CÔNG ngay lần 1.
- move -> review: THẤT BẠI cả 3 lần (500 x3), đã hết hạn 2 lần thử lại.
- Mỗi lệnh cách nhau 5s, timeout 30s, đúng lệnh.
- Trạng thái bảng hiện tại (theo response đã nhận): thẻ 145 ở `doing`,
  đã có comment báo cáo. Viện trưởng hoặc nhịp tim sau đẩy giúp `doing`
  -> `review` khi Kanzo khỏe lại; người kiểm chéo theo mô tả thẻ: NCKH-012.

## 2026-11-21 01:40 — kiểm chéo thẻ 139 [ML] Tái hiện ml_distinguisher (NCKH-002 Trần An): ĐẠT

- Vai: NCKH-007 Vũ An, nhóm PQC, lượt kiểm chéo đợt 1 (xét 002).
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-002.md`,
  `docs/research/06-ml-distinguisher.md`, toàn bộ `tools/ml_distinguisher.py`.
- Số gốc cần kiểm (seed 1337, train 6000/test 2000, epochs 5):
  R=5 → 0.5970, R=6 → 0.5245, R=7 → 0.5070.
- Nguyên tắc: KHÔNG chạy lại đúng lệnh của tác giả; kiểm bằng ĐƯỜNG KHÁC
  (seed khác + số mẫu khác).
- Run độc lập 1 — seed 99, train 3000/test 1000, epochs 5:
  R=5 → 0.5300, R=6 → 0.4790, R=7 → 0.4740 (mỗi R ~0.3s).
  Lệnh: `python tools/ml_distinguisher.py --rounds 5,6,7 --samples 3000
  --test-samples 1000 --epochs 5 --seed 99`, EXIT=0
  (log: `$env:TEMP\NCKH-007-xet002-139.log`).
- Run bổ trợ 2 — seed 99, mẫu gốc 6000/2000, epochs 5 (cô lập ảnh hưởng
  của seed, chỉ đổi seed so với tác giả):
  R=5 → 0.5810, R=6 → 0.5070, R=7 → 0.4980 (mỗi R ~0.5s).
  Lệnh: `python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000
  --test-samples 2000 --epochs 5 --seed 99`, EXIT=0
  (log: `$env:TEMP\NCKH-007-xet002-139-b2.log`).
- Đối chiếu xu hướng: cả 2 run giữ thứ tự R5 > R6 > R7; R=5 luôn phân
  biệt rõ trên đoán mò (0.53/0.58); R=7 luôn quanh đoán mò (0.47-0.51).
  R=6 tín hiệu yếu, nhạy seed/mẫu (0.5245 gốc → 0.5070/0.4790) nhưng
  không đảo xu hướng.
- Giải thích chênh lệch run 1: train chỉ 3000 (một nửa ngân sách gốc) +
  test 1000 (sai số chuẩn của đoán mò ~0.016) nên R5 giảm về 0.53 là
  hợp lý; run 2 chứng minh với đủ mẫu, seed 99 cho R5=0.5810, chỉ lệch
  -0.016 so với gốc → kết quả gốc ổn định, không phải may mắn seed.
- Đối chiếu tài liệu: `docs/research/06-ml-distinguisher.md` ghi
  0.5970/0.5245/0.5070, KHỚP TUYỆT ĐỐI sổ NCKH-002; nhận xét
  R5 rõ/R6 yếu/R7 mù đứng vững qua kiểm độc lập.
- Kết luận: ĐẠT. Tái hiện đáng tin, xu hướng vững qua seed và ngân sách
  mẫu khác nhau.
- Kanzo (opportunistic, mỗi lệnh cách 5s, timeout 30s, tối đa 2 lần thử
  lại — tức 3 attempts/lệnh):
  - `POST /api/tasks/139/comments` ([KIEM-DINH] đạt + lý do): THẤT BẠI
    3/3 (lần 1 timeout 30s, lần 2-3 HTTP 500).
  - `POST /api/tasks/139/move {"status":"done"}`: THẤT BẠI 3/3 (500 x3).
  - Đúng triệu chứng SQLite khóa DB khi ghi dồn dập. Nhờ Viện trưởng vá
    giúp khi Kanzo khỏe: gắn comment kiểm định ĐẠT (nội dung như lệnh
    đã thử) + chuyển thẻ 139 -> done. Trạng thái thật của việc:
    ĐÃ KIỂM CHÉO ĐẠT.
- Cam kết repo: chỉ nối thêm file sổ này; không sửa code/docs; không git
  commit; log chạy ở `$env:TEMP`; mọi lệnh shell đều kèm `shell="pwsh"`.
