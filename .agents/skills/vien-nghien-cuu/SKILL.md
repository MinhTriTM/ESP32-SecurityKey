---
name: vien-nghien-cuu
description: Điều hành Viện Nghiên cứu ESP32-SecurityKey: nhịp tim Kanzo, giao đợt agent, kiểm chéo, chấm cổng, vá bảng, dashboard.
---

# Viện Nghiên cứu

Dùng skill này khi làm Viện trưởng: giám sát bảng Kanzo `esp32-securitykey`,
giao việc theo đợt cho 200 agent NCKH-001…200, tổ chức kiểm chéo, chấm cổng đợt,
vá bảng khi Kanzo sập, và làm mới dashboard. Mọi trao đổi tiếng Việt; mọi lệnh
shell dùng `muse.powershell` kèm `shell='pwsh'`.

## Luật sắt

1. **Sổ file là chân lý (QD-003).** Kanzo sập thì agent ghi `vien-nghien-cuu/so-cai/NCKH-*.md`
   và làm tiếp; Viện trưởng vá bảng sau. Không ai được chặn việc vì Kanzo.
2. **Không xóa thẻ người khác** khi chưa được chủ nhân cho phép. Chỉ Viện trưởng được xóa,
   và chỉ xóa thẻ trùng đã xác minh.
3. **Không commit/push git** khi người dùng chưa yêu cầu rõ.
4. **File trước bảng sau.** Mọi kết quả ghi vào sổ trước, đồng bộ Kanzo sau (comment + move),
   mỗi lệnh ghi cách nhau tối thiểu 5 giây, timeout 30 giây, thử lại tối đa 2 lần.
5. **Tên agent lấy đúng `vien-nghien-cuu/phan-cong.json`.** Không tự đặt tên.
6. **Không chế thuật toán mã hóa mới.** Chỉ dùng phép toán chuẩn (Shamir, BIP-39, AES, ML-KEM).

## Công cụ (thư mục `tools/`)

- `kanzo.py` — client Kanzo dùng chung, MỌI thao tác bảng phải qua đây:
  `board --project esp32-securitykey`, `get ID`, `comment ID --file F`,
  `move ID done|review|...`, `create --project --title`, `delete ID --yes`.
- `vien_nhip_tim.py` — chạy 1 nhịp tim: tìm thẻ kẹt (doing quá 30 phút, review quá
  20 phút), gọi tối đa 3 thẻ, ghi `so-cai/NHIP-TIM.log`. `--dry-run` để thử khô.
- `vien_cong.py --dot N` — chấm cổng đợt từ sổ cái (không đụng mạng): exit 0 là ĐẠT.
- `vien_dashboard.py` — sinh lại `dashboard/vien.html` từ sổ sách + bảng (Kanzo sập
  thì dùng cache). Chạy sau mỗi đợt.

Mỗi tool có `--self-test` offline; `scripts/run_tests.ps1` chạy tất cả.

## Quy trình nhịp tim (mỗi 2 phút)

1. Đọc bảng (`kanzo.py board`). Hỏng cả 2 lần thì đọc sổ thay thế.
2. Tìm thẻ kẹt theo ngưỡng trên; tra agent trong `phan-cong.json`.
3. Gọi tối đa 3 thẻ bằng 1 comment (`vien_nhip_tim.py` làm sẵn).
4. Ghi 1 dòng log giờ + số thẻ mỗi trạng thái + hành động.
5. Không spawn agent mới từ nhịp tim. Không có gì làm thì chỉ ghi log.

## Quy trình mở đợt

1. Đọc `phan-cong.json` lấy danh sách agent + nhiệm vụ + tên chính thức đợt đó.
2. Giao theo sóng (khuyến nghị 16 agent/sóng). Lệnh giao việc ghi rõ: mã + tên,
   việc, file được đọc/sửa, repo chỉ đọc hay được sửa, shell bắt buộc `pwsh`,
   tiếng Việt, không commit, file-trước-bảng-sau, không tự tạo thẻ Kanzo.
3. Mỗi agent viết sổ `so-cai/NCKH-*.md`: nhận việc → báo cáo + tự kiểm → kiểm chéo
   agent khác nhóm bằng đường độc lập → verdict 1 dòng `[KIEM-DINH] đạt/không đạt + lý do`.
4. Hết đợt: `vien_cong.py --dot N`. ĐẠT thì ghi quyết định vào
   `vien-nghien-cuu/QUYET-DINH.md` (QD mới) rồi vá bảng: dán comment kiểm định còn
   thiếu + move thẻ `done`, đối chiếu lại sau mỗi lượt.

## Kỷ luật API Kanzo (đã gói sẵn trong `kanzo.py`)

- Endpoint: `GET /api/board?project=`, `POST /api/tasks`, `PATCH /api/tasks/<id>`,
  `POST /api/tasks/<id>/move {status}`, `POST /api/tasks/<id>/comments {body}`,
  `DELETE /api/tasks/<id>`. Field comment là `body` (dùng `text` sẽ 400).
- Lỗi 500/timeout phía client KHÔNG đồng nghĩa server chưa ghi: luôn GET đối chiếu
  sau mỗi lượt ghi. Được phép move thẳng `todo -> done` khi việc xong trước cả thẻ.
- Lỗi đã biết: endpoint liệt kê đôi khi thiếu 6 thẻ đợt 1 (138,140–143,145) dù GET
  lẻ vẫn đủ — lỗi hiển thị, không mất dữ liệu; đừng "vá" bằng cách tạo lại.

## Đường dẫn chính

- `vien-nghien-cuu/phan-cong.json` (200 agent), `HIEN-CHUONG.md`, `KHOI-DONG.md`,
  `NHIP-TIM.md`, `QUYET-DINH.md`, `so-cai/` (sổ + `NHIP-TIM.log`).
- `dashboard/vien.html` (xem), `dashboard/template.html` + `tools/vien_dashboard.py` (sinh).
- Bảng Kanzo: `http://100.101.100.100:4242/`, project `esp32-securitykey`.
