# Nghiên cứu 06 — Distinguisher nơ-ron kiểu Gohr trên Speck32/64 rút gọn

Thí nghiệm học tập: huấn luyện MLP nhỏ phân biệt đầu ra của mã toy
Speck32/64 sau R vòng (chênh lệch bản rõ cố định) với dữ liệu ngẫu nhiên.
Script: `tools/ml_distinguisher.py` (numpy thuần, chạy CPU vài giây).

Kết luận trước: mạng phân biệt được ở ít vòng và "mù" dần khi tăng vòng —
đây là minh họa thám mã bằng ML, không phải bằng chứng an toàn.

## Thiết lập

- Mã toy: Speck32/64 tự cài đặt (encrypt + decrypt + mở rộng khóa),
  chạy rút gọn R = 5, 6, 7 vòng (chuẩn đầy đủ là 22 vòng).
- Chênh lệch bản rõ cố định: (dx, dy) = (0x0040, 0x0000), theo phong cách Gohr.
- Mẫu "thật": cặp bản rõ lệch nhau đúng chênh lệch trên, cùng khóa ngẫu nhiên,
  mã hóa R vòng; đặc trưng là 64 bit nối của cặp bản mã (nhãn 1).
- Mẫu "giả": 64 bit hoàn toàn ngẫu nhiên (nhãn 0). Tập cân bằng 50/50.
- Mô hình: MLP 64 -> 128 -> 64 -> 1 (ReLU + sigmoid), tối ưu Adam,
  mất mát BCE. Ngân sách nhỏ: 6000 mẫu train, 2000 mẫu test, 5 epoch mỗi R.
- Lệnh chạy: `python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000 --epochs 5`
- Tự kiểm nhanh: `python tools/ml_distinguisher.py --self-test`
  (kiểm vector + round-trip + micro-train 400 mẫu/1 epoch).

## Độ đúng của mã cài đặt

- Round-trip decrypt(encrypt(p)) == p: PASS (200 khóa/bản rõ ngẫu nhiên,
  kiểm ở cả R = 5 và R = 22). Đây là cổng kiểm tra tính đúng chính.
- Test vector Speck32/64 (key 1918 1110 0908 0100, pt 6574 694c
  -> ct a868 42f2): khớp khi chạy cục bộ với k0 là từ cuối
  (k0=0x0100, k1=0x0908, k2=0x1110, k3=0x1918). Trạng thái: **chưa xác nhận** —
  phiên này không đối chiếu được nguồn tin cậy độc lập ngoài repo,
  nên vector chỉ mang tính tham khảo, không dùng làm cổng đạt/không đạt.

## Kết quả quan sát (seed 1337, CPU)

| R (số vòng) | Accuracy trên 2000 mẫu test | Nhận xét |
|-------------|-----------------------------|----------|
| 5 | 0.5970 | Phân biệt rõ trên mức đoán mò 0.50 |
| 6 | 0.5245 | Còn tín hiệu yếu |
| 7 | 0.5070 | Gần như đoán mò |

Thời gian: ~2 giây cho cả 3 mức R (sinh dữ liệu + huấn luyện).

## Bài học

1. Thám mã bằng ML là thật: với chênh lệch tốt và ít vòng, MLP rẻ tiền
   cũng học được đặc trưng vi sai mà mắt thường không thấy.
2. Thêm vòng giết distinguisher nhanh: chỉ từ R = 5 lên R = 7, accuracy
   đã rơi từ ~0.60 về ~0.51. Đúng vai trò của số vòng trong thiết kế mã khối.
3. Quan trọng nhất: mã "chống được mạng này" không phải bằng chứng an toàn.
   Kết quả âm tính chỉ nói mạng cụ thể này, với ngân sách cụ thể này,
   không tìm ra gì — kẻ tấn công thật không bị giới hạn đó. Chuẩn mực an toàn
   vẫn là phép toán chuẩn + nhiều năm phân tích công khai (xem nghiên cứu 05).
4. Không dùng mã toy rút gọn vòng vào sản phẩm: script này chỉ phục vụ học
   và minh họa trong `docs/research`, mọi khóa thật của dự án vẫn dùng
   phép toán đã kiểm chứng.
