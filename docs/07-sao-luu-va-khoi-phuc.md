# 07 — Sao lưu và khôi phục đa thiết bị

Mục tiêu: mất ESP thì vẫn vào được tài khoản, kẻ nhặt được ESP thì không dùng được,
mất bớt thiết bị vẫn khôi phục được, mất hết thiết bị vẫn còn đường cuối bằng giấy.

## Vì sao không gắn ESP với USB theo số serial

Ý tưởng "ESP chỉ chạy khi cắm đúng USB có serial X" nghe hay nhưng không làm được
chắc trên board này, vì ba lý do:

1. Cổng C thứ hai của DevKit chỉ là UART qua chip cầu nối, ESP nhìn thấy mỗi đường
   serial chứ không thấy USB. Không thể cắm ổ cứng vào đó để ESP đọc serial.
2. ESP32-S3 chỉ có một controller USB OTG. Key đang cắm vào PC ở chế độ thiết bị thì
   không thể đồng thời làm chủ để đọc thêm ổ USB khác.
3. Serial hay MAC của ổ đĩa đọc được trong một phút và giả mạo được. Khóa theo serial
   mà không có mã hóa thì chỉ là then cửa giấy: kẻ trộm flash lại firmware là qua.

Thêm nữa, credential FIDO không xuất ra được theo thiết kế, nên không có chuyện
"cắm USB vào là chép credential sang ESP mới". Khôi phục đúng nghĩa của FIDO là:
key dự phòng đã đăng ký sẵn cộng mã khôi phục của dịch vụ.

## Cái gì bảo vệ khi ESP bị lấy mất

- PIN FIDO: tài khoản đăng ký dạng passkey đòi PIN thì kẻ trộm không qua được.
- Secure Boot, Flash Encryption và khóa cổng nạp như [tài liệu bảo mật](06-bao-mat.md):
  chống đọc trộm và flash firmware giả; mã hóa tầng app của pico là lớp thứ hai.
- Đăng ký hai key cho mỗi tài khoản quan trọng: mất key nào thì gỡ đúng tên key đó
  ngay bằng key còn lại.

## Một bí mật gốc, ba đường khôi phục

Toàn bộ hệ thống xoay quanh một bí mật gốc S duy nhất: 32 byte ngẫu nhiên
(256 bit). S có ba hình thức tương đương nhau, khôi phục đường nào cũng ra cùng S:

1. Key FIDO dự phòng đã đăng ký sẵn: đường nhanh nhất khi mất ESP chính.
2. Share Shamir trên các thiết bị: cần đủ ngưỡng đa số mới ghép lại được S.
3. Cụm 24 từ tiếng Anh trên giấy hoặc thép: đường cuối khi mất hết thiết bị.

Từ S suy ra mọi thứ khác: mật khẩu mở két mã hóa (chứa mã khôi phục các dịch vụ)
chính là dạng hex của S. Két tạo bằng `tools/vault.py` (AES-256-GCM), để ở đâu
cũng được, kể cả cloud.

## Sơ đồ ba đường khôi phục

Ba đường dưới đây đều dẫn về cùng một bí mật gốc S (32 byte). Mất ESP chính thì
đi từ trên xuống: thử đường 1 trước, không có key dự phòng thì đi đường 2,
mất hết thiết bị thì còn đường 3.

```text
                               MAT ESP CHINH
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
            v                         v                         v
+----------------------+  +----------------------+  +----------------------+
| DUONG 1              |  | DUONG 2              |  | DUONG 3              |
| KEY FIDO DU PHONG    |  | SHARE SHAMIR         |  | CUM 24 TU (BIP-39)   |
| (nhanh nhat)         |  | (nguong da so)       |  | (duong cuoi cung)    |
+----------------------+  +----------------------+  +----------------------+
            |                         |                         |
            v                         v                         v
  Dang nhap truc tiep     Gom >= K share (vd        Doc 24 tu tren giay
  bang key du phong       3/5) ve 1 may tin cay,    hoac thep theo dung thu
  da dang ky san          chay combine -> S         tu -> to-entropy -> S
  (khong can S)           (S dai 32 byte)           (checksum bat go sai)
            |                         |                         |
            |                         +-------------------------+
            |                                                   |
            |                                                   v
            |                                      S (32 byte - bi mat goc duy nhat)
            |                                                   |
            |                                      Hex cua S = mat khau mo ket
            |                                                   |
            |                                      vault.py decrypt ket.bin
            |                                                   |
            |                                      Ma khoi phuc cac dich vu
            |                                                   |
            +-------------------------+-------------------------+
                                      |
                                      v
                     Vao tai khoan -> go ten key da mat
                             -> dang ky key moi
```

Đọc sơ đồ:

- Đường 1 — key FIDO dự phòng đã đăng ký sẵn: nhanh nhất, đăng nhập thẳng không
  cần S (xem mục "Khi mất ESP thật").
- Đường 2 — share Shamir ngưỡng đa số: gom ít nhất K share (K lớn hơn nửa N,
  cấu hình gợi ý 3/5) về một máy tin cậy, chạy `combine` để ghép lại S.
- Đường 3 — cụm 24 từ trên giấy hoặc thép: gõ đúng thứ tự, `to-entropy` đổi về S,
  checksum BIP-39 bắt lỗi gõ nhầm.
- Hội tụ: hex của S chính là mật khẩu mở két `ket.bin` (`vault.py decrypt`),
  lấy mã khôi phục từng dịch vụ, vào tài khoản, gỡ tên key đã mất rồi đăng ký
  key mới.

(Sơ đồ: Trịnh An, NCKH-017)

## Ngưỡng đa số: chỉ khôi phục được khi có phần lớn thiết bị

Quy tắc chốt: ngưỡng K phải lớn hơn nửa số share N. Kẻ xấu gom dưới một nửa thì
biết đúng 0 bit về S (tính chất toán học của Shamir), còn bạn mất dưới một nửa
thiết bị thì vẫn đủ share để mở. Cấu hình gợi ý: 5 share, cần 3.

| Share | Thiết bị | Cách đưa vào |
|-------|----------|--------------|
| 1 | PC bàn | file gốc khi chia |
| 2 | Laptop | Bluetooth, Quick Share hoặc cáp USB |
| 3 | Điện thoại | Bluetooth hoặc Quick Share, lưu trong app Files |
| 4 | USB số 1 | chép file, cất ở nhà |
| 5 | USB số 2 | chép file, gửi nhà người thân |

Mất bất kỳ 2 nơi nào vẫn mở được két. Kẻ trộm lấy 2 nơi vẫn không mở được.
Thêm thiết bị thì chia lại với N lớn hơn, luôn giữ K lớn hơn nửa N.

## Cụm 24 từ: ví lạnh trên giấy

Cụm từ do `tools/mnemonic.py` sinh ra, tương thích chuẩn BIP-39 của ví lạnh thật:
24 từ mã hóa đúng 256 bit của S kèm checksum để phát hiện gõ nhầm. Ghi ra giấy
bằng bút (hai bản, hai nơi) hoặc khắc lên thép nếu muốn chống cháy nước.

Vì sao 24 từ chứ không phải 32: chuẩn BIP-39 tối đa 24 từ cho 256 bit, và 256 bit
đã là mức không thể brute-force (2^256 phép thử). Thêm từ không vừa công thức
checksum của chuẩn, cũng không an toàn hơn mà chỉ dễ ghi nhầm hơn. Giữ đúng chuẩn
còn có lợi là đọc được bằng mọi ví lạnh và tool BIP-39 khác.

## Quy trình dựng một lần

1. Sinh bí mật gốc và cụm từ:
   `python tools/mnemonic.py new --words 24 --out s.bin`.
   Ghi 24 từ ra giấy NGAY theo đúng thứ tự.
2. Chia share ngưỡng đa số:
   `python tools/split_secret.py split --shares 5 --threshold 3 --from-file s.bin --out shares`.
   Xóa `s.bin` sau khi chia xong.
3. Gom mã khôi phục mọi dịch vụ vào file recovery.txt, lấy hex của S
   (`python tools/mnemonic.py to-entropy <24 từ>`), rồi mã hóa:
   `python tools/vault.py encrypt --in recovery.txt --out ket.bin`.
   Chép ket.bin lên mọi USB và giữ một bản trên PC. Mở két bằng
   `python tools/vault.py decrypt --in ket.bin --out recovery.txt`.
4. Chuyển mỗi share sang đúng một thiết bị theo bảng trên. Trên Windows gửi file
   qua Bluetooth ở Settings rồi Bluetooth và devices. Giữa Android với nhau dùng
   Quick Share (bản chất chạy trên WiFi Direct). Muốn nhanh thì vẽ QR
   (`python tools/split_secret.py qr share-X-of-5.txt`) rồi quét sang điện thoại.
   Xong thì xóa file tạm và file ảnh QR trên máy gửi.
5. Diễn tập ngay: gom 3 share bất kỳ về một máy, chạy `combine`, đối chiếu hex với
   `to-entropy`, mở két thử rồi xóa dấu vết. Diễn tập thất bại bây giờ còn hơn thất
   bại lúc mất key thật.
6. Ghi vào sổ tay giấy: két nằm ở đâu, share nằm ở đâu, ai giữ USB số 2.

## Khi mất ESP thật

1. Lấy key dự phòng đăng nhập từng dịch vụ, gỡ tên key đã mất.
2. Nếu tài khoản nào chưa đăng ký key dự phòng: gom 3 share bất kỳ (hoặc đọc cụm
   24 từ trên giấy), lấy S, mở két, dùng mã khôi phục của dịch vụ đó để vào tài
   khoản rồi đăng ký key mới.
3. Không bao giờ gom đủ K share hay gõ cụm từ lên máy lạ hoặc máy đã nhiễm mã độc.

## Quy tắc giữ share và giữ giấy

- Không để K share trở lên trên cùng một máy, một tài khoản cloud hay một chùm
  backup tự động. Đủ ngưỡng trên một chỗ là mất hết ý nghĩa chia.
- Điện thoại giữ share phải có khóa màn hình và mã hóa máy (mặc định đã bật trên
  Android mới). Mất điện thoại thì coi như mất một share, còn 4 share vẫn đủ.
- Giấy ghi 24 từ không chụp ảnh, không lưu vào app ghi chú có đồng bộ cloud.
  Ai có đủ 24 từ đúng thứ tự là mở được két, không cần thiết bị nào khác.
- Đổi bí mật gốc và làm lại toàn bộ khi nghi một nơi giữ share hoặc tờ giấy bị lộ.
- Mỗi sáu tháng diễn tập ghép thử một lần để chắc file share còn đọc được.

## Vì sao không chế thuật toán mới

Thuật toán mã hóa tự chế hầu như luôn có lỗ hổng mà chỉ lộ khi bị tấn công thật,
lịch sử đã chứng minh nhiều lần. Hệ thống này chỉ dùng phép toán chuẩn đã được
phân tích công khai hàng chục năm: Shamir (1979), BIP-39, SHA-256, PBKDF2. Phần
riêng của bạn — và cũng là phần kẻ tấn công không biết — là quy trình vận hành:
thiết bị nào giữ gì, ngưỡng bao nhiêu, két ở đâu. An toàn nằm ở bí mật S, không
nằm ở việc giấu quy trình.

## Xem thêm

- Thử nghiệm hậu lượng tử: `tools/pqc.py` (ML-KEM-768, chạy qua `scripts/run_tests.*`).
- Vì sao chỉ dùng phép toán chuẩn: [nghiên cứu distinguisher ML](research/06-ml-distinguisher.md).
- Cả hai chỉ để học và thử, hệ thống sao lưu trên vẫn dùng phép toán chuẩn.
