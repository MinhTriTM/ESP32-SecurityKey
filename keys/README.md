# Khóa ký firmware (BÍ MẬT — không bao giờ commit)

Thư mục này chứa khóa ký Secure Boot cho bản firmware phát hành (U053).
`.gitignore` đã chặn mọi file trong này trừ chính README này.

## Quy tắc sắt

1. KHÔNG commit, KHÔNG chụp màn hình, KHÔNG gửi khóa qua chat/email.
2. Ngay sau khi tạo: mã hóa khóa bằng `tools/vault.py` (mật khẩu = hex của
   bí mật gốc S), rồi chia theo quy trình Shamir trong `docs/07`.
3. Mất khóa ký = không ra được bản cập nhật hợp lệ nữa (khóa mới không khớp
   digest đã đốt vào eFuse). Mất là làm lại từ board trắng.
4. Ai có khóa ký là ký được firmware giả chạy trên key của bạn. Máy này là
   "máy lạnh": chỉ build và ký, không duyệt web bừa bãi, không cắm USB lạ.

## Tạo khóa (chạy 1 lần duy nhất)

```
python tools/gen_sign_key.py
```

Lệnh trên sinh `secure-boot-signing.key` (ECDSA NIST P-256, PEM) với quyền
hạn chế. Kiểm tra vân tay rồi backup ngay theo mục 2.

## File trong thư mục

- `secure-boot-signing.key`: khóa ký Secure Boot (PEM). Không có file này
  thì chỉ build được bản thử (không ký), không ra được bản phát hành.
- Mọi file `.key`/`.pem` khác (nếu có) cũng là bí mật tương tự.
