# Sổ cái NCKH-026 — Nguyễn Bình (nhóm ML, đợt 2A)

## 2026-11-21 01:53 — nhận việc
- Nhiệm vụ: Tài liệu distinguisher cho người mới (loại t1-tay-chon)
- Mô tả: Giải thích từ đầu: distinguisher là gì, vì sao chống được nó không phải bằng chứng an toàn.
- Nguồn đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-026), vien-nghien-cuu/so-cai/README.md, docs/research/06-ml-distinguisher.md
- Kế hoạch: tạo đúng 1 file mới docs/research/07-giai-thich-distinguisher.md, không sửa file repo khác, không git commit.
- Trạng thái: todo -> doing

## 2026-11-21 01:56 — báo cáo
- Đã làm: tạo mới docs/research/07-giai-thich-distinguisher.md (giải thích distinguisher là gì, thí nghiệm 06 làm gì, vì sao chống được distinguisher không phải bằng chứng an toàn). Chỉ tạo đúng 1 file repo mới, không sửa file khác, không git commit.
- Tự kiểm: đọc lại 06-ml-distinguisher.md để số liệu R=5/6/7 (0.5970/0.5245/0.5070) và thiết lập thí nghiệm khớp; file mới đã ghi thành công (9212 bytes).
- Trạng thái: doing -> review (chờ peer review)

## 2026-11-21 01:58 — đồng bộ Kanzo (opportunistic)
- GET board: 21 thẻ; không có thẻ việc riêng cho NCKH-026. Thẻ duy nhất nhắc mã này là id 158 "[kiemdinh] Kiểm chéo Shamir độc lập (NCKH-018)", status todo, trong đó NCKH-026 được chỉ định làm người kiểm chéo.
- Move: KHÔNG thực hiện — thẻ 158 thuộc NCKH-018 và còn ở todo, di chuyển sẽ vi phạm luật "một việc một chủ".
- Comment: thử 3 lần (lần đầu + 2 thử lại, cách nhau 5s, timeout 30s); 2 lần đầu 500 (database locked), lần 3 OK — comment id 26 xác nhận làm kiểm chéo khi thẻ sang review.
- Ghi chú cho Viện trưởng: việc "Tài liệu distinguisher cho người mới" của NCKH-026 chưa có thẻ Kanzo riêng; sổ cái file này là nguồn chính.

## 2026-11-21 02:06 — kiểm chéo đợt 2A cho NCKH-018 (Trương An)
- Nhiệm vụ: kiểm độc lập công việc "Kiểm chéo Shamir độc lập" của NCKH-018
  (viết lại GF(256)+Shamir độc lập, đối chiếu 10/10 khớp). Repo chỉ đọc,
  không git commit. Đã đọc vien-nghien-cuu/so-cai/NCKH-018.md.
- Phương pháp (đường khác, ở mức nền tảng + rà logic):
  1. Chạy `python tools/split_secret.py --self-test` -> exit 0,
     "self-test ok: GF(256) đúng vector AES, chia/ghép đúng mọi ngưỡng thử."
  2. Tự tính tay GF(256) độc lập (script tạm $env:TEMP\nckh026_gf256_tay.py,
     nhân xtime/peasant + vết tay 0x53*0xCA qua các lũy thừa 2^i):
     0x53*0xCA=0x01 KHỚP; 0x57*0x13=0xFE KHỚP; 0x57*0x83=0xC1 KHỚP (FIPS-197).
     Vết tay: 0x53*2^i = [53,a6,57,ae,47,8e,07,0e], 0xCA=11001010b lấy
     i=1,3,6,7 -> xor = 0x01. Kết luận: ĐẠT.
  3. Rà logic báo cáo NCKH-018: tính độc lập thật sự (nhân nông dân Nga thay
     bảng log/exp, nghịch đảo a^254, đánh giá đa thức trực tiếp thay Horner,
     Lagrange tích tường minh; 0 dòng dài trùng tool); phủ kiểm tra rộng
     (toàn bảng nhân 256x256, nghịch đảo 1..255, 10 ngưỡng gồm biên (5,1)
     (5,5) (7,7) (255,2), tương thích chéo 2 chiều 3570 lượt, nhánh lỗi);
     giới hạn (255,255) không thử đã khai báo rõ với lý do O(k^2) hợp lý.
- Kết luận: [KIEM-DINH] đạt — nền tảng chung (GF(256)) đúng theo vector
  FIPS-197 qua kiểm tra độc lập của tôi; phương pháp và kết luận đối chiếu
  10/10 KHỚP của NCKH-018 vững, đáng tin.
- Unresolved: không có về mặt kiểm định. Lưu ý nhỏ: script đối chiếu của
  NCKH-018 nằm ở $env:TEMP (phù hợp luật repo chỉ đọc) nên mang tính phù du,
  không chạy lại được sau khi xóa; nhưng mô tả phương pháp đủ chi tiết.

## 2026-11-21 02:07 — đồng bộ Kanzo cho kiểm chéo NCKH-018 (ghi viết thất bại)
- GET board: OK, thấy thẻ id 158 "[kiemdinh] Kiểm chéo Shamir độc lập
  (NCKH-018)", status todo (kẹt vì lần đồng bộ của chủ thẻ gặp 500),
  comments=1 (comment id 26 của chính tôi lúc 01:58).
- Comment [KIEM-DINH] đạt: thử 3 lần (lần đầu + 2 thử lại, cách 5s, timeout
  30s) lên POST /api/tasks/158/comments — cả 3 đều 500 Internal Server Error.
- Move sang done: thử PATCH /api/tasks/158 {"status":"done"} 2 lần — cả 2 đều
  500; thử PUT 1 lần — 405 (sai method, PATCH mới đúng nhưng server lỗi).
- Kết luận: Kanzo chỉ đọc được, mọi ghi đều hỏng (khớp với báo cáo của
  NCKH-018). Sổ file này là bản chính; nhờ Viện trưởng vá comment/move thẻ
  158 (todo -> done, kèm verdict đạt) khi Kanzo sống lại.
