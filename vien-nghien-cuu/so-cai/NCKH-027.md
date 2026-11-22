# Sổ cái NCKH-027 — Trần Bình (nhóm firmware, đợt 2A)

## 2026-11-21 — nhận việc
- Nhiệm vụ: Chốt mã module N16R8 — đối chiếu chữ in shield với tài liệu Espressif, cập nhật BOM (theo phan-cong.json).
- File được sửa (sản phẩm): `hardware/BOM.md` — đúng 1 file.
- Đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-027 trong `vien-nghien-cuu/phan-cong.json`, `vien-nghien-cuu/so-cai/README.md`, `hardware/BOM.md`, `docs/03-phan-cung.md`, `hardware/wiring.md`, `hardware/keys.md`, ảnh `docs/assets/62256.jpg`, `62257.jpg`, `65436.jpg`.
- Ghi chú: `HIEN-CHUONG.md` và `phan-cong.json` nằm dưới `vien-nghien-cuu/` (không ở root workspace).
- Trạng thái Kanzo: sẽ đồng bộ cuối việc (GET board → move + comment).


## 2026-11-21 — báo cáo
- Đã làm: chốt module ESP32-S3-WROOM-1-N16R8 (flash 16 MB + PSRAM 8 MB, Octal SPI); sửa đúng 1 file sản phẩm hardware/BOM.md (dòng Board + thêm mục Đối chiếu mã module N16R8 + cập nhật mục Kiểm tra khi nhận board).
- Bằng chứng: ảnh docs/assets/62256.jpg (dải N8R2/N8R8/N16R8, không có N26R8); PDF DEVKITC-1-N16R8V tr.53 nguyên văn 16 MB flash + 8 MB PSRAM, tr.51; User Guide N16R8 (WROOM-1, Octal, GPIO35-37 bận nội bộ).
- Tự kiểm: đọc lại hardware/BOM.md sau sửa, đủ 30 dòng, đúng nội dung; git status chỉ 2 file thay đổi (BOM.md + sổ cái của mình).
- Unresolved: chưa xác nhận vật lý chữ in trên shield (không có board trong tay) — để lại việc cho người cầm board.



## 2026-11-21 — đồng bộ Kanzo
- GET /api/board: thử 1 hỏng 500 Internal Server Error, thử 2 (sau 5s) thành công — đọc được 21 thẻ (NCKH-001..021).
- Kết quả: KHÔNG có thẻ nào của NCKH-027 (việc Chốt mã module N16R8) trên bảng → không có move/comment nào để thực hiện.
- Ghi chú: thẻ id=159 (NCKH-019) ghi NCKH-027 là người kiểm chéo, nhưng đó không phải việc được giao trong phan-cong.json nên không chạm vào (một việc một chủ). Không tự tạo thẻ mới — nhờ Viện trưởng tạo thẻ giúp.
- Trạng thái việc: xong phần file, chờ review.



## 2026-11-21 — đính chính mục báo cáo
- Dòng tự kiểm ghi sai: repo chưa có commit nào nên git status hiện toàn bộ file là untracked, không dùng để đếm file thay đổi được.
- Đính chính: trong phiên này tôi chỉ gọi edit trên đúng 1 file sản phẩm hardware/BOM.md (2 lần edit) + tạo 1 file sổ cái của mình vien-nghien-cuu/so-cai/NCKH-027.md; không chạm file nào khác, không git commit.

## 2026-11-21 — kiểm chéo NCKH-019 (Mai An, khảo sát PQC trên S3), đợt 2A
- Vai: Trần Bình (NCKH-027), nhóm firmware, lượt KIỂM CHÉO (khác nhóm với PQC).
- Đối tượng: `vien-nghien-cuu/so-cai/NCKH-019.md` (báo cáo mlkem-native khả thi nhưng KHÔNG đưa vào firmware) + thẻ Kanzo id 159 (đang review).
- Phương pháp (ĐƯỜNG KHÁC tác giả): Mai An tra tài liệu công khai rồi tổng hợp; tôi đối chiếu độc lập từng số liệu gốc
  với nguồn công khai KHÁC (upstream mlkem-native, paper arXiv, repo ESP32 độc lập, tài liệu Yubico/FIDO) + đánh giá lại
  lập luận CTAP theo đặc tả hiện tại. Không sửa file nào ngoài sổ này, không git commit.

### Đối chiếu 1 — flash mlkem-native ≈ 11,3 KB: KHỚP
- NCKH-019 ghi: .text 10.831 B + .rodata 448 B ≈ 11,3 KB (nguồn: blog Aethyr Edge Node).
- Kiểm độc lập: mở lại blog gốc aethyrresearch.com/blog/post-quantum-esp32-edge-node — nguyên văn
  "ML-KEM operations added just 10,831 bytes of code (.text) and 448 bytes of constants (.rodata)";
  swap kyber-ref → mlkem-native chỉ tốn thêm 1.802 B flash trên tổng firmware 832 KB → "không đáng kể" là đúng.
- Nguồn độc lập thứ hai: repo Saxich/mlkem-esp32 (không liên quan Aethyr) có project comparison/mlkem-native
  build mlkem-native v1.0.0 trên ESP32/ESP-IDF (menuconfig: ML-KEM-768, MLKEM_NATIVE_ARITH_BACKEND_C) → khẳng định
  độc lập rằng mlkem-native build được trên Xtensa/ESP-IDF bằng backend C thuần, đúng như NCKH-019 kết luận.

### Đối chiếu 2 — stack đỉnh 18,8 KB / task 24 KB: CÙNG BẬC ĐỘ LỚN, có lưu ý +10%
- NCKH-019 ghi: stack đỉnh 18,8 KB cả chu trình keygen+encap+decap; task FreeRTOS 24 KB an toàn.
- Kiểm độc lập: (a) blog Aethyr nguyên văn "Stack usage: full cycle peaked at 18,812 bytes... 24KB task stack is
  minimum safe size" → trích dẫn chính xác. (b) paper arXiv độc lập đo trên RP2040 (Cortex-M0+, nhóm khác, chip khác):
  ML-KEM-768 decap đỉnh 14,2 KB — cùng bậc độ lớn; full-cycle ≥ decap-riêng nên 18,8 KB trên Xtensa là hợp lý.
- Lưu ý mới (không làm đổi kết luận): release notes upstream mlkem-native v1.3.0 ghi "Correct decapsulation stack
  measurements, which previously returned before the full operation and understated peak stack use by around 10%".
  Aethyr đo trên v1.0.0 → số decap có thể thiếu ~10%; ước tính hiệu chỉnh ~20,7 KB, vẫn < 24 KB và << SRAM 512 KB.
  Khuyến nghị: khi tái hiện (U4 của NCKH-019) dùng mlkem-native ≥ v1.3.0 và cộng biên +10% vào số stack cũ.

### Đánh giá lập luận "CTAP không có chỗ cho KEM": ĐÚNG với đặc tả hiện tại
- PIN/UV auth protocol: tài liệu Yubico (CTAP2 PIN/UV auth protocol v1/v2) xác nhận dùng ECDH key agreement
  (P-256) để lập kênh mã hóa PIN — không có slot KEM trong thương lượng pinUvAuthProtocol (chỉ protocol 1/2, đều ECDH).
- Chuẩn PQC của FIDO: ghi nhận nghiên cứu độc lập Authkestra webauthn-pqc-spike (2026-09-02): WebAuthn L3
  Recommendation 2026-08-25 KHÔNG có PQC; chỉ có IETF individual draft draft-vitap-ml-dsa-webauthn-04 (về ML-DSA,
  tức chữ ký — không phải KEM); FIDO mới ở mức PQC Study Group + white paper 2024, chưa có CTAP PQC profile nào
  được công bố; CTAP 2.3 đã ra mắt mà không kèm thuật toán PQC nào.
- Nuance: hướng PQC của FIDO/WebAuthn hiện tập trung vào chữ ký (ML-DSA), không phải KEM; KEM chỉ liên quan nếu
  thay DH trong PIN protocol / hmac-secret — mà đó mới là ý tưởng nghiên cứu (vd. bài E2E PQC FIDO2 cho rằng
  "CTAP DH-based subroutine can be instantiated with a KEM" về mặt lý thuyết), chưa chuẩn hóa. Nhúng ML-KEM vào
  pico-fido hôm nay đúng là fork sâu không RP/browser nào hiểu — điểm 1 và 2 của NCKH-019 đứng vững.
- Trả lời một phần U2 của NCKH-019: tính đến 2026-09, chưa có draft CTAP/WebAuthn PQC chính thức nào (ngoài
  individual IETF draft về ML-DSA); điều kiện mở lại "FIDO chuẩn hóa PQC" vẫn chưa xảy ra.

### Kết luận kiểm định: ĐẠT
- Số liệu trích đúng nguồn gốc; đối chiếu độc lập cùng bậc độ lớn; lập luận CTAP đúng với đặc tả hiện tại;
  kết luận "KỸ THUẬT ĐƯỢC, SẢN PHẨM CHƯA — KHÔNG đưa vào firmware" hợp lý và có cơ sở.
- Yêu cầu sửa: KHÔNG có (chỉ 2 ghi nhận không bắt buộc: cộng biên stack +10% khi tái hiện; U2 đã có đáp án một phần).
- Đề nghị thẻ 159: review -> done.

## 2026-11-21 — đồng bộ Kanzo (thẻ 159, opportunistic)
- GET board: OK lần 1 (đọc được bảng, thẻ 159 status=review, comments=1).
- POST comment [KIEM-DINH] ĐẠT: OK ngay lần 1.
- POST move review->done: HỎNG cả 3 lần (lần đầu + 2 thử lại, cách 5s, timeout 30s) — HTTP 500 cả 3 lần.
- GET đối chiếu lại: HỎNG (HTTP 500) — đúng bệnh nghẽn SQLite đã biết.
- Nhờ Viện trưởng vá giúp khi Kanzo sống lại: move thẻ 159 -> done (comment kiểm định đã lên OK).

