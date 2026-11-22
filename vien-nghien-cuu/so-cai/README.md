# Sổ cái file (dự phòng khi Kanzo sập)

Mỗi agent ghi nhật ký vào `NCKH-XXX.md` của mình TRƯỚC khi đồng bộ lên thẻ Kanzo.
Khi Kanzo sống lại, Viện trưởng đối chiếu và vá phần thiếu lên bảng.

Mẫu một mục (mỗi agent nối thêm, không sửa mục cũ):

```
## 2026-11-21 10:05 — nhận việc
- Thẻ: [PQC] Rà soát tools/pqc.py (Kanzo id 138)
- Trạng thái: todo -> doing

## 2026-11-21 10:40 — báo cáo
- Đã làm: ...
- Tự kiểm: lệnh ... -> output ...
- Trạng thái: doing -> review

## 2026-11-21 11:10 — kiểm chéo thẻ NCKH-006 (người kiểm: NCKH-001)
- [KIEM-DINH] đạt/không đạt + lý do
- Trạng thái thẻ: review -> done (hoặc về doing)
```
