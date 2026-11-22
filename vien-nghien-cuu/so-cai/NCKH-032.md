# Sổ cái NCKH-032 — Vũ Bình, nhóm ML, Viện, đợt 2B

## 2026-11-21 02:21 — nhận việc
- Thẻ: [ML] Kiểm thử chéo Speck (mã NCKH-032; id Kanzo tra cứu cuối việc qua GET board)
- Trạng thái: todo -> doing (đồng bộ Kanzo cuối việc; file trước bảng sau)
- Việc nhận (theo `vien-nghien-cuu/phan-cong.json`, NCKH-032 Vũ Bình, nhóm ML, đợt 2):
  "Kiểm thử chéo Speck" — Vector chuẩn + round-trip + đối chiếu implement độc lập tự viết.
- Tài liệu đã đọc:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, §6 API Kanzo + luật ghi file-trước-bảng-sau)
  - Mục NCKH-032 trong `vien-nghien-cuu/phan-cong.json` (Vũ Bình, nhóm ML, thành viên, đợt 2)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu sổ cái)
  - `vien-nghien-cuu/NHIP-TIM.md` (luật ghi Kanzo)
  - Toàn bộ `tools/ml_distinguisher.py` (Speck32/64 toy + MLP)
  - `docs/research/06-ml-distinguisher.md` (trạng thái vector "chưa xác nhận")
  - `vien-nghien-cuu/so-cai/NCKH-020.md` (nguồn đối chiếu ngoài repo: Gohr deep_speck speck.py,
    expand_key lấy ks[0]=k[-1], test vector key (0x1918,0x1110,0x0908,0x0100),
    pt (0x6574,0x694c) -> ct (0xa868,0x42f2), k0 là TỪ CUỐI)
- Kế hoạch kiểm (3 trụ):
  1. Test vector chuẩn Speck32/64 full 22 vòng + đối chiếu thứ tự khóa k0=từ cuối
     theo nguồn Gohr đã xác nhận (NCKH-020).
  2. Round-trip decrypt(encrypt(p))==p trên NHIỀU R (1..22) + khóa/bản rõ ngẫu nhiên.
  3. Implement Speck32/64 ĐỘC LẬP tự viết trong `$env:TEMP` (không copy code tool,
     viết lại từ đặc tả: n=16, m=4, T=22, alpha=7, beta=2), đối chiếu chéo
     encrypt/decrypt/key-schedule với tool trên vector + ngẫu nhiên nhiều R.
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; không git commit;
  mọi script kiểm riêng trong `$env:TEMP`.
- Shell: mọi lệnh `muse.powershell` kèm `shell="pwsh"`.

## 2026-11-21 02:22 — báo cáo: kiểm thử chéo Speck ĐẠT
- Thẻ: [ML] Kiểm thử chéo Speck (mã NCKH-032)
- Đã làm (3 trụ, REPO CHỈ ĐỌC, mọi script trong `$env:TEMP`):

### Trụ 1 — Test vector chuẩn Speck32/64 (full 22 vòng)
- Nguồn đối chiếu ngoài repo (đã được NCKH-020 xác nhận từ Gohr deep_speck `speck.py`):
  key tài liệu (0x1918,0x1110,0x0908,0x0100), pt (0x6574,0x694c) -> ct (0xa868,0x42f2),
  với `expand_key` lấy ks[0]=k[-1], tức k0 là TỪ CUỐI (k0=0x0100).
- Kết quả trên `tools/ml_distinguisher.py`:
  - k0=từ cuối (0x0100,0x0908,0x1110,0x1918) -> (0xa868,0x42f2) KHỚP vector.
  - k0=từ đầu (0x1918,0x1110,0x0908,0x0100) -> (0x8b78,0xab2e) LỆCH (đúng kỳ vọng:
    chỉ một thứ tự khóa là đúng, loại trừ khả năng vector khớp tình cờ cả hai).
  - decrypt(ct, k0=từ cuối) -> đúng pt (0x6574,0x694c).
- Kết luận trụ 1: ĐẠT. Cách hiểu "k0=tu-cuoi" của tool được nguồn Gohr xác nhận
  độc lập; đề nghị cập nhật trạng thái vector trong `docs/research/06` và comment
  `TEST_KEY_WORDS` trong tool từ "chưa xác nhận" thành "khớp Gohr deep_speck"
  (ngoài phạm vi thẻ này — chỉ kiểm, không sửa).

### Trụ 2 — Round-trip nhiều R (tool tự kiểm: decrypt(encrypt(p))==p)
- Script `$env:TEMP/NCKH-032-roundtrip.py` (seed 32032): R=1..22, mỗi R 200 cặp
  khóa/bản rõ ngẫu nhiên + 5 cặp biên (khóa/pt toàn 0, toàn 0xFFFF, hỗn hợp,
  bit đơn) tại R=1,5,11,22.
- Kết quả: TỔNG 4420 case, LỖI=0 -> PASS. Tool gốc chỉ kiểm R=5,22; kiểm chéo này
  phủ toàn bộ R=1..22.

### Trụ 3 — Đối chiếu implement độc lập tự viết
- File `$env:TEMP/NCKH-032-speck-indep.py`: cài đặt Speck32/64 độc lập từ đặc tả
  (n=16, m=4, T=22, alpha=7, beta=2; hàm `_ror/_rol/lich_khoa/ma_hoa/giai_ma`,
  tên và cấu trúc vòng lặp khác tool, không copy code, không import tool).
  Tự kiểm nội bộ: vector k0=từ cuối -> (a868,42f2) KHỚP; giải mã ngược đúng pt.
- Script `$env:TEMP/NCKH-032-crosscheck.py` (seed 32032):
  - Vector 22 vòng: tool=(a868,42f2), indep=(a868,42f2) -> KHỚP nhau và khớp tài liệu.
  - Lịch khóa: 4 khóa (vector, toàn 0, toàn FFFF, 1234/5678/9ABC/DEF0),
    round key từng vòng khớp 22/22 (vd khóa vector rk0=0100 rk21=ed64).
  - Ngẫu nhiên R=1..22, mỗi R 200 cặp khóa/bản rõ: tool-encrypt == indep-encrypt,
    giải mã chéo 2 chiều (indep giải mã của tool, tool giải mã của indep) đều đúng pt,
    tool-decrypt == indep-decrypt. TỔNG 4400 cặp, LỖI=0 -> PASS.
- Kết luận trụ 3: ĐẠT. Hai cài đặt độc lập khớp nhau tuyệt đối trên vector,
  lịch khóa và 4400 cặp ngẫu nhiên phủ mọi R.

- Tự kiểm (lệnh đã chạy + output chính, shell pwsh, Python 3.12.0, numpy 2.5.4):
  - `python tools/ml_distinguisher.py --self-test` -> vector KHOP (k0=tu-cuoi),
    round-trip PASS, micro-train acc=0.505, KET LUAN PASS, EXIT=0.
  - `python -c ...` (vector 2 thứ tự khóa + decrypt ngược) -> k0=từ cuối KHOP,
    k0=từ đầu LỆCH (8b78,ab2e), decrypt KHOP, EXIT=0.
  - `python $env:TEMP/NCKH-032-roundtrip.py` -> R=1..22 mỗi R 200 mẫu OK +
    biên OK, TONG 4420 case LOI=0 PASS, EXIT=0.
  - `python $env:TEMP/NCKH-032-speck-indep.py` -> vector KHOP + giải mã KHOP, EXIT=0.
  - `python $env:TEMP/NCKH-032-crosscheck.py` -> vector KHOP, 4 lịch khóa KHOP,
    R=1..22 mỗi R 200 cặp OK, TONG 4400 cap LOI=0 PASS, EXIT=0.
  - Repo: chỉ ghi file sổ cái này; không sửa tool/tài liệu; không git commit.
- Kết luận chung: Speck trong `tools/ml_distinguisher.py` ĐÚNG — vector chuẩn khớp
  (k0=từ cuối, có nguồn Gohr xác nhận), round-trip phủ mọi R, implement độc lập
  khớp tuyệt đối. Không phát hiện bug.
- Trạng thái: doing -> review (chờ kiểm chéo; peer review cần đường kiểm độc lập,
  không chạy lại đúng lệnh của tác giả).
- Kanzo: xem mục bên dưới (GET board + move + comment, mỗi lần cách 5s, timeout 30s,
  tối đa 2 lần thử lại; hỏng hoặc không thấy thẻ thì ghi sổ, KHÔNG tự tạo thẻ).

## 2026-11-21 02:24 — đồng bộ Kanzo: KHÔNG THẤY THẺ, đã ghi sổ
- GET board lần 1 (`/api/board?project=esp32-securitykey`, timeout 30s): OK, TOTAL=32.
  Liệt kê đủ id 138..172: các thẻ done NCKH-001..021,024..028 + 6 thẻ todo
  (id 167..172: 3 FIX-tooling, DOC build, OPS baseline, NCKH-022) — KHÔNG có thẻ
  nào mang mã NCKH-032 trong tiêu đề.
- GET board lần 2 (sau 5s, timeout 30s): OK, TOTAL=32, lọc cả title+description
  vẫn KHONG-THAY-THE NCKH-032.
- Kết quả: không move/comment được (không có id thẻ đích). Đúng chỉ thị và
  Hiến chương §6: hỏng hoặc không thấy thẻ thì ghi sổ và tiếp tục, KHÔNG tự tạo thẻ.
  Sổ cái này là nguồn chân lý.
- Nhờ Viện trưởng khi mở đợt 2B trên bảng: tạo thẻ `[ML] Kiểm thử chéo Speck (NCKH-032)`
  của Vũ Bình, dán comment báo cáo (nội dung = mục báo cáo 02:22 trong file này)
  và chuyển thẳng `todo -> doing -> review` (việc đã xong nội dung, chờ kiểm chéo).
- Unresolved:
  - U1: thẻ Kanzo NCKH-032 chưa tồn tại (xác nhận 2 lần GET OK) — nhờ Viện trưởng tạo/vá.
  - U2 (ngoài phạm vi, chuyển Viện trưởng/nhóm tài liệu): trạng thái vector Speck trong
    `docs/research/06-ml-distinguisher.md` và comment `TEST_KEY_WORDS` trong
    `tools/ml_distinguisher.py` vẫn ghi "chưa xác nhận" — sau kiểm chéo này đã đủ
    bằng chứng đổi thành "khớp Gohr deep_speck (k0=từ cuối)".

## 2026-11-21 02:32 — kiểm chéo NCKH-040 Lý Bình: ĐẠT
- Vai: Vũ Bình (NCKH-032), lượt KIỂM CHÉO đợt 2B, kiểm độc lập công việc rà vault
  file hỏng của NCKH-040 (thông điệp gộp gây hiểu lầm, mk rỗng không nhất quán).
- Tài liệu đã đọc: `vien-nghien-cuu/so-cai/NCKH-040.md` (toàn bộ 3 mục),
  `tools/vault.py` (toàn bộ 152 dòng, đối chiếu logic từng ca).
- Đường kiểm ĐỘC LẬP (không dùng probe tác giả `$env:TEMP\nckh040_*_probe.py`):
  script tự viết `$env:TEMP\NCKH-032-vault-crosscheck.py` + lệnh CLI trực tiếp
  trong `$env:TEMP\NCKH032cli`; shell mọi lệnh `muse.powershell` kèm `shell="pwsh"`.
- Kết quả tái hiện (GOOD tự tạo 74B, plain `du-lieu-kiem-cheo-032`):
  1. File 0 byte báo "sai magic" — KHỚP tác giả (gây hiểu lầm, đáng lẽ báo file rỗng).
     API: `rong-0B => ValueError: file không phải két của tool này (sai magic)`;
     CLI decrypt 0 byte: exit 1, cùng câu. Nguyên nhân gốc (tự soi code, dòng 55):
     `blob[:9] != MAGIC` đúng với mọi blob ngắn/rỗng, không có nhánh `len==0` riêng.
  2. Két cụt báo TRÙNG HỆT sai-mk — KHỚP tác giả trên mọi điểm cắt đã thử:
     cut-10B (trong salt), cut-25B (thiếu toàn bộ nonce), header-37B (thiếu cipher),
     cụt 1B cuối (thiếu 1B tag) đều `ValueError: sai mật khẩu hoặc file bị sửa đổi`,
     trùng ca sai-mk. CLI: cut25 và sai-mk cùng exit 1, cùng câu chữ.
     Nguyên nhân gốc (tự soi, dòng 53-63): không kiểm tra độ dài tối thiểu
     (HDR 37B + tag 16B = 53B) trước khi cắt lát; mọi ngoại lệ (nonce ngắn,
     InvalidTag) bị `except Exception` nuốt thành một câu.
  3. password-file rỗng tạo két được — KHỚP tác giả (không nhất quán với nhánh
     tương tác): CLI `encrypt --password-file` rỗng exit 0 (tạo két),
     `decrypt` bằng rỗng exit 0, round-trip KHỚP (True). Nhánh tương tác
     `read_password(confirm=True)` chặn rỗng (dòng 72: `if first != second or
     not first`), còn nhánh `--password-file` (dòng 68) trả nguyên byte file —
     đúng như tác giả mô tả, xác nhận thêm bằng chạy thật chứ không chỉ đọc code.
  4. Tính từ chối đúng: mọi ca hỏng đều bị từ chối (API ValueError, CLI exit 1),
     không ca nào giải mã lọt — KHỚP cột "bị từ chối đúng" của tác giả.
- Tự kiểm (lệnh đã chạy + output chính, shell pwsh):
  - `python tools/vault.py --self-test` -> "self-test ok...", EXIT=0.
  - `python $env:TEMP\NCKH-032-vault-crosscheck.py` -> GOOD-LEN 74; 0B báo sai
    magic; 4 ca cụt + sai-mk cùng một câu sai-mk; EXIT=0.
  - CLI: `encrypt --password-file` rỗng ENC-EMPTY-EXIT=0; `decrypt` bằng rỗng
    DEC-EMPTY-EXIT=0, ROUNDTRIP-KHOP=True; decrypt 0B exit 1 (sai magic);
    decrypt cut25 exit 1 (sai-mk...); decrypt sai-mk exit 1 (cùng câu).
  - 1 lệnh inline `python -c` hỏng do quote pwsh (ParserError, thiếu escape),
    đã chuyển sang script tự viết — không ảnh hưởng kết quả.
- Đối chiếu đề xuất tác giả (không sửa code, repo chỉ đọc): 4 kiến nghị (báo riêng
  két cụt theo độ dài tối thiểu 53B; báo riêng file rỗng; chặn mk rỗng ở nhánh
  password-file; giữ gộp sai-mk/sửa-bit) đều hợp lý, đúng nguyên nhân gốc tôi tự
  soi; ngoài phạm vi kiểm chéo nên chỉ ghi nhận, để chủ tool/Hội đồng quyết.
- Kết luận kiểm định: ĐẠT. Mọi phát hiện chính của NCKH-040 tái hiện được 100%
  bằng đường độc lập; bảng ca hỏng + bảng CLI + phân tích nguyên nhân gốc chính
  xác; không phát hiện phóng đại hay thiếu sót nghiêm trọng (U1-U4 của tác giả
  được ghi rõ, trung thực).
- Repo: CHỈ ĐỌC, trừ chính file sổ cái này (nối thêm mục này); không git commit.
- Kanzo: xem mục đồng bộ bên dưới (GET board tìm thẻ NCKH-040, thử comment
  `[KIEM-DINH]` + move review->done, mỗi lệnh cách 5s, timeout 30s, tối đa 2 thử
  lại; hỏng hoặc không thấy thẻ thì ghi sổ, KHÔNG tự tạo thẻ).

## 2026-11-21 02:33 — đồng bộ Kanzo kiểm chéo NCKH-040: KHÔNG THẤY THẺ
- GET board lần 1 (timeout 30s): OK, TOTAL=45 (tăng từ 32 — Viện trưởng đã mở thêm
  thẻ đợt 2B). Lọc title+description khớp `NCKH-040`: 1 HIT duy nhất id=180
  `[ML] Kiểm thử chéo Speck (NCKH-032)`, status=todo.
- GET board lần 2 (sau 5s, timeout 30s): OK, TOTAL=45. Lọc riêng theo title:
  KHONG-CO-TITLE mang `NCKH-040`. HIT id=180 chỉ khớp ở MÔ TẢ
  (`Nguoi kiem cheo: NCKH-040 (khac nhom)`) — tức NCKH-040 được phân công kiểm
  chéo thẻ Speck của tôi, không phải thẻ việc vault của chính NCKH-040.
- Kết luận: không có thẻ Kanzo cho việc "Rà soát vault file hỏng" của NCKH-040
  (nhất quán với ghi nhận của tác giả lúc 02:23). KHÔNG comment/move được —
  đúng chỉ thị: ghi sổ và tiếp tục, KHÔNG tự tạo thẻ. Kết luận kiểm định ĐẠT
  nằm ở mục 02:32 trong file này (nguồn chân lý).
- Ghi chú cho Viện trưởng: khi tạo thẻ việc NCKH-040, dán comment
  `[KIEM-DINH] đạt — Vũ Bình (NCKH-032) tái hiện độc lập 100%: 0B báo sai magic,
  két cụt trùng sai-mk, password-file rỗng tạo két được; xem sổ NCKH-032 mục
  02:32` và chuyển thẳng `todo -> doing -> review -> done` (việc xong, đã qua
  kiểm chéo). Thẻ id=180 của tôi vẫn ở todo — nhờ Viện trưởng chuyển
  `todo -> doing -> review` (nội dung Speck đã xong từ 02:22, chờ NCKH-040 kiểm).
- Unresolved kiểm chéo:
  - U1: thẻ Kanzo NCKH-040 chưa tồn tại (xác nhận 2 lần GET OK, TOTAL=45).
  - U2: chưa kiểm đường gõ mật khẩu tương tác (getpass) — kế thừa U1 của tác giả;
    nhánh tương tác chỉ xác nhận bằng đọc code dòng 66-75, không chạy thật.
  - U3: 4 kiến nghị sửa thông điệp của tác giả chưa được duyệt/vá — ngoài phạm vi.
