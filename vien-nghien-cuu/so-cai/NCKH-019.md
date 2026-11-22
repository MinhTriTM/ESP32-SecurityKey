# Sổ cái NCKH-019 — Mai An (nhóm PQC, đợt 2A)

## 2026-11-21 01:53 — nhận việc
- Thẻ: [PQC] Khảo sát PQC trên ESP32-S3 (mã NCKH-019)
- Việc: thư viện PQC (ML-KEM) nào chạy được trên S3, tốn bao nhiêu RAM/flash; kết luận có nên đưa vào firmware không.
- Trạng thái: todo -> doing

## 2026-11-21 01:53 — báo cáo khảo sát ML-KEM trên ESP32-S3

### 1. Ngân sách phần cứng (board N16R8: flash 16 MB, PSRAM octal 8 MB)
- CPU Xtensa LX7 2 nhân, tối đa 240 MHz; SRAM nội 512 KB (heap app thực tế vài trăm KB tùy cấu hình).
- Không có lệnh tăng tốc lattice; không chạy được mã asm ARM (pqm4) hay AVX2.
- Tham chiếu repo: `hardware/BOM.md`, `docs/03-phan-cung.md`, `docs/04-firmware.md` (firmware dùng thật = pico-fido v8.2 trên ESP-IDF v5.5.1).

### 2. Ứng viên thư viện (đã tra tài liệu công khai)
| Thư viện | Chạy trên S3? | RAM (ML-KEM-768) | Flash | Tốc độ @240MHz | Giấy phép | Ghi chú |
|---|---|---|---|---|---|---|
| mlkem-native (pq-code-package) | CÓ, đã chứng minh (Aethyr Edge Node, ESP-IDF component) | stack đỉnh 18,8 KB cả chu trình; task FreeRTOS 24 KB an toàn | .text 10.831 B + .rodata 448 B ≈ 11,3 KB | keygen 9,05 ms / encap 10,07 ms / decap 12,2 ms | Apache-2.0 (code mới) | C90, formally verified, FIPS 203; backend C thuần (chưa có asm Xtensa); nhanh hơn kyber-ref ~20% |
| kyber reference / pqclean-pure C | CÓ (portable C) | tương đương mlkem-native (~15-20 KB stack) | ~10 KB | chậm hơn mlkem-native ~20% | CC0/MIT | Phương án dự phòng nếu không muốn API mới của mlkem-native |
| esp-pqc (Espressif, ML-KEM-768 + ML-DSA-65) | CÓ nhưng evaluation-only | chưa công bố ổn định | chưa công bố | chưa công bố | xem repo | Espressif ghi rõ "for evaluation only, not production-ready"; theo dõi, chưa dùng |
| pqm4 | KHÔNG | — | — | — | — | Chỉ ARM Cortex-M4 (asm), S3 là Xtensa LX7 → loại |
| liboqs nguyên bản | KHÔNG khả thi | ~900 KB heap (số liệu bài HVAC trên S3, vượt SRAM) | lớn | — | MIT | Giữ trên máy tính (`tools/pqc.py`), không đưa vào firmware |
| wolfSSL/wolfCrypt ML-KEM | Có thể (cần kiểm chứng build) | chưa đo | chưa đo | chưa đo | GPL/commercial dual | Dự phòng thương mại; chưa có số liệu S3 công khai trong tay |

Nguồn: github.com/pq-code-package/mlkem-native; aethyrresearch.com/blog/post-quantum-esp32-edge-node (số liệu đo S3);
github.com/espressif/esp-pqc; github.com/Saxich/mlkem-esp32 (so sánh 4 backend); bài HVAC arXiv 2609.27828 (liboqs 900 KB).

### 3. Kích thước đối tượng ML-KEM-768 (chuẩn FIPS 203, khớp `tools/pqc.py`)
- Public key 1184 B, secret key 2400 B, ciphertext 1088 B, shared secret 32 B.
- Khóa bí mật 2400 B vừa NVS + flash encryption hiện có, không cần thêm phần cứng.

### 4. Kết luận: KỸ THUẬT ĐƯỢC, SẢN PHẨM CHƯA — KHÔNG đưa vào firmware đợt này
- Về kỹ thuật: chi phí không đáng kể (~11 KB flash / 16 MB, ~24 KB stack / 512 KB SRAM, ~10 ms/op).
  Nếu đưa vào thì chọn **mlkem-native + ML-KEM-768** (đồng bộ với `tools/pqc.py`), backend C, task stack 24 KB.
- Vì sao chưa đưa:
  1. Firmware dùng thật là pico-fido (upstream AGPL ngoài repo); chuẩn CTAP 2.x hiện tại không có chỗ cho KEM
     (PIN protocol dùng ECDH P-256). Nhúng ML-KEM = fork sâu, mất khả năng theo upstream, không RP/browser nào hiểu.
  2. Chưa có đặc tả dùng ML-KEM vào việc gì trong key (mở khóa két? PIN protocol riêng?). Không nhúng thuật toán khi chưa có giao thức.
  3. esp-pqc chính chủ còn evaluation-only; đợi Espressif hoặc FIDO Alliance chốt chuẩn PQC rồi theo.
- Hướng đúng đợt này: giữ PQC ở tầng tool máy tính — két lai X25519+ML-KEM (NCKH-013), bọc bản sao S (NCKH-025).
  Điều kiện mở lại: FIDO chuẩn hóa PQC, hoặc thiết kế xong giao thức vendor riêng dùng ML-KEM ngoài CTAP.

### 5. Unresolved (cần người khác / đợt sau)
- U1: wolfSSL ML-KEM trên S3 tốn bao nhiêu (chưa có số liệu công khai trong tay).
- U2: FIDO Alliance đã có draft PQC nào cho CTAP/WebAuthn chưa (chưa tra, ảnh hưởng điều kiện mở lại).
- U3: pico-fido upstream còn bao nhiêu flash/SRAM trống sau build (chưa build kiểm chứng trên máy này — phụ thuộc NCKH-012/033).
- U4: Số liệu Aethyr đo trên ESP-IDF bản nào, cấu hình tối ưu nào (cần đối chiếu khi tái hiện).

- Tự kiểm: chỉ đọc repo (không sửa file nào ngoài sổ này); số liệu đều có URL nguồn công khai ở mục 2.
- Trạng thái: doing -> review

## 2026-11-21 01:5x — đồng bộ Kanzo (thẻ id 159)
- GET board: lần 1 hỏng 500, lần 2 OK (thẻ đang todo).
- MOVE todo->doing: OK. Comment nhận việc: OK. MOVE doing->review: OK.
- Comment báo cáo: hỏng cả 2 lần thử (500). GET đối chiếu lại cũng 500 (Kanzo chập chờn, đúng bệnh SQLite đã biết).
- Viện trưởng đối chiếu khi Kanzo sống lại: thẻ có thể đã ở review nhưng thiếu comment báo cáo — nội dung báo cáo đầy đủ nằm ở mục trên trong sổ này.

## 2026-11-21 — kiểm chéo NCKH-027 Trần Bình (chốt BOM N16R8) — KẾT LUẬN: ĐẠT
- Phạm vi kiểm: `vien-nghien-cuu/so-cai/NCKH-027.md` + mục mới trong `hardware/BOM.md` (dòng Board, mục Đối chiếu mã module N16R8, mục Kiểm tra khi nhận board). Repo chỉ đọc, không git commit.
- Đối chiếu 1 — ảnh `docs/assets/62256.jpg` (tự mở xem trực tiếp): chú thích ghi nguyên văn "ESP32-S3-WROOM-1 N8R2/N8R8/N16R8 module", khớp từng chữ với trích dẫn trong BOM; không có N26R8. ĐẠT.
- Đối chiếu 2 — file PDF reference tồn tại đúng tên trong `docs/reference/`: `ESP32-S3-DEVKITC-1-N16R8V_Espressif_Systems.pdf` (23.450.872 B) và `ESP32-S3-N16R8_User_Guide.pdf` (247.606 B). ĐẠT (tên file; số trang tr.51/53 chưa kiểm độc lập vì máy thiếu thư viện đọc PDF, không cài thêm).
- Quy ước đặt tên N<flash>R<PSRAM>: hợp logic — dải N8R2/N8R8/N16R8 khớp flash {8,16} MB + PSRAM {2,8} MB; N26R8 hàm ý flash 26 MB (không phải cỡ JEDEC, không có trong lineup Espressif). Quét repo: N26R8 chỉ còn ở dòng cũ `docs/03-phan-cung.md:5` (đã tự ghi ngờ là ghi nhầm), ghi chú "ghi nhầm" trong BOM và sổ cái — không xuất hiện trong tài liệu hay ảnh nào. ĐẠT.
- Phạm vi sửa: `phan-cong.json` giao NCKH-027 "cập nhật BOM" — đúng 1 file sản phẩm `hardware/BOM.md`. Bằng chứng: BOM.md + sổ NCKH-027 cùng phiên 21/11 01:57–01:58; `docs/03-phan-cung.md` giữ nguyên từ 20/11 (vẫn còn dòng cũ) nên tác giả không sửa lan; repo chưa có commit nên không đếm bằng git status được (tác giả đã tự đính chính điểm này trong sổ). ĐẠT. Chéo: sổ NCKH-023 ghi BOM tăng 21→30 dòng do NCKH-027; sổ NCKH-015 tham chiếu BOM:5,19-26 đã chốt — nhất quán.
- Kanzo http://100.101.100.100:4242/api (shell pwsh, timeout 30s, cách nhau 5s): GET board lần 1–2 hỏng 500; lần 3 OK nhưng output cắt trước khi tới thẻ ESP32; 3 lần lọc thẻ NCKH-027 sau đó đều 500. Hết số thử lại → không comment/move được, ghi sổ theo quy định. Tác giả cũng báo bảng chỉ có thẻ NCKH-001..021, không có thẻ NCKH-027 — nhờ Viện trưởng tạo thẻ và move giúp khi Kanzo sống lại.
- Unresolved: (1) chữ in vật lý trên nắp shield chưa ai xác nhận (không có board trong tay — tác giả đã khai báo, để lại cho người cầm board); (2) số trang PDF tr.51/53 chưa kiểm độc lập; (3) Kanzo chưa đồng bộ (comment kiểm định + move review→done còn treo).
