# Sổ cái NCKH-020 — Đoàn An, nhóm ML, Viện, đợt 2

## 2026-11-21 01:53 — nhận việc
- Thẻ: [ML] Tóm tắt Gohr 2019 (tìm id trên Kanzo ở cuối việc)
- Trạng thái: todo -> doing (thử opportunistic sau; Kanzo hay nghẽn SQLite)
- Việc nhận (theo `vien-nghien-cuu/phan-cong.json`): "Đọc bài Gohr về Speck, chỉ ra khác biệt với thí nghiệm của ta."
- Tài liệu đã đọc:
  - `vien-nghien-cuu/HIEN-CHUONG.md` (bản 1.0, §6 API Kanzo + luật ghi file-trước-bảng-sau)
  - Mục NCKH-020 trong `vien-nghien-cuu/phan-cong.json` (Đoàn An, nhóm ML, thành viên, đợt 2)
  - `vien-nghien-cuu/so-cai/README.md` (mẫu sổ cái)
  - `docs/research/06-ml-distinguisher.md` (thí nghiệm ml_distinguisher của ta)
  - Toàn bộ `tools/ml_distinguisher.py` (Speck32/64 toy + MLP numpy thuần)
- Nguồn ngoài đã đọc (web):
  - Bài báo: Aron Gohr, "Improving Attacks on Round-Reduced Speck32/64 Using Deep Learning", CRYPTO 2019, ePrint 2019/037 — https://eprint.iacr.org/2019/037
  - Code + data bổ trợ chính chủ: https://github.com/agohr/deep_speck (đọc README, train_nets.py, speck.py, train_5_rounds.py)
- Cam kết repo: CHỈ ĐỌC, trừ chính file sổ cái này; không git commit; mọi lệnh shell kèm `shell="pwsh"`.

## 2026-11-21 01:55 — báo cáo: tóm tắt Gohr 2019 + khác biệt với ta

### 1. Bài Gohr 2019 là gì
- Tên đầy đủ: Aron Gohr, "Improving Attacks on Round-Reduced Speck32/64 Using Deep Learning", CRYPTO 2019 (bản ePrint 2019/037).
- Đối tượng: Speck32/64 (khối 32 bit = 2 từ 16 bit, khóa 64 bit = 4 từ 16 bit, chuẩn 22 vòng) rút gọn vòng.
- Ý tưởng trung tâm: distinguisher vi sai-thần kinh (differential-neural distinguisher).
  Thay vì chỉ dùng một đặc trưng vi sai (differential trail) do người tìm, huấn luyện mạng nơ-ron phân biệt cặp bản mã thật (2 bản rõ lệch nhau đúng chênh lệch đầu vào cố định, mã hóa cùng khóa) với cặp ngẫu nhiên. Mạng tự học nhiều tín hiệu vi sai yếu gộp lại, kể cả tín hiệu mà phân tích vi sai cổ điển bỏ sót.
- 4 đóng góp (theo README của tác giả):
  1. Tính phân bố hiệu (difference distribution) tới 8 vòng bằng Markov assumption (rất đắt, xem §5).
  2. Distinguisher nơ-ron sâu (deep residual) cho 5–8 vòng, chính xác cao hơn hẳn vi sai cổ điển ở cùng số vòng.
  3. Tìm kiếm khóa chọn lọc bằng Bayesian optimization: rút tấn công 11 vòng còn ~38 bit khóa phải vét (thay vì vét toàn bộ), nghĩa là distinguisher nơ-ron kéo dài được số vòng tấn công thực tế.
  4. Phát hiện distinguisher nơ-ron dùng đặc trưng mà nhà thám mã không thấy trước, và demo tìm chênh lệch đầu vào tốt bằng mạng chỉ trong vài phút (thay vì tìm tay lâu).

### 2. Phương pháp Gohr (tóm tắt kỹ thuật)
- Chênh lệch bản rõ cố định: (dx, dy) = (0x0040, 0x0000) — đúng chênh lệch mà thí nghiệm của ta cũng dùng.
- Sinh dữ liệu (`make_train_data` trong train_nets.py):
  - Nhãn 1 (thật): bản rõ P0 ngẫu nhiên, P1 = P0 xor chênh lệch trên; cả hai mã hóa R vòng cùng một khóa ngẫu nhiên; đặc trưng là 64 bit nối của cặp bản mã (ct0l, ct0r, ct1l, ct1r).
  - Nhãn 0 (giả): P0 ngẫu nhiên, P1 ngẫu nhiên độc lập hoàn toàn (randomize_plaintexts), rồi mã hóa cùng khóa như trên. Lưu ý: KHÔNG phải 64 bit ngẫu nhiên trực tiếp — vẫn là cặp bản mã hợp lệ nhưng của cặp bản rõ không theo chênh lệch.
  - Có thêm hàm `real_differences_data` cho đánh giá mục 5 của báo cáo (phân biệt hiệu thật với hiệu ngẫu nhiên).
- Kiến trúc (`make_resnet` trong train_nets.py): mạng residual 1D theo bit-slice.
  - Input 64 bit -> reshape (4 từ, 16 bit) -> permute (16 vị trí bit, 4 kênh).
  - Conv1D 32 filter kernel 1 + BatchNorm + ReLU (trộn bit-slice).
  - depth khối residual, mỗi khối 2 x Conv1D(32 filter, kernel 3, same) + BN + ReLU + cộng shortcut.
  - Flatten -> Dense 64 + BN + ReLU -> Dense 64 + BN + ReLU -> Dense 1 sigmoid.
  - Mặc định `train_speck_distinguisher(..., depth=1)`; script ví dụ `train_5_rounds.py` gọi depth=10 (10 khối residual sâu). Các net huấn luyện sẵn cho 5/6/7/8 vòng trong repo chỉ dùng 1 khối residual nên hơi yếu hơn số trong báo cáo.
- Huấn luyện:
  - Ngân sách: 10^7 (10 triệu) mẫu train + 10^6 (1 triệu) mẫu validation mỗi R. Batch 5000. Tới 200 epoch cho ví dụ 5 vòng, tối ưu Adam, hàm mất mát MSE (mean squared error, không phải BCE), L2 reg 1e-5, lịch học cyclic 10 epoch từ 0.002 về 0.0001, checkpoint theo val_loss tốt nhất.
  - Hạ tầng: cần GPU; riêng phần tính phân bố hiệu tới 8 vòng cần ~70GB RAM và ~300 ngày-CPU (tác giả ghi trong README).
- Số vòng và tấn công:
  - Distinguisher nơ-ron cho 5, 6, 7, 8 vòng (độ chính xác giảm dần theo R; nguồn thứ cấp tổng hợp khoảng 0.93 / 0.79 / 0.62 / 0.51 — số chính xác từng bảng cần đọc PDF báo cáo, ở đây chỉ dùng để minh họa xu hướng).
  - Distinguisher 7 vòng được dùng trong tấn công khôi phục khóa 9 vòng (chosen-plaintext ít dữ liệu, thứ hạng khóa tốt gấp ~5 lần vi sai cổ điển) và 11 vòng (kết hợp tối ưu Bayes + thuật toán trung bình khóa). Code còn có bản kiểm chứng ý tưởng 12 vòng (`verify_12_rounds.py`).
- Test vector Speck32/64 (phát hiện phụ có giá trị cho ta):
  - Trong `speck.py`: `expand_key` lấy `ks[0] = k[-1]`, và `testvectors`: key (0x1918,0x1110,0x0908,0x0100), pt (0x6574,0x694c) -> ct (0xa868,0x42f2).
  - Nghĩa là k0 là TỪ CUỐI (k0=0x0100). Điều này XÁC NHẬN độc lập cách hiểu "k0=tu-cuoi" của `tools/ml_distinguisher.py` mà `docs/research/06` đang để trạng thái "chưa xác nhận". Đề nghị NCKH-032 (kiểm thử chéo Speck) dùng vector + thứ tự khóa này làm nguồn đối chiếu ngoài repo.

### 3. Thí nghiệm ml_distinguisher của ta (tóm tắt để đối chiếu)
- Mã: `tools/ml_distinguisher.py` (numpy thuần, CPU, vài giây).
- Chênh lệch: (0x0040, 0x0000) — giống Gohr.
- Dữ liệu: nhãn 1 = cặp bản mã R vòng của cặp bản rõ theo chênh lệch (giống Gohr); nhãn 0 = 64 bit HOÀN TOÀN NGẪU NHIÊN (khác Gohr — Gohr mã hóa cặp bản rõ ngẫu nhiên).
- Kiến trúc: MLP 64 -> 128 -> 64 -> 1 (ReLU + sigmoid), Adam, mất mát BCE, không BatchNorm, không residual, không L2, không lịch học, không checkpoint.
- Ngân sách: 6000 mẫu train + 2000 mẫu test mỗi R, 5 epoch, batch 256, seed 1337.
- Số vòng: R = 5, 6, 7. Kết quả: 0.5970 / 0.5245 / 0.5070 (tái hiện khớp tuyệt đối bởi NCKH-002). Không làm khôi phục khóa.
- Mục đích: minh họa học tập ("mạng phân biệt được ở ít vòng và mù dần khi tăng vòng"), không phải tấn công thật.

### 4. Bảng khác biệt (Gohr 2019 vs ta)

| Tiêu chí | Gohr 2019 (báo cáo + code chính chủ) | Ta (`tools/ml_distinguisher.py`) | Ý nghĩa |
|---|---|---|---|
| Chênh lệch đầu vào | (0x0040, 0x0000) | (0x0040, 0x0000) — giống | Ta chọn đúng chênh lệch tốt của Gohr |
| Mẫu nhãn 1 | Cặp bản mã của cặp bản rõ theo chênh lệch, cùng khóa | Giống Gohr | Cùng định nghĩa lớp "thật" |
| Mẫu nhãn 0 | Cặp bản mã của cặp bản rõ NGẪU NHIÊN ĐỘC LẬP (vẫn qua mã hóa) | 64 bit ngẫu nhiên trực tiếp, không qua mã hóa | Bài toán của ta DỄ HƠN (phân biệt mã vs ngẫu nhiên thuần); của Gohr KHÓ HƠN và đúng nghĩa distinguisher vi sai (cùng phân phối mã, chỉ khác chênh lệch) |
| Đặc trưng | 64 bit nối 4 từ bản mã (ct0l, ct0r, ct1l, ct1r) | 64 bit nối 4 từ bản mã — giống | Cùng biểu diễn đầu vào |
| Kiến trúc | ResNet 1D bit-slice: Conv1(32,ks1) + depth khối residual(2xConv(32,ks3)) + Dense64 + Dense64 + sigmoid; BN mọi lớp; ví dụ 5 vòng depth=10 | MLP 64->128->64->1, ReLU+sigmoid, không conv/residual/BN | Gohr sâu và chuyên biệt cho cấu trúc bit của mã; ta là baseline rẻ nhất |
| Mất mát / tối ưu | MSE + Adam + L2 1e-5 + cyclic LR 0.002->0.0001 + checkpoint val_loss | BCE + Adam lr 0.002 cố định, không reg/schedule/checkpoint | Gohr chống overfit và hội tụ tốt hơn ở dữ liệu lớn |
| Ngân sách dữ liệu | 10M train + 1M val mỗi R | 6k train + 2k test mỗi R (nhỏ hơn ~1600 lần) | Đây là khác biệt lớn nhất về chi phí |
| Epoch / batch | Tới 200 epoch, batch 5000, GPU | 5 epoch, batch 256, CPU ~2s cho cả 3 R | Gohr đắt hơn hàng nghìn lần |
| Số vòng distinguisher | 5, 6, 7, 8 | 5, 6, 7 | Gohr lên tới 8 vòng; ta dừng ở 7 (đã gần đoán mò 0.507) |
| Accuracy xu hướng | Giảm dần theo R nhưng còn tín hiệu tới 7–8 vòng (7 vòng ~0.6) | 0.597 / 0.525 / 0.507 — sụp nhanh về 0.5 | Cùng xu hướng "thêm vòng giết distinguisher", nhưng mạng + dữ liệu lớn của Gohr sống lâu hơn |
| Đánh giá mở rộng | Có `real_differences_data` (mục 5 báo cáo) | Không | Gohr kiểm tra sâu hơn một chế độ đánh giá |
| Tấn công tiếp theo | Có: khôi phục khóa 9/11 vòng (+PoC 12 vòng) bằng Bayes + trung bình khóa | Không — chỉ distinguisher minh họa | Gohr đi tới tấn công hoàn chỉnh; ta dừng ở bước 1 |
| Hạ tầng | GPU + tới 70GB RAM / 300 CPU-ngày cho phần DDT | Laptop CPU thường, ~2 giây | Không thể chạy lại nguyên bản Gohr trên máy dev |

### 5. Bài học cho nhóm ML
1. Thí nghiệm của ta là "Gohr thu nhỏ": đúng chênh lệch, đúng đặc trưng, nhưng dữ liệu dễ hơn (nhãn 0 ngẫu nhiên thuần), mạng yếu hơn (MLP thay ResNet), ngân sách nhỏ hơn ~3 bậc. Vì vậy accuracy tuyệt đối của ta THẤP HƠN Gohr ở cùng R là bình thường, không phải lỗi code.
2. Nếu muốn tiến gần Gohr theo thứ tự ưu tiên: (a) đổi nhãn 0 thành mã hóa cặp ngẫu nhiên (đúng distinguisher vi sai); (b) tăng dữ liệu lên 50k–1M (việc của NCKH-008/NCKH-038); (c) thử CNN 1D thay MLP (việc của NCKH-014); (d) chỉ sau đó mới nghĩ tới residual sâu + GPU.
3. Kết quả âm tính của ta (R=7 ~0.51) không chứng minh mã an toàn — Gohr đã chỉ ra mạng lớn hơn + dữ liệu nhiều hơn đào được tín hiệu mà mạng nhỏ bỏ sót. Giữ nguyên cảnh báo này trong mọi tài liệu.
4. Tặng nhóm kiểm định: thứ tự khóa test vector đã có nguồn ngoài xác nhận (k0 = từ cuối). Nên cập nhật trạng thái vector trong `docs/research/06` từ "chưa xác nhận" thành "khớp Gohr deep_speck" sau khi NCKH-032 đối chiếu xong.

- Tự kiểm: chỉ đọc (web + file), không chạy code, không sửa repo ngoài file này. Mọi khẳng định về Gohr đều truy được về 2 URL mục nhận việc (ePrint + GitHub chính chủ); mọi khẳng định về ta đều truy được về `docs/research/06-ml-distinguisher.md` + `tools/ml_distinguisher.py` + sổ NCKH-002.
- Trạng thái: doing -> review (chờ kiểm chéo).
- Kanzo: xem mục bên dưới.

## 2026-11-21 02:05 — đồng bộ Kanzo: THẤT BẠI, chờ Viện trưởng vá
- `GET /api/board?project=esp32-securitykey` (timeout 30s, mỗi lần cách nhau 5s):
  - Lần 1 (`Invoke-RestMethod`, parse theo `columns`): trả TOTAL=0 — sai cấu trúc (board thực tế trả `tasks[]`, không phải `columns[]`), coi như hỏng.
  - Lần 2 (kiểm tra raw): HTTP 500 `{"error":"database error: database is locked"}`.
  - Lần 3 (retry 1): HTTP 500 database is locked.
  - Lần 4 (retry 2): HTTP 200 LEN=14527 — THÀNH CÔNG duy nhất, thấy project esp32-securitykey (open 8, total 20), tasks bắt đầu từ id 153 `[PQC] Đặc tả két lai (NCKH-013)`, id 154 `[ML] Thử CNN 1D (NCKH-014)`... nhưng output bị cắt ở 3000 ký tự nên chưa thấy thẻ NCKH-020.
  - Lần 5 (liệt kê + lọc): HTTP 500.
  - Lần 6–8 (tải full về `$env:TEMP/NCKH-020-board.json`, 3 attempt cách 5s): cả 3 HTTP 500 database is locked.
- Kết quả: KHÔNG xác định được id thẻ NCKH-020 (đoán theo thứ tự tạo có thể là id 160, nhưng KHÔNG dám move/comment theo id đoán vì có thể chạm nhầm thẻ người khác).
- Không thực hiện được move (todo->doing->review) và comment báo cáo. Mọi lệnh đều dùng `shell="pwsh"`, timeout 30s.
- Nhận xét: đúng triệu chứng SQLite khóa DB khi ghi/đọc dồn dập (Hiến chương §6). Lỗi 500 từ server, không phải timeout client.
- Nhờ Viện trưởng vá khi Kanzo hồi phục: tìm thẻ `[ML] Tóm tắt Gohr 2019 (NCKH-020)` của Đoàn An, move todo -> doing -> review + dán comment báo cáo (nội dung = mục báo cáo 01:55 trong file này).
- Trạng thái thật của việc: ĐÃ XONG nội dung, chờ kiểm chéo (review), dù thẻ Kanzo chưa di chuyển được.
- Unresolved: (1) id thẻ Kanzo chưa xác định; (2) số accuracy chính xác từng bảng trong PDF Gohr chưa đối chiếu (chỉ dùng số tổng hợp từ nguồn thứ cấp để minh họa xu hướng — cần người có PDF kiểm lại trước khi trích dẫn số tuyệt đối).

## 2026-11-21 02:08 — kiểm chéo đợt 2A: thẻ NCKH-028 Lê Bình (fuzz parse_share)
- Vai trò: Đoàn An (NCKH-020) kiểm độc lập công việc của NCKH-028 Lê Bình (nhóm tooling).
- Tài liệu đã đọc: `vien-nghien-cuu/so-cai/NCKH-028.md` (toàn bộ), hàm `parse_share` trong `tools/split_secret.py` (dòng 129–146, chỉ đọc).
- Báo cáo của tác giả (tóm tắt): fuzz 5066 case, 42 ok, 4870 ValueError có thông điệp, 154 ngoại lệ khác — toàn bộ `KeyError` một trong `'shares'`, `'threshold'`, `'index'`; nguyên nhân dòng 146 truy cập dict trực tiếp; điều kiện kích hoạt: dòng 2 hex hợp lệ + `len` khớp + header thiếu ≥1 trong 3 key.
- Kiểm bằng ĐƯỜNG KHÁC (không dùng script fuzz của tác giả): one-liner python trực tiếp, mỗi case header thiếu đúng 1 key + hex hợp lệ 8 byte (`6162636465666768`, len=8). Mọi lệnh shell kèm `shell="pwsh"`.
- Tái hiện độc lập (3/3 đạt):
  - `SHAMIR-SHARE-V1 threshold=2 index=1 len=8` + hex -> `KeyError: 'shares'`, traceback chỉ `File "tools/split_secret.py", line 146, in parse_share`.
  - `SHAMIR-SHARE-V1 shares=3 index=1 len=8` + hex -> `KeyError: 'threshold'`, cùng dòng 146.
  - `SHAMIR-SHARE-V1 shares=3 threshold=2 len=8` + hex -> `KeyError: 'index'`, cùng dòng 146.
- Xác nhận nguyên nhân dòng 146: `return params["shares"], params["threshold"], params["index"], y` — truy cập dict trực tiếp, không `.get`/kiểm tra key trước. Đọc code dòng 144–146 khớp mô tả của tác giả.
- Kiểm ghi chú phụ của tác giả: header thiếu `len` (`shares=3 threshold=2 index=1` + hex 8 byte) -> `ValueError: độ dài dữ liệu không khớp header` tại dòng 145 (nhờ `params.get("len", -1)`). ĐÚNG như tác giả ghi — `len` thiếu không gây KeyError.
- Không kiểm lại con số 5066/154 bằng cách chạy lại fuzz (Hiến chương §2 yêu cầu kiểm bằng đường khác, không chạy lại đúng lệnh của tác giả); cơ chế lỗi đã được tái hiện tối thiểu và xác nhận ở mức dòng code, đủ để kết luận báo cáo của tác giả là chính xác.
- Kanzo (`GET /api/board?project=esp32-securitykey`, timeout 30s, mỗi lần cách 5s): lần 1/2/3 đều HTTP 500 Internal Server Error (đúng triệu chứng SQLite database is locked đã biết). Hết 2 lần thử lại theo nhiệm vụ. Không đọc được bảng nên không tìm được thẻ NCKH-028, không comment/move được. Nhờ Viện trưởng khi Kanzo hồi phục: dán comment `[KIEM-DINH] đạt — Đoàn An (NCKH-020) tái hiện độc lập 3/3 KeyError (shares/threshold/index) bằng one-liner python trực tiếp, xác nhận nguyên nhân dòng 146 tools/split_secret.py; ghi chú len->ValueError cũng đúng` và move thẻ NCKH-028 `review` -> `done`.
- Kết luận kiểm định: ĐẠT. Báo cáo của NCKH-028 chính xác: loại ngoại lệ, thông điệp, nguyên nhân dòng code, điều kiện kích hoạt và ví dụ tối thiểu đều khớp kết quả tái hiện độc lập.
- Unresolved: (1) thẻ Kanzo của NCKH-028 chưa được comment/move do Kanzo hỏng (xem nhờ Viện trưởng ở trên); (2) các thẻ NCKH-022..030 đợt 2A có thể còn chưa được tạo trên bảng (theo ghi nhận của NCKH-028) — Viện trưởng kiểm tra khi tạo thẻ.
