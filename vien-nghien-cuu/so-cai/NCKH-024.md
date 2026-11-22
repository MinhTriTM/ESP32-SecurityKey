# Sổ cái NCKH-024 — Tạ An (nhóm kiemdinh, đợt 2A)

## 2026-11-21 01:55 — nhận việc
- Nhiệm vụ (phan-cong.json): "Vector BIP-39 bổ sung" — Tra thêm vector 24 từ chuẩn, chạy qua tool mnemonic.
- Thẻ Kanzo: tìm ở bước đồng bộ cuối (GET board, lọc mã NCKH-024).
- Trạng thái: todo -> doing

## 2026-11-21 01:57 — báo cáo kiểm định BIP-39
- Đã làm: tra 24 vector BIP-39 tiếng Anh chuẩn, chạy từng vector qua `tools/mnemonic.py`
  cả 3 chiều `from-entropy`, `to-entropy`, `seed --passphrase TREZOR`.
- Nguồn vector (duy nhất, tin cậy): `trezor/python-mnemonic`, file `vectors.json`
  (bản master, tải ngày 2026-11-21 qua
  `https://raw.githubusercontent.com/trezor/python-mnemonic/master/vectors.json`).
  Đây là vector của implementation tham chiếu BIP-39, mỗi mục gồm
  entropy hex + mnemonic + seed(passphrase "TREZOR") + xprv.
- Phương pháp (chống chép tay sai): script `nckh024_vectors.ps1` đọc entropy/mnemonic/seed
  TRỰC TIẾP từ `vectors.json` đã tải, gọi CLI thật của tool, so sánh chuỗi chính xác.
  Entropy ghi ra file tạm trong `$env:TEMP` (repo chỉ đọc, không ghi file tạm vào repo).
- Quy ước: KHỚP = output của tool trùng 100% vector nguồn; LỆCH = khác.

### Nhóm 24 từ (8 vector, ưu tiên)
- VEC-09 | entropy `0000000000000000000000000000000000000000000000000000000000000000`
  - mnemonic: abandon abandon abandon abandon abandon abandon abandon abandon abandon
    abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon
    abandon abandon abandon abandon art
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-10 | entropy `7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f`
  - mnemonic: legal winner thank year wave sausage worth useful legal winner thank year
    wave sausage worth useful legal winner thank year wave sausage worth title
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-11 | entropy `8080808080808080808080808080808080808080808080808080808080808080`
  - mnemonic: letter advice cage absurd amount doctor acoustic avoid letter advice cage
    absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic
    bless
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-12 | entropy `ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`
  - mnemonic: zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo
    zoo zoo zoo zoo zoo vote
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-15 | entropy `68a79eaca2324873eacc50cb9c6eca8cc68ea5d936f98787c60c7ebc74e6ce7c`
  - mnemonic: hamster diagram private dutch cause delay private meat slide toddler razor
    book happy fancy gospel tennis maple dilemma loan word shrug inflict delay length
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-18 | entropy `9f6a2878b2520799a44ef18bc7df394e7061a224d2c33cd015b157d746869863`
  - mnemonic: panda eyebrow bullet gorilla call smoke muffin taste mesh discover soft
    ostrich alcohol speed nation flash devote level hobby quick inner drive ghost inside
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-21 | entropy `066dca1a2bb7e8a1db2832148ce9933eea0f3ac9548d793112d9a95c9407efad`
  - mnemonic: all hour make first leader extend hole alien behind guard gospel lava path
    output census museum junior mass reopen famous sing advance salt reform
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-24 | entropy `f585c11aec520db57dd353c69554b21a89b20fb0650966fa0a9d6f74fd989d8f`
  - mnemonic: void come effort suffer camp survey warrior heavy shoot primary clutch
    crush open amazing screen patrol group space point ten exist slush involve unfold
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP

### Nhóm 12 từ (8 vector)
- VEC-01 | entropy `00000000000000000000000000000000`
  - mnemonic: abandon abandon abandon abandon abandon abandon abandon abandon abandon
    abandon abandon about
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-02 | entropy `7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f`
  - mnemonic: legal winner thank year wave sausage worth useful legal winner thank yellow
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-03 | entropy `80808080808080808080808080808080`
  - mnemonic: letter advice cage absurd amount doctor acoustic avoid letter advice cage above
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-04 | entropy `ffffffffffffffffffffffffffffffff`
  - mnemonic: zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-13 | entropy `9e885d952ad362caeb4efe34a8e91bd2`
  - mnemonic: ozone drill grab fiber curtain grace pudding thank cruise elder eight picnic
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-16 | entropy `c0ba5a8e914111210f2bd131f3d5e08d`
  - mnemonic: scheme spot photo card baby mountain device kick cradle pact join borrow
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-19 | entropy `23db8160a31d3e0dca3688ed941adbf3`
  - mnemonic: cat swing flag economy stadium alone churn speed unique patch report train
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-22 | entropy `f30f8c1da665478f49b001d94c5fc452`
  - mnemonic: vessel ladder alter error federal sibling chat ability sun glass valve picture
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP

### Nhóm 18 từ (8 vector)
- VEC-05 | entropy `000000000000000000000000000000000000000000000000`
  - mnemonic: abandon abandon abandon abandon abandon abandon abandon abandon abandon
    abandon abandon abandon abandon abandon abandon abandon agent
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-06 | entropy `7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f`
  - mnemonic: legal winner thank year wave sausage worth useful legal winner thank year
    wave sausage worth useful legal will
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-07 | entropy `808080808080808080808080808080808080808080808080`
  - mnemonic: letter advice cage absurd amount doctor acoustic avoid letter advice cage
    absurd amount doctor acoustic avoid letter always
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-08 | entropy `ffffffffffffffffffffffffffffffffffffffffffffffff`
  - mnemonic: zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo when
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-14 | entropy `6610b25967cdcca9d59875f5cb50b0ea75433311869e930b`
  - mnemonic: gravity machine north sort system female filter attitude volume fold club
    stay feature office ecology stable narrow fog
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-17 | entropy `6d9be1ee6ebd27a258115aad99b7317b9c8d28b6d76431c3`
  - mnemonic: horn tenant knee talent sponsor spell gate clip pulse soap slush warm silver
    nephew swap uncle crack brave
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-20 | entropy `8197a4a47f0425faeaa69deebc05ca29c0a5b5cc76ceacc0`
  - mnemonic: light rule cinnamon wrap drastic word pride squirrel upgrade then income
    fatal apart sustain crack supply proud access
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP
- VEC-23 | entropy `c10ec20dc3cd9f652c7fac2f1230f7a3c828389a14392f05`
  - mnemonic: scissors invite lock maple supreme raw rapid void congress muscle digital
    elegant little brisk hair mango congress clump
  - from-entropy: KHỚP | to-entropy: KHỚP | seed: KHỚP

### Tự kiểm (lệnh đã chạy + output)
- `python tools/mnemonic.py --self-test` (Python 3.12.0) ->
  `self-test ok: bảng BIP-39 nguyên vẹn, vector chuẩn đúng, checksum bắt lỗi.`
- Script `nckh024_vectors.ps1` (72 lệnh CLI: 24 from-entropy + 24 to-entropy + 24 seed) ->
  `TONG: pass=24 fail=0 total=24` (log đầy đủ ở `$env:TEMP/nckh024_vectors.log`).
- Đối chiếu thủ công VEC-15 (không qua script, gõ tay từng lệnh):
  - `python tools/mnemonic.py from-entropy --from-file spot.bin` (32 byte
    `68a79eac...e6ce7c`) -> đúng cụm `hamster diagram ... delay length`.
  - `python tools/mnemonic.py to-entropy hamster diagram ... delay length` ->
    `Entropy (32 byte): 68a79eaca2324873eacc50cb9c6eca8cc68ea5d936f98787c60c7ebc74e6ce7c`.
- Không sửa code repo: chỉ ghi đúng file sổ cái này; file tạm entropy chỉ ở `$env:TEMP`.

### Kết luận
- 24/24 vector KHỚP cả 3 chiều, 0 LỆCH. Riêng 8/8 vector 24 từ KHỚP.
- `tools/mnemonic.py` tương thích BIP-39 chuẩn trên toàn bộ vector tham chiếu tiếng Anh.
- Trạng thái: doing -> review (đồng bộ Kanzo sau, xem mục tiếp theo).

## 2026-11-21 02:01 — đồng bộ Kanzo (thất bại đúng quy trình, đã ghi sổ)
- GET `http://100.101.100.100:4242/api/board?project=esp32-securitykey` (timeout 30s):
  lần 1 -> 500 Internal Server Error; chờ 5s thử lại lần 2 -> 500; chờ 5s thử
  lại lần 3 -> 200, đọc được 21 thẻ (todo 5, doing 2, review 2, done 12).
- Kết quả tìm thẻ: KHÔNG có thẻ nào mang mã NCKH-024 (thẻ đợt 2A mới chỉ có tới
  NCKH-021; chưa có thẻ NCKH-022/023/024). Không có thẻ nên không thể move/comment.
- Quyết định: KHÔNG tự tạo thẻ (việc tạo thẻ sóng thuộc về Viện trưởng; các sổ
  NCKH-001..012 đều nhận thẻ có sẵn). Không ghi gì lên bảng trong nhịp này.
- Nhờ Viện trưởng: tạo thẻ `[kiemdinh] Vector BIP-39 bổ sung (NCKH-024)`, chuyển
  thẳng `review` với nội dung báo cáo ở mục trên (24/24 vector KHỚP).
- Trạng thái thẻ: (chưa có thẻ) — sổ file này là bản chính cho tới khi đồng bộ.

## 2026-11-21 02:07 — kiểm chéo NCKH-016 (Đinh An: rà hid_echo)

- Vai: Tạ An (NCKH-024), lượt kiểm chéo đợt 2A, REPO CHỈ ĐỌC (trừ sổ này),
  shell `pwsh`, không git commit.
- Đối tượng: `vien-nghien-cuu/so-cai/NCKH-016.md` + `tools/hid_echo.py` (88 dòng).
  Tác giả báo 3 phát hiện chính: bắt nhầm thiết bị 0xFF00, assert, report ID.
- Đã đọc: toàn bộ sổ NCKH-016, toàn bộ `tools/hid_echo.py`.
  KHÔNG chạy lại script của tác giả (`nckh016_selftest.py`, `nckh016_probe.py`);
  mọi probe dưới đây tự viết mới trong `$env:TEMP` (tiền tố `nckh024_`).

### Đường kiểm độc lập (khác tác giả)

1. Quét HID thật bằng probe riêng `$env:TEMP/nckh024_scan.py`: liệt kê TOÀN BỘ
   thiết bị (không chỉ đếm), in đầy đủ VID/PID/usage/usage_page/manufacturer/
   product/path, mô phỏng logic first-match `hid_echo.py:51`, kiểm tra VID
   ESP32 phổ biến (0x303A/0x10C5/0x1A86). Chạy với
   `PYTHONPATH=.tooling/pylibs` (tìm thấy `hid.cp312-win_amd64.pyd` ở đó;
   python hệ thống không có sẵn module hid).
2. Tái hiện phát hiện #2 (assert) bằng ĐƯỜNG KHÁC: gọi TRỰC TIẾP
   `build_report(bytes(65))` (không qua `self_test()` như tác giả), chạy cùng
   file 2 chế độ `python` và `python -O` (`nckh024_assert.py`).
3. Tái hiện phát hiện #3 (report ID) bằng mock viết lại từ đầu: chặn
   `sys.modules["hid"]` (vì `main()` import hid cục bộ), mock trả echo 65 byte
   với byte0=2 nhưng body khớp payload, kèm case đối chứng ID=1
   (`nckh024_reportid.py`).

### Số liệu độc lập

- Quét thật (`nckh024_scan.py`, EXIT=0): TỔNG 17 HID, đúng 2 thiết bị 0xFF00 —
  KHỚP con số của tác giả, có thêm chi tiết VID/PID:
  - #0: VID=0x06CB PID=0xCEA1, usage_page=65280, usage=1,
    Microsoft / HIDI2C Device (touchpad Synaptics, theo path VEN_06CB).
  - #1: VID=0x187C PID=0x0551, usage_page=65280, usage=1,
    Alienware / AW-ELC.
- FIRST-MATCH theo logic tool: mở đúng #0 HIDI2C (driver hệ thống) — tái hiện
  phát hiện #1: tool sẽ gửi 65 byte lạ vào driver touchpad.
- Thiết bị VID ESP32 (303A/10C5/1A86): 0 — KHỚP "không có ESP32" của tác giả.
- Assert (`nckh024_assert.py`): `python` thường từ chối 65 byte
  ("payload tối đa 64 byte"); `python -O` CHẤP NHẬN, đóng gói report dài
  66 byte (byte0=1) để ghi xuống HID — tái hiện phát hiện #2.
- Report ID (`nckh024_reportid.py`, EXIT=0): echo ID=2 vẫn in "HID echo ok",
  rc=0; đối chứng ID=1 rc=0 (mock hợp lệ) — tái hiện phát hiện #3.

### Đánh giá (ngoài 3 phát hiện được giao kiểm)

- Phát hiện #1 VỮNG, nhưng đề xuất sửa "lọc thêm usage==1" của tác giả là
  KHÔNG ĐỦ: cả 2 thiết bị lạ đều có usage=1 (số liệu trên). Muốn hết bắt nhầm
  phải lọc VID/PID hoặc liệt kê cho người dùng chọn — hai phương án còn lại
  trong cùng đề xuất của tác giả vẫn đúng. Ghi nhận là bổ sung, không trừ điểm
  (phát hiện lỗi mới là chính, đề xuất sửa chỉ là gợi ý).
- Phát hiện #2, #3 VỮNG, tái hiện độc lập 100%.
- Các mục nhẹ #4 (hai nền tảng report ID), #5 (thiết bị câm): đọc code
  `hid_echo.py:68-75` thấy logic đúng như tác giả mô tả (bóc byte0 khi dài 65,
  `not echo` -> rc=1); không chạy lại mock của tác giả theo đúng luật kiểm
  chéo (chỉ tái hiện tối thiểu 1/3 — thực tế đã tái hiện cả 3/3 chính).
- Đối chiếu firmware (#7): `hwtest.ino` (Usage Page 0xFF00, Report ID 1,
  Count 64) khớp mô tả; không xác minh sâu vì ngoài phạm vi 3 phát hiện.
- Unresolved U1-U3 của tác giả (thiếu board thật, thiếu Linux, chưa đo _onOutput):
  hợp lý, giữ nguyên, không chặn đạt (đúng phạm vi rà soát).

### Kết luận kiểm chéo: ĐẠT

- Cả 3/3 phát hiện chính tái hiện độc lập thành công bằng probe tự viết.
- Số liệu quét thật khớp hoàn toàn (2 thiết bị 0xFF00, đúng tên HIDI2C/AW-ELC,
  không ESP32), có bổ sung VID/PID và bằng chứng first-match mở nhầm driver.
- Bổ sung 1 lưu ý cho đợt sau: đề xuất lọc usage==1 không đủ (cả 2 thiết bị lạ
  đều usage=1) — nên ưu tiên lọc VID/PID.
- Đề xuất Kanzo: thẻ 156 review -> done + comment `[KIEM-DINH]`.

### Unresolved (lượt kiểm chéo)

- U-X1: chưa kiểm #4/#5 bằng mock riêng (chỉ đọc code) — chấp nhận được vì đã
  vượt yêu cầu tối thiểu (3/3 thay vì 1/3).
- U-X2: main() end-to-end với ESP32 thật vẫn chưa ai chạy (kế thừa U1 tác giả).
- U-X3: Kanzo: xem mục đồng bộ dưới (ghi sau khi thử API).

## 2026-11-21 02:10 — đồng bộ Kanzo kiểm chéo NCKH-016 (thẻ 156, thành công)

- GET board OK lần 1: tìm thẻ `[tooling] Rà soát hid_echo hai nền tảng
  (NCKH-016)`, id 156, status=review (đúng như sổ tác giả).
- Comment `[KIEM-DINH] đạt...`: 500 lần 1, OK lần 2.
- Move review->done: timeout 30s lần 1, 500 lần 2, OK lần 3 (trả status=done).
  Mỗi lệnh cách nhau 5s, đúng quota tối đa 2 thử lại.
- Đối chiếu sau đợt (GET board): thẻ 156 status=done, comments=2 (trước đó
  tác giả ghi comments=1) — khớp đúng +1 comment kiểm định, không trùng lặp
  (lần 500 đầu không ghi). Không đọc được nội dung comment (API không có
  GET comments — thử GET trả 405), nhưng số lượng khớp nên tin cậy.
- Kết quả: thẻ 156 review -> done, đủ comment kiểm định. Lượt kiểm chéo hoàn tất.
