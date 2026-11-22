# Nhịp tim Viện (cron mỗi 2 phút) + luật ghi Kanzo

## Lệnh gài nhịp (Viện trưởng chạy khi mở đợt 1)

Cron `*/2 * * * *`, nội dung prompt:

> Bạn là Viện trưởng trực nhịp tim. Workspace: D:\Download\ESP32-SecurityKey, shell pwsh.
> 1. Đọc bảng Kanzo `GET /api/board?project=esp32-securitykey` (timeout 12s, thử lại 1 lần).
>    Nếu Kanzo sập: đọc sổ file `vien-nghien-cuu/so-cai/` thay thế, không làm gì thêm ngoài ghi log.
> 2. Thẻ `doing` quá 30 phút hoặc `review` quá 20 phút: comment gọi agent phụ trách vào việc.
> 3. Nếu không có workflow nào đang chạy (kiểm tra work_list) và còn thẻ `todo` của đợt
>    đang mở: mở workflow một sóng tối đa 16 agent theo `phan-cong.json`.
> 4. Nhịp nào không có gì làm: ghi một dòng log rồi nghỉ, không bịa việc.
> 5. Mọi thao tác Kanzo tuân thủ luật ghi bên dưới.

## Luật ghi Kanzo (bắt buộc với mọi agent)

Máy chủ Kanzo dùng SQLite và khóa database khi ghi dồn dập (đã quan sát thực tế).
Vì vậy:

1. File trước, bảng sau: agent luôn ghi nhật ký vào file của mình
   (`vien-nghien-cuu/so-cai/NCKH-XXX.md`) trước, rồi mới đồng bộ lên thẻ Kanzo.
2. Thao tác Kanzo cách nhau ít nhất 1 giây; lỗi `database is locked` hoặc timeout thì
   chờ 3 giây thử lại, tối đa 3 lần, vẫn hỏng thì ghi vào sổ file và báo Viện trưởng.
3. Không bao giờ xóa thẻ của người khác. Chỉ Viện trưởng được xóa (dọn thẻ thử).
4. Comment ngắn gọn, một comment một việc: nhận việc, báo cáo, `[KIEM-DINH]`, `[BIEU-QUYET]`.
5. Thẻ kẹt ở `doing`/`review` do lỗi Kanzo (không phải do việc khó) thì agent ghi rõ
   trong sổ file để nhịp tim không gọi oan.
