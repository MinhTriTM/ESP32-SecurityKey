# Trình tự khởi động Viện (đọc trước khi mở đợt 1)

## Điều kiện tiên quyết (cả 3 phải xanh)

1. Team PQC/ML/tích hợp hiện tại đã hạ cánh (không mở workflow mới khi còn owner khác).
2. Kanzo sống lại ở `http://100.101.100.100:4242/`: kiểm tra `GET /api/board?project=esp32-securitykey`
   trả 200. Nếu vẫn sập: Viện chạy chế độ sổ file (`vien-nghien-cuu/so-cai/`) và đồng bộ
   lên Kanzo sau, không dừng vì Kanzo.
3. `phan-cong.json` đã sinh (200 agent, mã và tên không trùng — chạy `gen_phan_cong.py` để tái tạo).

## Đợt 1: thí điểm 12 agent (NCKH-001..012)

- NCKH-001..006 (6 nhóm trưởng): làm nhiệm vụ tầng 1 của nhóm mình.
- NCKH-007..012 (6 kiểm định viên): mỗi người kiểm chéo 1 thẻ của nhóm trưởng khác nhóm.
- NCKH-001 kiêm tổ trưởng đợt 1: xác minh vòng ghi Kanzo (tạo-sửa-chuyển-bình luận)
  trước khi cả đợt dùng bảng. Hỏng thì cả Viện chuyển sổ file.
- Cổng qua đợt 1: 12/12 thẻ `done`, 0 thẻ kẹt `review` quá 2 vòng, Kanzo (hoặc sổ file) đầy đủ log.

## Mở rộng dần: đợt 2 → 3 → 4

- Mỗi đợt chỉ mở khi đợt trước đạt cổng: trên 90% thẻ `done`, không còn tranh cãi treo hội đồng.
- Đợt 2 (44 agent), đợt 3 (72), đợt 4 (72). Hệ thống chạy tối đa 16 agent cùng lúc nên
  mỗi đợt đi theo sóng 16; Viện trưởng nạp sóng tiếp theo khi sóng trước xong quá nửa.
- Agent mỗi sóng đọc nhiệm vụ của mình trong `phan-cong.json` theo đúng mã, không nhận việc khác.

## Nhịp tim 2 phút (gài sau khi đợt 1 xanh)

Cron `*/2 * * * *` với nội dung: đọc bảng Kanzo (hoặc sổ file), gọi agent của thẻ kẹt
(`doing` quá 30 phút, `review` quá 20 phút), giao việc cho agent rảnh theo thứ tự:
thẻ `review` tồn → thẻ `todo` → nghiên cứu bổ sung → kiểm định chéo thẻ `done` mới nhất.
Nhịp nào không có gì làm thì ghi một dòng log rồi nghỉ, không bịa việc.

## Luật bàn tròn khi mở rộng

- Tranh cãi trong nhóm: nhóm trưởng quyết sau tối đa 3 vòng `[TRAN-LUAN]`.
- Tranh cãi liên nhóm hoặc kiến trúc: đưa hội đồng (6 nhóm trưởng), biểu quyết `[BIEU-QUYET]`,
  hòa thì Viện trưởng quyết. Quyết định ghi vào comment thẻ và sổ cái.
- Không agent nào tự ý đổi hiến chương; muốn đổi phải qua biểu quyết toàn Viện (đa số đợt đang chạy).
