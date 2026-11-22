# Sổ cái NCKH-029 — Phạm Bình (nhóm tailieu, Viện, đợt 2B)

## 2026-11-21 02:22 — nhận việc

- Thẻ: [tailieu] Viết FAQ dự án (mã NCKH-029, id Kanzo tra cuối việc qua GET board)
- Người nhận: Phạm Bình (NCKH-029)
- Việc nhận (theo `phan-cong.json` + lệnh giao việc): gom các câu hỏi đã gặp trong
  quá trình làm dự án thành FAQ có trả lời. File mới duy nhất: `docs/FAQ.md`.
  Ràng buộc: shell BẮT BUỘC `shell='pwsh'`, tiếng Việt, không git commit.
- Tài liệu đã đọc TRƯỚC khi làm:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, toàn bộ)
  - mục NCKH-029 trong `vien-nghien-cuu/phan-cong.json` (Phạm Bình, tailieu,
    thành viên, đợt 2, "Viết FAQ dự án", loại t1-tay-chon)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu nhật ký, luật file-trước-bảng-sau)
  - `vien-nghien-cuu/NHIP-TIM.md` + `vien-nghien-cuu/KHOI-DONG.md` (luật ghi Kanzo,
    trình tự đợt)
- Trạng thái: todo -> doing (dự kiến; đồng bộ Kanzo opportunistic cuối việc,
  Kanzo đang chập chờn theo lệnh giao việc)

## 2026-11-21 02:22 — đang làm: phạm vi nguồn đã đọc

- `docs/`: 00-y-tuong-goc.txt, 01..07 (.md), 2 runbook hwtest
  (windows/ubuntu), toàn bộ `docs/research/01..07`.
- `README.md` gốc repo.
- Sổ cái: khung + câu hỏi toàn bộ `NCKH-001..028` (trích tiêu đề/dòng hỏi),
  đọc sâu `NCKH-003` (race echo), `NCKH-014` (CNN), `NCKH-016` (hid_echo),
  `NCKH-019` (PQC trên S3), `NCKH-020` (Gohr), `NCKH-022` (biên Shamir),
  `NCKH-023` (chính tả 51 mục), `NCKH-025` (bọc S hybrid), `NCKH-027` (BOM N16R8),
  `NCKH-028` (fuzz parse_share); `NHIP-TIM.log` 13 dòng (01:53-02:21).
- Ghi chú phạm vi file: lệnh giới hạn "chỉ được tạo đúng 1 file mới" là
  `docs/FAQ.md` (deliverable); file sổ cái này là nhật ký bắt buộc theo
  Hiến chương §file-trước-bảng-sau và lệnh "ghi tiến độ TRƯỚC", tạo trước
  deliverable. Không sửa file repo nào khác, không git commit.

## 2026-11-21 02:22 — báo cáo

- Đã làm: tạo mới `docs/FAQ.md` (file deliverable duy nhất): 91 câu hỏi có trả
  lời + nguồn, 10 nhóm (dự án chung, phần cứng, nạp firmware, dùng key,
  bảo mật, sao lưu, tool kiểm thử, PQC, ML/Gohr, quy trình Viện) + bảng 15
  unresolved gom từ sổ cái. Nguồn: toàn bộ `docs/` (00-07, 2 runbook,
  research 01-07), `README.md`, sổ `NCKH-001..028`, `NHIP-TIM.log`.
- Tự kiểm (shell pwsh): script trích 23 link nội bộ duy nhất → 13 link file
  tồn tại đủ 13/13 (10 "thiếu" còn lại là anchor # trong cùng file, đúng ngữ
  cảnh); đếm `###` = 91 câu hỏi; 10 heading `##` khớp mục lục.
- Không sửa file repo nào khác ngoài sổ cái này + `docs/FAQ.md`; không git commit.
- Trạng thái: doing -> review (dự kiến; đồng bộ Kanzo opportunistic bên dưới).

## 2026-11-21 02:22 — đồng bộ Kanzo (KHÔNG CÓ THẺ, đã ghi sổ)

- `GET /api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s,
  shell pwsh): lần 1 HỎNG 500 Internal Server Error, lần 2 OK — bảng có 34 thẻ.
- KHÔNG có thẻ nào mang mã NCKH-029 (bảng mới có thẻ NCKH-001..028 + 5 thẻ
  FIX/DOC/OPS + thẻ NCKH-022/023 mới tạo). Không thử move/comment (không có id
  đích; cố gọi mò sẽ ghi nhầm thẻ người khác).
- Không tự tạo thẻ mới theo lệnh giao việc. Sổ cái này là kênh báo cáo duy nhất.
- Nhờ Viện trưởng khi tạo thẻ: [tailieu] Viết FAQ dự án (Phạm Bình NCKH-029),
  dán comment báo cáo (mục báo cáo 02:22 trong sổ này) + move todo -> doing
  -> review giúp. Nội dung việc ĐÃ XONG, chờ kiểm chéo.

## Unresolved

1. Thẻ Kanzo NCKH-029 chưa tồn tại trên bảng → nhờ Viện trưởng tạo + move giúp.
2. 15 câu hỏi unresolved trong `docs/FAQ.md` (mục cuối) chờ các nhóm/đợt sau.

## 2026-11-21 02:40 — kiểm chéo đợt 2B: NCKH-037 Hồ Bình (tài liệu đe dọa lượng tử)

- Vai: Phạm Bình (NCKH-029), kiểm độc lập bằng ĐƯỜNG KHÁC (không đọc lại văn mà
  đối chiếu từng khẳng định với code thật + kiến thức chuẩn Shor/Grover).
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-037.md` (3 mục 02:22/02:30/02:35),
  `docs/de-doa-luong-tu.md` (toàn bộ 5 mục), `tools/vault.py`, `tools/split_secret.py`,
  `tools/mnemonic.py`, `tools/pqc.py`, `docs/06-bao-mat.md`, `docs/07-sao-luu-va-khoi-phuc.md`.
- Đối chiếu nhóm VỠ (khẳng định → code/chuẩn → kết quả):
  1. FIDO ECDSA P-256 vỡ hoàn toàn (Shor suy private từ public trên server) →
     khớp mô hình 06 ("private key không rời chip", credential gắn domain);
     Shor phá log rời rạc đường cong là kiến thức chuẩn → ĐÚNG.
  2. PIN CTAP2 ECDH P-256 vỡ, "thu hoạch hôm nay giải mã ngày mai", mức thực tế
     thấp hơn 1.1 vì phải nghe đúng phiên → đúng chuẩn CTAP2 (pinUvAuthToken qua
     ECDH P-256), tự hạ mức nguy hiểm là đánh giá công bằng → ĐÚNG.
  3. Chữ ký Secure Boot ECDSA/RSA vỡ, nêu rõ là vấn đề chung không riêng board →
     khớp 06 (Secure Boot V2 + Flash Encryption); Shor suy khóa ký từ public là
     đúng nguyên tắc → ĐÚNG.
- Đối chiếu nhóm CÒN:
  4. Két AES-256-GCM + PBKDF2-HMAC-SHA256 600.000 vòng → khớp từng hằng số code
     (`PBKDF2_ROUNDS=600_000`, `hashes.SHA256()`, `length=32`, `AESGCM`);
     Grover còn ~128 bit + mật khẩu là hex(S) 256 bit ngẫu nhiên thật (khớp 07:
     S 32 byte) → ĐÚNG.
  5. SHA-256/SHA-512 còn, chỉ nhận "chống tiền ảnh còn nửa bit", checksum chỉ bắt
     lỗi gõ → khớp code (`hashlib.sha256` checksum, `pbkdf2_hmac` sha512 2048 vòng);
     không nhận bừa về chống va chạm lượng tử → ĐÚNG, phạm vi chuẩn.
  6. Shamir GF(256) "miễn nhiễm tuyệt đối", dưới ngưỡng biết đúng 0 bit → khớp code
     (đa thức AES x^8+..., hệ số ngẫu nhiên `secrets.randbelow`, Lagrange) và lý
     thuyết thông tin; RNG dùng CSPRNG nên không có lỗ hổng nguồn ngẫu nhiên → ĐÚNG.
  7. Cụm 24 từ = mã hóa 256 bit entropy, không có khóa công khai → khớp code
     (`VALID_BITS 256:24`) và 07 (24 từ cho 256 bit + checksum) → ĐÚNG.
  8. Mã hóa flash AES còn, tách bạch với chữ ký vỡ → đúng bản chất đối xứng +
     khớp 06 (Flash Encryption riêng với Secure Boot) → ĐÚNG.
- Bảng tổng hợp 8 dòng: khớp từng mục 1.1–2.5, không thừa không thiếu → ĐÚNG.
- Kiểm 4 ưu tiên sửa (logic + nhất quán với 06/07):
  - Ưu tiên 1 (theo dõi chuẩn PQC FIDO, cấm tự chế): đúng — thuật toán nằm trong
    WebAuthn/CTAP2 + firmware pico-fido, ngoài code dự án; chờ chuẩn + nâng cấp +
    đăng ký lại là đường duy nhất; viện dẫn nguyên tắc không-tự-chế của 07 → HỢP LÝ.
  - Ưu tiên 2 (giữ hầm đối xứng, cấm hạ cấp AES-256/SHA-256+/K>N/2): đúng là bất
    biến 0 chi phí, khớp code hiện tại và quy tắc ngưỡng đa số của 07 → HỢP LÝ.
  - Ưu tiên 3 (vận hành lưới phi-FIDO: 2 key + diễn tập 3 đường mỗi 6 tháng +
    ket.bin để đâu cũng được): suy ra trực tiếp từ 06 (quy tắc hai key) và 07
    (3 đường, diễn tập 6 tháng), làm ngay rẻ → HỢP LÝ.
  - Ưu tiên 4 (giữ `pqc.py` ML-KEM-768 xanh, bọc KEM khi share đi mạng công cộng,
    chữ ký lai chờ Espressif): khớp code (`ALG="ML-KEM-768"`, đúng chuẩn FIPS 203),
    khớp 07 (share hiện chỉ đi Bluetooth/QR/cáp), điều kiện "nếu sau này" nên
    không vẽ việc thừa → HỢP LÝ, thứ tự thấp nhất đúng.
- Góp ý nhỏ (không trừ đạt): mục 1.1 có thể nêu tên ứng viên chữ ký PQC cho FIDO
  (ML-DSA/SLH-DSA) để người đọc khỏi tưởng ML-KEM (trao đổi khóa ở ưu tiên 4)
  dùng để ký đăng nhập; tài liệu hiện tại không sai, chỉ có thể rõ hơn.
- Sổ NCKH-037: ghi đủ nhận việc/báo cáo/Kanzo, quyết định KHÔNG tự tạo thẻ khi
  không thấy là đúng lệnh → sổ SẠCH.
- Đồng bộ Kanzo (shell pwsh, timeout 30s, cách nhau 5s):
  - GET board lần 1: 500; lần 2: OK nhưng parse thô; lần 3 (raw): HTTP 200,
    project esp32-securitykey total=43; lần 4: 500; lần 5: OK — 44 thẻ
    (done=26, todo=18, không có thẻ nào ở review/doing), tìm 'NCKH-037' trong
    title/description chỉ trúng id=176 là thẻ "[tailieu] Viết FAQ dự án (NCKH-029)"
    (trúng ở description nhắc 037, không phải thẻ của NCKH-037); lần 6–7: 500, 500
    (hết 2 thử lại).
  - Kết luận: KHÔNG có thẻ riêng cho NCKH-037 trên bảng → KHÔNG comment/move
    (comment nhầm vào thẻ NCKH-029 của chính mình sẽ gây nhiễu), KHÔNG tự tạo thẻ.
    Sổ này là kênh báo cáo duy nhất.
- KẾT LUẬN KIỂM CHÉO: **ĐẠT** — mọi khẳng định crypto đối chiếu đúng với code thật
  và kiến thức chuẩn; 4 ưu tiên logic, nhất quán 06/07, thứ tự đúng; sổ sạch.
- Unresolved của lượt kiểm này: nhờ Viện trưởng tạo thẻ NCKH-037 (hoặc xác nhận
  xong trên sổ) và dán giúp comment `[KIEM-DINH] đạt — Phạm Bình (NCKH-029):
  8/8 khẳng định crypto khớp code (vault AES-GCM+PBKDF2-600k, Shamir GF(256),
  mnemonic SHA-256/PBKDF2-SHA512, pqc ML-KEM-768) và chuẩn Shor/Grover; 4 ưu tiên
  logic, nhất quán docs/06+07; sổ sạch; góp ý nhỏ: nêu tên ML-DSA/SLH-DSA ở ưu
  tiên 1 để khỏi nhầm với ML-KEM` + move review -> done giúp.
