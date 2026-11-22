# Sổ cái — Trịnh An (NCKH-017), nhóm tailieu, đợt 2A

## 2026-11-21 01:52 — nhận việc
- Thẻ: [TAILIEU] Sơ đồ luồng khôi phục (mã NCKH-017, id Kanzo sẽ đối chiếu ở cuối việc)
- Nhiệm vụ (theo phan-cong.json): Vẽ 3 đường khôi phục cho 07
  (tức docs/07-sao-luu-va-khoi-phuc.md)
- Phạm vi sửa repo: CHỈ đúng 1 file docs/07-sao-luu-va-khoi-phuc.md
- Đã đọc trước khi làm: vien-nghien-cuu/HIEN-CHUONG.md,
  mục NCKH-017 trong vien-nghien-cuu/phan-cong.json, vien-nghien-cuu/so-cai/README.md,
  docs/07-sao-luu-va-khoi-phuc.md (126 dòng, chưa có sơ đồ ASCII nào)
- Ghi chú: file sổ cái này chưa tồn tại trước khi tạo nên tạo mới thay vì nối thêm
- Kế hoạch: chèn mục mới "Sơ đồ ba đường khôi phục" (sơ đồ ASCII + giải thích)
  vào giữa mục "Một bí mật gốc, ba đường khôi phục" và mục "Ngưỡng đa số";
  không chạm bất kỳ file repo nào khác; không git commit
- Trạng thái: todo -> doing (thử Kanzo opportunistic ở cuối việc)

## 2026-11-21 01:56 — báo cáo
- Đã làm: chèn mục mới "Sơ đồ ba đường khôi phục" vào docs/07-sao-luu-va-khoi-phuc.md,
  giữa mục "Một bí mật gốc, ba đường khôi phục" và mục "Ngưỡng đa số",
  gồm: sơ đồ ASCII 33 dòng trong code block ```text (MẤT ESP CHÍNH tỏa 3 nhánh:
  đường 1 key FIDO dự phòng đăng nhập thẳng không cần S; đường 2 gom >=K share
  Shamir chạy combine ra S; đường 3 gõ 24 từ to-entropy ra S; hội tụ S -> hex
  -> vault.py decrypt ket.bin -> mã khôi phục -> vào tài khoản, gỡ key mất,
  đăng ký key mới) + đoạn mở đầu + phần "Đọc sơ đồ" 4 gạch đầu dòng tiếng Việt
  có dấu + dòng ký tên (Sơ đồ: Trịnh An, NCKH-017). Sơ đồ dùng tiếng Việt không
  dấu để thẳng hàng tuyệt đối. Không chạm bất kỳ file repo nào khác, không git commit
- Tự kiểm: script pwsh quét mọi ký tự neo (+, |, v) trong code block —
  phân nhánh/3 nhánh/box/hội tụ đều thẳng 100% (trục 12/38/64, viền box tại
  0/23/26/49/52/75, hội tụ cuối đối xứng +@12/38/64 với 38 là trung điểm);
  3 chữ "v" còn lại là chữ cái trong từ thường (vd, ve, vault, vu), không phải
  mũi tên; code fence mở/đóng cân bằng (đếm được 2); đọc lại toàn mục sau khi
  sửa, markdown hợp lệ, nội dung cũ hai bên giữ nguyên
- Trạng thái: doing -> review (thử Kanzo opportunistic tiếp)

## 2026-11-21 01:57 — Kanzo báo cáo (opportunistic, THẤT BẠI, dừng thử)
- GET /api/board?project=esp32-securitykey -> cả 3 lần đều lỗi 500
  (Internal Server Error), mỗi lần cách nhau 5s, timeout 30s, đã hết quota
  (tối đa 2 lần thử lại). Không đọc được bảng nên không xác định được id thẻ
  của NCKH-017 -> KHÔNG thử move/comment (tránh ghi nhầm sang thẻ người khác)
- Kết luận: Kanzo nghẽn hoàn toàn lúc này, dừng mọi thử đọc/ghi thêm. Toàn bộ
  bằng chứng công việc nằm trong sổ cái này; nhờ Viện trưởng đối chiếu và vá
  thẻ NCKH-017 lên review khi Kanzo sống lại
- Trạng thái thực tế công việc: ĐÃ XONG, chờ review (cần peer khác nhóm tailieu)

## 2026-11-21 02:06 — kiểm chéo đợt 2A: đặc tả NCKH-025 (Hà An, bọc S bằng ML-KEM)

- Vai: Trịnh An (NCKH-017) kiểm độc lập công việc của Hà An (NCKH-025).
  Lúc đọc, sổ NCKH-025 đã có mục đến 02:10. REPO CHỈ ĐỌC (chỉ nối thêm
  chính sổ này), shell pwsh, không git commit.
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-025.md` (toàn bộ),
  `tools/pqc.py` (297 dòng), `tools/split_secret.py` (308 dòng),
  `tools/vault.py` (đầu file, xác nhận lib), `docs/07-sao-luu-va-khoi-phuc.md`
  (S 32 byte, ngưỡng đa số, két vault), `vien-nghien-cuu/NHIP-TIM.md` (luật Kanzo).

### Tính toán độc lập (đường khác, tự chạy lại)

1. Cộng kích thước gói PQC-WRAP-V1 (pwsh):
   12+2+2+2+16+12+2+1088+2+32+16+32 = 1218. Phép cộng của NCKH-025 ĐÚNG
   với giả thiết magic = 12 byte.
2. PHÁT HIỆN 1 (sai đặc tả, phải sửa trước khi code): chuỗi
   `PQC-WRAP-V1` dài 11 ký tự (đếm bằng pwsh `$s.Length`), KHÔNG phải 10
   như sổ NCKH-025 ghi. Vậy "10 ký tự + 2 byte 0x00 0x01" mâu thuẫn với
   magic 12 byte: nếu giữ nguyên chuỗi thì magic = 13 byte và tổng gói =
   1219, không phải 1218. Người code phải chốt một trong hai: (a) magic 12
   byte = `PQC-WRAP-V` (10 ký tự) + 2 byte phiên bản, hoặc (b) magic 13 byte
   và sửa tổng thành 1219 + tiêu chí chấp nhận số 1. Lỗi đếm chữ, không phải
   lỗi thiết kế.
3. Probe Shamir với sk 2400 byte (chạy thật `tools/split_secret.py`):
   split 2400 byte 5/3 cho share dài đúng 2400 byte, hex 4800 ký tự,
   file 4855 byte (khớp "hex ~4800 ký tự + header"); cả 10 tập con 3 share
   đều combine ra đúng sk; 2 share không ra sk. Khả thi, khớp đặc tả.
4. PHÁT HIỆN 2 (khẳng định tương thích SAI, đã chứng minh bằng chạy thật):
   đề xuất "thêm trường `kind=S|SK`, parser cũ vẫn đọc được" là SAI.
   `parse_share` gọi `int(val)` cho MỌI cặp key=value nên header có
   `kind=SK` bị parser cũ từ chối với `invalid literal for int(): 'SK'`
   (chạy thật). Cách sửa: dùng kind DẠNG SỐ (ví dụ `kind=1|2`) — đã kiểm
   chứng parser cũ đọc được và bỏ qua khóa lạ. Đây mới là "mở rộng tương
   thích" thật.
5. Trộn share S (len=32) với share sk (len=2400): `combine` từ chối sạch
   ("các share không cùng độ dài..."). Khớp đặc tả và tiêu chí số 6.
6. Đối chiếu `tools/pqc.py`: pk 1184 / sk 2400 / ct 1088 / ss 32 khớp
   docstring; đọc kích thước từ `kem.details` (không hardcode) khớp;
   `_read_exact` tồn tại khớp; mã thoát 2 khi thiếu lib khớp; từ chối ngầm
   (self-test bước 3-4) khớp phân tích an toàn. ĐÚNG hết.
7. Đối chiếu `tools/vault.py`: dùng lib `cryptography` (AESGCM, PBKDF2HMAC,
   SHA256), salt 16 + nonce 12 — cùng họ với salt 16/nonce 12/HKDF-SHA256
   của đặc tả. Khẳng định "cùng lib với vault.py" KHẢ THI (HKDF có sẵn trong
   cùng lib `cryptography.hazmat.primitives.kdf.hkdf`).
8. Khẳng định "share sk 2400 byte KHÔNG chuyển bằng QR": ĐÚNG. QR chứa tối đa
   ~4296 ký tự chữ-số ở mức sửa lỗi thấp nhất (nhị phân ~2953 byte), file
   share ~4855 ký tự vượt xa. Chuyển bằng file là đúng.
9. Toán ngưỡng: K=3 > 5/2 (đa số) ĐÚNG; mất dưới N-K+1=3 nơi thì còn >=3,
   vẫn khôi phục được — ĐÚNG.
10. HKDF/AAD: HKDF-SHA256(ss 32B, salt 16B, info cố định, L=32) chuẩn,
    domain separation tốt, salt/nonce mới mỗi lần bọc ĐÚNG nguyên tắc.
    PHÁT HIỆN 3 (mơ hồ nhỏ): AAD ghi "từ magic đến hết ct (tức mọi thứ trước
    C)" — nhưng `c_len` nằm giữa ct và C. Nếu AAD dừng ở hết ct thì `c_len`
    không được xác thực, mâu thuẫn chữ "mọi thứ". Đề nghị chốt: AAD = mọi byte
    từ magic đến hết `c_len` (tức toàn bộ trước C). Rủi ro thực tế gần như
    không có (parser đã kiểm tra c_len=32), chỉ cần viết rõ một dòng.
11. R1/R2 khép kín: R1 đủ 6 bước (tải gói -> đối chiếu fingerprint sổ giấy
    -> gom 3 share -> combine -> decap/HKDF/giải GCM -> đối chiếu 24 từ +
    mở két + xóa vết), mỗi bước đều có điều kiện dừng sạch. R2 đủ 4 bước
    (khôi phục -> sinh mới/bọc lại/chia lại -> thu hồi cũ + cập nhật sổ ->
    diễn tập, cấm tái dùng salt/nonce/ct). Hai lưu ý nhỏ, không trừ điểm:
    (a) bước R1.3 viện dẫn kiểm tra `kind=SK` trong khi kind chưa tồn tại —
    đến lúc code xong kind thì khép, trước đó dùng kiểm tra (n,k,len);
    (b) R2.3 "xóa gói cloud cũ" trên drive có lưu phiên bản có thể không xóa
    thật, và rotation không thu hồi được share cũ đã lọt ra ngoài — đây là
    giới hạn cố hữu của share offline, nên ghi thêm một dòng rủi ro còn lại.

### Kết luận kiểm chéo: ĐẠT (với 3 mục bắt buộc sửa trước khi code)

- Thiết kế hybrid KEM+DEM đúng chuẩn, không chế thuật toán mới, tái dùng đúng
  3 công cụ/lib hiện có, số liệu đối chiếu khớp, quy trình dựng/khôi phục/
  luân chuyển khép kín, probe thực thi xác nhận phần Shamir khả thi.
- 3 mục NCKH-025 (hoặc thẻ code tiếp theo) phải sửa trong đặc tả: (1) chốt
  magic 12 hay 13 byte và tổng 1218 hay 1219; (2) kind dạng số, không phải
  `S|SK`; (3) viết rõ AAD có gồm `c_len` không. Cả 3 đều là sửa một dòng,
  không đổi kiến trúc nên vẫn ĐẠT.
- Comment Kanzo dự kiến: `[KIEM-DINH] ĐẠT — cộng lại gói đúng 1218 (với
  magic 12B); Shamir 5/3 trên sk 2400B chạy thật đạt 10/10 tập con; R1/R2
  khép kín. 3 mục sửa trước khi code: magic 11 ký tự≠10 (chốt 1218/1219),
  kind phải dạng số (parser cũ từ chối kind=SK), AAD làm rõ c_len.`

### Kanzo (THẤT BẠI, đúng luật opportunistic)

- `GET /api/board?project=esp32-securitykey`: 3/3 lần HTTP 500, mỗi lần cách
  5s, timeout 30s, đã hết quota (tối đa 2 thử lại).
- Không đọc được bảng nên không có id thẻ NCKH-025 -> KHÔNG thử comment/move
  (tránh ghi nhầm thẻ người khác, đúng tiền lệ các sổ NCKH-002/007/008/011).
- Nhờ Viện trưởng khi Kanzo sống lại: comment `[KIEM-DINH] ĐẠT` lên thẻ
  NCKH-025 theo nội dung trên và move review -> done giúp.
- Unresolved: (1) 3 mục sửa đặc tả chờ NCKH-025 xác nhận; (2) chưa đồng bộ
  Kanzo do sập 500 (việc kiểm định đã xong, không kẹt việc).
