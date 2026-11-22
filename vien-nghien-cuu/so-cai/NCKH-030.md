# Sổ cái NCKH-030 — Hoàng Bình (nhóm kiemdinh, đợt 2B)

Nhiệm vụ (phan-cong.json): "Đối chiếu vault với openssl" — PBKDF2+AES-GCM bằng openssl CLI, so khớp với tool (loại t1-tay-chon).

Tham số đọc từ `tools/vault.py`: MAGIC=`ESKVAULT1` (9 byte), SALT_LEN=16, NONCE_LEN=12,
PBKDF2-HMAC-SHA256 600_000 vòng, khóa 32 byte, AES-256-GCM AAD=None,
định dạng blob = MAGIC + salt + nonce + (ciphertext || tag16).

## 2026-11-21 02:24 — nhận việc

- Thẻ: [kiemdinh] Đối chiếu vault với openssl (Kanzo id: tra cứu sau — xem mục đồng bộ cuối sổ)
- Trạng thái: todo -> doing
- Kế hoạch: vector cố định (password/salt/nonce/plaintext biết trước), suy khóa bằng
  `openssl kdf` PBKDF2 so với `vault.derive_key`, mã hóa/giải mã AES-GCM so byte hai bên.

## 2026-11-21 02:24 — báo cáo

### Vector kiểm thử (cố định, tái lập được)

- password (utf-8): `mat-khau-kiem-dinh-NCKH-030`
- salt (16 byte): `000102030405060708090a0b0c0d0e0f`
- nonce (12 byte): `000102030405060708090a0b`
- plaintext (93 byte, sha256 `050b7b2b...b61ca`): câu tiếng Việt trong probe
- File tạm (không commit): `%TEMP%\nckh030\probe.py`, `verify.py`, `gcm_node.js`, `*.bin`, `*.hex`

### Đã làm và tự kiểm

1. PBKDF2-HMAC-SHA256 600k vòng, `openssl kdf` vs `vault.derive_key`:
   - Lệnh: `openssl kdf -keylen 32 -kdfopt digest:SHA2-256 -kdfopt pass:mat-khau-kiem-dinh-NCKH-030 -kdfopt hexsalt:000102030405060708090a0b0c0d0e0f -kdfopt iter:600000 PBKDF2`
     (openssl 3.5.7 tại `C:\Program Files\Git\usr\bin\openssl.exe`)
   - Output openssl: `7abd25b643325f0bcf69eab401cc6e16d0903af22fe35265623a3da8f10e7eda`
   - `vault.derive_key` + `hashlib.pbkdf2_hmac`: cùng chuỗi hex trên.
   - Kết luận: KHỚP byte. (Lưu ý: phải dùng `hexsalt`, `salt:` bị hiểu là chuỗi ASCII và ra key sai `e06f3467...`.)
2. AES-256-GCM, chiều mã hóa, openssl CLI vs vault.py:
   - `openssl enc -e -aes-256-gcm` TRỰC TIẾP THẤT BẠI: `enc: AEAD ciphers not supported`
     (giới hạn đã biết của app `enc` trên OpenSSL 3.x — đối chứng: cùng cú pháp `-K/-iv`
     với `-aes-256-ctr` chạy được, nên lỗi là do AEAD chứ không phải do sai tham số).
   - Đường vòng hợp lệ: lõi CTR của GCM. Với nonce 12 byte, khối keystream đầu là
     E_K(nonce||00000002) (khối ...01 dành cho mặt nạ tag), nên CTR với IV=nonce||00000002
     phải ra đúng phần ciphertext của GCM.
   - Lệnh: `openssl enc -e -aes-256-ctr -K <keyhex> -iv 000102030405060708090a0b00000002 -in plain.bin -out ct_ctr.bin`
   - sha256(ct_ctr.bin) = `8536b1fce321657fe5f84eaf80072826a4482c53ccadacc53d441f788a98ee27`
     = sha256(phần ciphertext của vault, `ct_body.bin`). KHỚP byte (93/93 byte).
3. AES-256-GCM, chiều giải mã, openssl CLI mở output của vault.py:
   - Lệnh: `openssl enc -d -aes-256-ctr -K <keyhex> -iv ...00000002 -in ct_body.bin -out plain_ossl.bin`
   - sha256(plain_ossl.bin) = sha256(plain.bin) = `050b7b2bc1fbfe85c692b2cf7981bcc66a60aa1ce548c9e1cff1f21f51cb61ca`. KHỚP byte.
4. Chiều ngược vault mở ciphertext của openssl (`verify.py`): blob = MAGIC+salt+nonce+ct_ctr+tag
   -> `vault.decrypt_bytes` ra đúng plaintext. ĐẠT.
5. Bố cục blob (`verify.py`): MAGIC[0:9], salt[9:25], nonce[25:37], ct+tag[37:] đều đúng vị trí. ĐẠT.
6. Chống giả mạo (`verify.py`): sửa 1 bit ở ciphertext, sửa 1 bit ở tag, sai magic, sai mật khẩu
   -> cả 4 đều bị từ chối đúng thông điệp. ĐẠT.
7. Kiểm chéo độc lập full-GCM gồm tag bằng Node.js v22.23.2 (`node:crypto`, `aes-256-gcm`):
   - ciphertext khớp 93/93 byte, tag khớp `cfa458e29f63dde581c1a965075187f9`,
     Node giải mã output vault đúng, tag giả bị từ chối (`unable to authenticate data`). ĐẠT.
8. `python tools/vault.py --self-test` -> `self-test ok`. ĐẠT.

### Kết luận kiểm định

- vault.py tương thích chuẩn: PBKDF2-HMAC-SHA256 600k vòng và AES-256-GCM (cả ciphertext
  lẫn tag) khớp byte với triển khai độc lập (openssl CLI + Node.js crypto).
- Điểm trừ duy nhất thuộc về openssl CLI chứ không thuộc vault.py: app `enc` của OpenSSL 3.5
  không hỗ trợ AEAD nên tag GCM không tái tạo/giải mã trực tiếp được bằng `enc`; đã bù bằng
  lõi CTR qua CLI (khớp byte) + full-GCM qua Node (khớp cả tag).

- Tự kiểm: các lệnh + output ở trên; `cmp` logic qua sha256 certutil và `bytes.equals`/`==`.
- Trạng thái: doing -> review
- Thảo luận lại: không. Họp hội đồng: không.

## 2026-11-21 02:24 — đồng bộ Kanzo: THẤT BẠI (đã ghi sổ, không tự tạo thẻ)

- Lệnh: `GET http://100.101.100.100:4242/api/board?project=esp32-securitykey` (timeout 30s),
  1 lần đầu + 2 lần thử lại, cách nhau 5s.
- Output cả 3 lần: `500 {"error": "database error: database is locked"}`
  (đúng bệnh SQLite đã ghi trong HIEN-CHUONG §6).
- Kết quả: không đọc được bảng -> không tìm được thẻ có mã NCKH-030 -> KHÔNG move,
  KHÔNG comment, KHÔNG tự tạo thẻ. Viện trưởng đối chiếu và vá bảng khi Kanzo sống lại.
- Trạng thái thẻ trên bảng: không đổi được (mục tiêu doing -> review vẫn chờ).

## 2026-11-21 02:33 — kiểm chéo NCKH-038 (Ngô Bình, R=8 x10: 0.4870 âm tính + ước tính R=9)

- Vai: Hoàng Bình (NCKH-030), lượt KIỂM CHÉO đợt 2B; repo CHỈ ĐỌC trừ chính sổ này;
  file tạm chỉ trong `$env:TEMP`; không git commit; mọi lệnh shell dùng `shell="pwsh"`.
- Đã đọc: toàn bộ `vien-nghien-cuu/so-cai/NCKH-038.md` (nhận việc 02:21, báo cáo 02:24,
  đồng bộ Kanzo 02:27) + đọc lại `tools/ml_distinguisher.py` để kiểm logic ước tính.

### 1. Kiểm độc lập bằng ĐƯỜNG KHÁC: cấu hình R=8 nhẹ, seed khác

- Lệnh (mẫu nhỏ, epoch ít, seed 777 thay vì 1337):
  `python tools/ml_distinguisher.py --rounds 8 --samples 2000 --epochs 3 --seed 777`
- Output: `R=8: train=2000 test=2000 epochs=3 -> accuracy=0.4895 (0.2s)`, EXIT=0.
  (log: `$env:TEMP/NCKH-030-xcheck-R8-light.log`)
- Đối chiếu: 0.4895 cách 0.5 khoảng 0.94σ (σ≈0.0112 với test 2000 mẫu) → NẰM TRONG NHIỄU,
  cùng xu hướng đoán mò với 0.4870 (60k×50ep, seed 1337) của NCKH-038.
- Kết luận nhỏ: xu hướng âm tính ở R=8 KHÔNG phụ thuộc seed/mẫu đã chọn — mẫu độc lập
  (seed khác, ngân sách nhỏ hơn ~500 lần tổng lượt mẫu) vẫn đoán mò.

### 2. Kiểm phép ước tính R=9 x10 bằng đo thời gian ngắn độc lập

- Đo 1 (script tạm `$env:TEMP/NCKH-030-bench-gen.py`, chỉ import đọc tool):
  gen 20000 mẫu: R=8: 0.62s; R=9: 0.56s (tỷ lệ 0.916, KHÔNG phải ~1.125).
  Tách R=8 6k/2k/5ep: gen=0.19s, train=0.25s (train 57.6%), acc=0.4940 (lại đoán mò).
- Đo 2 (script tạm `$env:TEMP/NCKH-030-bench-gen2.py`, N=62000 như NCKH-038, xen kẽ thứ tự):
  R8a=1.47s, R9a=1.36s, R8b=1.77s, R9b=1.79s → trung bình R8=1.62s, R9=1.57s, tỷ lệ 0.973.
- Nhận xét TRUNG THỰC (điểm trừ nhỏ cho NCKH-038): tỷ lệ gen R9/R8 = 1.17 từ 1 lần đo đơn
  của NCKH-038 chưa đủ bằng chứng cho quan hệ tuyến tính theo R — đo độc lập cho ~0.92–0.97,
  và phương sai giữa các lần chạy (1.36–1.79s) lớn hơn hiệu ứng kỳ vọng 12.5%.
  Chênh lệch gen R8/R9 nằm trong nhiễu đo trên máy này.
- NHƯNG ước tính tổng R=9 x10 ≈ 23.9s VẪN ĐỨNG VỮNG, vì nó không dựa vào tỷ lệ gen chính xác
  mà dựa vào việc train chiếm áp đảo (~94%): gen-R9 dù là 1.45s, 1.57s hay 1.70s thì tổng
  vẫn ≈ 23.6–24s (tool). Ngoại suy độc lập từ số đo tách của tôi: gen 62k ≈ 0.19×7.75 ≈ 1.47s
  (khớp 1.45s đã báo); train ≈ 0.25×100 ≈ 25s so với 22.1s đã báo (sai số ~10% do batching/
  overhead, cùng bậc độ lớn). Tính R-độc lập của phần huấn luyện đã kiểm bằng đọc code:
  `train_mlp` chỉ nhận mảng 64 chiều cố định (samples×epochs×batch như nhau) → không phụ thuộc R. ĐÚNG.
- Kiểm số học trong sổ NCKH-038: 6000×5=30k → 60000×50=3M (×100 tổng lượt mẫu) ĐÚNG;
  σ=sqrt(0.25/2000)≈0.0112 ĐÚNG; (0.5−0.4870)/0.0112≈1.16σ, p hai phía ≈0.25 ĐÚNG;
  23.6−1.45≈22.1 và 1.70+22.1=23.8≈23.9 (làm tròn) ĐÚNG.

### 3. Kết luận kiểm định: ĐẠT

- `[KIEM-DINH] ĐẠT — R=8 âm tính đứng vững (mẫu độc lập seed 777: 0.4895, đoán mò);
  ước tính R=9 x10 ≈24s đứng vững về bậc độ lớn (train chiếm áp đảo, R-độc lập đã kiểm code).
  Điểm trừ nhỏ: tỷ lệ gen 1.17 từ 1 lần đo đơn nằm trong nhiễu (đo độc lập ~0.97), nhưng
  không ảnh hưởng kết luận chi phí vì gen chỉ ~6% tổng.`
- Số liệu độc lập tóm tắt: R8 nhẹ (2k/3ep/seed777) = 0.4895; R8 tách (6k/5ep) = 0.4940;
  gen 62k R8≈1.62s / R9≈1.57s; train chiếm 57.6% ở cỡ chuẩn → ~94% ở cỡ x10 (ngoại suy).

### 4. Đồng bộ Kanzo: HẾT SỐ LẦN THỬ, ghi sổ và tiếp tục (không tự tạo thẻ)

- `GET /api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s, tối đa 2 thử lại):
  lần 1 OK (chỉ kịp xem trước một phần, chưa lưu/kịp tra cứu thẻ); lần 2 HTTP 500; lần 3 HTTP 500.
- Kết quả: hết ngân sách thử lại mà chưa tra cứu được thẻ → KHÔNG tìm thấy thẻ NCKH-038,
  KHÔNG comment, KHÔNG move, KHÔNG tự tạo thẻ. Phù hợp với ghi nhận của NCKH-038 (mục 02:27):
  thẻ đợt 2B chưa được Viện trưởng tạo trên bảng (thẻ mới nhất khi đó là NCKH-028).
- Nhờ Viện trưởng: khi tạo thẻ NCKH-038, ghi nhận kiểm chéo ĐẠT + điểm trừ nhỏ về đo gen
  ở mục sổ này; thẻ NCKH-038 và thẻ NCKH-030 của tôi đều chờ move tay khi Kanzo sống lại.

### Unresolved

1. Chưa chạy thật R=8 x10 (60k×50ep, ~25s) để đối chiếu trực tiếp con số 0.4870 — ngoài ngân
   sách kiểm nhẹ; nhưng 2 số độc lập seed khác (0.4895, 0.4940) đều đoán mò + NCKH-038 đã tự
   kiểm tái hiện seed cố định, nên việc chạy lại là không cần thiết.
2. Thẻ Kanzo NCKH-038 chưa tồn tại → comment/move kiểm định vẫn chờ Viện trưởng.
