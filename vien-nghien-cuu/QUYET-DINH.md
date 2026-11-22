# Sổ quyết định của Viện (Viện trưởng chốt, hội đồng phản biện khi cần)

## QD-001 — 2026-11-21: Không rời Arduino IDE cho hwtest
- Nguồn: thẻ NCKH-033 (Arduino core 4.0.0 không bật được secure boot/flash encryption) + kiểm chéo NCKH-041.
- Quyết định: hwtest giữ Arduino vì đó là tầng kiểm tra tạm thời — nạp, kiểm, xóa.
  Bản dùng thật là pico-fido build bằng ESP-IDF v5.5.1, bật secure boot + flash
  encryption theo docs/04. Cấm đốt eFuse thử nghiệm trên board chính.
- Việc tiếp theo: ghi rõ phân biệt này vào docs/04 (thẻ follow-up tài liệu).

## QD-002 — 2026-11-21: Chốt tên và tham số bọc S bằng ML-KEM
- Nguồn: thẻ NCKH-025 (đặc tả PQC-WRAP-V1).
- Quyết định: tên tool `pqc_wrap.py`; trường phân loại share dạng SỐ (`kind=1|2`,
  theo phát hiện của kiểm chéo NCKH-017 — `kind` chữ bị parser hiện tại từ chối);
  chu kỳ rotation khóa 2 năm.
- Việc tiếp theo: sửa 3 mục một dòng trong đặc tả trước khi code (thẻ NCKH-025).

## QD-003 — 2026-11-21: Quy tắc file sổ cái là nguồn chân lý khi Kanzo sập
- Nguồn: vận hành đợt 1-2 (Kanzo SQLite nghẽn nhiều lần).
- Quyết định: khi Kanzo lỗi, agent chỉ ghi sổ file và tiếp tục; Viện trưởng/nhịp tim
  vá bảng sau. Không agent nào được chặn việc vì Kanzo.

## QD-004 — 2026-11-21: Chốt cổng đợt 2B ĐẠT, vá bảng xong
- Nguồn: sổ NCKH-029..044 (16/16 bài làm xong, 16/16 lượt kiểm chéo độc lập, toàn ĐẠT).
- Quyết định: đợt 2B ĐẠT, không cần họp hội đồng. Mọi thẻ việc 2B trên Kanzo đã done.
- Ghi chú: thẻ 187/191 là bản trùng todo của NCKH-040 (thẻ 192 đã done) — chờ chủ nhân duyệt xóa.

## QD-005 — 2026-11-21: Chốt cổng đợt 2C ĐẠT, vá bảng xong
- Nguồn: sổ NCKH-045..056 (12/12 bài làm xong, 12/12 lượt kiểm chéo độc lập, toàn ĐẠT).
- Quyết định: đợt 2C ĐẠT, không cần họp hội đồng. Viện trưởng đã vá bù 6 thẻ todo -> done kèm comment kiểm định: 200 (xét bởi 054), 203 (045), 204 (046), 206 (049), 207 (050, comment có sẵn id=119), 208 (051, comment có sẵn id=121).
- Ghi chú 1: thẻ 204 có 2 comment (trùng 1 comment do thử lại khi Kanzo 500) — nội dung đúng, không ảnh hưởng.
- Ghi chú 2: endpoint GET board đang liệt kê thiếu 6 thẻ đợt 1 (138,140,141,142,143,145) dù GET từng thẻ vẫn 200 đủ comment — lỗi hiển thị phía Kanzo, không mất dữ liệu. Sổ cái là nguồn chân lý (QD-003).
