# Nghiên cứu 05 — QGAC: mật mã do AI tiến hóa (đánh giá)

Tài liệu này lưu ý tưởng gốc trong thư mục `QGAC/ý tưởng.txt` kèm đánh giá kỹ thuật.
Kết luận trước: đây là đề tài nghiên cứu, không phải hướng xây mật mã dùng thật.

## Ý tưởng gốc tóm tắt

Kết hợp Rust + mô phỏng lượng tử + CUDA + PyTorch + TensorFlow + JAX để AI tự
sinh và tự tấn công thuật toán mã hóa (gọi là Quantum Generative Adversarial
Cryptography). Ba sản phẩm đề xuất: mã hóa biến hình mỗi phiên, lattice PQC do
AI tối ưu nhỏ hơn chuẩn NIST, và QKD mô phỏng có mạng nơ-ron phát hiện nghe lén.

## Phần có thật

- AI hỗ trợ thám mã là lĩnh vực nghiên cứu nghiêm túc: mạng nơ-ron tìm đặc trưng
  vi sai (Gohr 2019 với Speck), học sâu tấn công kênh kề (side-channel).
- Mật mã kháng lượng tử có thật ở chuẩn NIST: ML-KEM (FIPS 203), ML-DSA, SLH-DSA,
  sau 8 năm bị phân tích công khai. Vòng NIST cũng gãy nhiều ứng viên (Rainbow,
  SIKE bị phá năm 2022 bằng tấn công cổ điển) — minh chứng vì sao phép toán mới
  cần nhiều năm "bị đánh" mới tin được.
- Rust viết crypto constant-time và quản lý bộ nhớ an toàn là thực hành tốt.
- CUDA hữu ích cho kiểm thử vét cạn, benchmark và huấn luyện mô hình tấn công.

## Phần chưa đứng

1. Đối kháng GAN chỉ chứng minh mã chống được đúng con AI tấn công trong phòng lab.
   Kẻ tấn công thật không giới hạn trong những gì mạng Eve học được, nên "không AI
   nào giải được" là tuyên bố không kiểm chứng được.
2. Mô phỏng 50+ qubit không chứng minh kháng lượng tử thật. Kháng lượng tử chỉ tin
   được qua bài toán khó đã nghiên cứu sâu (lattice, hash) cộng nhiều năm phân tích.
3. QKD mô phỏng trên GPU cộng mạng nơ-ron vẫn là mô phỏng. QKD thật cần phần cứng
   lượng tử (nguồn và detector photon đơn); không có phần cứng thì không có phân phối
   khóa lượng tử.
4. Mã hóa biến hình mỗi phiên đòi hai bên đồng bộ trạng thái hoàn hảo, tăng độ phức
   tạp mà an toàn không hơn stream cipher chuẩn. Phức tạp là kẻ thù của bảo mật.
5. "Nhỏ hơn NIST nhưng kháng hoàn toàn" không thể xác thực nếu thiếu phân tích công
   khai đa năm. Lịch sử SIKE cho thấy trực giác về độ khó rất dễ sai.

## Hướng làm thật rút ra từ ý tưởng

1. Tích hợp PQC chuẩn NIST qua thư viện đã kiểm chứng (`tools/pqc.py` dùng ML-KEM
   của liboqs). Đây mới là kháng lượng tử thật dùng được hôm nay.
2. Viết lại thành phần nhạy cảm bằng Rust khi cần hiệu năng và memory safety.
3. Thử nghiệm thám mã bằng ML trên mã toy (`tools/ml_distinguisher.py`) để học,
   không bao giờ dùng kết quả đó làm bằng chứng an toàn cho sản phẩm.

Nguyên tắc giữ cho dự án key: sản phẩm chỉ dùng phép toán chuẩn đã kiểm chứng.
Phần "riêng" là quy trình vận hành, không phải phép toán.
