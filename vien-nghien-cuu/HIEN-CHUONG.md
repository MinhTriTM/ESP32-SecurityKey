# Hiến chương Viện Nghiên cứu (bản 1.0)

Viện là tập thể agent nghiên cứu bàn tròn: đề xuất, thảo luận, biểu quyết rồi cùng làm.
Mọi hoạt động ghi lên bảng Kanzo project `esp32-securitykey`
(`http://100.101.100.100:4242/`, API đã khảo sát ngày 2026-11-21).

## 1. Tổ chức và mã nhân viên

- Viện trưởng (Viện): điều phối, ra quyết định cuối khi hội đồng hòa phiếu.
- Hội đồng: 5 agent thâm niên, họp khi có tranh cãi hoặc quyết định kiến trúc.
- Nhóm chuyên môn: PQC, ML, firmware, tooling, tài liệu, kiểm định. Mỗi nhóm có nhóm trưởng.
- Mã nhân viên: `NCKH-001`, `NCKH-002`, ... gắn với tên Việt Nam duy nhất
  (ví dụ NCKH-001 Nguyễn An, NCKH-002 Trần Bình...). Viện trưởng cấp mã theo thứ tự vào viện,
  không tái sử dụng mã của agent đã giải thể.

## 2. Kanban là sổ cái duy nhất

Cột Kanzo dùng đúng nghĩa: `backlog` → `todo` → `doing` → `review` → `done`.

Mỗi thẻ việc có tiêu đề `[MÃ-NHÓM] tên việc` và mô tả ghi đủ:
người nhận (tên + mã), việc nhận, đã làm gì, bắt đầu/kết thúc khi nào,
tự kiểm tra (lệnh đã chạy + output), peer review (ai kiểm, kết luận),
có thảo luận lại không, có cần họp hội đồng không và quyết định cuối.

Luật di chuyển thẻ:
- Nhận việc: `todo` → `doing`, comment nhận việc + giờ bắt đầu.
- Xong việc: tự kiểm tra trước, rồi `doing` → `review`, comment báo cáo + bằng chứng.
- Kiểm chéo: agent khác nhóm nhận review, kiểm độc lập (không chạy lại đúng lệnh của tác giả
  mà kiểm bằng đường khác), comment `[KIEM-DINH] đạt/không đạt + lý do`.
- Đạt: `review` → `done`. Không đạt: về `doing` kèm comment yêu cầu sửa.
- Tranh cãi quá 2 vòng sửa: nhóm trưởng đưa lên hội đồng, thẻ ở `review` chờ quyết định.

## 3. Bàn tròn: đề xuất, thảo luận, biểu quyết

Mọi ý tưởng lớn đi qua 3 comment trên đúng thẻ của nó:
- `[DE-XUAT]`: nội dung + chi phí ước tính (agent, thời gian).
- `[TRAN-LUAN]`: mỗi nhóm cử 1 đại diện phản biện, tối đa 3 vòng.
- `[BIEU-QUYET]`: mỗi agent một phiếu `+1/-1`, hội đồng công bố kết quả, hòa thì Viện trưởng quyết.
Việc nhỏ (một agent làm dưới 15 phút) được miễn biểu quyết nhưng vẫn phải qua `review`.

## 4. Nhịp tim 2 phút

Cron `*/2 * * * *` gọi Viện trưởng dậy mỗi 2 phút. Mỗi nhịp:
1. Đọc bảng Kanzo: thẻ nào kẹt `doing` quá 30 phút, `review` quá 20 phút thì gọi agent phụ trách.
2. Agent rảnh việc được giao ngay theo thứ tự ưu tiên: thẻ `review` tồn → thẻ `todo` → nghiên cứu
   bổ sung (đọc code liên quan, tìm edge case) → kiểm định chéo thẻ `done` gần nhất.
3. Không bao giờ để agent ngồi không mà cũng không giao việc trùng: một việc một chủ.

## 5. Danh sách agent

200 agent đã tuyển trên giấy: xem `vien-nghien-cuu/phan-cong.json` (mã, tên, nhóm, vai trò,
đợt, nhiệm vụ). Tái tạo bằng `python vien-nghien-cuu/gen_phan_cong.py`. 6 nhóm trưởng là
NCKH-001..006, đồng thời là hội đồng. Trình tự mở từng đợt ở `KHOI-DONG.md`.

## 6. API Kanzo đã khảo sát (Kanzo 0.3.0)

- `GET /api/board?project=esp32-securitykey` — đọc toàn bảng.
- `POST /api/tasks` `{project, title}` — tạo thẻ, trả về `id`.
- `PATCH /api/tasks/<id>` `{title?, description?, tags?}` — sửa thẻ.
- `POST /api/tasks/<id>/move` `{status}` — chuyển cột (`backlog|todo|doing|review|done`).
- `POST /api/tasks/<id>/comments` `{body}` — thảo luận, biểu quyết, kiểm định.
- `DELETE /api/tasks/<id>` — xóa thẻ (chỉ Viện trưởng được xóa).
- Agent gọi API bằng `Invoke-RestMethod` (pwsh) với timeout 30s. Vòng ghi đã kiểm chứng
  ngày 2026-11-21 nhưng phát hiện Kanzo dùng SQLite và khóa database khi ghi dồn dập
  (timeout client không đồng nghĩa server chưa ghi — đối chiếu lại bảng sau mỗi đợt).
  Vì vậy mọi agent tuân thủ luật ghi trong `NHIP-TIM.md`: file trước bảng sau, cách nhau
  ít nhất 1 giây, thử lại tối đa 3 lần rồi báo Viện trưởng.
