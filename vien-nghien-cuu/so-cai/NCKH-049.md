# Sổ cái NCKH-049 — Tạ Bình (nhóm PQC, thành viên, đợt 2C)

## 2026-11-21 03:10 — nhận việc

- Người nhận: Tạ Bình (NCKH-049)
- Việc nhận: Nghiên cứu ký số PQC — ML-DSA/SLH-DSA cái nào hợp để ký bản tin firmware sau này. So sánh kích thước chữ ký.
- Tài liệu đã đọc TRƯỚC khi làm (theo lệnh giao việc):
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, đã đọc toàn bộ)
  - mục NCKH-049 trong `vien-nghien-cuu/phan-cong.json` (Tạ Bình, nhóm PQC, thành viên, đợt 2, nhiệm vụ "Nghiên cứu ký số PQC", loại t1-tay-chon)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu nhật ký sổ cái)
- Tài liệu repo đọc thêm (REPO CHỈ ĐỌC, phục vụ bối cảnh):
  - `vien-nghien-cuu/NHIP-TIM.md`, `vien-nghien-cuu/QUYET-DINH.md`, `vien-nghien-cuu/KHOI-DONG.md`
  - `docs/de-doa-luong-tu.md` (mục 1.3 chữ ký Secure Boot vỡ dưới Shor; ưu tiên 4: chữ ký firmware lai cổ điển + PQC, chờ Espressif, không tự vá bootloader)
  - `docs/04-firmware.md` (hai tầng firmware, pico-fido v8.2, secure boot V2), `docs/06-bao-mat.md`
  - `tools/pqc.py` (ML-KEM-768 qua liboqs — tầng KEM đã có, chưa có tầng ký số)
- Quy tắc: tiếng Việt, shell pwsh, không git commit, repo chỉ đọc. Ghi sổ TRƯỚC, đồng bộ Kanzo sau (opportunistic).
- Trạng thái thẻ: todo -> doing (dự kiến; đối chiếu Kanzo ở mục cuối)

## 2026-11-21 03:10 — quá trình nghiên cứu

### Phạm vi

- So sánh ML-DSA (FIPS 204, tên cũ Dilithium) với SLH-DSA (FIPS 205, tên cũ SPHINCS+) ở 3 trục: kích thước chữ ký, kích thước khóa công khai, tốc độ.
- Số liệu lấy từ tài liệu công khai (chuẩn NIST FIPS 204/205 và các bảng tổng hợp công khai), không đo mới, không chạy code repo (task nghiên cứu thuần túy).
- Mục tiêu sử dụng: ký bản tin firmware sau này (ký offline trên máy tính, xác thực khi flash / kiểm tra trước khi nạp).

### 1. Kích thước khóa công khai và chữ ký (byte)

ML-DSA (FIPS 204) — 3 bộ tham số:

| Bộ tham số | Mức an toàn NIST | Khóa công khai | Khóa bí mật | Chữ ký |
|---|---|---|---|---|
| ML-DSA-44 | Level 2 (≈ AES-128) | 1312 | 2560 | 2420 |
| ML-DSA-65 | Level 3 (≈ AES-192) | 1952 | 4032 | 3309 |
| ML-DSA-87 | Level 5 (≈ AES-256) | 2592 | 4896 | 4627 |

SLH-DSA (FIPS 205) — 12 bộ tham số (SHA2/SHAKE × 128/192/256 × s/f); `s` = small (chữ ký nhỏ, ký chậm), `f` = fast (ký nhanh hơn, chữ ký to gấp ~2 lần). Kích thước không phụ thuộc SHA2 hay SHAKE:

| Bộ tham số | Mức an toàn NIST | Khóa công khai | Khóa bí mật | Chữ ký |
|---|---|---|---|---|
| SLH-DSA-128s | Level 1 | 32 | 64 | 7856 |
| SLH-DSA-128f | Level 1 | 32 | 64 | 17088 |
| SLH-DSA-192s | Level 3 | 48 | 96 | 16224 |
| SLH-DSA-192f | Level 3 | 48 | 96 | 35664 |
| SLH-DSA-256s | Level 5 | 64 | 128 | 29792 |
| SLH-DSA-256f | Level 5 | 64 | 128 | 49856 |

So sánh cùng mức an toàn:

- Level 1/2: ML-DSA-44 (pk 1312 B, sig 2420 B) vs SLH-DSA-128s (pk 32 B, sig 7856 B) — SLH-DSA khóa công khai nhỏ hơn ~40 lần, nhưng chữ ký to hơn ~3,2 lần.
- Level 3: ML-DSA-65 (pk 1952 B, sig 3309 B) vs SLH-DSA-192s (pk 48 B, sig 16224 B) — chữ ký SLH-DSA to hơn ~4,9 lần (bản `f` to hơn ~10,8 lần).
- Level 5: ML-DSA-87 (pk 2592 B, sig 4627 B) vs SLH-DSA-256s (pk 64 B, sig 29792 B) — chữ ký SLH-DSA to hơn ~6,4 lần (bản `f` ~10,8 lần, gần 50 KB).

### 2. Tốc độ (bậc độ lớn, CPU x86-64 từ benchmark công khai liboqs/eBACS)

- ML-DSA: ký ~0,05–0,3 ms/lần (hàng nghìn–chục nghìn lần/giây), xác thực ~0,05–0,15 ms/lần (hàng chục nghìn lần/giây). Nhanh hơn SLH-DSA từ 1 đến 3 bậc độ lớn ở chiều ký.
- SLH-DSA bản `s`: ký chậm, ~10–100+ ms/lần (chỉ vài chục lần/giây); bản `f`: ký nhanh hơn, ~1–5 ms/lần (hàng trăm lần/giây). Xác thực ~0,5–2 ms/lần — chậm hơn ML-DSA khoảng 1 bậc nhưng vẫn chấp nhận được cho xác thực firmware (làm 1 lần mỗi lần flash).
- Trên vi điều khiển hạn chế (hướng ESP32-S3 sau này): ML-DSA verify nhẹ hơn nhiều (RAM/stack vừa phải, đã có bản triển khai embedded và được esp-pqc theo hướng lattice); SLH-DSA verify tốn tính toán băm lặp đi lặp lại, bản `s` ký quá chậm nếu thiết bị phải tự ký.

### 3. Giả thiết an toàn và định vị của NIST

- ML-DSA (lattice, Module-LWE): NIST chọn làm chữ ký số PQC dùng chung chính (primary). Hiệu năng tốt, kích thước cân bằng cả 3 thành phần.
- SLH-DSA (hash-based, không giả thiết đại số): NIST định vị là phương án dự phòng bảo thủ — an toàn chỉ dựa vào tính chất hàm băm, phòng trường hợp lattice bị phá. Đánh đổi: chữ ký rất to, ký chậm.
- Hệ quả thực tế: trừ khi có yêu cầu "không tin lattice", chuẩn chung của ngành là ML-DSA; SLH-DSA chỉ dùng khi cần bảo thủ tuyệt đối hoặc khi khóa công khai bắt buộc cực nhỏ (32–64 B).

### 4. Đối chiếu với bài toán ký firmware của dự án

- Kịch bản: ký offline trên máy tính (tốc độ ký không phải nút cổ chai), đính chữ ký vào bản tin firmware (~1–2 MB image pico-fido), xác thực trước khi flash / trong Secure Boot lai sau này.
- Chữ ký vài KB (ML-DSA ~2,4–4,6 KB) so với image MB là không đáng kể; chữ ký SLH-DSA 8–50 KB vẫn "chịu được" về dung lượng nhưng gây cồng kềnh cho manifest, QR/giấy (nếu in), và đặc biệt cho verify trên thiết bị hạn chế.
- Khóa công khai ML-DSA ~1,3–2,6 KB phải nhúng vào bootloader/vùng tin cậy — vẫn nhỏ so với flash 16 MB của ESP32-S3, không phải lý do loại ML-DSA. Lợi thế pk 32–64 B của SLH-DSA chỉ có ý nghĩa khi vùng tin cậy cực hẹp (không phải trường hợp này).
- Ràng buộc từ repo (`docs/de-doa-luong-tu.md` ưu tiên 4 + QD hiện hành): chữ ký firmware lai cổ điển + PQC, CHỜ Espressif hỗ trợ trên ESP32-S3, không tự vá bootloader. Nghiên cứu này là để sẵn, chưa triển khai.

### Nguồn công khai đã tra

- NIST FIPS 204 (ML-DSA) và FIPS 205 (SLH-DSA) — kích thước tham số chuẩn.
- Bảng tổng hợp: `hadamard.com/c/ml-dsa-vs-slh-dsa-signatures-compared` (ML-DSA vs SLH-DSA: Sizes, Speed, Use Cases), `starkquantum.com/pqc/signatures-ml-dsa-and-slh-dsa`, `fieldguide.lamarrlabs.com` (FIPS-204, SLH-DSA-parameter-sets, PQC-at-a-Glance), `postquantum.wiki/slh-dsa`, `duokey.com` (ML-DSA sizes), `quantakrypto.com/guides/ml-dsa-vs-slh-dsa`.
- Benchmark tốc độ: số liệu liboqs / eBACS được các nguồn trên trích dẫn (bậc độ lớn, x86-64).

## 2026-11-21 03:10 — báo cáo

- Đã làm: đọc hiến chương + phân công + sổ README + tài liệu repo liên quan; tra tài liệu công khai về ML-DSA/SLH-DSA; lập bảng so sánh kích thước pk/sk/sig cho toàn bộ 3 bộ ML-DSA và 6 họ SLH-DSA; so sánh tốc độ theo bậc độ lớn; đối chiếu với bài toán ký firmware và ràng buộc "chờ Espressif" của repo; đưa khuyến nghị dưới đây. REPO CHỈ ĐỌC — không sửa file nào ngoài sổ cái này, không git commit.
- Tự kiểm: lệnh `Get-ChildItem -Force vien-nghien-cuu` + `so-cai` -> liệt kê thành công (HIEN-CHUONG.md, phan-cong.json, 40+ sổ NCKH-001..044, chưa có NCKH-049); lệnh trích `phan-cong.json` bằng `ConvertFrom-Json` -> đúng mục NCKH-049 (Tạ Bình, PQC, đợt 2); `Select-String` toàn `docs/`, `tools/`, `README.md` -> xác nhận repo mới chỉ có ML-KEM-768 (KEM), chưa có chữ ký số PQC nào, khớp `docs/de-doa-luong-tu.md`; tra cứu web 5 lượt (FIPS 204, FIPS 205, so sánh tốc độ, SLH-DSA level 3/5, định vị NIST) -> số liệu các nguồn khớp nhau. Không có lệnh nào ghi ngoài sổ cái này.
- Khuyến nghị: **chọn ML-DSA (cụ thể ML-DSA-65, level 3) cho ký bản tin firmware sau này.**
  - Lý do 1 — chữ ký nhỏ hơn nhiều: 3309 B so với 16224–35664 B của SLH-DSA cùng level 3 (nhỏ hơn ~5–11 lần), gọn cho manifest firmware và mọi kênh phân phối.
  - Lý do 2 — tốc độ vượt trội: ký nhanh hơn 1–3 bậc, xác thực nhanh hơn ~1 bậc; verify nhẹ phù hợp thiết bị hạn chế sau này.
  - Lý do 3 — là chuẩn chính của NIST cho chữ ký dùng chung; SLH-DSA chỉ là dự phòng bảo thủ. Đi theo chuẩn chính thì sau này tương thích với hỗ trợ của Espressif/pico-fido dễ hơn.
  - Lý do 4 — nhược điểm duy nhất của ML-DSA (pk ~2 KB so với 32–64 B của SLH-DSA) không thành vấn đề vì flash ESP32-S3 16 MB dư chỗ nhúng khóa công khai.
  - Điều kiện kèm theo: giữ nguyên ràng buộc repo — triển khai dạng lai cổ điển + PQC và CHỜ Espressif hỗ trợ, không tự vá bootloader (theo `docs/de-doa-luong-tu.md` ưu tiên 4). Nếu sau này có yêu cầu bảo thủ "không tin lattice" thì mới xét SLH-DSA-128s/192s làm phương án B.
- Trạng thái thẻ: doing -> review (dự kiến; đồng bộ Kanzo opportunistic ở mục dưới)
- Unresolved:
  - U1: chưa đối chiếu số đo tốc độ thực tế trên liboqs cụ thể của repo (`.tooling/oqs`) vì task chỉ yêu cầu số liệu tài liệu công khai — có thể giao thẻ đo benchmark khi cần.
  - U2: chưa chốt dạng lai (concatenation vs composite OID, thứ tự verify) — thuộc thẻ thiết kế sau, ngoài phạm vi nghiên cứu này.
  - U3: trạng thái thẻ Kanzo của NCKH-049 (xem mục Kanzo dưới).

## 2026-11-21 03:12 — đồng bộ Kanzo (opportunistic, THẤT BẠI — Kanzo sập)

- GET `/api/board?project=esp32-securitykey` (timeout 30s, mỗi lần cách nhau 5s): THẤT BẠI cả 3 lần (lần đầu + 2 thử lại), đều `500 Internal Server Error`.
- Không đọc được bảng nên không tìm được thẻ mang mã NCKH-049; không thử move/comment (không có id thẻ, đúng luật không tự tạo thẻ).
- Kết luận: thẻ NCKH-049 (nếu có) giữ nguyên trạng thái trên bảng; Viện trưởng/nhịp tim đối chiếu và vá bảng khi Kanzo sống lại (theo QD-003: sổ file là nguồn chân lý khi Kanzo sập). Sổ cái file này là nguồn sự thật duy nhất cho nhiệm vụ NCKH-049.

## 2026-11-21 03:28 — kiểm chéo NCKH-056 đợt 2C (KẾT LUẬN: ĐẠT)

- Vai: Tạ Bình (NCKH-049, nhóm PQC) kiểm độc lập NCKH-056 Phan Cường (nhóm ML) — khác nhóm, đúng luật kiểm chéo Hiến chương §2. Đối tượng: "Đề xuất thí nghiệm tiếp theo: Simon hay Skinny?" (Simon32/64 trước, SKINNY sau + thẻ Speck song song). Đã đọc toàn bộ `vien-nghien-cuu/so-cai/NCKH-056.md` (3 mục).
- Nguyên tắc kiểm: ĐƯỜNG KHÁC — không tin trích dẫn của tác giả mà tự tra nguồn gốc + tự tính lại số học: (1) mở trực tiếp bài báo Hou et al. 2021 (Wiley, open access) đối chiếu từng chênh lệch/số accuracy; (2) đối chiếu khổ mã Simon/Speck/SKINNY với đặc tả công khai + code `tools/ml_distinguisher.py`; (3) tính lại ngân sách CPU và ngưỡng thống kê bằng pwsh từ số đo NCKH-002/038. REPO CHỈ ĐỌC (trừ sổ này); không git commit; mọi lệnh shell dùng `shell="pwsh"`.

### Kiểm 1 — Tái dùng pipeline Simon: CÓ THẬT
- Bài báo Hou et al. Table 10/11: SIMON32/64 = khối 32, khóa 64, từ 16 bit, 32 vòng; SPECK32/64 = khối 32, khóa 64, từ 16 bit, α=7 β=2, 22 vòng — khớp từng chữ với code (`MASK16`, `ALPHA=7`, `BETA=2`, `FULL_ROUNDS=22`) và với khẳng định §3-mục-1 của đề xuất.
- Suy ra: đặc trưng 64 bit nối cặp bản mã + MLP 64->128->64->1 (`MLP.w1` shape (64,128) trong code) tái dùng nguyên vẹn, chỉ thay encrypt/mở rộng khóa/chênh lệch. Khẳng định "so sánh công bằng (cùng mạng, cùng tiền)" đứng vững.
- Điểm trừ duy nhất đã được tác giả tự khai: nhãn-0-kiểu-Gohr đòi sửa `make_dataset` (hiện nhãn 0 là 64 bit ngẫu nhiên thuần, `docs/research/06` + code dòng 123-127) — đề xuất ghi rõ ở §4, không giấu việc.

### Kiểm 2 — Chênh lệch Abed et al. và các số trích từ bài báo 2021: TỒN TẠI, TRÍCH ĐÚNG
- Tự mở bài báo (Wiley 10.1155/2021/9288229), đối chiếu từng số:
  - SIMON32/64 (0x0,0x40) ← Ref[17] Abed et al., 9 vòng, 59.07% (Table 3) — khớp §4 "chênh lệch chính".
  - SIMON32/64 (0x0,0x80) ← Algorithm 1 của chính bài báo (SAT solver, KHÔNG phải Abed), 9 vòng, 59.77% (Table 3) — tác giả ghi nguồn "bài báo 2021", KHÔNG gán nhầm cho Abed (§3-mục-3, §4) — đúng.
  - 8 vòng SIMON32/64 82.2% ← Ref[10] Benamira et al. Eurocrypt 2021 (Table 1) — khớp §3-mục-3.
  - SPECK32/64 (0x2800,0x10) 8 vòng 56.49% ← định dạng MOD k=32 (Table 7) — khớp §6, và tác giả ghi đúng "MOD, không phải SCP".
  - Chênh lệch Gohr Speck (0x40,0x0) trong bài báo khớp `FIXED_DX/DY` của tool.
- Phát hiện nhỏ (không ảnh hưởng kết luận): Table 6 của bài báo ghi SCP (0x0,0x80) 9 vòng = 59.07%, lệch với Table 3 (59.77%) — mâu thuẫn nội bộ của bài báo (có vẻ lỗi đánh máy, hoán đổi với số Abed). Dù lấy số nào, tín hiệu >55% ở 9 vòng với ResNet vẫn tồn tại, nên luận điểm "chắc chắn có tín hiệu ở vòng thấp để đối chứng pipeline" của đề xuất không suy suyển.
- SKINNY-64-128: khối 64 + TK-2 → 36 vòng (đặc tả SKINNY: 64-bit block với t=n/2n/3n → 32/36/40 vòng) — khớp §5-mục-2. Tác giả KHÔNG bịa chênh lệch SKINNY mà giao cho thẻ đọc tài liệu — trung thực.

### Kiểm 3 — Ngân sách "dưới 3 phút CPU": KHỚP SỐ ĐO NCKH-002/038
- Neo kiểm tra: NCKH-002 (0.5–0.6s/vòng ở 6k/5ep) và NCKH-038 (x10 = 23.6s tool / 25.19s wall, gen R=8 1.45s, train ≈ 22.1s) — các số này được đề xuất trích lại chính xác (đã đối chiếu từng sổ).
- Tự tính lại bằng pwsh: gen/x10 = 1.45/23.6 = 6.1% (≈6% như đề xuất); train = 22.15s (≈22.1s); tổng GĐ1+Speck ở biên trên (5s sweep + 35s x10 + 1s + 25s + 5s self-test) ≈ 71s < 180s — còn biên 2.5 lần. Wall ước (~10s + ~40s + ~35s ≈ 85s) cũng dưới 3 phút. Khẳng định "DƯỚI 3 PHÚT" ĐÚNG.
- Số SKINNY là ước thô ±2 lần do tác giả tự gắn nhãn "chưa có số đo" + bắt thẻ implement đo thật trước khi mở sweep x10 (§6, §7) — cách trình bày trung thực, chấp nhận được cho đề xuất.

### Kiểm 4 — Tiêu chí thành công/thất bại (§8): ĐO ĐƯỢC, TÍNH ĐÚNG
- Tự tính lại: σ(test 2000) = √(0.25/2000) = 0.01118 (≈0.0112 như đề xuất); ngưỡng 0.525 = 2.24σ (≈2.2σ); σ(test 10k) = 0.005; ngưỡng 0.515 = đúng 3.00σ. Số học chính xác.
- Tính đo được: cổng 0 (vector khớp nguồn ngoài + round-trip nhiều R 0 lỗi + kiểm chéo độc lập, theo mẫu NCKH-032) đo được; ngưỡng đạt (≥0.525 @2k hoặc ≥0.515 @10k + lặp ≥2 seed) đo được; đối chứng dương R=3–4 ≥0.55 đo được; điều kiện fail (mù cả R thấp → bug pipeline, không được rào đón) phân biệt rõ "âm tính thật" với "bug" — đây là điểm mạnh nhất của §8.
- Ranh giới diễn giải (âm tính ≠ mã an toàn) giữ đúng cảnh báo của `docs/research/06` §Bài học.

### Phát hiện thêm (có lợi cho tác giả)
- Test vector Simon32/64 mà tác giả ghi "theo trí nhớ, CHƯA xác minh" (khóa 1918 1110 0908 0100, pt 6565 6877 → ct c69b e9bb): kiểm chéo xác minh ĐÚNG qua 2 nguồn độc lập (patent Justia US20220158819 + luận văn Stony Brook, cả hai trích bảng vector chuẩn NSA). Tuy vậy vẫn giữ nguyên tắc cổng 0: người implement phải đối chiếu đặc tả gốc, không dùng số trí nhớ làm cổng đạt/không đạt.
- Bảng hiện trạng §1 trích đúng cả 6 thẻ (đã đối chiếu NCKH-002/008/038 từng số; NCKH-014/020/032 khớp nội dung đã đọc ở đợt trước).

- KẾT LUẬN KIỂM CHÉO: ĐẠT. Đề xuất Simon-trước-SKINNY-sau + thẻ Speck song song khả thi: pipeline tái dùng có thật, mọi chênh lệch/số accuracy trích đúng nguồn (Abed + Hou et al. 2021 + Benamira), ngân sách <3 phút CPU khớp số đo với biên 2.5 lần, tiêu chí §8 đo được và tính đúng. Chỗ chưa xác minh được tác giả tự khai báo đầy đủ, không phát hiện số liệu bịa.
- Tự kiểm: exit code 0 ở lệnh tính pwsh; bài báo đọc trực tiếp (không qua trung gian); không chạy lại lệnh của tác giả (thẻ này chỉ viết văn bản, không có lệnh để chạy lại — đường kiểm là tra nguồn + tính lại).
- Unresolved: không về nội dung. (Kanzo: xem mục đồng bộ dưới.)

## 2026-11-21 03:28 — đồng bộ Kanzo kiểm chéo NCKH-056: THẤT BẠI, nhờ Viện trưởng vá
- `GET /api/board?project=esp32-securitykey` (timeout 30s, mỗi lần cách nhau 5s, shell pwsh): THẤT BẠI cả 3 lần (lần đầu + 2 thử lại), đều `500 Internal Server Error` — đúng triệu chứng SQLite khóa DB trong Hiến chương §6.
- Không đọc được bảng nên không tìm được thẻ NCKH-056 (bản thân tác giả ở mục 03:25 cũng báo chưa thấy thẻ này trên bảng — 61 tasks, 0 hit); không thử comment/move (không có id thẻ, đúng luật không tự tạo thẻ).
- Nhờ Viện trưởng khi Kanzo sống lại: (1) tạo thẻ [ML] Đề xuất thí nghiệm tiếp theo (NCKH-056) nếu chưa có, cho đi todo -> doing -> review; (2) comment `[KIEM-DINH] ĐẠT — pipeline tái dùng có thật, chênh lệch Abed/bài báo 2021 trích đúng, ngân sách <3 phút khớp số đo, tiêu chí §8 đo được (chi tiết ở sổ NCKH-049 mục 03:28)` của NCKH-049; (3) move thẻ review -> done.
- Trạng thái thật của việc kiểm chéo: ĐÃ XONG, kết luận ĐẠT; nội dung kiểm định đầy đủ nằm ở mục trên.
