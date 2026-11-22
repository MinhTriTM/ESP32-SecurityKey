# Sổ cái NCKH-035 — Bùi Bình (nhóm tailieu, đợt 2B)

## 2026-11-21 02:22 — nhận việc
- Thẻ: [TAILIEU] Hướng dẫn môi trường dev Windows (mã NCKH-035, đợt 2B)
- Việc nhận: viết hướng dẫn dựng môi trường dev từ máy Windows trắng đến chạy được run_tests và build (python, arduino-cli, core ESP32, lib hid/oqs, biến môi trường, lỗi thường gặp) thành file mới `docs/moi-truong-dev-windows.md`. Chỉ tạo đúng 1 file mới này, không git commit.
- Đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-035 trong `vien-nghien-cuu/phan-cong.json`, `vien-nghien-cuu/so-cai/README.md`, `scripts/run_tests.ps1`, `scripts/build_hwtest.ps1`.
- Trạng thái: todo -> doing (sẽ đồng bộ Kanzo cuối việc vì server chập chờn)

## 2026-11-21 02:23 — báo cáo
- Đã làm: tạo `docs/moi-truong-dev-windows.md` (11 mục: bản đồ thành phần, cài Python, lấy repo, cài 4 requirements + numpy, DLL liboqs 2 đường, arduino-cli + core ESP32 4.0.0, bảng biến môi trường, chạy run_tests/build_hwtest, bảng 11 lỗi thường gặp, checklist, đọc tiếp). Sửa 1 liên kết gãy (bỏ link tới file Ubuntu chưa xuất bản).
- Tự kiểm: `Test-Path` 3 liên kết nội bộ trong file mới + chính file -> True cả 4. Số liệu trong bài lấy từ máy thật: `python --version` -> 3.12.0, `arduino-cli version` -> 1.6.0, `core list` -> esp32:esp32 4.0.0, `board details` xác nhận USBMode=default là USB-OTG và CDCOnBoot=cdc là Enabled.
- File mới: đúng 1 file docs theo giao (`docs/moi-truong-dev-windows.md`); file sổ này là nhật ký bắt buộc theo Hiến chương §2/NHIP-TIM (file trước bảng sau).
- Trạng thái: doing -> review

## 2026-11-21 02:24 — đồng bộ Kanzo
- GET board OK ngay lần 1 (timeout 30s): 6 thẻ todo (id 167-172), 0 doing/review, 22 done. Không thấy thẻ mang mã NCKH-035.
- Theo lệnh: không tự tạo thẻ, không move/comment. Viện trưởng đối chiếu sổ này khi mở thẻ đợt 2B.

## 2026-11-21 02:34 — kiểm chéo đợt 2B: NCKH-043 Trương Bình (gọi oqs trực tiếp vs self-test pqc)
- Đối tượng: `vien-nghien-cuu/so-cai/NCKH-043.md` (mục báo cáo 02:25: script riêng 21/21 ĐẠT + self-test tool 5/5 PASS + luồng CLI file, đối chiếu khớp 100%). Lúc đọc (02:3x) sổ 043 đã mọc thêm mục kiểm chéo NCKH-035 (02:32) và mục Kanzo (02:33) — chỉ kiểm phần pqc, không kiểm phần kiểm chéo đó.
- Phương pháp ĐƯỜNG KHÁC (không dùng lại script/kết quả của 043): script riêng `$env:TEMP\nckh035_kiemcheo_043.py` chỉ `import oqs` (có assert chặn nếu `tools.pqc`/`pqc` lọt vào `sys.modules`), oracle kích thước là hằng FIPS 203 hardcode độc lập (pk/sk/ct/ss = 1184/2400/1088/32) thay vì đọc từ tool; 1 vòng keygen/encap/decap trong 1 KEM context + 1 ca lỗi ct cắt ngắn 1 byte; chạy lại `python tools/pqc.py --self-test` để đối chiếu hành vi. Môi trường: PYTHONPATH=.tooling/pylibs, OQS_INSTALL_PATH=.tooling/oqs, Python 3.12.0.
- Chạy độc lập (8/8 ĐẠT, exit 0): `liboqs 0.16.0, liboqs-python 0.16.0.2` (khớp 043); 4/4 kích thước khớp FIPS 203; keygen/encap đúng cỡ; round-trip ss khớp từng byte (sha256=d79e73a142917617...); ct cắt ngắn (1087 byte) -> ValueError sạch đúng từng ký tự message 043 đã ghi: `Ciphertext length must be 1088 bytes, got 1087 bytes`.
- Self-test tool chạy lại (5/5 PASS, exit 0): in đúng từng dòng 043 mô tả (phiên bản, kích thước, mục 1-5, `self-test PASS`). Hành vi self-test mục 5 (ct cắt ngắn -> ValueError) khớp đúng ca lỗi script độc lập của tôi.
- Đối chiếu: khớp 100% trên mọi chiều đã kiểm (phiên bản, 4 kích thước, round-trip khớp byte, từ chối lỗi sạch + đúng message). Không phát hiện phóng đại hay sai số nào trong báo cáo 043.
- Kết luận: ĐẠT. Kết luận "khớp 100%" của NCKH-043 VỮNG trên phạm vi kiểm chéo. Đề nghị thẻ 043 review -> done.
- Giới hạn phạm vi (ghi rõ để không quá đà): tôi chỉ lặp 1 vòng + 1 ca lỗi + self-test theo lệnh, KHÔNG lặp lại toàn bộ 50 vòng/12 ca lỗi/luồng CLI file của 043; phần chưa lặp lại tin ở 043 (không có dấu hiệu nghi ngờ vì 3 điểm neo độc lập đều khớp).
- Repo: CHỈ ĐỌC đúng lệnh — chỉ nối thêm mục này vào sổ của chính mình, không sửa file repo khác, không git commit. File tạm duy nhất: `$env:TEMP\nckh035_kiemcheo_043.py` (2196 byte).

## 2026-11-21 02:34 — đồng bộ Kanzo cho kiểm chéo NCKH-043 (HỎNG 3/3, đã ghi sổ)
- GET `http://100.101.100.100:4242/api/board?project=esp32-securitykey` (timeout 30s, mỗi lần cách 5s): lần 1 HỎNG 500; thử lại 1/2 HỎNG 500; thử lại 2/2 HỎNG 500. Hết số lần thử.
- Comment `[KIEM-DINH]` + move review->done: KHÔNG thực hiện — không lấy được board nên không có id thẻ NCKH-043; KHÔNG tự tạo thẻ theo lệnh. Không lưu được raw JSON (cả 3 lần đều 500 trước khi parse).
- Nhờ Viện trưởng khi Kanzo sống lại: dán comment `[KIEM-DINH] đạt — Bùi Bình (NCKH-035) kiểm bằng đường khác: script oqs trực tiếp 8/8 ĐẠT (oracle FIPS 203 độc lập, round-trip khớp byte, ct cắt ngắn báo đúng message) + self-test tool 5/5 PASS; khớp 100% báo cáo 043, không phát hiện lỗi` và move thẻ NCKH-043 review -> done.
- Unresolved: (1) đồng bộ Kanzo treo do server 500 (nội dung kiểm định đầy đủ nằm ở mục trên); (2) phạm vi kiểm chéo theo lệnh chỉ 1 vòng + 1 ca lỗi, chưa lặp hết 50 vòng/12 ca của 043.
