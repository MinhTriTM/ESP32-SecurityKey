# Sổ cái NCKH-025 — Hà An (nhóm PQC, thành viên, đợt 2A)

## 2026-11-21 01:53 — nhận việc

- Người nhận: Hà An (NCKH-025)
- Việc nhận: Bọc bản sao bí mật gốc S bằng ML-KEM (thiết kế quy trình, CHƯA code).
- Yêu cầu: mã hóa S dưới khóa công khai ML-KEM để lưu cloud, khóa bí mật chia Shamir, các bước khôi phục. Viết đặc tả vào sổ cái.
- Ràng buộc: REPO CHỈ ĐỌC (không sửa code, không git commit), shell bắt buộc `pwsh`, tiếng Việt, file trước bảng sau.
- Tài liệu đã đọc TRƯỚC khi làm:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, toàn bộ)
  - mục NCKH-025 trong `vien-nghien-cuu/phan-cong.json` (Hà An, nhóm PQC, đợt 2, "Bọc bản sao S bằng ML-KEM", loại t1-tay-chon)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu nhật ký)
  - `vien-nghien-cuu/NHIP-TIM.md` (luật ghi Kanzo: file trước bảng sau, cách nhau, thử lại)
  - `docs/07-sao-luu-va-khoi-phuc.md` (toàn bộ: S 32 byte, 3 đường khôi phục, ngưỡng đa số 5/3, két vault.py)
  - `tools/pqc.py` (toàn bộ 297 dòng: ML-KEM-768 keygen/encap/decap qua liboqs, pk 1184, sk 2400, ct 1088, ss 32)
  - `tools/split_secret.py` (đọc thêm để thiết kế khớp: Shamir GF(256), header SHAMIR-SHARE-V1, split/combine, từ chối lẫn lộn hai lần chia)
- Trạng thái thẻ: sẽ đối chiếu Kanzo cuối việc (GET board tìm thẻ có mã NCKH-025, thử move+comment cách nhau 5s, timeout 30s, tối đa 2 thử lại).

## 2026-11-21 02:00 — đặc tả quy trình bọc S bằng ML-KEM (CHƯA code)

### 1. Vị trí trong hệ thống hiện tại

- `docs/07` chốt: một bí mật gốc S duy nhất (32 byte ngẫu nhiên), 3 hình thức tương đương: (1) key FIDO dự phòng, (2) share Shamir ngưỡng đa số (gợi ý 5/3), (3) cụm 24 từ BIP-39 trên giấy. Từ S suy ra hex mở két `tools/vault.py` (AES-256-GCM).
- Đặc tả này thêm ĐƯỜNG THỨ 4 (tùy chọn, không thay 3 đường cũ): bản bọc S bằng ML-KEM-768 lưu được trên cloud. Mục tiêu: mất hết thiết bị cục bộ nhưng còn cloud + đủ share khóa bí mật thì vẫn ra S; cloud bị đọc trộm hoặc máy lượng tử tương lai cũng không lộ S.
- Nguyên tắc `docs/07`: không chế thuật toán mới. Tái dùng: `tools/pqc.py` (KEM), `tools/split_secret.py` (Shamir), AES-256-GCM + HKDF-SHA256 chuẩn (cùng họ với két hiện tại).

### 2. Vì sao phải hybrid KEM+DEM (không "mã hóa S bằng ML-KEM" trực tiếp)

- ML-KEM-768 là KEM (FIPS 203): `encap(pk) -> (ct, ss)`, `decap(sk, ct) -> ss`. Nó không nhận plaintext tùy ý, chỉ tạo shared secret 32 byte chung cho hai đầu. Muốn bọc S (32 byte) phải dùng cấu trúc hybrid chuẩn KEM+DEM:
  - KEM phần: `ct (1088 byte) + ss (32 byte)`.
  - KDF: `Ke = HKDF-SHA256(ss, salt 16 byte, info="ESP32-SK-PQC-WRAP-V1", L=32)`. Không dùng ss trực tiếp làm khóa AES để có domain separation và thay được salt mỗi lần bọc.
  - DEM phần: `AES-256-GCM(Ke, nonce 12 byte, plaintext=S 32 byte, aad=header) -> C (32 byte) + tag (16 byte)`.
- Gói lưu cloud = header + salt + nonce + ct + C + tag (tổng ~1164 byte + header). Chi tiết ở mục 5.

### 3. Vật liệu khóa và ngưỡng

- Cặp bọc ML-KEM-768: `pk 1184 byte` (công khai, đi kèm gói cloud), `sk 2400 byte` (bí mật, KHÔNG lên cloud bao giờ).
- Chia `sk` bằng Shamir qua `split_secret.split(sk, n=5, k=3)` (đúng ngưỡng đa số K > N/2 của `docs/07`). Mỗi share sk dài 2400 byte (hex ~4800 ký tự + header). Phân bố 5 nơi đúng bảng `docs/07`: PC bàn, laptop, điện thoại, USB nhà, USB nhà người thân.
- Lưu ý vận hành: share sk (2400 byte) to gấp 75 lần share S (32 byte) nên KHÔNG chuyển bằng QR (QR mã ~4800 hex vượt quá sức chứa thực tế, dễ quét lỗi). Chỉ chuyển bằng file: Bluetooth/Quick Share/cáp/USB, rồi xóa file tạm và kiểm tra xóa.
- Phân biệt hai họ share: share S (len=32) và share sk (len=2400) đã được `split_secret.combine` từ chối lẫn lộn nhờ kiểm tra `(n,k,len)` (dòng 185-187). Để người dùng không nhầm bằng mắt, đề xuất khi code sẽ thêm tag loại vào tên file (`share-sk-X-of-5.txt` vs `share-S-X-of-5.txt`) và một trường `kind=S|SK` trong header (mở rộng tương thích, parser cũ vẫn đọc được vì chỉ kiểm tra hậu tố). CHƯA code trong thẻ này.

### 4. Quy trình dựng một lần (máy sạch, offline, không cloud)

1. Chuẩn bị máy dựng: máy cài sẵn `.tooling/pylibs` + liboqs native, ngắt mạng, tắt backup/sync tự động, kiểm tra không có K share nào khác trên máy.
2. Sinh cặp bọc: tương đương `pqc.py keygen` (ML-KEM-768) -> `mlkem768.pk` (1184), `mlkem768.sk` (2400). Ghi `chmod 0o600` cho `.sk` (khắc phục mục NCKH-001 đã nêu).
3. Lấy S 32 byte: từ `s.bin` hiện có (quy trình `docs/07` bước 1) hoặc `mnemonic.py to-entropy`. KHÔNG sinh S mới nếu hệ thống đã có S (giữ "một S duy nhất").
4. Bọc S: sinh `salt 16 byte + nonce 12 byte` bằng CSPRNG; `encap(pk) -> (ct, ss)`; `Ke = HKDF(ss, salt)`; `AES-GCM(Ke, nonce, S, aad=header) -> C+tag`. Ghi gói `ket-pqc.bin` theo định dạng mục 5. Ghi `mlkem768.pk` cạnh gói để người khôi phục biết dùng pk nào (pk công khai, không bí mật).
5. Chia sk: `split_secret.split(sk, 5, 3)` -> 5 file `share-sk-X-of-5.txt`. Chép mỗi file sang đúng một thiết bị theo bảng `docs/07`. Xong thì xóa thư mục share tạm trên máy dựng.
6. Dọn vết trên máy dựng: xóa `s.bin` (nếu còn), `mlkem768.sk`, mọi `ss/Ke` trung gian, gói tạm. Kiểm tra bằng tìm file (`*.sk`, `s.bin`, `shares*`) còn sót không. Chỉ giữ lại `ket-pqc.bin + mlkem768.pk` để đưa lên cloud.
7. Đưa lên cloud: chép `ket-pqc.bin + mlkem768.pk` lên cloud/drive. Cho phép để chung một tài khoản cloud vì không có sk thì gói này vô dụng (kể cả với máy lượng tử, theo độ an toàn ML-KEM-768 hiện tại).
8. Diễn tập ngay (bắt buộc như `docs/07` bước 5): sang máy thứ hai, tải gói cloud về, gom đúng 3 share sk bất kỳ, chạy quy trình khôi phục mục 6, đối chiếu S thu được với `to-entropy` của 24 từ và mở két `vault.py` thử. Diễn tập thất bại thì làm lại từ bước 2 với cặp khóa mới, KHÔNG vá bằng cách sửa file cũ.
9. Ghi sổ giấy: gói cloud nằm ở đâu (tài khoản/đường dẫn), 5 share sk nằm ở đâu, ngày dựng, fingerprint SHA-256 của pk (để phát hiện gói bị tráo pk).

### 5. Định dạng gói bọc đề xuất (PQC-WRAP-V1, CHƯA code)

- Tất cả số nguyên big-endian. File nhị phân, cấu trúc nối tiếp:
  - `magic 12 byte`: ASCII `PQC-WRAP-V1` (10 ký tự + 2 byte `0x00 0x01` phiên bản).
  - `alg_id 2 byte`: `0x0001` = ML-KEM-768.
  - `kdf_id 2 byte`: `0x0001` = HKDF-SHA256, L=32, info cố định `ESP32-SK-PQC-WRAP-V1`.
  - `dem_id 2 byte`: `0x0001` = AES-256-GCM, nonce 12, tag 16.
  - `salt 16 byte`, `nonce 12 byte`.
  - `ct_len 2 byte` (=1088) + `ct` (1088 byte ML-KEM).
  - `c_len 2 byte` (=32) + `C` (32 byte bản mã S).
  - `tag 16 byte` của AES-GCM.
  - `pk_sha256 32 byte`: SHA-256 của `mlkem768.pk` dùng lúc bọc (ràng buộc gói với đúng pk, chống tráo pk trên cloud).
- Kích thước gói: 12+2+2+2+16+12+2+1088+2+32+16+32 = 1218 byte.
- AAD của AES-GCM = toàn bộ header từ `magic` đến hết `ct` (tức mọi thứ trước C đều được xác thực, kẻ sửa salt/nonce/ct/header đều làm tag trượt).
- Parser khi code phải: kiểm tra magic + id đã biết (từ chối id lạ, không "đoán"), kiểm tra đúng độ dài từng trường (`_read_exact` kiểu `pqc.py`), kiểm tra GCM tag trước khi dùng S, so sánh `pk_sha256` với pk đi kèm.

### 6. Quy trình khôi phục (hai đường)

- Đường R1 — khôi phục S từ cloud (dùng khi mất ESP và mất share S nhưng còn cloud + đủ share sk):
  1. Tải `ket-pqc.bin + mlkem768.pk` về máy sạch (KHÔNG phải máy lạ/nhiễm độc, đúng quy tắc `docs/07`).
  2. Kiểm tra `SHA-256(pk tải về)` khớp fingerprint trong sổ giấy. Lệch thì dừng (cloud bị tráo).
  3. Gom đủ K=3 share sk từ 3 nơi khác nhau về máy này. Kiểm tra mỗi file parse được, cùng `(n,k,len=2400,kind=SK)`. KHÔNG bao giờ gom K share trên máy lạ.
  4. `combine` 3 share -> `sk` (2400 byte). Parse gói: kiểm tra magic/id/độ dài/`pk_sha256`.
  5. `decap(sk, ct) -> ss`; `Ke = HKDF(ss, salt)`; `AES-GCM-decrypt(Ke, nonce, C, tag, aad=header) -> S`. Tag trượt -> dừng, báo "gói hỏng hoặc sai sk", KHÔNG thử "sửa 1 byte rồi mở lại".
  6. Đối chiếu `S.hex()` với `mnemonic.py to-entropy <24 từ>` nếu còn giấy (phải khớp từng byte), rồi dùng S mở két `vault.py` như `docs/07`. Xong thì xóa `sk/ss/Ke/S` và gói tạm khỏi máy khôi phục.
- Đường R2 — luân chuyển (rotation, dùng khi nghi lộ: mất USB giữ share sk, nghi cloud bị ghi đè có chủ ý, hoặc định kỳ 2 năm):
  1. Khôi phục S theo R1 (hoặc đọc từ giấy) trên máy sạch.
  2. Sinh cặp ML-KEM mới, bọc lại S thành `ket-pqc.bin` mới (salt/nonce/ct mới hoàn toàn), chia sk mới thành 5 share mới.
  3. Thu hồi và hủy toàn bộ vật liệu cũ: xóa gói cloud cũ (ghi đè nếu drive cho phép), thu hồi/xóa 5 share sk cũ, cập nhật sổ giấy (ngày rotation, fingerprint pk mới).
  4. Diễn tập lại như mục 4 bước 8. Không tái dùng salt/nonce/ct cũ cho gói mới.

### 7. Phân tích an toàn (tóm tắt cho người duyệt)

- Cloud tò mò/thu thập-trước-giải-mã-sau: chỉ thấy gói 1218 byte + pk. Muốn ra S phải phá ML-KEM-768 (mục tiêu an toàn hậu lượng tử, khác hẳn RSA/ECDH hiện tại) rồi phá AES-256-GCM. Đây chính là giá trị của thẻ này so với két `vault.py` thuần AES (két AES vẫn an toàn trước lượng tử về mặt khóa 256 bit, nhưng đường bọc này dự phòng cho kịch bản muốn thay toàn bộ trao đổi khóa sang PQC sau này).
- Kẻ gom dưới K share sk: biết đúng 0 bit về sk (tính chất Shamir trên GF(256), đã dùng ở `split_secret.py`), suy ra 0 bit về S qua đường này.
- Mất dưới N-K+1=3 nơi giữ share sk (tức còn >=3): vẫn khôi phục được. Mất cloud nhưng còn share S hoặc giấy: vẫn còn 3 đường `docs/07` cũ, không phụ thuộc cloud.
- Toàn vẹn: mọi byte header/salt/nonce/ct đều nằm trong AAD của GCM; sửa 1 bit bất kỳ -> tag trượt -> dừng sạch, không trả S sai. ML-KEM còn có từ chối ngầm (sai sk/ct vẫn ra 32 byte lạ, `pqc.py` self-test bước 3-4) nên tầng DEM càng phải kiểm tag, không được so sánh ss.
- Không gom K share lên một máy/cloud/tài khoản (kế thừa quy tắc `docs/07`): share sk cũng là share, áp cùng luật. Gói cloud + K share sk không bao giờ thường trú cùng một máy ngoài lúc khôi phục ngắn ngủi.
- Rủi ro còn lại: máy dựng/khôi phục nhiễm độc (keylogger đọc S/sk lúc ghép) — giảm bằng máy sạch offline + xóa vết; người dùng lẫn share S với share sk — giảm bằng tên file + trường kind + kiểm tra len; mất đồng thời cloud + quá nửa share sk + giấy — hết đường, phải chấp nhận (đúng triết lý `docs/07`: không có đường nào miễn phí).

### 8. Giao diện CLI đề xuất cho thẻ code tiếp theo (CHỈ đặc tả, KHÔNG implement ở đây)

- File mới `tools/pqc_wrap.py` (tên đề xuất, người code được đổi sau khi bàn tròn): dùng chung `load_oqs/check_alg` của `pqc.py`, dùng `split/combine/format_share/parse_share` của `split_secret.py`, dùng AES-GCM/HKDF của `cryptography` (cùng lib với `vault.py`).
- Lệnh `wrap --s-file s.bin --out-bundle ket-pqc.bin --out-pk mlkem768.pk --shares 5 --threshold 3 --out-shares shares-sk/`: sinh cặp, bọc, chia sk, ghi gói + pk + share. Từ chối khi threshold <= N/2 (ép ngưỡng đa số).
- Lệnh `unwrap --bundle ket-pqc.bin --pk mlkem768.pk --shares share-sk-*.txt --out-s s.bin`: kiểm tra fingerprint, combine sk, decap, giải GCM, ghi S. Mọi lỗi (thiếu share, sai định dạng, tag trượt, pk lệch) in tiếng Việt một dòng + mã thoát 1; thiếu liboqs/DLL mã thoát 2 (đúng quy ước `pqc.py`/`hid_echo.py`).
- Lệnh `rotate` = `unwrap` nội bộ + `wrap` mới + dọn cũ (hoặc hướng dẫn 3 bước thủ công nếu chưa muốn tự động xóa).
- Cờ `--self-test`: vòng tròn sinh->bọc->chia->gom 3/5->mở phải ra đúng S; các ca phá hoại (sửa 1 bit ct/C/tag/salt/nonce, thiếu share, tráo pk, lẫn share S len=32) đều phải thất bại sạch, không trả S sai.

### 9. Tiêu chí chấp nhận cho người code + kiểm định

1. Gói đúng 1218 byte, parse từ chối magic/id lạ và mọi trường lệch cỡ.
2. Round-trip 5/3: mọi tập con 3 share sk đều mở ra đúng S (32 byte).
3. Dưới 3 share: không ra S (kết quả khác S với xác suất áp đảo, hoặc báo thiếu share nếu code ép kiểm đếm trước).
4. Sửa 1 bit ở bất kỳ vị trí nào trong gói (salt/nonce/ct/C/tag/header): `unwrap` thất bại, không ghi file S.
5. Tráo pk (pk khác nhưng gói cũ): bị từ chối nhờ `pk_sha256`.
6. Lẫn share S (len=32) vào tập share sk: bị từ chối sạch (kế thừa kiểm tra của `split_secret`).
7. File `.sk` và `s.bin` trung gian ghi với quyền hạn chế (`0o600` trên POSIX, ACL hạn chế trên Windows nếu làm được) và có bước xóa vết được tài liệu hóa.

## 2026-11-21 02:05 — báo cáo

- Đã làm: đọc 7 tài liệu/code nguồn, thiết kế xong quy trình bọc S bằng ML-KEM hybrid (KEM+HKDF+AES-GCM), định dạng gói PQC-WRAP-V1 1218 byte, quy trình dựng/khôi phục/luân chuyển, phân tích an toàn, đặc tả CLI và tiêu chí chấp nhận cho thẻ code tiếp theo. CHƯA viết code theo đúng yêu cầu thẻ.
- Tự kiểm: đối chiếu kích thước ML-KEM-768 với `tools/pqc.py` (pk 1184, sk 2400, ct 1088, ss 32, đọc từ `kem.details`, không hardcode); đối chiếu Shamir/GF(256)/header/kiểm tra lẫn lộn với `tools/split_secret.py`; đối chiếu S 32 byte + ngưỡng 5/3 + két vault.py + quy tắc vận hành với `docs/07`; không sửa bất kỳ file repo nào ngoài sổ cái này; không git commit.
- Trạng thái thẻ: doing -> review (dự kiến; sẽ thử đẩy lên Kanzo bên dưới, hỏng thì Viện trưởng đẩy tay).
- Unresolved: (1) tên file CLI mới (`pqc_wrap.py`) và trường header `kind` cần bàn tròn chốt với nhóm tooling để không vỡ parser cũ; (2) quyền file `0o600` trên Windows cần người code xác nhận cách làm tương đương; (3) chu kỳ rotation (đề xuất 2 năm) cần Viện chốt; (4) chưa đồng bộ Kanzo (xem mục dưới).

## 2026-11-21 02:10 — đồng bộ Kanzo (THẤT BẠI, đúng luật opportunistic)

- GET /api/board?project=esp32-securitykey: THẤT BẠI cả 3 lần thử (500 Internal Server Error cả 3), mỗi lần cách nhau 5s, timeout 30s.
- Kết quả: không đọc được bảng nên không tìm được id thẻ có mã NCKH-025, không thử move/comment (không có id để gọi, cố gọi mò sẽ ghi nhầm thẻ người khác).
- Sổ cái file này là nguồn sự thật duy nhất cho thẻ NCKH-025 đợt này. Nhờ Viện trưởng khi Kanzo sống lại: tìm/tạo thẻ "[PQC] Bọc bản sao S bằng ML-KEM" (người nhận Hà An NCKH-025), đẩy comment báo cáo + move doing -> review giúp.
- Thẻ không kẹt do việc khó mà do Kanzo sập (500), nhịp tim không gọi oan.

## 2026-11-21 02:11 — kiểm chéo đợt 2A cho NCKH-017 (Trịnh An, sơ đồ 3 đường khôi phục)

- Vai: Hà An (NCKH-025) kiểm độc lập công việc của Trịnh An (NCKH-017, nhóm tailieu).
- Tài liệu đã đọc: `vien-nghien-cuu/so-cai/NCKH-017.md` (toàn bộ 3 mục),
  `docs/07-sao-luu-va-khoi-phuc.md` (toàn bộ sau khi sửa, 182 dòng).
- Ràng buộc lượt kiểm: REPO CHỈ ĐỌC (chỉ nối thêm sổ cái này), shell `pwsh`, tiếng Việt, không git commit.

### 1. Kết luận: ĐẠT (với 1 ghi chú mỹ thuật nhỏ, không bắt sửa)

- Sơ đồ mới ("Sơ đồ ba đường khôi phục", dòng 43-97) đúng vị trí đã hẹn
  (giữa "Một bí mật gốc, ba đường khôi phục" và "Ngưỡng đa số"), nội dung cũ
  hai bên giữ nguyên, markdown hợp lệ, fence cân bằng (đếm được đúng 2).
- Cả 3 nhánh + đoạn hội tụ đều khớp văn bản `docs/07` (chi tiết mục 2).
- Căn lề ASCII kiểm bằng script riêng: trục đối xứng, box đều, hội tụ đúng
  (chi tiết mục 3). Tác giả chỉ sửa đúng 1 file repo (chi tiết mục 4).
- Ghi chú mỹ thuật (không ảnh hưởng kết luận): tiêu đề `MAT ESP CHINH`
  rộng 13 ký tự, tâm rơi vào cột 37 trong khi trục đứng ở cột 38 — lệch 1 ký
  tự sang phải. Mắt thường không nhận ra; tác giả muốn thì dịch tiêu đề sang
  trái 1 dấu cách, không bắt buộc.

### 2. Đối chiếu từng nhánh sơ đồ với văn bản docs/07 (đường kiểm khác tác giả)

- Đường 1 — key FIDO dự phòng, đăng nhập thẳng, "khong can S": KHỚP dòng 35
  (đường nhanh nhất khi mất ESP chính), dòng 19-20 (khôi phục FIDO = key dự
  phòng + mã khôi phục), và §"Khi mất ESP thật" bước 1 (dòng 152: lấy key dự
  phòng đăng nhập, gỡ tên key mất).
- Đường 2 — gom >= K share (vd 3/5), "chay combine -> S", S 32 byte: KHỚP
  dòng 36 (cần đủ ngưỡng đa số), §"Ngưỡng đa số" (dòng 101-103: K > N/2, gợi ý
  5 share cần 3), và bước diễn tập (dòng 145: gom 3 share, chạy `combine`).
- Đường 3 — cụm 24 từ, "to-entropy -> S", "checksum bat go sai": KHỚP dòng 37
  (đường cuối khi mất hết thiết bị), §"Cụm 24 từ" (dòng 118-119: 24 từ = đúng
  256 bit S kèm checksum; dòng 122: chuẩn tối đa 24 từ), và dòng 136
  (`mnemonic.py to-entropy`). Nhãn "BIP-39" khớp dòng 118 (tương thích BIP-39).
- Hội tụ — "Hex cua S = mat khau mo ket" -> "vault.py decrypt ket.bin" ->
  "Ma khoi phuc cac dich vu": KHỚP dòng 39-41 (hex của S là mật khẩu két,
  két AES-256-GCM bằng `tools/vault.py`) và dòng 135-139 (lấy hex S, mã hóa/
  giải mã `ket.bin` bằng `vault.py`).
- Trình tự cuối — "Vao tai khoan -> go ten key da mat -> dang ky key moi":
  KHỚP dòng 27-28 (mất key nào gỡ đúng tên key đó bằng key còn lại) và §"Khi
  mất ESP thật" bước 1-2 (dòng 152-155: đăng nhập, gỡ key mất, đăng ký key mới).
- Phần "Đọc sơ đồ" 4 gạch đầu dòng + dòng ký tên (dòng 85-97): đủ 4 ý, đúng
  tiếng Việt có dấu, số liệu (K lớn hơn nửa N, 3/5) khớp §"Ngưỡng đa số"; tham
  chiếu "(xem mục "Khi mất ESP thật")" trỏ đúng mục tồn tại (dòng 150).
- Không phát hiện số liệu mâu thuẫn (không có ngưỡng lạ, không sai tên tool/
  lệnh, không đảo trình tự gỡ key/đăng ký mới).

### 3. Kiểm căn lề ASCII bằng script riêng (pwsh, logic khác tác giả)

- Script tự viết: tách code block giữa 2 fence, đếm dòng, quét ký tự >126,
  liệt kê vị trí mọi `+`, `|`, `v` từng dòng. Kết quả:
  - Sơ đồ đúng 33 dòng, 0 ký tự ngoài ASCII 0-126 (thuần ASCII, không dấu).
  - Phân nhánh (dòng R2) và hội tụ cuối (R28) cùng `+` tại cột 12/38/64, đối
    xứng tuyệt đối (38 là trung điểm của 12 và 64).
  - Mọi `|`/`v` trên 3 trục đứng đều rơi đúng 12/38/64, `v` nằm ngay dưới `|`.
  - 3 box (R5-R9) viền `+`/`|` tại cột 0/23/26/49/52/75, đều nhau cả 5 dòng;
    mỗi box rộng 24 ký tự, trục nhánh lệch nửa ký tự so với tâm box (11.5/37.5/
    63.5 so với 12/38/64) — sai số không thể tránh với box chẵn, nhìn cân.
  - Nhánh giữa nhập vào đường phải tại R17 (`|`→`+`), mũi tên `v` cuối tại
    cột 38 trỏ đúng giữa dòng "Vao tai khoan..." (tâm chữ trùng cột 38).
  - Các chữ `v` còn lại (R12/R13/R24/R26/R31) đều là chữ cái trong từ thường
    (vd, ve, vault, dich vu, Vao), không phải mũi tên lạc — khớp tự kiểm của
    tác giả nhưng ra từ script độc lập.

### 4. Xác nhận phạm vi: chỉ sửa đúng 1 file repo

- Chuỗi neo `MAT ESP CHINH` chỉ xuất hiện trong đúng 1 file:
  `docs/07-sao-luu-va-khoi-phuc.md` (tìm toàn repo).
- Chữ ký `Trịnh An, NCKH-017` chỉ xuất hiện trong 2 file: `docs/07-...` và
  chính sổ cái NCKH-017 (đúng chỗ, không dây sang file khác).
- Giờ sửa `docs/07` là 01:55:50, nằm trong khung việc tác giả khai
  (01:52 nhận việc → 01:56 báo cáo); sổ NCKH-017 sửa lúc 01:57:35, khớp tiếp.
- Giới hạn chứng cứ: repo chưa có commit git nào (`git log` báo chưa có commit,
  mọi file untracked) nên không đối chiếu được `git diff`; các file khác cùng
  khung giờ đều là sổ cái của thành viên khác đang làm song song. Trong giới hạn
  này, không có dấu hiệu tác giả chạm file repo thứ hai.

### 5. Đồng bộ Kanzo (THẤT BẠI, đúng luật opportunistic)

- GET `/api/board?project=esp32-securitykey`: THẤT BẠI cả 3 lần (500 Internal
  Server Error cả 3), mỗi lần cách nhau 5s, timeout 30s, đã hết quota (tối đa
  2 lần thử lại).
- Không đọc được bảng nên không tìm được id thẻ mang mã NCKH-017 → KHÔNG thử
  move/comment (không có id để gọi, cố gọi mò sẽ ghi nhầm thẻ người khác).
- Nhờ Viện trưởng khi Kanzo sống lại: tìm thẻ có mã NCKH-017
  ([TAILIEU] Sơ đồ luồng khôi phục), thay mặt Hà An (NCKH-025) comment
  `[KIEM-DINH] đạt — 3 nhánh khớp văn bản docs/07, ASCII thẳng trục 12/38/64,
  đúng 1 file; ghi chú nhỏ: tiêu đề MAT ESP CHINH lệch tâm 1 cột, không bắt sửa`
  và move thẻ review -> done giúp.

### 6. Unresolved

- (1) Chưa đẩy được comment/move Kanzo do Kanzo sập 500 (cần Viện trưởng đẩy tay
  theo nội dung mục 5). (2) Ghi chú lệch tâm tiêu đề 1 cột là mỹ thuật, để tác
  giả tự quyết có sửa hay không ở đợt sau.
