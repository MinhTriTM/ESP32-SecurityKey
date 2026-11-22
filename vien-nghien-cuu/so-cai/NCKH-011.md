# Sổ cái — Đỗ An (NCKH-011), nhóm tailieu, đợt 1

## 2026-11-21 01:29 — nhận việc
- Thẻ: [TAILIEU] Sơ đồ kiến trúc ASCII (Kanzo id 149)
- Nhiệm vụ (theo phan-cong.json): Vẽ luồng Browser→OS→ESP32 cho docs/02-kien-truc.md
- Phạm vi sửa repo: CHỈ đúng 1 file docs/02-kien-truc.md (người duy nhất đợt này được sửa repo)
- Đã đọc trước khi làm: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-011 trong
  vien-nghien-cuu/phan-cong.json, vien-nghien-cuu/so-cai/README.md, docs/02-kien-truc.md
- Ghi chú: file sổ cái này chưa tồn tại trước khi tạo (đã thử đọc, hệ thống báo
  không tìm thấy file) nên tạo mới thay vì nối thêm
- Trạng thái: todo -> doing (thử Kanzo opportunistic, xem mục Kanzo bên dưới)

## 2026-11-21 01:30 — Kanzo nhận việc (opportunistic)
- Lệnh 1: POST /api/tasks/149/move {status: doing} -> THÀNH CÔNG ngay lần 1
  (server trả status: doing, thẻ "[tailieu] Sơ đồ kiến trúc ASCII (NCKH-011)")
- Nghỉ 5s theo luật nghẽn
- Lệnh 2: POST /api/tasks/149/comments {nhận việc 01:29} -> lần 1 lỗi 500
  (Internal Server Error, đúng kiểu SQLite khóa khi ghi dồn dập), lần 2 THÀNH CÔNG
- Ghi chú: theo Hiến chương, lỗi 500/timeout không đồng nghĩa server chưa ghi;
  sẽ đối chiếu lại số comment trên bảng ở cuối việc

## 2026-11-21 01:31 — báo cáo
- Đã làm: thay code block 1 dòng trong mục "Tổng quan luồng" của docs/02-kien-truc.md
  bằng: dòng luồng tóm tắt + sơ đồ sequence ASCII 7 bước
  (Browser-WebAuthn -> OS-CTAPHID -> ESP32-pico-fido -> nút BOOT -> ký -> trả về)
  + phần "Giải thích các bước" tiếng Việt có dấu. Không chạm bất kỳ file repo nào khác
- Tự kiểm: script pwsh quét mọi dòng chứa '|' trong code block, tất cả 21 dòng đều
  có '|' tại đúng vị trí 8,40,72,104 (thẳng hàng 100%); đọc lại toàn mục sau khi sửa,
  markdown hợp lệ, nội dung cũ (luồng tóm tắt) được giữ lại dạng text
- Trạng thái: doing -> review (thử Kanzo opportunistic tiếp)

## 2026-11-21 01:32 — đính chính tên từ Viện trưởng
- Viện trưởng đính chính tên chính thức theo phan-cong.json là Đỗ An (mã NCKH-011
  giữ nguyên). Đối chiếu: từ đầu việc tôi đã dùng đúng tên Đỗ An trong sổ cái,
  trong docs/02-kien-truc.md và trong comment Kanzo — không có gì phải sửa

## 2026-11-21 01:33 — Kanzo báo cáo (opportunistic, THẤT BẠI, dừng thử)
- Lệnh 3: POST /api/tasks/149/move {status: review} -> cả 3 lần đều lỗi 500
  (Internal Server Error), đã hết quota thử lại (tối đa 2 lần thử lại)
- Đối chiếu: GET /api/board?project=esp32-securitykey -> 2 lần đều lỗi 500,
  không đọc được trạng thái thực của thẻ 149 (có thể server đã ghi move nhưng
  không trả lời được, hoặc chưa ghi — không thể xác minh lúc này)
- Kết luận: Kanzo nghẽn hoàn toàn, dừng mọi thử ghi/đọc thêm. Toàn bộ bằng chứng
  công việc nằm trong sổ cái này; nhờ Viện trưởng đối chiếu và vá thẻ 149 lên
  review khi Kanzo sống lại
- Trạng thái thực tế công việc: ĐÃ XONG, chờ review (peer: NCKH-004 khác nhóm)

## 2026-11-21 01:39 — kiểm chéo thẻ 144 của NCKH-006 (đợt 1, lượt kiểm chéo)
- Vai: Đỗ An (NCKH-011), nhóm tailieu, làm lượt KIỂM CHÉO độc lập thẻ
  [KIEMDINH] Chạy run_tests tiến trình sạch (Kanzo id 144) của Phan An (NCKH-006)
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-006.md (báo 7/7 xanh, EXIT_CODE=0,
  output thô đầy đủ từ scripts/run_tests.ps1)
- Phương pháp kiểm độc lập (ĐƯỜNG KHÁC): KHÔNG qua scripts/run_tests.ps1,
  chạy từng self-test RIÊNG LẺ bằng pwsh (shell='pwsh' bắt buộc) với
  $env:PYTHONPATH='.tooling/pylibs'; $env:OQS_INSTALL_PATH='.tooling/oqs';
  python tools/<tool>.py --self-test; ghi mã thoát từng tool
- Kết quả từng tool (mỗi lệnh một phiên pwsh riêng):
  1. fido_check: exit 0 — "self-test ok: framing, gói nối, CBOR, GetInfo
     và hội thoại đầu-cuối đều đúng."
  2. hid_echo: exit 0 — "self-test ok: đóng gói report HID echo đúng."
  3. split_secret: exit 0 — "self-test ok: GF(256) đúng vector AES,
     chia/ghép đúng mọi ngưỡng thử."
  4. mnemonic: exit 0 — "self-test ok: bảng BIP-39 nguyên vẹn, vector chuẩn
     đúng, checksum bắt lỗi."
  5. vault: exit 0 — "self-test ok: mã hóa/giải mã đúng, sai mật khẩu
     và file sửa bị từ chối."
  6. pqc: exit 0 — liboqs 0.16.0, liboqs-python 0.16.0.2, pk=1184/sk=2400/
     ct=1088/ss=32; keygen ok, round-trip ok, sai khóa ok, sửa 1 bit ok,
     cắt ngắn bản mã ok (ValueError sạch); "self-test PASS: ML-KEM-768
     keygen/encap/decap đúng."
  7. ml_distinguisher: exit 0 — [vector] KHOP (k0=tu-cuoi, chưa xác nhận
     độc lập), [round-trip] PASS (200 mẫu x R=5,22), [micro-train] R=5
     acc=0.505; "== KET LUAN: PASS =="
- Ca lỗi (nhánh lỗi sạch): $env:PYTHONPATH=''; python tools/pqc.py --self-test
  -> exit 2, stderr/stdout gọn: "Thiếu thư viện PQC (No module named 'oqs').
  Chạy: pip install --target .tooling/pylibs -r tools/requirements-pqc.txt
  rồi chạy lại với PYTHONPATH=.tooling/pylibs" — nhánh lỗi sạch, có hướng dẫn sửa
- Kết luận kiểm định: ĐẠT — 7/7 xanh bằng đường chạy độc lập, khớp 100%
  output và mã thoát với báo cáo của NCKH-006; ca lỗi thiếu lib thoát sạch exit 2
- REPO CHỈ ĐỌC: không sửa bất kỳ file repo nào ngoài nối thêm sổ cái này;
  không git commit
- Tiếp theo: thử Kanzo opportunistic (comment [KIEM-DINH] + move review->done),
  mỗi lệnh cách 5s, timeout 30s, tối đa 2 lần thử lại; hỏng thì ghi sổ và tiếp tục

## 2026-11-21 01:40 — Kanzo kiểm chéo thẻ 144 (opportunistic, THÀNH CÔNG)
- Lệnh 1: POST /api/tasks/144/comments {body: "[KIEM-DINH] ĐẠT ..."} ->
  lần 1 lỗi 500 {"error":"database error: database is locked"},
  lần 2 lỗi 500 giống hệt, lần 3 THÀNH CÔNG (comment id=13, task_id=144,
  author=me, created_at=2026-11-20T18:40:02Z). Mỗi lần thử cách nhau 5s,
  timeout 30s, đúng quota tối đa 2 lần thử lại
- Nghỉ 5s theo luật nghẽn
- Lệnh 2: POST /api/tasks/144/move {status: done} -> THÀNH CÔNG ngay lần 1
  (server trả id=144, status=done, position=164.0,
  title="[kiemdinh] Chạy run_tests tiến trình sạch (NCKH-006)", comments=1)
- Kết luận: thẻ 144 đã review -> done, kiểm chéo ĐẠT có bằng chứng đầy đủ
  trong sổ cái này và trên Kanzo (1 comment [KIEM-DINH])
