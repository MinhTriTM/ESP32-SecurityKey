# Sổ theo dõi key

Mỗi board là một key vật lý duy nhất. Ghi một dòng cho mỗi board ngay khi nạp sketch hwtest xong, lấy MAC từ dòng `MAC: ...` trong log serial.

| Tên key | MAC | Ngày flash hwtest | Commit pico-fido | Dịch vụ đã đăng ký | Ghi chú |
|---------|-----|-------------------|------------------|--------------------|---------|
| key-01 | 28:84:85:86:92:74 | 2026-11-23 | 15b848d821b4995eb1b29a5c2a4c24c25d1a768e | (không dùng thật) | VẬT CHỨNG test lỗi: bản hardened FE làm hỏng kho (CTAP 0x21), UART bị chặn, không flash lại được; rút nguồn 10s + GetInfo vẫn 0x21 (2026-11-23) — KHÔNG đăng ký tài khoản thật |
| key-02 | | | | | Key dự phòng, cất ở nhà |

## Quy tắc ghi sổ

- Tên key trùng với tên đặt khi đăng ký trên Google, GitHub, Microsoft để khỏi nhầm.
- MAC chỉ để định danh board, không phải bí mật. Xem [tài liệu bảo mật](../docs/06-bao-mat.md).
- Mất key nào thì gỡ đúng tên key đó khỏi từng dịch vụ, rồi ghi chú vào cột cuối.
- File này chứa thông tin quản lý, không chứa PIN hay mã khôi phục. PIN nhớ trong đầu, mã khôi phục in ra giấy cất riêng.
