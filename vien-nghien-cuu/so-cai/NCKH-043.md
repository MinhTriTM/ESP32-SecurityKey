# Sổ cái NCKH-043 — Trương Bình (nhóm PQC, đợt 2B)

## 2026-11-21 02:24 — nhận việc
- Nhiệm vụ: Kiểm thử chéo pqc self-test (loại t1-tay-chon)
- Mô tả: Gọi oqs trực tiếp bằng script riêng, so kết quả với self-test của tool.
- Nguồn đọc: vien-nghien-cuu/HIEN-CHUONG.md, vien-nghien-cuu/phan-cong.json (mục NCKH-043), vien-nghien-cuu/so-cai/README.md, tools/pqc.py
- Kế hoạch: repo CHỈ ĐỌC (không sửa file repo ngoài sổ cái này, không git commit); script riêng trong $env:TEMP gọi oqs trực tiếp (không import tools.pqc): 50 vòng keygen/encap/decap ML-KEM-768 + 12 ca lỗi; chạy self-test của tools/pqc.py (PYTHONPATH=.tooling/pylibs, OQS_INSTALL_PATH=.tooling/oqs) và luồng CLI file keygen/encap/decap để đối chiếu; ghi sổ cái này TRƯỚC rồi mới đồng bộ Kanzo.
- Trạng thái: todo -> doing

## 2026-11-21 02:25 — báo cáo
- Đã làm: kiểm thử chéo độc lập ML-KEM-768 bằng script riêng `$env:TEMP\nckh043_oqs_direct.py` (chỉ `import oqs`, không import `tools.pqc`), đối chiếu với `python tools/pqc.py --self-test` và luồng CLI file `keygen -> encap -> decap` + 1 ca lỗi CLI.
- Môi trường: Windows, Python 3.12.0, liboqs 0.16.0, liboqs-python 0.16.0.2, OQS_INSTALL_PATH=.tooling/oqs (oqs.dll 16.666.405 byte), PYTHONPATH=.tooling/pylibs. oqs báo enabled=38, supported=41 thuật toán.
- Kết quả self-test của tool (5/5 PASS, exit 0):
  - `liboqs 0.16.0, liboqs-python 0.16.0.2.`
  - `Kích thước: pk=1184, sk=2400, ct=1088, ss=32.`
  - 1 keygen đúng cỡ; 2 round-trip khớp từng byte; 3 sai khóa từ chối ngầm; 4 sửa 1 bit khác hẳn; 5 cắt ngắn bản mã báo ValueError sạch; `self-test PASS`.
- Kết quả script độc lập (21/21 ĐẠT, 0 RỚT, exit 0):
  - Phiên bản + kích thước: `liboqs 0.16.0, liboqs-python 0.16.0.2`, pk/sk/ct/ss = 1184/2400/1088/32, khớp FIPS 203.
  - 50/50 vòng keygen/encap/decap round-trip khớp ss từng byte (tổng ~0.01s, ~0.2ms/vòng); 50 pk, 50 ct, 50 ss đôi một khác nhau.
  - Cùng pk encap 2 lần cho ct/ss khác nhau (ngẫu nhiên); decap cùng ct 2 lần cho cùng ss (tất định).
  - Ca lỗi: E1 sai khóa -> 32 byte KHÁC (từ chối ngầm); E2 sửa 1 bit ct ở 3 vị trí đầu/giữa/cuối (0, 544, 1087) -> ss khác; E3 ct cắt ngắn 1 byte -> ValueError sạch (`Ciphertext length must be 1088 bytes, got 1087 bytes`); E4 ct thừa 1 byte -> ValueError; E5 ct toàn zero / toàn 0xFF -> 32 byte khác, không crash; E7 sk cắt ngắn -> ValueError; E8 pk cắt ngắn -> ValueError; E9 pk thừa 1 byte -> ValueError; E10 sk/ct kiểu str -> ValueError; E11 pk rỗng -> ValueError; E12 tên thuật toán sai -> MechanismNotSupportedError.
- Kết quả luồng CLI file (đường vòng 3, file trong $env:TEMP\nckh043_out, repo không dính file mới):
  - `keygen` ghi mlkem768.pk 1184 byte + mlkem768.sk 2400 byte; `encap` ghi ct.bin 1088 byte + ss.a 32 byte; `decap` ghi ss.b 32 byte; SHA256(ss.a) = SHA256(ss.b) = 46E09F0B...17D5E, KHỚP.
  - Ca lỗi CLI: decap với ct cắt ngắn (1087 byte) -> báo `dài 1087 byte, đáng lẽ 1088 byte`, exit=1, không crash (lớp `_read_exact` chặn trước khi tới oqs, khác với self-test/E3 chặn ở wrapper oqs nhưng cùng sạch).
- Đối chiếu self-test vs kiểm thử chéo (khớp 100%, không lệch):
  - Kích thước 1184/2400/1088/32: self-test mục 1 = script mục details = CLI file = FIPS 203.
  - Round-trip khớp ss: self-test mục 2 (1 vòng) = script 50 vòng + kiểm đôi một + CLI SHA256 khớp.
  - Sai khóa từ chối ngầm: self-test mục 3 = script E1.
  - Sửa 1 bit ct: self-test mục 4 (byte 0) = script E2 (byte 0/544/1087) + E5 (zero/0xFF toàn phần).
  - Ct cắt ngắn báo lỗi sạch: self-test mục 5 (ValueError) = script E3 (đúng message) + CLI exit 1 (lớp _read_exact).
  - Phủ thêm ngoài self-test: ngẫu nhiên hóa encap, tất định decap, ct thừa, sk/pk sai cỡ, kiểu sai, rỗng, tên sai — tất cả sạch, không crash, không khớp lén chỗ nào.
- Kết luận: self-test của tools/pqc.py PHẢN ÁNH ĐÚNG hành vi liboqs thật; kiểm thử chéo độc lập KHỚP TOÀN BỘ, không phát hiện lỗi hay phóng đại trong tool.
- Tự kiểm: `python tools/pqc.py --self-test` (exit 0, PASS); `python $env:TEMP\nckh043_oqs_direct.py` (exit 0, 21 ĐẠT/0 RỚT); CLI `keygen/encap/decap` + so SHA256 ss.a/ss.b (KHỚP) + decap ct cắt ngắn (exit 1 sạch). Mọi file tạm nằm trong $env:TEMP (nckh043_oqs_direct.py, nckh043_out/); repo chỉ ghi thêm đúng file sổ cái này, không commit.
- Trạng thái: doing -> review (chờ peer review khác nhóm kiểm bằng đường khác)

## 2026-11-21 02:26 — đồng bộ Kanzo (opportunistic)
- GET board lần 1: HTTP OK nhưng parse theo `.columns[].tasks` được 0 thẻ, không thấy NCKH-043 (không lưu raw JSON nên không loại trừ khả năng sai cấu trúc parse — ghi nhận để lần sau lưu raw trước).
- GET board lần 2 (soi cấu trúc): HỎNG — `500 Internal Server Error`.
- GET board lần 3 (sau 5s, timeout 30s, thử lại lần 2/2): HỎNG — `500 Internal Server Error`.
- Move/comment: KHÔNG thực hiện — hết 2 lần thử lại mà Kanzo vẫn 500, không có id thẻ của mình để di chuyển; KHÔNG tự tạo thẻ theo lệnh.
- Ghi chú cho Viện trưởng: thẻ của NCKH-043 (nếu có) chưa đồng bộ được; sổ cái file này là nguồn chính. Kết quả kiểm thử chéo (khớp 100% self-test, 21/21 ĐẠT) nằm ở mục báo cáo phía trên. Thẻ kẹt ở `doing`/`review` (nếu có) là do lỗi Kanzo, không phải do việc khó.

## 2026-11-21 02:32 — kiểm chéo đợt 2B: NCKH-035 Bùi Bình (hướng dẫn dev Windows)
- Đối tượng: `docs/moi-truong-dev-windows.md` + sổ `vien-nghien-cuu/so-cai/NCKH-035.md`. Phương pháp: ĐƯỜNG KHÁC — không tin số liệu trong bài, tự chạy lệnh trên máy thật và đối chiếu từng mục.
- Phiên bản (khớp 9/9): `python --version` -> 3.12.0; `arduino-cli version` -> 1.6.0; `core list` -> esp32:esp32 4.0.0; `pip show` -> hidapi 0.15.0, liboqs-python 0.16.0.2 (+liboqs 0.16.0), cryptography 50.0.2, qrcode 8.2, pillow 13.0.0, numpy 2.5.4. Đúng từng số trong bảng mục 0.
- Board options (khớp 2/2): `board details -b esp32:esp32:esp32s3` xác nhận USBMode=default là USB-OTG (TinyUSB), CDCOnBoot=cdc là Enabled. Đúng như sổ 035 và mục 7.2.
- Đường dẫn (True 11/11): `.tooling/pylibs`, `.tooling/oqs`, `.tooling/data`, `.tooling/oqs/bin/oqs.dll` (16.666.405 byte), `.tooling/arduino-cli/arduino-cli.exe`, `scripts/run_tests.ps1`, `scripts/build_hwtest.ps1`, 4 requirements (`tools/requirements.txt`, `-vault`, `-qr`, `-pqc`). Nội dung 4 requirements đúng như doc mô tả (hidapi/cryptography/qrcode+pillow/liboqs-python).
- Liên kết nội bộ (True 3/3): `docs/runbook-nap-hwtest-windows.md`, `firmware/hwtest/README.md`, `docs/04-firmware.md`. Không còn link gãy (035 đã sửa link Ubuntu).
- Script (khớp 4/4): `run_tests.ps1` tự set PYTHONPATH+OQS_INSTALL_PATH, chạy đúng 7 tool với `--self-test`; `build_hwtest.ps1` tự set ARDUINO_DIRECTORIES_DATA, FQBN `esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default` đúng từng ký tự.
- Góp ý nhỏ (không chặn đạt): lệnh kiểm nhanh mục 3 `python -c "import hid, oqs, ..."` chưa set `OQS_INSTALL_PATH` mà đã import oqs trước mục 4 (DLL). Kiểm chứng trực tiếp: chạy thiếu biến này khiến `import oqs` chui vào luồng tự build (clone liboqs, phải kill tiến trình). Đề nghị 035 thêm dòng set OQS_INSTALL_PATH vào mục 3 hoặc dời `oqs` khỏi lệnh import đó. Ngược lại, chính sự cố này xác nhận cảnh báo "bước dễ hỏng nhất" trong doc là có thật.
- Không kiểm được: "đúng 1 file mới" — `git status` cho thấy toàn repo còn untracked (chưa có commit nào) nên không có baseline để đếm; chỉ xác nhận file doc tồn tại và đúng nội dung.
- Kết luận: ĐẠT. 29/29 mục đối chiếu được đều khớp máy thật; 1 góp ý nhỏ về thứ tự biến môi trường ở mục 3.

## 2026-11-21 02:33 — đồng bộ Kanzo cho kiểm định NCKH-035
- GET board lần 1 (timeout 30s): HỎNG — `500 Internal Server Error`.
- GET board lần 2 (sau 5s, thử lại 1/2... hết 2 lượt theo lệnh): HỎNG — `500 Internal Server Error`.
- Comment `[KIEM-DINH] đạt...` + move review->done: KHÔNG thực hiện — không lấy được board nên không có id thẻ NCKH-035; KHÔNG tự tạo thẻ theo lệnh.
- Ghi chú cho Viện trưởng: kết luận kiểm định NCKH-035 là ĐẠT (chi tiết ở mục kiểm chéo phía trên); khi Kanzo hồi phục, Viện trưởng move thẻ 035 review->done giúp và dán comment: `[KIEM-DINH] đạt — 29/29 mục khớp máy thật (9 phiên bản, 2 board options, 11 đường dẫn, 3 link nội bộ, 4 điểm script); 1 góp ý nhỏ: mục 3 nên set OQS_INSTALL_PATH trước khi import oqs (Trương Bình NCKH-043, 2026-11-21)`.
