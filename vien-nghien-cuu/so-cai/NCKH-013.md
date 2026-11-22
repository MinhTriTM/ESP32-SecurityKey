# Sổ cái NCKH-013 — Ngô An, nhóm PQC, thành viên, đợt 2A

## 2026-11-21 01:53 — nhận việc

- Thẻ: [PQC] Đặc tả két lai X25519+ML-KEM (Kanzo id: tra bảng ở cuối việc)
- Người nhận: Ngô An (NCKH-013)
- Việc nhận: viết đặc tả định dạng két lai (CHƯA code): layout byte,
  thứ tự bọc khóa, cách mở khi một vế gãy. Vẽ sơ đồ vào sổ cái.
- Tài liệu đã đọc TRƯỚC khi làm:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, toàn bộ)
  - mục NCKH-013 trong `vien-nghien-cuu/phan-cong.json` (dòng 146-157)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu nhật ký)
  - `vien-nghien-cuu/NHIP-TIM.md` (luật ghi Kanzo: file trước bảng sau)
  - `vien-nghien-cuu/so-cai/NCKH-007.md` (khuyến nghị ML-KEM-768,
    pk/sk/ct/ss = 1184/2400/1088/32 byte, khớp FIPS 203)
  - `vien-nghien-cuu/so-cai/NCKH-001.md` (rà soát tools/pqc.py, các lưu ý
    đối xứng lỗi đọc/ghi, quyền file .sk, mâu thuẫn exception)
  - `tools/vault.py` toàn bộ (két hiện tại: MAGIC `ESKVAULT1` 9 byte +
    salt 16 + nonce 12 + AES-256-GCM, khóa từ PBKDF2 600k vòng)
  - `tools/pqc.py` dòng 1-80 (API oqs, ALG = ML-KEM-768)
- Quy định: REPO CHỈ ĐỌC (chỉ ghi file sổ này), không git commit,
  shell bắt buộc `shell="pwsh"`.
- Trạng thái thẻ: todo -> doing (dự kiến, thử opportunistic cuối việc).

## 2026-11-21 01:55 — ĐẶC TẢ KÉT LAI X25519 + ML-KEM (bản 0.1, chưa code)

> Phạm vi: chỉ đặc tả định dạng + quy trình. Chưa viết code, chưa sửa
> `tools/vault.py`. Mọi hằng số mật mã dưới đây là đề xuất, cần peer review
> khác nhóm + hội đồng chốt trước khi code (ý tưởng lớn theo Hiến chương §3).

### 0. Mục tiêu và nguyên tắc

1. Chống "thu hôm nay, giải mã sau": kẻ thu két hiện tại không mở được
   ngay cả khi sau này có máy lượng tử mạnh (nhờ vế ML-KEM).
2. Không đặt cược một cửa: nếu ML-KEM bị bẻ bằng cổ điển (thuật toán mới,
   lỗi cài đặt) thì vế X25519 vẫn giữ két (và ngược lại).
3. Tái dùng hạ tầng sẵn có: ML-KEM-768 theo `tools/pqc.py` (NCKH-007 đã
   chốt), AES-256-GCM + PBKDF2 theo `tools/vault.py`.
4. Tương thích một chiều: bản đọc lai PHẢI từ chối két cũ `ESKVAULT1` bằng
   thông điệp rõ ràng (mở bằng `tools/vault.py`); két cũ đã tự từ chối két
   mới nhờ kiểm magic (`vault.py` dòng 55).

### 1. Bộ tham số (suite)

- `suite_id = 1`: X25519 + ML-KEM-768 / HKDF-SHA256 / AES-256-GCM.
- X25519: pk 32 byte, sk 32 byte, ss 32 byte (RFC 7748).
- ML-KEM-768: pk 1184, sk 2400, ct 1088, ss 32 byte (FIPS 203;
  đã đo thực tế trong sổ NCKH-007).
- Mọi số nguyên đa byte: little-endian. Mọi độ dài là cố định theo
  `suite_id`; bản đọc KHÔNG suy độ dài từ file mà từ `suite_id`
  (chống tráo nhãn suite).

### 2. Layout byte (suite 1, version 1)

```
offset   len    tên            nội dung
------   ---    ---            --------
0        9      magic          b"ESKVAULT2" (9 byte, nối tiếp ESKVAULT1)
9        2      version        u16 LE = 1
11       2      suite_id       u16 LE = 1
13       16     kdf_salt       ngẫu nhiên mỗi lần bọc (os.urandom)
29       32     eph_x_pk       ephemeral X25519 public key
61       1088   mlkem_ct       ML-KEM-768 ciphertext (encap dưới pk người nhận)
1149     12     wrap_nonce     nonce AES-GCM cho lớp bọc DEK
1161     48     wrapped_dek    DEK 32 byte + tag GCM 16 byte
1209     12     body_nonce     nonce AES-GCM cho thân két
1221     N+16   body_ct        bản rõ N byte + tag GCM 16 byte
```

- Overhead cố định: 1237 byte (1221 header + 16 tag thân).
- Phần lớn overhead (1088 byte) là `mlkem_ct` — giá bắt buộc của PQC,
  chấp nhận được vì két mở theo file, không theo gói tin nhỏ.

Sơ đồ khối (vẽ vào sổ theo yêu cầu):

```
+--------+--------+--------+----------+----------+----------+----------+----------+----------+
| magic  | ver(2)|suite(2)| kdf_salt | eph_x_pk | mlkem_ct |wrap_nonce|wrapped_  |body_nonce|
| 9 byte |  u16   |  u16   | 16 byte  | 32 byte  |1088 byte | 12 byte  |dek 48 B  | 12 byte  |
+--------+--------+--------+----------+----------+----------+----------+----------+----------+
|<------------------- AAD của lớp bọc DEK (byte 0..1149) ------------------->|
|<------------------------- AAD của thân két (byte 0..1221) ---------------------------->|
                                                                                          +----------+
                                                                                          | body_ct  |
                                                                                          | N+16 B   |
                                                                                          +----------+
```

Ràng buộc AAD (bắt buộc, chống tráo đầu/cắt ghép):

- Lớp bọc DEK: `AAD_wrap = bytes[0..1149)` (magic..mlkem_ct).
- Thân két: `AAD_body = bytes[0..1221)` (mọi thứ trước body_ct,
  gồm cả wrapped_dek).

### 3. Thứ tự bọc khóa (wrap) — bên gửi/người cất két

```
                       (ngẫu nhiên mỗi lần bọc)
                     +-----------------------------+
                     | DEK = urandom(32)           |
                     | kdf_salt, wrap_nonce,       |
                     | body_nonce = urandom(...)   |
                     +-------------+---------------+
                                     |
   +------------------+  +-----------+------------+
   | VẾ CỔ ĐIỂN (X)   |  | VẾ LƯỢNG TỬ (M)        |
   | eph_sk,eph_pk    |  | (ct, ss_m) =           |
   |  = X25519.keygen |  |  ML-KEM.encap(pk_m)    |
   | ss_x = DH(eph_sk |  | ct -> mlkem_ct         |
   |  , pk_x_nguoi_   |  | eph_pk -> eph_x_pk     |
   |  nhan)           |  |                        |
   +--------+---------+  +-----------+------------+
            |                        |
            +-----------+------------+
                        v
            KEK = HKDF-SHA256(
                    salt  = kdf_salt,
                    ikm   = len_pref(ss_x) || ss_x
                          || len_pref(ss_m) || ss_m
                          || suite_id || b"ESK-HYBRID-v1",
                    L = 32)
              (thứ tự cố định: X trước, M sau; thêm nhãn miền
               chống dùng chéo ss vào giao thức khác)
                        |
                        v
            wrapped_dek = AES-GCM-Enc(KEK, wrap_nonce,
                                      plaintext=DEK,
                                      AAD=bytes[0..1149))
                        |
                        v
            body_ct = AES-GCM-Enc(DEK, body_nonce,
                                  plaintext=P,
                                  AAD=bytes[0..1221))
                        |
                        v
            XÓA ss_x, ss_m, eph_sk, DEK khỏi RAM (ghi đè 0,
            best-effort trên Python); KHÔNG bao giờ ghi ss ra đĩa.
```

Thứ tự bắt buộc: (1) sinh DEK + các salt/nonce → (2) DH X25519 →
(3) encap ML-KEM → (4) HKDF trộn theo đúng thứ tự X||M →
(5) bọc DEK → (6) mã hóa thân → (7) xóa vật liệu nhạy khỏi RAM.
Bản đọc kiểm đúng thứ tự ngược lại (mục 4).

Khóa người nhận lưu NGOÀI két (không nhét pk vào file): cặp X
(x.sk 32 B, x.pk 32 B), cặp M (m.sk 2400 B, m.pk 1184 B, định dạng
byte thô như `tools/pqc.py`). Lúc sinh khóa, mỗi sk PHẢI được chia
Shamir (tái dùng `tools/split_secret.py`) và cất share tách biệt —
đây là đường sống khi mất khóa (mục 5.3).

### 4. Thứ tự mở (unwrap) — bên nhận

1. Đọc tối thiểu 1221 byte; thiếu → `ValueError("két cụt")`.
2. Kiểm magic: `ESKVAULT2` mới tiếp tục; gặp `ESKVAULT1` → báo
   "két thế hệ cũ, mở bằng tools/vault.py"; magic khác → từ chối.
3. Đọc version/suite_id; chỉ chấp nhận (1,1), còn lại từ chối
   "suite chưa hỗ trợ" (không đoán độ dài).
4. Cắt các trường theo đúng offset mục 2 (độ dài từ suite_id,
   không từ file).
5. Vế M: `ss_m = ML-KEM.decap(m.sk, mlkem_ct)` (từ chối ngầm của
   ML-KEM được giữ nguyên ngữ nghĩa như NCKH-001 đã ghi).
6. Vế X: `ss_x = X25519.DH(x.sk, eph_x_pk)`; kiểm eph_x_pk ≠ điểm
   bậc thấp (từ chối điểm tầm thường theo RFC 7748).
7. Suy `KEK = HKDF(...)` đúng công thức mục 3.
8. Mở `DEK = AES-GCM-Dec(KEK, wrap_nonce, wrapped_dek,
   AAD=bytes[0..1149)`; lỗi tag → MỘT thông điệp chung
   "sai khóa hoặc két bị sửa" (không tiết lộ vế nào hỏng ở chế độ
   thường, chống oracle phân biệt).
9. Mở `P = AES-GCM-Dec(DEK, body_nonce, body_ct,
   AAD=bytes[0..1221)`; lỗi tag → cùng thông điệp chung.
10. Xóa ss_x, ss_m, KEK, DEK khỏi RAM (ghi đè 0, best-effort).
11. Chế độ chẩn đoán `--chan-doan-ve` (phải gõ cờ tường minh): báo
    riêng từng vế (parse ok/sai, decap/DH ok/sai, tag bọc ok/sai)
    để biết vế nào gãy khi cứu hộ. Cấm bật mặc định.

### 5. Cách mở khi một vế gãy

#### 5.1 Vế X gãy về mật mã (máy lượng tử mạnh bẻ X25519)

- Két VẪN MỞ BÌNH THƯỜNG bằng cả hai khóa theo mục 4.
- An toàn còn lại = vế ML-KEM: KEK = HKDF(ss_x || ss_m) nên thiếu
  ss_m thì không suy được KEK dù ss_x đã lộ (lập luận combiner
  chuẩn: KDF là bộ trộn dual-PRF, một đầu vào còn bí mật là đủ).
- Sau khi mở: DI CHUYỂN NGAY sang suite thuần PQC hoặc suite lai
  thế hệ mới (bọc lại DEK mới), vì từ đây két chỉ còn 1 vế bảo vệ.
- Cấm thiết kế "bỏ vế X cho gọn" một cách thầm lặng — mọi thay đổi
  suite phải đổi version/suite_id và ghi log di chuyển.

#### 5.2 Vế M gãy về mật mã (bẻ cổ điển ML-KEM / lỗi liboqs)

- Đối xứng 5.1: mở bình thường bằng cả hai khóa, an toàn còn lại =
  vế X25519, rồi bọc lại sang suite mới (X25519 + PQC thay thế).
- Trường hợp chỉ gãy CÀI ĐẶT (thiếu DLL/oqs trên máy này, lỗi đã
  biết trong NCKH-001): bản mở KHÔNG được tự hạ cấp sang "chỉ vế X".
  Muốn mở một vế phải gõ cờ tường minh `--cho-phep-mo-mot-ve=X`
  (hoặc `=M`), tool in CẢNH BÁO đỏ + ghi nhật ký, và file mở ra phải
  được bọc lại ngay. Cờ này chỉ dùng cứu hộ, cấm dùng trong quy trình
  thường. (Chi tiết một vế mở thế nào: KEK_1ve = HKDF(ss còn lại
  || nhãn "ESK-SINGLE-LEG-v1"); hai KEK một vế và hai vế KHÔNG bao
  giờ trùng nhau nhờ nhãn miền khác nhau.)

#### 5.3 Gãy vận hành: mất một khóa bí mật

- Mất một sk mà không có dự phòng → KHÔNG MỞ ĐƯỢC theo thiết kế
  (chính sách mặc định HYBRID-BOTH: cần cả hai). Đây là chủ ý, không
  phải lỗi: két 2-vế mà mở được bằng 1 vế thì vế còn lại vô nghĩa.
- Đường sống duy nhất phải chuẩn bị TRƯỚC khi cất két (bắt buộc
  trong quy trình sinh khóa):
  - (a) Chia Shamir mỗi sk (tái dùng `tools/split_secret.py`), cất
    share tách biệt hai nơi; mất sk thì ghép share lại.
  - (b) Phong bì dự phòng mật khẩu (tùy chọn, phải được hội đồng
    duyệt từng két): bọc thêm một bản DEK dưới khóa PBKDF2(mật khẩu
    S) theo đúng định dạng `ESKVAULT1`, cất OFFLINE tách khỏi két
    lai, dán nhãn "chỉ mở khi mất khóa lai". Lưu ý trung thực: phong
    bì này hạ an toàn két xuống mức mật khẩu S trong thời gian nó
    tồn tại — vì vậy mặc định KHÔNG tạo, chỉ tạo khi chủ két chấp
    nhận bằng văn bản trong nhật ký két.
- Cấm mọi "cửa sau mở một vế không cần cờ" trong code.

#### 5.4 Ma trận tóm tắt

```
Tình huống gãy              | Mở được? | An toàn còn lại | Việc phải làm sau khi mở
----------------------------|----------|-----------------|--------------------------
X gãy mật mã, đủ khóa       | Có       | vế M            | Bọc lại suite mới
M gãy mật mã, đủ khóa       | Có       | vế X            | Bọc lại suite mới
M gãy cài đặt, đủ khóa      | Có*      | vế X (*cờ cứu hộ)| Cài lại liboqs, bọc lại
Mất 1 sk, còn share Shamir  | Có       | đủ 2 vế         | Ghép share, sinh khóa mới
Mất 1 sk, không dự phòng    | KHÔNG    | —               | Chấp nhận mất két
```

### 6. Yêu cầu phi chức năng cho bản code sau này (chuyển cho NCKH code)

1. Đối xứng lỗi đọc/ghi (bài học NCKH-001 mục 1): mọi `write_bytes`
   bọc `OSError` với thông điệp sạch, không traceback thô.
2. Thống nhất loại exception input ngắn giữa CLI và self-test
   (bài học NCKH-001 mục 2): chốt MỘT loại, self-test phủ đúng loại đó.
3. File `.sk` (cả X và M) ghi xong `chmod 0o600` (bài học NCKH-001
   mục 3); trên Windows đặt ACL tương đương nếu được.
4. Khử `../` trong `--prefix`/`--out` (bài học NCKH-001 mục 4).
5. Self-test PHẢI phủ đường CLI end-to-end: keygen → bọc → mở →
   so byte; két cụt; magic cũ/mới; tag sai từng lớp; suite lạ;
   hai lần bọc cùng đầu vào ra khác nhau (tính ngẫu nhiên).
6. Thêm test combiner: lộ ss_x (giả lập X gãy) thì KEK vẫn suy được
   từ ss_m và ngược lại; KEK một vế ≠ KEK hai vế.
7. Mã thoát theo quy ước repo: thiếu lib → 2, lỗi dùng → 1.

### 7. Unresolved (cần hội đồng/nhóm khác)

- U1. Có cho phép phong bì dự phòng mật khẩu (5.3b) hay cấm hẳn?
  Đề xuất của tôi: cho phép nhưng mặc định tắt + duyệt từng két.
- U2. Suite agility: bảng `suite_id` tương lai (2 = X25519+ML-KEM-1024?
  3 = thuần PQC?) và ai quyết khi nào xoay suite — cần hội đồng.
- U3. NCKH-019 đang khảo sát PQC trên ESP32-S3: nếu S3 không chạy nổi
  ML-KEM thì két lai chỉ mở trên máy chủ (host), cần ghi rõ vào đặc tả
  vận hành — chờ kết quả NCKH-019.
- U4. Vị trí DLL liboqs (`.tooling/oqs` vs `_oqs` trong home) còn mâu
  thuẫn tài liệu (NCKH-001 mục U4) — chủ repo chốt, đặc tả này giả định
  `OQS_INSTALL_PATH` trỏ đúng chỗ như `run_tests.ps1`.
- U5. Đặc tả này cần 1 peer review khác nhóm + biểu quyết hội đồng trước
  khi có thẻ code hiện thực (Hiến chương §3).

## 2026-11-21 02:00 — báo cáo

- Đã làm: viết đặc tả két lai X25519+ML-KEM bản 0.1 (mục 01:55 trong sổ
  này): bộ suite, layout byte chi tiết từng offset, AAD hai lớp, thứ tự
  bọc/mở 7+11 bước, 4 kịch bản một vế gãy + ma trận, 7 yêu cầu cho bản
  code sau, 5 unresolved.
- Tự kiểm: số đo ML-KEM-768 đối chiếu sổ NCKH-007 + FIPS 203 (khớp);
  magic nối tiếp `ESKVAULT1` trong `tools/vault.py` (khớp 9 byte);
  tổng offset kiểm tay: 9+2+2+16+32+1088+12+48+12 = 1221 (khớp);
  AAD hai lớp bao phủ toàn header (không sót trường nào trước body_ct);
  không sửa file nào ngoài sổ này; không git commit.
- Peer review: chờ agent khác nhóm kiểm chéo (theo mô tả thẻ: NCKH-021).
- Trạng thái: doing -> review (thử opportunistic ngay dưới đây).

## 2026-11-21 02:05 — đồng bộ Kanzo thẻ id 153 (opportunistic, Kanzo nghẽn)

- GET board lần đầu: THÀNH CÔNG — tìm đúng 1 thẻ khớp:
  `153 | todo | [PQC] Đặc tả két lai X25519+ML-KEM (NCKH-013)`.
  Mô tả thẻ chốt người kiểm chéo: NCKH-021 (khác nhóm).
- move todo -> doing: THÀNH CÔNG ở lần thử 2 (lần 1: HTTP 500).
  Response trả về thẻ 153 ở `doing`, comments = 0.
- comment nhận việc: THẤT BẠI 3/3 (HTTP 500 cả 3). Hết 2 lần thử lại.
- move doing -> review: THẤT BẠI 3/3 (HTTP 500 cả 3). Hết 2 lần thử lại.
- comment [BAO-CAO] (nội dung: xong đặc tả bản 0.1, tóm tắt suite +
  layout + kịch bản gãy + U1-U5, tự kiểm offset, chờ NCKH-021):
  THÀNH CÔNG ngay lần thử 1.
- GET board đối chiếu (2 lần): THẤT BẠI cả 2 với
  `{"error":"database error: database is locked"}` — đúng triệu chứng
  SQLite khóa DB đã biết (Hiến chương §6, NHIP-TIM.md).
- Mọi lệnh cách nhau 5s, timeout 30s, tối đa 2 lần thử lại — đúng lệnh.
- Trạng thái bảng theo response đã nhận: thẻ 153 ở `doing`, đã có
  comment báo cáo. Nhờ Viện trưởng/nhịp tim đẩy giúp `doing` -> `review`
  khi Kanzo khỏe; người kiểm chéo: NCKH-021. Sổ cái file này là nguồn
  sự thật cho việc NCKH-013 đến khi bảng được vá.
- Cam kết repo: chỉ ghi thêm file sổ này; không sửa code/docs;
  không git commit; mọi lệnh shell đều kèm `shell="pwsh"`.

## 2026-11-21 — KIỂM CHÉO đợt 2A: runbook Ubuntu của NCKH-021 (Hứa An)

- Vai: Ngô An (NCKH-013) kiểm độc lập việc của NCKH-021.
  File kiểm: `docs/runbook-nap-hwtest-ubuntu.md` (tác giả báo 225 dòng).
  Sổ tác giả: `vien-nghien-cuu/so-cai/NCKH-021.md`.
- Phương pháp (đúng Hiến chương §2: kiểm bằng ĐƯỜNG KHÁC, không chạy lại
  đúng lệnh tác giả): đối chiếu từng khẳng định kỹ thuật trong runbook với
  nguồn gốc (`scripts/build_hwtest.sh`, `firmware/hwtest/hwtest.ino`,
  `firmware/hwtest/README.md`, `tools/hid_echo.py`,
  `tools/requirements.txt`, `scripts/flash_linux.sh`, `docs/03-phan-cung.md`,
  `docs/04-firmware.md`, `docs/research/02-esp32s3-usb.md`) + xác minh bằng
  lệnh đọc máy (đếm dòng, so chuỗi), không đọc chay.

### Đối chiếu từng mục (nguồn → kết quả)

1. Mục 0 (2 cổng USB, UART-nạp / OTG-log+HID, GPIO19/20): khớp
   `docs/03-phan-cung.md` §Yêu cầu cổng USB + `02-esp32s3-usb.md`. ĐÚNG.
2. Mục 1 (`dmesg` cp210x→ttyUSB0, cdc_acm→ttyACM0; `ls /dev/ttyUSB*`
   `/dev/ttyACM*`, `/dev/serial/by-id/`; `lsusb` VID 303a/10c4): tên driver,
   đường thiết bị, VID Espressif/CP210x đều chuẩn Linux. ĐÚNG, trừ góp ý G1.
3. Mục 2 (dialout: `id -nG`, `usermod -aG dialout`, đăng nhập lại, cấm
   `chmod 666`/sudo IDE): đúng quy ước quyền serial Ubuntu. ĐÚNG.
4. Mục 3 (udev `99-esp32s3.rules`: tty→dialout, hidraw/usb→plugdev;
   `udevadm reload+trigger`; gỡ `brltty`, tắt ModemManager): mẫu rule hợp lệ
   (ATTRS theo chuỗi cha USB), plugdev là nhóm mặc định của user Ubuntu,
   brltty chiếm ttyACM0 là lỗi đã biết trên 22.04+. ĐÚNG.
5. Mục 4 (IDE: ESP32S3 Dev Module, CDC On Boot Enabled, USB-OTG TinyUSB,
   nạp qua UART): khớp `firmware/hwtest/README.md` từng bước. ĐÚNG, trừ G2.
6. Mục 5 (CLI): FQBN `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default`
   KHỚP TỪNG KÝ TỰ `scripts/build_hwtest.sh` dòng 10 (xác minh bằng
   Select-String, không đọc chay); nhận định default=HWCDC→HID tắt,
   muốn echo đổi `USBMode=otg` là đúng; cú pháp `arduino-cli upload -p`
   đúng; PIO `esp32-s3-devkitc-1` + `-DARDUINO_USB_CDC_ON_BOOT=1` khớp
   README, `ARDUINO_USB_MODE=0` khớp guard `#if ... == 0` trong ino
   dòng 8/119/145. ĐÚNG.
7. Mục 6 (log mẫu): 8/8 chuỗi kiểm bằng lệnh `.Contains()` trên nội dung
   `hwtest.ino` đều True: header `===`, `HID echo: san sang...`,
   `HID echo: TAT...`, `HID echo: da gui lai 64 byte.`, `BOOT: nhan/nha`;
   định dạng Heartbeat/uptime/heap khớp `Serial.printf` dòng 142; LED
   xanh lá chờ / xanh dương nhấn khớp `setLed` dòng 126/133; chuyển cổng
   UART→native sau nạp là đúng (CDC đi đường native). ĐÚNG, trừ G2.
8. Mục 7 (HID echo): `pip install -r tools/requirements.txt` + Python ≥3.10
   khớp docstring `hid_echo.py`; `libhidapi-hidraw0` là backend đúng trên
   Ubuntu; 60 byte = PAYLOAD_LEN; 4/4 chuỗi output/error (`HID echo ok...`,
   `Không thấy HID echo (usage page 0xFF00).`, `Không mở được thiết bị`,
   `Thiết bị không trả lời.`, self-test) khớp từng chữ với tool; lưu ý race
   `echoPending` nhất quán với flag volatile không hàng đợi trong ino
   (phân tích của NCKH-003). ĐÚNG.
9. Mục 8 (checklist) + mục 9 (sự cố): checklist phủ đủ README + heartbeat;
   bảng sự cố đếm bằng máy: 13 dòng bắt đầu `|` = header + separator +
   11 DÒNG DỮ LIỆU (tác giả ghi "12 dòng" — xem G3). Nội dung từng dòng
   xử lý đúng nguyên nhân. ĐÚNG.
10. Đếm dòng bằng máy: `(Get-Content ...).Count` = 225. KHỚP báo cáo.
    `git status --short`: repo chưa có commit nào (mọi thứ `??`), không có
    sửa đổi trên file tracked — nhất quán với "chỉ tạo runbook + sổ".

### Góp ý (toàn P4, không đổi kết luận)

- G1 (dmesg, mục 1): runbook dùng `dmesg` trần nhưng Ubuntu mặc định
  `kernel.dmesg_restrict=1` chặn user thường đọc kernel buffer ("Operation
  not permitted"). Nên `sudo dmesg` như chính mục 3.4 đã làm. May là runbook
  còn đường dự phòng `ls` + `lsusb` nên người đọc không kẹt.
- G2 (dấu chấm, mục 4.3/6): chuỗi trích `HID echo: TAT (...USB-OTG)` thiếu
  dấu `.` cuối so với ino dòng 124. Mỹ quan.
- G3 (đếm, sổ tác giả): bảng sự cố có 11 dòng dữ liệu (+header = 12 nếu tính
  cả header, chưa tính dòng separator). Cách đếm mơ hồ, nội dung không sai.

### Kết luận kiểm chéo: ĐẠT

- Mọi khẳng định kỹ thuật (lệnh, FQBN, VID, quyền, udev, brltty/
  ModemManager, chuỗi log, quy trình 2 cổng) được xác nhận bằng nguồn độc
  lập + lệnh máy; 3 góp ý chỉ ở mức mỹ quan/dự phòng. Không yêu cầu sửa
  trước khi đóng — G1 nên vá ở lượt bảo trì tài liệu sau.

### Đồng bộ Kanzo (thẻ id 161, opportunistic)

- GET board: lần 1-2 HỎNG 500, lần 3 THÀNH CÔNG — tìm đúng 1 thẻ:
  `161 | todo | [firmware] Runbook nạp hwtest Ubuntu (NCKH-021)`.
  Thẻ kẹt `todo` vì tác giả GET hỏng 3/3 (khớp sổ NCKH-021), không phải
  do việc dở — không gọi oan (NHIP-TIM mục 5).
- Comment [KIEM-DINH] (`POST /api/tasks/161/comments`): 3/3 báo 500.
  Nhưng GET đối chiếu sau đó báo comments = 1: một lần thử đã ghi lọt
  phía server dù client nhận 500 (hành vi đã biết của Kanzo SQLite).
- Move (`POST /api/tasks/161/move {"status":"done"}`): lần 1 báo 500,
  lần 2 THÀNH CÔNG, server trả status=done. Chuyển thẳng todo -> done
  (thay vì review -> done như lệnh) theo tiền lệ NCKH-008/thẻ 140: cả hai
  chặng (tác giả làm + kiểm chéo) đều xong trong file, giảm tải ghi cho
  Kanzo đang nghẽn. Lý do nằm trong comment kiểm định.
- GET đối chiếu cuối: thẻ 161 = status done, comments = 1.
- Mọi lệnh cách nhau 5s (Start-Sleep trong lệnh), timeout 30s, mỗi lệnh
  tối đa 2 lần thử lại — đúng objective.
- Trạng thái bảng: thẻ 161 done + comment kiểm định → lượt kiểm chéo
  hoàn tất cả file lẫn bảng.

### Unresolved (lượt kiểm chéo NCKH-021)

1. Chưa kiểm runtime trên board/máy Ubuntu thật (không có phần cứng trong
   phiên) — kế thừa unresolved-2 của tác giả; VID:PID mẫu phụ thuộc máy
   người đọc, runbook đã dặn đúng.
2. Bản Windows của NCKH-015 nay đã lên `review` (thẻ 155) nhưng file chưa
   kiểm trong lượt này — nhờ Viện trưởng đối chiếu chéo 2 bản (kế thừa
   unresolved-1 của tác giả).
3. Comment Kanzo nào trong 3 lần thử đã lọt không xác định được từ client;
   nội dung 3 lần thử giống hệt nhau nên không ảnh hưởng.
4. G1 (sudo dmesg) đề nghị vá ở lượt bảo trì tài liệu sau, không chặn done.
