# Sổ cái NCKH-006 — Phan Phúc (nhóm kiemdinh, nhóm trưởng, đợt 1)

## 2026-11-21 01:29 — nhận việc
- Thẻ: [KIEMDINH] Chạy run_tests tiến trình sạch (Kanzo id 144)
- Nhiệm vụ (theo phan-cong.json): "Ghi toàn bộ output, xác nhận 5 self-test xanh."
- Lưu ý: scripts/run_tests.ps1 hiện tại chạy 7 tool (fido_check, hid_echo,
  split_secret, mnemonic, vault, pqc, ml_distinguisher); kiểm định theo thực tế 7 self-test.
- Trạng thái: todo -> doing (thử opportunistic sau khi ghi sổ)

## 2026-11-21 01:29 — báo cáo
- Đã làm: chạy `scripts/run_tests.ps1` trong tiến trình sạch
  (`pwsh -NoProfile -NonInteractive -ExecutionPolicy Bypass -File scripts/run_tests.ps1`),
  lệnh duy nhất, không sửa repo (REPO CHỈ ĐỌC).
- Tự kiểm: lệnh trên -> mã thoát 0, cả 7 self-test xanh:
  1. fido_check: ok (framing, gói nối, CBOR, GetInfo, hội thoại đầu-cuối)
  2. hid_echo: ok (đóng gói report HID echo)
  3. split_secret: ok (GF(256) đúng vector AES, chia/ghép đúng mọi ngưỡng thử)
  4. mnemonic: ok (bảng BIP-39 nguyên vẹn, vector chuẩn đúng, checksum bắt lỗi)
  5. vault: ok (mã hóa/giải mã đúng, sai mật khẩu và file sửa bị từ chối)
  6. pqc: PASS (ML-KEM-768 keygen/encap/decap đúng; keygen, round-trip,
     sai khóa, sửa 1 bit, cắt ngắn bản mã đều ok)
  7. ml_distinguisher: PASS ([vector] KHOP, [round-trip] PASS 200 mẫu x R=5,22,
     [micro-train] R=5 acc=0.505)
- Toàn bộ output thô:

```
=== fido_check ===
self-test ok: framing, gói nối, CBOR, GetInfo và hội thoại đầu-cuối đều đúng.
=== hid_echo ===
self-test ok: đóng gói report HID echo đúng.
=== split_secret ===
self-test ok: GF(256) đúng vector AES, chia/ghép đúng mọi ngưỡng thử.
=== mnemonic ===
self-test ok: bảng BIP-39 nguyên vẹn, vector chuẩn đúng, checksum bắt lỗi.
=== vault ===
self-test ok: mã hóa/giải mã đúng, sai mật khẩu và file sửa bị từ chối.
=== pqc ===
liboqs-python faulthandler is disabled
liboqs 0.16.0, liboqs-python 0.16.0.2.
Kích thước: pk=1184, sk=2400, ct=1088, ss=32.
1. keygen ok: cặp khóa đúng kích thước.
2. round-trip ok: shared secret hai đầu khớp từng byte.
3. sai khóa ok: secret trả về khác hẳn (từ chối ngầm), không khớp lén.
4. sửa 1 bit ok: secret trả về khác hẳn, không khớp lén.
5. cắt ngắn bản mã ok: báo ValueError sạch.
self-test PASS: ML-KEM-768 keygen/encap/decap đúng.
=== ml_distinguisher ===
== self-test: Speck32/64 + micro-train ==
[vector] KHOP (k0=tu-cuoi; trang thai: chua xac nhan doc lap)
[round-trip] PASS (200 mau x R=5,22)
[micro-train] R=5, 400 mau, 1 epoch -> acc=0.505 (0.0s)
== KET LUAN: PASS ==
Ghi chu: cong kiem tra tinh dung chinh la round-trip; vector o tren
chi mang tinh tham khao vi chua doi chieu nguon tin cay doc lap.
EXIT_CODE=0
```

- Môi trường: shell mặc định `powershell` (5.1) không tồn tại trên máy này
  (tool báo "program not found"); đã dùng `pwsh` thay thế. Ngày giờ máy: 2026-11-21 01:29.
- Trạng thái: doing -> review (thử opportunistic sau khi ghi sổ)
- Unresolved: không có về mặt kiểm định (7/7 xanh, exit 0). Chỉ còn đồng bộ Kanzo
  (xem mục bên dưới).

## 2026-11-21 01:30 — đồng bộ Kanzo (opportunistic, id 144)
- move todo -> doing: OK (server trả status=doing).
- move doing -> review: OK (server trả status=review, position=6.0).
- comment [BAO-CAO]: HỎNG cả 3 lần thử (lần đầu + 2 thử lại, cách nhau 5s,
  timeout 30s) — server trả HTTP 500 Internal Server Error (đúng hiện tượng
  nghẽn SQLite đã biết). Nội dung comment đầy đủ nằm trong sổ này (mục báo cáo
  ở trên); nhờ Viện trưởng đối chiếu/vá khi Kanzo sống lại.
- Người kiểm chéo theo mô tả thẻ: NCKH-011 (khác nhóm).

## 2026-11-21 01:40 — kiểm chéo thẻ 138 (NCKH-001 rà soát tools/pqc.py), đợt 1
- Vai: Phan An (NCKH-006), nhóm kiemdinh, lượt KIỂM CHÉO.
- Đối tượng: thẻ Kanzo id 138 "[PQC] Rà soát tools/pqc.py" của NCKH-001 Nguyễn An,
  kết luận "[KIEM-DINH] KHÔNG ĐẠT có điều kiện" với 4 điểm.
- Tài liệu đã đọc: `vien-nghien-cuu/so-cai/NCKH-001.md` (toàn bộ),
  `tools/pqc.py` (297 dòng, toàn bộ), `vien-nghien-cuu/HIEN-CHUONG.md` mục 6 (API Kanzo).
- Phương pháp (ĐƯỜNG KHÁC tác giả): NCKH-001 chỉ đọc tĩnh (shell hỏng);
  tôi kiểm bằng THỰC THI trên liboqs 0.16.0 / liboqs-python 0.16.0.2 thật
  (shell pwsh sống, `PYTHONPATH=.tooling/pylibs`, `OQS_INSTALL_PATH=.tooling/oqs`).
  Mọi file thử ghi ra `$env:TEMP` (ngoài repo); REPO CHỈ ĐỌC, không git commit.

### Lệnh đã chạy + output quan sát (bằng chứng độc lập)
1. `python tools/pqc.py --self-test` -> PASS, EXIT 0, đủ 5 bước
   (keygen, round-trip, sai khóa, sửa 1 bit, cắt ngắn báo ValueError);
   `Kích thước: pk=1184, sk=2400, ct=1088, ss=32`.
2. Probe exception (`$env:TEMP/probe_pqc_exc.py`, gọi trực tiếp hàm pqc):
   - ct cắt ngắn -> `ValueError: Ciphertext length must be 1088 bytes, got 1087 bytes`
   - pk sai cỡ -> `ValueError: Public key length must be 1184 bytes, got 1183 bytes`
   - sk sai cỡ -> `ValueError: Secret key length must be 2400 bytes, got 2399 bytes`
   - ct dài hơn -> `ValueError: Ciphertext length must be 1088 bytes, got 1089 bytes`
   => wrapper CHỈ ném ValueError cho cả 4 ca sai cỡ, thông điệp rõ ràng.
3. Vòng CLI thật trong TEMP (`keygen --out-dir $t --prefix k1` -> `encap` ->
   `decap`, dùng đúng alias `encap`/`decap`): 3 lệnh EXIT 0, file pk 1184 /
   sk 2400 / ct 1088 / ss 32 byte, `SS_KHOP=True LEN=32`.
4. Nhánh ĐỌC lỗi: `encap` với pk không tồn tại -> thông điệp sạch
   `Không đọc được khóa công khai ... [Errno 2]...`, EXIT 1, không traceback.
5. Nhánh GHI lỗi: `encap` với `--out-ct` trong thư mục cha chưa có ->
   traceback thô `FileNotFoundError` từ dòng 159 `write_bytes`, EXIT 1.
   `keygen` với `--out-dir` là file có sẵn -> traceback thô `FileExistsError`
   từ dòng 139 `mkdir`, EXIT 1.
6. Traversal: `keygen --out-dir sub --prefix ..\oat` -> EXIT 0, file `oat.pk`/
   `oat.sk` GHI RA NGOÀI `--out-dir` (rơi vào thư mục cha). Đã dọn 2 file thử.
7. Tìm kiếm trong `tools/pqc.py`: không có `chmod`/`0o600` ở bất kỳ đâu;
   `cmd_keygen/cmd_encapsulate/cmd_decapsulate` chỉ được gọi từ `main()`
   (dòng 288-292), `self_test()` (dòng 184-240) không hề chạm tầng CLI.
8. `git status --porcelain`: chỉ có dòng `??` (untracked có sẵn), không có
   `M`/`D` — repo không bị sửa bởi lượt kiểm này.

### Đối chiếu từng điểm trong kết luận của NCKH-001
- Điểm 1 (mất đối xứng lỗi đọc/ghi, trung bình): XÁC NHẬN NGUYÊN VẸN bằng
  thực thi (mục 4 vs 5 ở trên). Đọc báo sạch, ghi crash traceback.
- Điểm 2 (self-test chỉ bắt ValueError, CLI bắt (ValueError, RuntimeError),
  trung bình): HIỆU CHỈNH GIẢM MỨC. Thực đo wrapper chỉ ném ValueError
  (mục 2), self-test bước 5 PASS ổn định — không có crash như mối lo.
  CLI bắt rộng hơn là phòng thủ vô hại, không phải mâu thuẫn gây lỗi.
  Đề nghị gộp self-test thành `(ValueError, RuntimeError)` cho bền bản sau,
  mức NHẸ. Điểm "chưa được kiểm chứng" của tác giả nay đã được kiểm chứng.
- Điểm 3 (file `.sk` không chmod 0o600, nhẹ): XÁC NHẬN (mục 7, không có
  chmod trong code). Lưu ý thêm: trên Windows mô hình ACL khác, vẫn nên
  khóa quyền vì tool chạy đa nền tảng.
- Điểm 4 (self-test chưa chạm tầng CLI): XÁC NHẬN (mục 7). Bổ sung độc lập:
  tôi đã chạy thay phần còn thiếu — vòng CLI keygen->encap->decap qua file
  thật + alias encap/decap đều PASS (mục 3). Khoảng trống là độ phủ test,
  không phải hỏng chức năng.
- Điểm phụ prefix `../` (tác giả xếp nhẹ): XÁC NHẬN và ĐỀ NGHỊ NÂNG MỨC lên
  trung bình — thực thi cho thấy ghi ra ngoài `--out-dir` thành công (mục 6).

### Kết luận kiểm chéo
- [KIEM-DINH] ĐẠT cho THẺ REVIEW 138: bài rà soát của NCKH-001 chính xác
  (3/4 điểm xác nhận nguyên vẹn bằng thực thi độc lập, 1 điểm hiệu chỉnh
  giảm mức nhưng quan sát gốc đúng), trung thực về giới hạn (tự khai chỉ
  đọc tĩnh, liệt kê đúng mục cần chạy thật — tôi đã chạy đúng các mục đó).
- Đồng ý với verdict của tác giả về TOOL: `tools/pqc.py` KHÔNG ĐẠT có điều
  kiện — cần bọc OSError đường ghi, chmod `.sk`, chặn prefix traversal,
  bổ sung self-test tầng CLI rồi review lại.
- Trạng thái thẻ 138: review -> done (đẩy opportunistic; xem mục Kanzo dưới).
- Unresolved: (1) đồng bộ Kanzo (nghẽn SQLite, opportunistic); (2) mâu thuẫn
  tài liệu vị trí DLL liboqs (`.tooling/oqs` vs `_oqs` trong home) vẫn cần
  chủ repo chốt — tôi chạy với `OQS_INSTALL_PATH=.tooling/oqs` và PASS nên
  `.tooling/oqs` là đường đúng trên máy này; (3) hành vi wrapper trên bản
  liboqs khác 0.16 (loại exception có thể đổi) — lý do vẫn nên bắt rộng.

## 2026-11-21 01:44 — đồng bộ Kanzo (opportunistic, thẻ 138): THẤT BẠI, chờ Viện trưởng vá
- COMMENT `[KIEM-DINH] ĐẠT...` (nội dung đầy đủ trong script
  `C:\Users\user\AppData\Local\Temp\kanzo_xcheck138.ps1`): HỎNG 3/3
  (lần đầu + 2 thử lại, cách nhau 5s, timeout 30s) — HTTP 500 cả 3 lần.
- MOVE 138 -> done: HỎNG 3/3 (2 lần HTTP 500 + 1 lần timeout 30s).
- Đúng hiện tượng nghẽn SQLite đã biết; dừng thử theo luật, không spam thêm.
- Sổ cái file này là nguồn sự thật: Viện trưởng vá giúp khi Kanzo sống lại —
  comment [KIEM-DINH] ĐẠT + move thẻ 138 -> done (nội dung báo cáo ở mục trên).
