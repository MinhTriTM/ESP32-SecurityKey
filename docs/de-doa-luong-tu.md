# Đe dọa lượng tử đối với dự án

Khi máy tính lượng tử đủ mạnh (chạy được thuật toán Shor với hàng triệu qubit
ổn định) xuất hiện, không phải mọi thứ trong dự án này đều vỡ cùng lúc.
Tài liệu này chia hệ thống thành hai nhóm — vỡ và còn — rồi xếp thứ tự ưu tiên sửa.

> Quy ước đọc nhanh: **Shor** phá thuật toán khóa công khai (ECC, RSA);
> **Grover** chỉ làm yếu một nửa số bit hiệu quả của thuật toán đối xứng và hàm băm.

## 1. Phần vỡ — khóa công khai đường cong elliptic

### 1.1 Đăng nhập FIDO2 (vỡ hoàn toàn)

Key đăng nhập bằng chữ ký **ECDSA P-256** (xem [mô hình đe dọa](06-bao-mat.md)).
Shor suy được private key từ public key, mà public key của credential (credential public key)
lại nằm trên server của từng dịch vụ. Kịch bản vỡ cụ thể:

1. Kẻ tấn công lấy được database public key trên server (rò rỉ, mua, thu thập dần).
2. Dùng máy lượng tử suy ra private key tương ứng.
3. Giả mạo chữ ký đăng nhập mà không cần chạm vào key vật lý.

Lúc đó toàn bộ ý nghĩa "private key không rời chip" (xem [mô hình đe dọa](06-bao-mat.md))
không còn bảo vệ được nữa, vì kẻ tấn công tính lại được private key từ phía public.

### 1.2 Mã PIN và giao thức PIN của FIDO (vỡ)

CTAP2 bảo vệ mã PIN bằng **ECDH P-256** (trao đổi khóa để lập kênh mã hóa
`pinUvAuthToken` giữa máy tính và key). Shor phá được ECDH nên kẻ nghe lén
kênh USB hôm nay, ghi lại rồi giải mã sau ("thu hoạch hôm nay, giải mã ngày mai")
sẽ đọc được PIN. Mức nguy hiểm thực tế thấp hơn mục 1.1 vì phải nghe lén
đúng phiên cắm key, nhưng về nguyên tắc là vỡ.

### 1.3 Chữ ký firmware và Secure Boot (vỡ)

Secure Boot của ESP32-S3 xác thực firmware bằng chữ ký số (ECDSA/RSA, xem
[tài liệu bảo mật](06-bao-mat.md)). Với máy lượng tử, kẻ tấn công suy được
khóa ký từ khóa công khai nhúng trong chip rồi ký firmware giả.
Đây là vấn đề của mọi thiết bị dùng secure boot cổ điển, không riêng board này.

## 2. Phần còn — đối xứng, băm, chia sẻ bí mật

### 2.1 Két mã hóa `tools/vault.py` (còn)

Két dùng **AES-256-GCM**, khóa suy từ mật khẩu bằng **PBKDF2-HMAC-SHA256**
600.000 vòng. Grover chỉ giảm AES-256 còn khoảng 128 bit hiệu quả —
vẫn ngoài tầm với của mọi máy tính đã biết, cổ điển hay lượng tử.
Mật khẩu két là dạng hex của bí mật gốc S (256 bit ngẫu nhiên thật),
không phải mật khẩu do người đặt, nên không có đường brute-force khả thi.

### 2.2 Hàm băm SHA-256 / SHA-512 (còn)

SHA-256 (checksum cụm từ, PBKDF2 của két) và PBKDF2-HMAC-SHA512 (seed BIP-39
trong `tools/mnemonic.py`) đều là hàm băm đối xứng. Grover giảm độ an toàn
chống tiền ảnh còn một nửa số bit (~128 bit với SHA-256), vẫn an toàn.
Checksum BIP-39 chỉ để bắt lỗi gõ nhầm, không phải mục tiêu tấn công có giá trị.

### 2.3 Chia sẻ Shamir `tools/split_secret.py` (còn, miễn nhiễm tuyệt đối)

Shamir trên trường GF(256) an toàn theo lý thuyết thông tin: dưới ngưỡng K share
thì kẻ tấn công biết đúng 0 bit về S (xem [ngưỡng đa số](07-sao-luu-va-khoi-phuc.md)).
Tính chất này là toán học thuần túy, không dựa vào độ khó tính toán,
nên máy lượng tử mạnh tùy ý cũng không làm gì được.

### 2.4 Cụm 24 từ BIP-39 trên giấy (còn)

Cụm từ chỉ là cách mã hóa 256 bit entropy của S thành chữ để ghi giấy
(xem [cụm 24 từ](07-sao-luu-va-khoi-phuc.md)). Không có thuật toán khóa công khai
nào ở đây nên Shor không chạm tới được. Kẻ thù của tờ giấy vẫn là mắt người
và máy ảnh, như cũ.

### 2.5 Mã hóa flash trên chip (còn)

Flash Encryption của ESP32-S3 dùng AES — thuật toán đối xứng, còn theo cùng
lý lẽ mục 2.1. Chỉ phần chữ ký (Secure Boot) là vỡ, như đã nêu ở mục 1.3.

## 3. Bảng tổng hợp

| Thành phần | Thuật toán | Thuật toán lượng tử | Kết luận |
|---|---|---|---|
| Chữ ký đăng nhập FIDO | ECDSA P-256 | Shor | VỠ — giả mạo được không cần key |
| Giao thức PIN CTAP2 | ECDH P-256 | Shor | VỠ — nghe lén giải mã sau |
| Chữ ký Secure Boot | ECDSA/RSA | Shor | VỠ — ký được firmware giả |
| Két `vault.py` | AES-256-GCM, PBKDF2-SHA256 | Grover (~128 bit còn lại) | CÒN |
| Băm, checksum, seed | SHA-256, SHA-512 | Grover | CÒN |
| Share Shamir | Shamir GF(256) | Không ảnh hưởng | CÒN, miễn nhiễm tuyệt đối |
| Cụm 24 từ giấy | Mã hóa entropy BIP-39 | Không ảnh hưởng | CÒN |
| Mã hóa flash | AES | Grover | CÒN |

## 4. Thứ tự ưu tiên sửa

### Ưu tiên 1 — Theo dõi chuẩn PQC cho FIDO, không tự chế (mặt vỡ lớn nhất)

Đăng nhập FIDO là thứ duy nhất vỡ mà không có đường vá trong tầm tay:
thuật toán chữ ký nằm trong chuẩn WebAuthn/CTAP2 và firmware pico-fido,
không phải code của dự án này. Việc cần làm:

1. Theo dõi chuẩn chữ ký hậu lượng tử cho FIDO/WebAuthn (đang được soạn thảo).
2. Khi pico-fido hoặc firmware thay thế hỗ trợ, nâng cấp key và đăng ký lại
   credential trên từng dịch vụ.
3. Tuyệt đối không tự chế giao thức đăng nhập "chống lượng tử" riêng —
   [lịch sử đã chứng minh thuật toán tự chế luôn có lỗ hổng](07-sao-luu-va-khoi-phuc.md).

### Ưu tiên 2 — Giữ nguyên hầm đối xứng, cấm hạ cấp (không tốn công)

Két, băm, Shamir, cụm từ đã an toàn trước lượng tử. Quy tắc duy nhất:
mọi chỗ mới viết sau này vẫn dùng AES-256 (không hạ xuống AES-128),
SHA-256 trở lên, ngưỡng Shamir giữ K lớn hơn nửa N.
Không cần sửa code hiện tại.

### Ưu tiên 3 — Vận hành: lưới an toàn phi-FIDO (làm ngay, rẻ)

Ngày FIDO vỡ, đường sống là hai key dự phòng + mã khôi phục + két:

1. Duy trì hai key cho mỗi tài khoản quan trọng (xem [quy tắc dùng thật](06-bao-mat.md)).
2. Diễn tập khôi phục đủ 3 đường (key dự phòng, share Shamir, cụm 24 từ)
   mỗi sáu tháng (xem [quy trình sao lưu](07-sao-luu-va-khoi-phuc.md)).
3. Két `ket.bin` để ở đâu cũng được, kể cả cloud — AES-256 còn thì két còn.

### Ưu tiên 4 — Dài hạn: thử nghiệm hậu lượng tử có sẵn (khi rảnh)

- `tools/pqc.py` đã thử nghiệm trao đổi khóa **ML-KEM-768** (chuẩn FIPS 203).
  Giữ tool này chạy xanh qua `scripts/run_tests.*` để khi cần là có sẵn.
- Nếu sau này share Shamir phải truyền qua mạng công cộng (hiện chỉ đi qua
  Bluetooth/QR/cáp cục bộ), bọc thêm một lớp ML-KEM cho kênh truyền.
- Chữ ký firmware lai cổ điển + PQC: chờ Espressif hỗ trợ trên ESP32-S3,
  không tự vá bootloader.

## 5. Một câu kết luận

Máy lượng tử lấy đi khả năng đăng nhập FIDO, nhưng không lấy được két,
share Shamir và cụm từ giấy. Ai giữ ba đường khôi phục trong
[tài liệu sao lưu](07-sao-luu-va-khoi-phuc.md) còn dùng được thì ngày đó
vẫn vào được tài khoản — chỉ là phải đăng ký lại key theo chuẩn mới.
