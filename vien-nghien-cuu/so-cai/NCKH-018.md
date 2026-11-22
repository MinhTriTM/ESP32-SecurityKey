# Sổ cái NCKH-018 — Trương An (nhóm kiemdinh, đợt 2)

Nhiệm vụ (phan-cong.json): Kiểm chéo Shamir độc lập — tự viết GF(256) riêng,
so kết quả chia/ghép với tool. Repo chỉ đọc, không git commit.

## 2026-11-21 01:52 — nhận việc
- Thẻ: [KIEMDINH] Kiểm chéo Shamir độc lập (tìm trên Kanzo theo mã NCKH-018)
- Trạng thái: todo -> doing
- Kế hoạch: viết GF(256)+Shamir độc lập trong $env:TEMP (không copy
  tools/split_secret.py), đối chiếu chia/ghép trên nhiều ngưỡng và secret ngẫu nhiên.

## 2026-11-21 02:00 — báo cáo
- Đã làm:
  - Viết mới hoàn toàn `nckh018_gf256.py` trong $env:TEMP: nhân GF(256) kiểu nông dân
    Nga (không dùng bảng log/exp), nghịch đảo a^254, đánh giá đa thức bằng tổng trực
    tiếp (không dùng Horner), Lagrange viết lại theo công thức tích tường minh.
  - Kiểm tra độc lập: 0 dòng dài (>40 ký tự) trùng với tools/split_secret.py.
  - Viết `nckh018_doi_chieu.py`: đối chiếu tool vs bản độc lập trên 10 ngưỡng
    (3,2) (5,3) (5,5) (8,2) (5,1) (7,7) (10,4) (16,8) (32,16) (255,2), secret dài
    1/8/16/32/64 byte (seed tái hiện + secrets.token_bytes thật), cả hai chiều
    tool->mine và mine->tool, mọi tập con K (lấy mẫu khi C(n,k) lớn).
- Tự kiểm: `python $env:TEMP\nckh018_doi_chieu.py --repo D:\Download\ESP32-SecurityKey`
  -> exit 0, TỔNG 10/10 mục KHỚP, thời gian ~34s. Chi tiết:
  - [KHỚP] A1 vector AES (6 vector nhân + 1 vector chia)
  - [KHỚP] A2 toàn bảng nhân 256x256 (65536 cặp, lệch 0)
  - [KHỚP] A3 nghịch đảo 1..255 (lệch 0)
  - [KHỚP] A4 chia ngẫu nhiên 2000 cặp (lệch 0)
  - [KHỚP] A5 đánh giá đa thức 500 mẫu (lệch 0)
  - [KHỚP] B tự ghép bản độc lập (1880 lượt ghép, lệch 0)
  - [KHỚP] C tương thích chéo tool<->mine (3570 lượt ghép chéo, lệch 0)
  - [KHỚP] D tính chất Shamir (thiếu share/K=1/qua format-parse của tool)
  - [KHỚP] E nhánh lỗi (ValueError/ZeroDivisionError cả hai bên)
  - [KHỚP] F self-test gốc của tool (return=0)
- Kết luận: [KIEM-DINH] đạt — tools/split_secret.py chia/ghép đúng trên mọi ngưỡng
  đã thử, tương thích hai chiều với implement độc lập, nhánh lỗi đầy đủ.
- Unresolved: không có. Lưu ý: ngưỡng rất lớn kiểu (255,255) không thử vì ghép
  O(k^2)/byte quá đắt cho bản Python thuần; đã phủ (32,16) và (255,2) thay thế.
- Trạng thái: doing -> review (đồng bộ Kanzo bên dưới)

## 2026-11-21 02:01 — đồng bộ Kanzo (thất bại, Kanzo sập)
- GET /api/board?project=esp32-securitykey (timeout 30s, cách 5s, 1 lần đầu + 2 thử
  lại) đều trả 500 Internal Server Error. Không tìm được thẻ, không move/comment được.
- Sổ file này là bản chính; nhờ Viện trưởng đối chiếu và vá lên bảng khi Kanzo sống lại.
- Không có thẻ nào kẹt do việc khó — việc kiểm định đã xong 10/10 KHỚP.

## 2026-11-21 02:06 — kiểm chéo đợt 2A: tài liệu của NCKH-026 Nguyễn Bình
- Đối tượng: docs/research/07-giai-thich-distinguisher.md (9212 bytes, mtime
  21/11/2026 1:53:50, khớp sổ NCKH-026) + sổ vien-nghien-cuu/so-cai/NCKH-026.md.
- Đường kiểm độc lập: đối chiếu từng số liệu/khẳng định trong doc 07 với
  tools/ml_distinguisher.py (đọc trực tiếp code) và docs/research/06-ml-distinguisher.md.
- Đối chiếu số liệu (7/7 KHỚP):
  - [KHỚP] R = 5, 6, 7; bản chuẩn 22 vòng — khớp 06 (§Thiết lập) và code
    (FULL_ROUNDS = 22, --rounds mặc định "5,6,7").
  - [KHỚP] (dx, dy) = (0x0040, 0x0000) kiểu Gohr — khớp 06 và code
    (FIXED_DX/FIXED_DY).
  - [KHỚP] Mẫu thật: cùng khóa ngẫu nhiên, nối 2 bản mã thành 64 bit (nhãn 1);
    mẫu giả 64 bit ngẫu nhiên (nhãn 0); tập cân bằng 50/50 — khớp 06 và
    make_dataset() (words_to_bits 4 từ 16 bit = 64 đặc trưng, nửa-nửa khi n chẵn).
  - [KHỚP] MLP 64 -> 128 -> 64 -> 1, ReLU + sigmoid, Adam, BCE — khớp class MLP.
  - [KHỚP] Ngân sách 6000 train / 2000 test / 5 epoch mỗi R — khớp 06 và
    argparse defaults của code.
  - [KHỚP] Lệnh chạy `python tools/ml_distinguisher.py --rounds 5,6,7
    --samples 6000 --epochs 5` — khớp 06 và docstring ví dụ trong code.
  - [KHỚP] Bảng accuracy 0.5970 / 0.5245 / 0.5070 (R = 5/6/7) — khớp từng chữ số
    với bảng trong 06; cách đọc (rõ rệt / yếu / gần đoán mò) khớp.
- Thuật ngữ & logic 4 phần:
  - [KHỚP] P1 (§1): hộp đen A/B, ngưỡng 50%, "rò rỉ cấu trúc", "bài kiểm tra
    tối thiểu", phân biệt cổ điển vs ML kiểu Gohr — chuẩn xác.
  - [KHỚP] P2 (§2): mô tả thí nghiệm (mã toy rút gọn, tạo mẫu, mô hình, đọc
    kết quả) đúng 06 + code; "~2 giây" khớp 06 (lưu ý nhỏ: docstring dòng 11
    của code ghi "vài phút" đã cũ — không phải lỗi của NCKH-026, doc 07 theo
    đúng số của 06).
  - [KHỚP] P3 (§3): 4 lý do (một mạng + một ngân sách; attacker không bị giới
    hạn; khẳng định phổ quát vs mẫu hữu hạn; chuẩn mực = thuật toán chuẩn +
    nhiều năm phân tích công khai, ref nghiên cứu 05) — logic đúng, khớp bài
    học 3-4 của 06, không suy luận quá đà.
  - [KHỚP] P4 (§4): tóm tắt đúng, không thêm khẳng định mới.
  - [KHỚP] Liên kết đọc kèm 06-ml-distinguisher.md tồn tại.
- Phạm vi: NCKH-026 khai chỉ tạo đúng 1 file mới, không sửa file khác, không
  commit. Kiểm: file 07 tồn tại đúng 9212 bytes; git chưa có commit nào nên
  không diff được, nhưng khung giờ 01:50-02:00 các file khác đổi đều thuộc việc
  của agent khác chạy song song (docs/07, runbooks, BOM, sổ NCKH-013/015/016/
  017/019/020/021/022/024/025/027/028) — không có dấu hiệu NCKH-026 chạm file
  repo khác. Không phát hiện vi phạm phạm vi.
- Kết luận: [KIEM-DINH] đạt — tài liệu đúng số liệu, đúng thuật ngữ, logic
  4 phần vững, phạm vi đúng 1 file mới.
- Unresolved: không có (về phía NCKH-026). Lưu ý cho Viện trưởng: (1) thẻ
  Kanzo 164 của NCKH-026 vẫn ở todo do tác giả chưa tự move doing->review;
  (2) docstring tools/ml_distinguisher.py dòng 11 ("vài phút") vênh với "~2 giây"
  trong 06/07 — nên sửa ở việc khác, ngoài phạm vi NCKH-026.
- Đồng bộ Kanzo (thẻ 164 "[ML] Tài liệu distinguisher cho người mới (NCKH-026)",
  status todo, tôi là người kiểm chéo được chỉ định):
  - GET board: 2 lần đầu 500, lần 3 OK (mỗi lệnh cách 5s, timeout 30s).
  - Comment: OK ngay lần đầu — comment id 32 "[KIEM-DINH] dat ..." (2026-11-20
    19:05:46Z).
  - Move sang done: HẾT 3 lần (PUT 405 Method Not Allowed; PATCH 500;
    POST /move 500) — Kanzo không nhận lệnh move. Nhờ Viện trưởng move tay
    thẻ 164 todo -> done theo kết luận đạt.
