# Sổ cái NCKH-056 — Phan Cường, nhóm ML, Viện, đợt 2C

## 2026-11-21 03:10 — nhận việc
- Thẻ: [ML] Đề xuất thí nghiệm tiếp theo (mã NCKH-056; id Kanzo tra cứu cuối việc qua GET board)
- Trạng thái: todo -> doing (đồng bộ Kanzo cuối việc; file trước bảng sau)
- Việc nhận (theo `vien-nghien-cuu/phan-cong.json`, NCKH-056 Phan Cường, nhóm ML, đợt 2):
  "Đề xuất thí nghiệm tiếp theo: Simon hay Skinny? Viết đề xuất kèm chi phí ước tính."
  Phạm vi: CHỈ VIẾT ĐỀ XUẤT, CHƯA CODE.
- Tài liệu đã đọc:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, §6 API Kanzo + luật file-trước-bảng-sau)
  - Mục NCKH-056 trong `vien-nghien-cuu/phan-cong.json`
  - `vien-nghien-cuu/so-cai/README.md`
  - `docs/research/06-ml-distinguisher.md` (toàn bộ)
  - Sổ cái nhóm ML: NCKH-002 (tái hiện baseline), NCKH-008 (50k mẫu R=7 âm tính),
    NCKH-014 (CNN 1D thua MLP), NCKH-020 (tóm tắt Gohr 2019 + bảng khác biệt),
    NCKH-032 (kiểm thử chéo Speck ĐẠT), NCKH-038 (R=8 ngân sách x10 âm tính + ước tính R=9)
  - Nguồn ngoài (web, đã đọc): Hou et al., "Improve Neural Distinguishers of SIMON
    and SPECK", Security and Communication Networks 2021 (Hindawi, open access) —
    bảng chênh lệch đầu vào + accuracy cho SIMON32/64 (trích chi tiết ở mục báo cáo).
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; không git commit;
  mọi lệnh shell kèm `shell="pwsh"`.

## 2026-11-21 03:20 — báo cáo: đề xuất thí nghiệm ML tiếp theo (Simon trước, Skinny sau)

### 1. Hiện trạng nhóm ML (điểm xuất phát của đề xuất)

| Thẻ | Việc | Kết quả (seed 1337, CPU) |
|-----|------|--------------------------|
| NCKH-002 | Tái hiện baseline Speck32/64, MLP 64->128->64->1, 6k/2k/5ep | R=5: 0.5970, R=6: 0.5245, R=7: 0.5070 (~2s cả 3 R) |
| NCKH-008 | Tăng mẫu 50k ở R=7 | 0.4970 — ÂM TÍNH, tăng mẫu không cứu được R=7 |
| NCKH-014 | CNN 1D thay MLP, cùng ngân sách | R=5: 0.500/0.507 (thua xa 0.597) — negative result có giá trị |
| NCKH-038 | R=8 ngân sách x10 (60k mẫu x 50 epoch) | 0.4870 — ÂM TÍNH; baseline R=8: 0.4905, R=9: 0.4910 |
| NCKH-020 | Tóm tắt Gohr 2019 | Lỗ hổng lớn nhất của ta: nhãn 0 là ngẫu nhiên thuần (bài toán DỄ hơn Gohr), dữ liệu nhỏ hơn ~1600 lần, MLP thay ResNet |
| NCKH-032 | Kiểm thử chéo Speck | ĐẠT: vector khớp Gohr deep_speck (k0=từ cuối), round-trip R=1..22 0 lỗi |

Kết luận nền: đường Speck32/64 + MLP + chênh lệch (0x0040,0x0000) đã cạn ở R>=7
với ngân sách CPU rẻ. Muốn học tiếp phải đổi MÃ (mới) hoặc đổi CHÊNH LỆCH/DỮ LIỆU
(cùng mã). Đề xuất dưới đây làm cả hai, theo thứ tự rẻ trước đắt sau.

### 2. Khuyến nghị chính (tóm tắt 1 đoạn)

Giai đoạn 1: làm **SIMON32/64** (cùng khổ khối/khóa 32/64 với Speck → tái dùng
nguyên pipeline MLP + ngân sách + so sánh trực tiếp; cấu trúc Feistel+AND khác hẳn
ARX của Speck nên câu hỏi khoa học là mới). Giai đoạn 2: **SKINNY-64-128** (họ SPN
khác hẳn hai mã trên, nhưng khối 64 bit khiến đặc trưng và cài đặt nặng hơn —
làm sau khi pipeline Simon đã ổn). Song song, 1 thẻ RẺ trên chính Speck: thử
chênh lệch mới (0x2800,0x0010) ở R=8 (tài liệu báo 8 vòng 56.49% với định dạng
mới — với MLP của ta có thể vẫn âm tính nhưng chỉ tốn ~25 giây CPU để biết).

### 3. Vì sao Simon32/64 trước

1. **Tái dùng toàn bộ pipeline:** Simon32/64 có khối 32 bit = 2 từ 16 bit, khóa
   64 bit = 4 từ 16 bit (chuẩn 32 vòng) — cùng khổ với Speck32/64. Đặc trưng
   64 bit nối cặp bản mã, MLP 64->128->64->1, ngân sách 6k/2k/5ep giữ nguyên được.
   So sánh Speck-vs-Simon là công bằng theo đúng nghĩa (cùng mạng, cùng tiền).
2. **Câu hỏi khoa học mới, không phải lặp lại:** Speck là ARX (cộng modulo là
   nguồn phi tuyến); Simon là Feistel với hàm f(x) = (S^1(x) & S^8(x)) xor S^2(x)
   (phép AND là nguồn phi tuyến). Distinguisher MLP "chết" ở vòng thứ mấy trên
   mỗi họ? Đây là kết quả so sánh mà nhóm chưa có.
3. **Tài liệu có sẵn chênh lệch tốt + bằng chứng nó học được:** bài báo 2021 đã
   đọc xác nhận: Benamira et al. (Eurocrypt 2021) dựng distinguisher nơ-ron
   8 vòng SIMON32/64 đạt 82.2%; với đúng định dạng Gohr (một cặp bản mã, SCP)
   chênh lệch (0x0,0x40) từ Abed et al. cho 9 vòng 59.07%, chênh lệch
   (0x0,0x80) cho 9 vòng 59.77% (mạng ResNet, ngân sách lớn). Nghĩa là tín hiệu
   tồn tại tới 9 vòng — MLP nhỏ của ta sẽ mù sớm hơn, nhưng chắc chắn có tín hiệu
   ở vòng thấp để đối chứng pipeline (xem tiêu chí thất bại ở §7).
4. **Chi phí tương đương Speck:** một vòng Simon chỉ gồm xoay bit + AND + XOR
   trên 16 bit — cùng độ phức tạp với một vòng Speck (cộng + xoay + XOR). Sinh
   dữ liệu numpy vector hóa dự kiến trong ±50% thời gian Speck; huấn luyện Y HỆT
   (cùng kích thước dữ liệu + cùng mạng). Không cần GPU, không cần RAM lớn.
5. **Test vector có sẵn:** đặc tả Simon của NSA kèm vector chuẩn cho mọi bản
   (Simon32/64: khóa 1918 1110 0908 0100, bản rõ 6565 6877 -> bản mã c69b e9bb —
   NGƯỜI NHẬN THẺ IMPLEMENT PHẢI ĐỐI CHIẾU LẠI TỪ ĐẶC TẢ, số này tôi ghi theo trí
   nhớ, CHƯA xác minh, không dùng làm cổng đạt/không đạt cho tới khi có nguồn).

### 4. Chênh lệch đề xuất cho Simon32/64

- **Chênh lệch chính: (dx, dy) = (0x0000, 0x0040).** Nguồn: Abed et al. (đặc trưng
  vi sai Simon), được dùng trong bài báo 2021 đã đọc (9 vòng SIMON32/64, 59.07%
  với định dạng SCP). Lưu ý quan trọng: khác Speck (chênh lệch ở từ đầu
  0x0040,0x0000), chênh lệch Simon tốt nằm ở TỪ THỨ HAI.
- **Chênh lệch dự phòng: (0x0000, 0x0080)** (bài báo 2021: 9 vòng 59.77% SCP).
  Chỉ thử khi chênh lệch chính cho kết quả mù toàn dải hoặc khi thẻ sweep còn dư
  ngân sách — mỗi chênh lệch thêm tốn gấp đôi tiền quét.
- **Dải vòng quét (ngân sách chuẩn 6k/2k/5ep trước): R = 5, 6, 7, 8, 9.**
  Lý do quét từ 5: tài liệu cho thấy Simon "sống" tới 9 vòng với mạng lớn, nhưng
  MLP nhỏ của ta có thể mù từ R=7 như Speck — quét từ thấp để (a) bắt được điểm
  rơi accuracy, (b) có đối chứng dương ở R thấp (xem §7).
- **Nhãn 0: DÙNG KIỂU GOHR NGAY TỪ ĐẦU** (cặp bản rõ ngẫu nhiên độc lập, cùng mã
  hóa R vòng — đúng distinguisher vi sai), thay vì 64 bit ngẫu nhiên thuần như
  tool Speck hiện tại (NCKH-020 đã chỉ ra đây là lỗ hổng phương pháp lớn nhất).
  Nếu người implement muốn so sánh công bằng với số Speck cũ thì chạy thêm 1 cấu
  hình nhãn-0-cũ — rẻ (sinh dữ liệu chỉ ~6% ngân sách x10, vài giây ở ngân sách
  chuẩn), và phải ghi rõ trong báo cáo cấu hình nào so với cấu hình nào.

### 5. Vì sao SKINNY-64-128 đi sau (giai đoạn 2)

1. **Giá trị khoa học:** SKINNY là họ SPN (Sbox 4 bit + ShiftRows + MixColumns,
   tweakey) — khác hẳn cả ARX (Speck) lẫn Feistel-AND (Simon). Có số liệu cả 3 họ
   thì nhóm mới có bức tranh so sánh đúng nghĩa. Đây là lý do DUY NHẤT nó đáng làm.
2. **Giá phải trả:** khối 64 bit → cặp bản mã 128 bit → đặc trưng GẤP ĐÔI (MLP
   lớp đầu 128 thay vì 64, tham số tăng ~2 lần); một vòng SKINNY gồm SubCells
   (16 tra Sbox) + AddConstants + AddRoundTweakey + ShiftRows + MixColumns (chuỗi
   XOR) — nặng hơn một vòng Speck/Simon khoảng 5–10 lần số phép numpy; chuẩn
   SKINNY-64-128 là 36 vòng (TK-2). Tổng: sinh dữ liệu chậm hơn Speck ước 3–8
   lần, huấn luyện nặng hơn ~2 lần (lớp đầu to gấp đôi). Vẫn chạy được trên CPU
   ở ngân sách chuẩn (xem §6), nhưng implement đúng + validate tốn 1–2 thẻ riêng.
3. **Chưa có chênh lệch cụ thể:** tôi CHƯA đọc tài liệu vi sai/ neural distinguisher
   cho SKINNY nên KHÔNG bịa chênh lệch ở đây. Giai đoạn 2 bắt đầu bằng 1 thẻ đọc
   tài liệu kiểu NCKH-020 (đặc tả SKINNY + bài neural distinguisher nếu có) rồi mới
   chốt chênh lệch + dải vòng. Bản đề xuất: SKINNY-64-128 (TK-2, 36 vòng), quét
   từ R thấp (4–8) ở ngân sách chuẩn trước.
4. **Thứ tự cứng:** KHÔNG mở thẻ implement SKINNY trước khi thẻ validate Simon
   xong — pipeline dữ liệu/nhãn-0-GOHR phải được chứng minh đúng trên Simon (mã
   rẻ) rồi mới mang sang mã đắt.

### 6. Hướng khác rẻ: Speck R=8 với chênh lệch mới (làm song song, 1 thẻ ngắn)

- Bài báo 2021 đã đọc báo: SPECK32/64 8 vòng với chênh lệch (0x2800,0x0010) đạt
  56.49% (định dạng MOD — ma trận nhiều hiệu đầu ra, không phải SCP; với SCP số
  này có thể thấp hơn). Nhóm ta ở R=8 với chênh lệch cũ (0x40,0x0) được 0.487–0.4905
  (NCKH-038). Câu hỏi 25-giây: đổi chênh lệch sang (0x2800,0x0010) ở ngân sách
  chuẩn/x10, MLP của ta có nhích khỏi 0.5 không?
- Dự đoán trung thực: khả năng cao VẪN ÂM TÍNH (56.49% kia dùng định dạng dữ liệu
  mạnh hơn + mạng lớn hơn), nhưng chi phí 1 lần chạy x10 ≈ 25 giây CPU nên đáng
  thử — âm tính cũng là dữ kiện (chênh lệch tốt của mạng lớn chưa chắc cứu được
  mạng nhỏ).
- Phạm vi thẻ này: chỉ đổi chênh lệch + chạy R=8 (chuẩn và x10), KHÔNG đụng kiến
  trúc/định dạng MOD (định dạng MOD cần mạng mới — vượt ngân sách CPU rẻ, để dành).

### 7. Ngân sách ước tính (neo theo số đo thật của nhóm)

Cơ sở đo (NCKH-002/038, máy dev CPU): Speck baseline 6k/5ep ≈ 0.5–0.6s/vòng
(tool); sinh 62k mẫu R=8 = 1.45s, R=9 = 1.70s; huấn luyện 3M lượt-mẫu ≈ 22.1s;
tổng x10 (60k x 50ep) ≈ 23.6s tool / ~25.2s wall, peak RAM ~52 MB.

| Hạng mục | Cấu hình | Ước CPU (tool) | Ước wall | RAM |
|----------|----------|----------------|----------|-----|
| Simon implement + self-test + vector + round-trip | code 1 lần | < 5s | — | < 100 MB |
| Simon sweep chuẩn R=5..9 (6k/2k/5ep, nhãn-0-Gohr) | 5 R | 5 x 0.5–1s ≈ 5s | ~10s | < 100 MB |
| Simon x10 ở R mù đầu tiên (60k x 50ep) | 1 R | ~25–35s | ~40s | ~60 MB |
| Simon chênh lệch dự phòng (nếu cần) | như sweep | x2 dòng sweep | x2 | như trên |
| Speck diff mới R=8 (chuẩn + x10) | 2 chạy | ~1s + ~25s | ~35s | ~60 MB |
| SKINNY-64 đọc tài liệu + chốt chênh lệch | 0 chạy | 0 | — | — |
| SKINNY-64 implement + validate | code 1 lần | < 30s | — | < 200 MB |
| SKINNY-64 sweep chuẩn R=4..8 | 5 R | 5 x 3–8s ≈ 15–40s | ~1–2 phút | < 200 MB |
| SKINNY-64 x10 (nếu sweep có tín hiệu) | 1–2 R | 2–6 phút/R | ~3–8 phút | < 300 MB |

- Thời gian AGENT (người): Simon implement+validate ≈ 1 thẻ (30–60 phút, mẫu là
  NCKH-032); Simon sweep ≈ 1 thẻ ngắn (15–30 phút); Speck diff mới ≈ 1 thẻ ngắn
  (15 phút); SKINNY đọc tài liệu ≈ 1 thẻ (30 phút); SKINNY implement ≈ 1–2 thẻ
  (1–2 giờ, nặng nhất); SKINNY sweep ≈ 1 thẻ ngắn.
- Tổng CPU cả giai đoạn 1 + thẻ Speck rẻ: DƯỚI 3 PHÚT. Tổng CPU giai đoạn 2:
  dưới 15 phút. Toàn bộ đề xuất chạy được trên máy dev hiện tại, không cần GPU,
  không cần mua gì. Rủi ro ước tính: số Simon tin cậy (±50%, cùng họ chi phí với
  Speck đã đo); số SKINNY là ước thô (±2 lần, chưa có số đo — người nhận thẻ
  implement phải đo thật và hiệu chỉnh trước khi mở thẻ sweep x10).

### 8. Tiêu chí thành công / thất bại (áp cho mọi thẻ thí nghiệm dưới đề xuất này)

- **Cổng 0 — đúng đắn cài đặt (BẮT BUỘC, fail là fail cả thẻ):** test vector khớp
  nguồn ngoài repo + round-trip decrypt(encrypt(p))==p trên mọi R quét (mẫu
  NCKH-032: nhiều R, 0 lỗi) + kiểm chéo implement độc lập. Chưa qua cổng 0 thì
  mọi số accuracy đều vô nghĩa.
- **Thành công thí nghiệm (đạt 1 trong 2):**
  (a) Có ≥1 mức R mà accuracy vượt 0.5 CÓ Ý NGHĨA THỐNG KÊ và TÁI HIỆN được:
  với test 2000 (σ≈0.0112) yêu cầu ≥0.525 (≈2.2σ); nếu muốn khẳng định yếu hơn
  (0.51–0.525) thì phải tăng test lên 10k (σ≈0.005, ≥0.515 ≈ 3σ) và lặp ≥2 seed
  khác nhau cho cùng kết luận. (b) Âm tính toàn dải R quét NHƯNG có đối chứng
  dương ở R rất thấp (R=3–4 phải >0.5 rõ ràng, vd ≥0.55) — chứng tỏ pipeline học
  được khi tín hiệu còn, và điểm mù ở R cao là dữ kiện thật (mẫu: NCKH-008/038).
- **Thất bại thí nghiệm (báo fail trung thực, không phải fail cá nhân):**
  (i) rớt cổng 0; (ii) MÙ CẢ Ở R=3–4 (accuracy ~0.5 ở vòng rất thấp nơi vi sai cổ
  điển còn tín hiệu mạnh) → gần như chắc chắn bug pipeline dữ liệu/nhãn, phải
  dừng và debug, không được rào đón bằng "kết quả âm tính"; (iii) kết quả đổi
  chiều khi đổi seed ở R thấp (không tái hiện).
- **Ranh giới diễn giải (bắt buộc ghi trong mọi báo cáo):** âm tính ở R cao chỉ
  nói MẠNG CỤ THỂ + NGÂN SÁCH CỤ THỂ này không tìm ra gì — không phải bằng chứng
  mã an toàn (kẻ tấn công không bị giới hạn ngân sách này; tài liệu cho thấy mạng
  lớn đào sâu hơn: Simon tới 9 vòng, Speck tới 8 vòng). Giữ nguyên cảnh báo của
  `docs/research/06` §Bài học.

### 9. Thứ tự thẻ đề xuất (4 thẻ, không mở ồ ạt)

1. **[ML] Implement + validate Simon32/64** (nặng nhất GĐ1): cài đặt Simon32/64 +
   test vector đối chiếu đặc tả + round-trip nhiều R + nhãn-0-Gohr; qua cổng 0.
2. **[ML] Sweep Simon R=5..9 + x10 điểm mù** (mở sau khi (1) qua cổng 0): ngân sách
   chuẩn toàn dải, x10 ở R mù đầu tiên, chênh lệch dự phòng nếu cần; báo cáo điểm
   rơi accuracy + so sánh Speck-vs-Simon.
3. **[ML] Speck R=8 chênh lệch (0x2800,0x0010)** (mở song song bất cứ lúc nào):
   2 chạy (chuẩn + x10), 15 phút cả thẻ.
4. **[ML] Đọc tài liệu SKINNY + chốt chênh lệch** (mở sau khi (1) xong): kiểu
   NCKH-020 cho SKINNY-64-128; CHƯA implement. Thẻ implement/sweep SKINNY chỉ mở
   sau khi (4) có chênh lệch + (2) chứng minh pipeline nhãn-0-Gohr đúng.

- Tự kiểm: đề xuất này chỉ là văn bản (không code, không chạy lệnh ngoài đọc
  file/web + ghi sổ); mọi số ngân sách đều truy được về sổ NCKH-002/008/038;
  mọi chênh lệch Simon/Speck đều truy được về bài báo 2021 đã đọc (đường dẫn ở
  mục nhận việc); chỗ CHƯA xác minh (vector Simon, chênh lệch SKINNY) đã ghi rõ
  là chưa xác minh và giao cho đúng thẻ sau xác minh.
- Trạng thái: doing -> review (chờ kiểm chéo; peer review kiểm độc lập: đối chiếu
  chênh lệch/số accuracy trích từ bài báo + tính lại ngân sách từ sổ NCKH-038).
- Unresolved:
  U1. Số test vector Simon32/64 trong §3-mục-5 ghi theo trí nhớ, CHƯA xác minh —
  người nhận thẻ implement phải đối chiếu từ đặc tả Simon, không dùng số này.
  U2. Chênh lệch cho SKINNY-64-128 chưa có — chờ thẻ đọc tài liệu (thẻ 4).
  U3. Số "82.2% 8 vòng Simon" và "59.07/59.77% 9 vòng" trích từ bài báo 2021 ở
  ngân sách ResNet+lớn — chỉ dùng để chứng minh tín hiệu tồn tại, KHÔNG phải mục
  tiêu accuracy cho MLP rẻ của ta (mục tiêu ở §8).

## 2026-11-21 03:25 — đồng bộ Kanzo: KHÔNG THẤY THẺ, ghi sổ và tiếp tục (không tự tạo)
- `GET /api/board?project=esp32-securitykey` (timeout 30s, cách nhau 5s, shell pwsh):
  lần 1 HTTP 500 (Internal Server Error, đúng triệu chứng SQLite khóa DB);
  lần 2 OK — 61 tasks, lưu JSON về `$env:TEMP/NCKH-056-board.json`.
- Đối chiếu: tìm theo title/description chứa "NCKH-056" và "056" → 0 HIT.
  Thẻ ML gần nhất trên bảng: NCKH-002/008/014/020/026/038/044 (done),
  NCKH-032 (review). Thẻ đợt 2C của NCKH-056 chưa được Viện trưởng tạo.
- Theo lệnh giao việc: không thấy thẻ → ghi sổ và tiếp tục, KHÔNG tự tạo thẻ,
  KHÔNG move/comment. Toàn bộ bằng chứng làm việc nằm trong 2 mục sổ phía trên.
- Nhờ Viện trưởng khi tạo thẻ [ML] Đề xuất thí nghiệm tiếp theo (NCKH-056):
  cho thẻ đi todo -> doing -> review kèm trỏ về sổ cái này; nội dung đề xuất
  đã sẵn ở mục 03:20 (9 mục, kèm ngân sách + tiêu chí).
- Trạng thái thật của việc: ĐÃ XONG, chờ kiểm chéo (review).

## 2026-11-21 03:31 — kiểm chéo đợt 2C: NCKH-051 Nguyễn Cường (checklist bring-up) — ĐẠT

- Vai: Phan Cường (NCKH-056) kiểm độc lập công việc của NCKH-051 bằng ĐƯỜNG KHÁC
  (đối chiếu ngược từng ô mẫu với nguồn gốc, không tin số tự báo).
- Tài liệu đã đọc: `vien-nghien-cuu/so-cai/NCKH-051.md` (toàn bộ),
  `docs/checklist-bring-up-board.md` (toàn bộ, 163 dòng),
  `docs/runbook-nap-hwtest-windows.md` (toàn bộ, W),
  `docs/runbook-nap-hwtest-ubuntu.md` (toàn bộ, U),
  `firmware/hwtest/README.md` (toàn bộ, R); đối chiếu điểm bằng
  `hardware/BOM.md`, `hardware/wiring.md`, `firmware/hwtest/hwtest.ino`,
  `tools/hid_echo.py`, `scripts/build_hwtest.sh`.
- Đếm độc lập (pwsh): dòng = 163 (KHỚP), ô `^- \[ \]` = 47 (KHỚP),
  giai đoạn `## Giai đoạn` = 11 (0–10, KHỚP), kích thước file = 11034 byte
  (KHỚP số NCKH-051 báo; 9571 là số ký tự, không phải byte — không phải lỗi).
- Mẫu xác minh ngẫu nhiên 10/10 ô ĐÚNG nguồn (lệnh/số/log mẫu/mục truy vết):

| # | Ô checklist (tóm tắt) | Nguồn đối chiếu | Kết quả |
|---|----------------------|-----------------|---------|
| 1 | GĐ0: module chốt N16R8, đối chiếu BOM | BOM.md: "ESP32-S3-WROOM-1-N16R8", flash 16MB + PSRAM 8MB, chốt 2026-11-21 | ĐÚNG |
| 2 | GĐ1: cổng native = GPIO19/GPIO20 | W0.2 "GPIO19/GPIO20", U0 "GPIO19 D-, GPIO20 D+", wiring.md D-/D+ | ĐÚNG |
| 3 | GĐ2: Python ≥3.10 + `libhidapi-hidraw0` | W0.3 "Python 3.10 trở lên", U7 `sudo apt install -y libhidapi-hidraw0` | ĐÚNG |
| 4 | GĐ3: `lsusb \| grep -i -E 'espressif\|cp210\|silicon\|303a'`, VID 303a/10c4 | U1 nguyên văn lệnh + VID | ĐÚNG |
| 5 | GĐ4: `usermod -aG dialout`, đăng xuất/nhập lại, `id -nG` | U2 nguyên văn 3 bước | ĐÚNG |
| 6 | GĐ5: ESP32S3 Dev Module + CDC Enabled + USB-OTG (TinyUSB) | W5/W6/W7, U4, R mục Arduino IDE | ĐÚNG |
| 7 | GĐ5: FQBN `USBMode=default`=HWCDC (echo TẮT), `USBMode=otg` để echo; PIO `ARDUINO_USB_MODE=0` | U5 nguyên văn + build_hwtest.sh FQBN `CDCOnBoot=cdc,USBMode=default` | ĐÚNG |
| 8 | GĐ6: kẹt Connecting → giữ BOOT, nhấn-nhả RESET, thả BOOT khi `Writing at...` | W9 nguyên văn 4 bước | ĐÚNG |
| 9 | GĐ7: log mẫu + heartbeat ~5s + `tio /dev/ttyACM0 -b 115200` | W10/U6 nguyên văn; hwtest.ino có đủ `USB mode: %d`, `HID echo: san sang`, `Heartbeat: uptime`, `BOOT: nhan/nha` | ĐÚNG |
| 10 | GĐ9: `pip install -r tools/requirements.txt`, `--self-test`, 60 byte khớp, serial 64 byte, race `echoPending` (NCKH-003) | W12/U7/R nguyên văn; hid_echo.py: `PAYLOAD_LEN=60`, `self-test ok`, `usage page 0xFF00`; hwtest.ino `da gui lai 64 byte`; U7 ghi nhận NCKH-003 | ĐÚNG |

- Lỗi/sai lệch phát hiện: KHÔNG. Ghi chú nhỏ (không trừ điểm): GĐ8 ghi LED ở
  GPIO38/GPIO48 nhưng `hwtest.ino` không chứa hằng GPIO này — truy vết đúng về
  W11 runbook ("thường ở GPIO38 hoặc GPIO48 tùy bản board"), không phải bịa.
- Kết luận kiểm định: **ĐẠT** — checklist bao phủ đủ 2 runbook + README hwtest,
  lệnh/số/log mẫu chính xác từng điểm mẫu, truy vết nguồn (W/U/R + mục) đúng.
- Đồng bộ Kanzo (thẻ 202 "[firmware] Checklist bring-up board mới (NCKH-051)",
  thấy ở `todo` trong 69 tasks — Viện trưởng đã tạo sau khi NCKH-051 báo không thấy):
  - POST comment `[KIEM-DINH] DAT...` → OK ngay lần 1.
  - move todo→doing: fail 3 lần (timeout 30s + 2×500), thử lại sau → 500 rồi OK.
  - move doing→review: OK lần 1. move review→done: fail 3 lần (500/timeout/500).
  - GET verify cuối: thẻ 202 = **done**, comments = 1 — một lệnh move tưởng hỏng
    đã ăn phía server (đúng bệnh SQLite khóa DB đã biết). Mọi lệnh timeout 30s,
    cách nhau 5s, tối đa 2 thử lại, shell pwsh.
- Unresolved:
  U1. Checklist chưa được chạy runtime trên board thật (kế thừa từ NCKH-051) —
  cần người có board tick từng ô; phần kiểm chéo này chỉ xác minh tính đúng
  nguồn, không thay thế bring-up vật lý.
  U2. Không — Kanzo đã đồng bộ xong (thẻ 202 done + comment kiểm định).
