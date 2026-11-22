# Sổ cái NCKH-050 — Hà Bình (nhóm ML, đợt 2C)

Nhiệm vụ (phan-cong.json): "Benchmark CPU vs GPU" — Cùng cấu hình train, so thời gian CPU và CUDA (nếu có). (loại t1-tay-chon).

Ràng buộc phiên: repo CHỈ ĐỌC (chỉ ghi chính sổ này); file tạm chỉ trong `$env:TEMP`; không git commit; mọi lệnh shell dùng `shell="pwsh"`; tiếng Việt.

Bối cảnh kỹ thuật (đọc trước khi đo): `tools/ml_distinguisher.py` là MLP numpy THUẦN (64->128->64->1, ReLU+sigmoid+Adam, BCE), không có nhánh torch/CUDA, không có cờ chọn device. Vì vậy "cùng 1 cấu hình train trên CPU và CUDA" chỉ khả thi nếu port mô hình sang torch; còn tool gốc chỉ chạy CPU. Nhiệm vụ cho phép: không có CUDA thì đo CPU đa cấu hình và kết luận rõ.

## 2026-11-21 02:36 — nhận việc

- Thẻ: [ML] Benchmark CPU vs GPU (Kanzo id: tra cứu cuối việc — xem mục đồng bộ cuối sổ)
- Trạng thái: todo -> doing
- Kế hoạch:
  1. Kiểm tra torch/CUDA (không cài thêm gì nặng >5 phút).
  2. Nếu không có CUDA: benchmark tool gốc trên CPU đa cấu hình (chuẩn/nhẹ/nặng, sweep batch, tách gen-vs-train, lặp lấy phương sai).
  3. Ghi mọi số liệu vào sổ TRƯỚC, rồi mới đồng bộ Kanzo (GET board, tìm thẻ NCKH-050, move+comment cách 5s, timeout 30s, tối đa 2 thử lại; hỏng thì ghi sổ, KHÔNG tự tạo thẻ).

## 2026-11-21 03:14 — báo cáo

### 0. Môi trường đo (lệnh + output thật)

- CPU: `13th Gen Intel(R) Core(TM) i7-13620H` (lệnh `Get-CimInstance Win32_Processor`).
- GPU vật lý: `NVIDIA GeForce RTX 4060 Laptop GPU, driver 621.24, 8188 MiB` (lệnh `nvidia-smi --query-gpu=...`). **GPU có tồn tại.**
- Python `3.12.0` (`C:\Program Files\Python\Python312\python.exe`); numpy `2.5.4`; BLAS `scipy-openblas 0.3.34.106.0, Haswell, MAX_THREADS=24, NO_AFFINITY` (`numpy.show_config`).
- torch `2.14.1+cpu`: `cuda_available=False`, `device_count=0` -> **torch KHÔNG dùng được CUDA** (bản CPU-only).
- Kết luận môi trường: phần cứng có GPU nhưng phần mềm không có đường CUDA nào (tool numpy thuần + torch CPU-only). Cài torch CUDA (~GB download) vượt ngân sách "không cài thêm gì nặng quá 5 phút" -> KHÔNG cài, KHÔNG có số CUDA. Toàn bộ dưới đây là benchmark CPU đa cấu hình + kết luận rõ, đúng phương án dự phòng của nhiệm vụ.

### 1. Tái hiện cấu hình chuẩn (đối chiếu docs)

- Lệnh: `python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000 --epochs 5 --seed 1337`
- Output: `R=5 -> 0.5970`, `R=6 -> 0.5245`, `R=7 -> 0.5070` — **khớp từng chữ số với `docs/research/06-ml-distinguisher.md`**, seed xác định (5 lần đo tách đều ra 0.5970 ở R=5).
- Self-test: `PASS` (vector KHOP k0=tu-cuoi, round-trip PASS, micro-train 0.505). EXIT=0.

### 2. Đo tách gen-vs-train, R=5, 6k/2k/5ep/batch256, seed 1337, 5 lần (script tạm `$env:TEMP/nckh050/tach.py`, chỉ import đọc tool)

| lần | gen | train | tổng | acc |
|-----|------|-------|------|-------|
| 1 | 0.372s | 0.397s | 0.769s | 0.5970 |
| 2 | 0.322s | 0.712s | 1.034s | 0.5970 |
| 3 | 0.260s | 0.481s | 0.741s | 0.5970 |
| 4 | 0.257s | 0.447s | 0.705s | 0.5970 |
| 5 | 0.256s | 0.478s | 0.734s | 0.5970 |

- acc bất biến theo seed (xác định); thời gian dao động mạnh giữa các lần (train 0.40–0.71s) — máy chia sẻ tải với nhiều agent chạy song song, số tuyệt đối chỉ có giá trị tương đối trong cùng phiên đo xen kẽ.

### 3. PHÁT HIỆN CHÍNH: slow path OpenBLAS đa luồng với batch ≥ 512

Sweep batch trên dataset cố định (R=5, 6k/2k/5ep), xen kẽ 3 vòng (script `$env:TEMP/nckh050/batch.py`):

| batch | vòng 1 | vòng 2 | vòng 3 | acc |
|-------|--------|--------|--------|-------|
| 64 | 1.184s | 0.977s | 1.223s | 0.7225 |
| 256 | 1.297s | 0.678s | 0.775s | 0.5970 |
| 1024 | 13.402s | 14.538s | 13.142s | 0.5195 |

- Batch 1024 chậm hơn batch 256 tới **~15 lần** — ngược lý thuyết (cùng tổng FLOPs/epoch, ít step hơn phải nhanh hơn).
- Profile 1 epoch (`profile.py`): copy/fwd/adam bình thường ở mọi batch; riêng **backward** bùng nổ: batch256 bwd=0.021s, batch512 bwd=1.034s, batch1024 bwd=1.697s.
- Đo từng op (`ops.py`): thủ phạm là các phép `X.T @ D` (toán hạng trái là view chuyển vị non-contiguous): B=256 mọi op <1ms; B=512 `dw1=x.T@dz1`=222ms; B=1024 `dw1`=578ms, `dw2` lần 2=141ms (lần 1 chỉ 2.9ms — không ổn định, đặc trưng pathology threading).
- **Kiểm chứng quyết định**: chạy lại đúng script với `$env:OPENBLAS_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'` -> batch1024/epoch từ 1.717s xuống **0.065s (nhanh hơn ~26 lần)**; sweep full 5 epoch: batch64 ~0.21s, batch256 ~0.21s, batch1024 ~0.20s — phẳng như lý thuyết.
- Kết luận: OpenBLAS 0.3.34 đa luồng (24 threads, NO_AFFINITY) trên Windows rơi vào slow path với phép `K×B @ B×N` non-contiguous khi B ≥ 512 ở cỡ ma trận nhỏ này; overhead thread vượt xa lợi ích. Batch ≤ 256 (mặc định tool) không dính. **Không sửa repo** (chỉ đọc) — ghi nhận để Viện quyết định (ví dụ đặt threads=1 khi batch lớn, hoặc `np.ascontiguousarray` trước `@`).

### 4. Batch ảnh hưởng accuracy mạnh (cùng 5 epoch, seed 1337, R=5)

- batch 64 -> acc **0.7225** (468 step); batch 256 -> 0.5970 (120 step); batch 1024 -> 0.5195 (30 step). Batch nhỏ hội tụ tốt hơn hẳn vì nhiều bước Adam hơn. So sánh accuracy giữa các nghiên cứu PHẢI cố định batch.

### 5. Sweep quy mô, R=5, batch 256, seed 1337 (script `$env:TEMP/nckh050/scale.py`)

| cấu hình (train/ep) | gen | train | tổng | acc |
|---|---|---|---|---|
| nhẹ 2k/3ep | ~0.10s | ~0.055s | ~0.15s | 0.5070 |
| chuẩn 6k/5ep | ~0.13s | ~0.20s | ~0.33s | 0.5970 |
| nặng 20k/10ep | ~0.40s | ~1.13s | ~1.53s | 0.7555 |
| rất nặng 60k/20ep | 1.50s | 7.44s | 8.93s | 0.7615 |

- Train gần tuyến tính theo (samples × epochs): 30k lượt-mẫu -> 0.20s; 200k (×6.7) -> 1.13s (×5.7); 1200k (×40) -> 7.44s (×37).
- Gen gần tuyến tính theo samples; ở cỡ rất nặng train chiếm ~83% tổng (phù hợp nhận định "train chiếm áp đảo" của NCKH-030 ở cỡ x10).
- Gen theo R (20k mẫu, xen kẽ 2 vòng): R5 0.424/0.344s; R6 0.545/0.465s; R7 0.428/0.494s — trung bình R5=0.384, R6=0.505, R7=0.461, **không đơn điệu**: ảnh hưởng của R lên thời gian gen nằm trong nhiễu máy, không đo được rõ (độc lập xác nhận ghi nhận của NCKH-030 ở R8/R9).

### 6. Tham khảo torch CPU (không phải train tương đương)

- MLP torch cùng kiến trúc (64->128->64->1, float64), forward batch 256: **0.753 ms/lần** (200 lần, `torchref.py`), cùng bậc với numpy forward (~0.63 ms/step từ profile). Hạ tầng torch CPU sẵn sàng — chỉ thiếu bản CUDA + port mô hình thì mới có số GPU để so.

### 7. Kết luận benchmark CPU-vs-GPU

1. **Không có số CUDA**: GPU RTX 4060 tồn tại vật lý nhưng torch là bản CPU-only và tool là numpy thuần không nhánh GPU; cài torch CUDA vượt ngân sách cho phép. So sánh CPU-vs-CUDA thật yêu cầu (a) cài torch CUDA, (b) port MLP sang torch — cả hai đều ngoài phạm vi phiên chỉ-đọc này; đề xuất thành việc follow-up.
2. Số CPU đã đo đầy đủ, đa cấu hình, có lặp và xen kẽ (bảng §2–§5).
3. Khuyến nghị kỹ thuật (không thực hiện vì repo chỉ đọc): giữ batch mặc định 256; nếu ai tăng batch ≥ 512 trên Windows+OpenBLAS thì đặt `OPENBLAS_NUM_THREADS=1` (nhanh hơn ~26 lần ở batch 1024); mọi so sánh accuracy phải cố định batch vì batch đổi acc từ 0.52 tới 0.72.

- Tự kiểm: mọi lệnh + output ở trên; log đầy đủ trong `$env:TEMP/nckh050/` (`chuan.log`, `tach.log`, `batch.log`, `batch_t1.log`, `profile.log`, `profile_t1.log`, `ops.log`, `scale.log`, `torchref.log`); không sửa file repo nào ngoài chính sổ này; không git commit.
- Trạng thái: doing -> review
- Thảo luận lại: không. Họp hội đồng: không.

### Unresolved

1. Chưa có số CUDA (lý do §0 + §7.1) — cần việc follow-up: cài torch CUDA + port MLP sang torch rồi đo cùng cấu hình.
2. Số tuyệt đối dao động giữa các thời điểm (máy chia sẻ tải nhiều agent) — chỉ nên dùng so sánh tương đối trong cùng phiên đo xen kẽ.
3. Thẻ Kanzo NCKH-050: xem mục đồng bộ dưới đây.

## 2026-11-21 03:2x — đồng bộ Kanzo: MOVE thành công, COMMENT một phần (đã ghi sổ)

- `GET /api/board?project=esp32-securitykey` (timeout 30s): lần 1 OK ngay — 64 thẻ, tìm thấy `id=201 status=todo title="[ML] Benchmark CPU vs GPU (NCKH-050)"`. Không phải tự tạo thẻ.
- `POST /api/tasks/201/move {doing}`: OK lần 1.
- `POST /api/tasks/201/comments` (nhận việc 02:36): lần 1 timeout 30s (theo HIEN-CHUONG §6, timeout client không đồng nghĩa server chưa ghi — có thể đã ghi), lần 2 + lần 3 HTTP 500 → hết ngân sách retry, trạng thái comment này KHÔNG chắc chắn.
- Cách 5s. `POST /api/tasks/201/move {review}`: OK lần 1.
- Cách 5s. `POST /api/tasks/201/comments` (báo cáo tóm tắt + trỏ sổ này): lần 1 HTTP 500, lần 2 OK.
- Đối chiếu lại bảng: lần 1 HTTP 500 (đúng bệnh SQLite lock); lần 2 OK → `id=201 status=review` ĐÃ XÁC MINH. Trường comments trả về 1 mục rỗng/khác schema (`body` trống) → chưa xác minh được comment nào hiển thị.
- GET raw JSON thẻ 201 để xem comments: HTTP 500 → dừng, không cố thêm (mọi chi tiết đã ở sổ file này).
- Kết luận: thẻ 201 đang ở đúng cột `review`; nhờ Viện trưởng khi Kanzo ổn định kiểm tra lại comments của thẻ (nhận việc có thể bị trùng/mất, báo cáo POST đã OK).
- Trạng thái: doing -> review (đã áp dụng trên bảng).

## 2026-11-21 03:35 — kiểm chéo đợt 2C: thẻ NCKH-045 của Đoàn Bình (làm lượt Hà Bình)

- Vai trò: kiểm định viên khác nhóm (ML kiểm firmware), kiểm độc lập bằng ĐƯỜNG KHÁC — không build lại toàn bộ, không đọc chay kết luận của tác giả.
- Đã đọc: `vien-nghien-cuu/so-cai/NCKH-045.md` (toàn bộ báo cáo 03:15 + mục Kanzo 03:20), `vien-nghien-cuu/so-cai/NCKH-012.md` (nguồn số liệu gốc), `README.md` (mục trạng thái: OTG 372 KB, HWCDC 302 KB), `firmware/hwtest/hwtest.ino` (154 dòng, để thẩm định tham chiếu dòng trong đề xuất).
- Phạm vi: REPO CHỈ ĐỌC, chỉ nối thêm chính sổ này; mọi lệnh shell dùng `shell="pwsh"`; không git commit.

### 1. Tính toán độc lập từ số byte gốc (pwsh, không chép % của tác giả)

- Lệnh: tính `% = dùng/tối đa*100` với flash tối đa 1310720 B, RAM tối đa 327680 B; ngưỡng 70% = flash 917504 B, RAM 229376 B; số dư, chênh OTG−HWCDC, headroom tới ngưỡng; đối chiếu KB thập phân cho README.
- Kết quả (output thật, exit 0):

| Chỉ số | Tôi tính độc lập | Tác giả ghi | Đối chiếu |
|---|---|---|---|
| OTG flash % | 28,4296% | 28,4296% / 28,43% | KHỚP |
| OTG RAM % | 16,9922% | 16,9922% / 16,99% | KHỚP |
| HWCDC flash % | 23,0991% | 23,0991% / 23,10% | KHỚP |
| HWCDC RAM % | 6,9531% | 6,9531% / 6,95% | KHỚP |
| OTG dư flash | 938087 B (71,57%) | 938087 B (71,57% ~ 916 KB) | KHỚP |
| OTG dư RAM | 272000 B (83,01%) | 272000 B (83,01% ~ 266 KB) | KHỚP |
| HWCDC dư flash | 1007955 B (76,90%) | 1007955 B (76,90% ~ 984 KB) | KHỚP |
| HWCDC dư RAM | 304896 B (93,05%) | 304896 B (93,05% ~ 298 KB) | KHỚP |
| Chênh flash OTG−HWCDC | 69868 B | 69868 B (~68,2 KB) | KHỚP |
| Chênh RAM OTG−HWCDC | 32896 B | 32896 B (~32,1 KB) | KHỚP |
| Headroom OTG tới 70% | flash 544871, RAM 173696 | flash 544871 (~532 KB), RAM 173696 (~170 KB) | KHỚP |
| Headroom HWCDC tới 70% | flash 614739, RAM 206592 | flash 614739 (~600 KB), RAM 206592 (~202 KB) | KHỚP |

- Xác minh logic ngưỡng: cả 4 chỉ số đều dưới 70%, cao nhất là flash OTG 28,43% — cách ngưỡng 41,57 điểm %. Kết luận "KHÔNG vượt ngưỡng → KHÔNG cắt giảm bắt buộc" của tác giả là ĐÚNG và có biên an toàn rất lớn (chỉ số cao nhất chưa bằng một nửa ngưỡng).
- Kiểm chéo số KB thập phân: 372633/1000 = 372,6; 302765/1000 = 302,8 → README ghi "OTG (372 KB) và HWCDC (302 KB)" là làm tròn đúng theo KB thập phân. (Nếu dùng KiB nhị phân sẽ là ~364/296 — README và tác giả nhất quán dùng KB thập phân, không sai.)

### 2. Đối chiếu nguồn số liệu (NCKH-012, README, objective)

- NCKH-012 (build sạch `--clean`): OTG 372633/55680, HWCDC 302765/22784, `.bin` 372784/302912, tối đa 1310720/327680 — tác giả NCKH-045 build lại và KHỚP TỪNG BYTE cả 4 số dùng + cả 2 cỡ `.bin`. Tái hiện 100% qua 2 agent độc lập, đáng tin.
- README: OTG ~372 KB, HWCDC ~302 KB — khớp như đã chứng minh ở mục 1.
- Objective đợt 2C: OTG 372633/55680, HWCDC 302765/22784 — khớp từng byte.
- Ghi chú trung thực: tôi KHÔNG build lại (đúng lệnh "không build lại toàn bộ"); tính độc lập của tôi nằm ở (a) tự tính lại mọi %/dư/headroom từ số byte thô bằng lệnh riêng, (b) tự đối chiếu 3 nguồn (objective/NCKH-012/README), (c) tự thẩm định đề xuất qua đọc code. Hai build độc lập NCKH-012/NCKH-045 đã đủ chứng minh tái hiện.

### 3. Thẩm định đề xuất dự phòng (đọc code, không tin chay)

- Tham chiếu dòng trong đề xuất 2: `printChipInfo()`/`printMac()`/heartbeat ở hwtest.ino dòng 74-95, 140-144 — TÔI XÁC MINH ĐÚNG (`printMac` 74-80, `printChipInfo` 82-95, heartbeat 140-144 trong file 154 dòng).
- Đề xuất 1 (đổi FQBN sang HWCDC, tiết kiệm 69868 B flash + 32896 B RAM, không sửa code): ĐÚNG số (bằng chênh đã kiểm ở mục 1), ĐÚNG cơ chế (nhánh HID echo `#if ARDUINO_USB_MODE == 0` dòng 8/119/145 chỉ biên dịch ở OTG) — là đòn dự phòng rẻ nhất, xếp hạng 1 chính xác.
- Đề xuất 3 (mặc định HWCDC, chỉ OTG khi cần `tools/hid_echo.py`): thực chất TRÙNG đề xuất 1 về mặt kỹ thuật (cùng đổi FQBN), chỉ khác cách diễn đạt quy trình — tác giả đã tự ghi rõ "tương đương mục 1", nên đây là trùng lặp có chủ ý, không phải lỗi, nhưng có thể gộp khi trình bày với Viện.
- Đề xuất 2+4 (gọn log Serial, bỏ `printf` định dạng nặng): HỢP LÝ — file có ~10 lệnh `Serial.print*` với chuỗi dài và `%02X:%02X...` (dòng 77); tiết kiệm ước "vài KB" là thận trọng, không thổi phồng.
- Đề xuất 5 (đổi partition `no_ota`/`huge_app`, mất OTA/SPIFFS): HỢP LÝ và TRUNG THỰC — nói rõ đây là tăng trần chứ không giảm dùng, kèm điều kiện "chỉ dùng khi đã cạn dư".
- Đề xuất 6 (giữ `-Os`, không `-g`/RTTI thừa, đổi cờ phải đo lại cả 2 FQBN): HỢP LÝ, đúng thực hành nhúng; yêu cầu đo lại khép kín với tiêu chí pass rõ (cả 4 chỉ số dưới 70% + HID echo/log còn đủ).
- "Đo lại sau đề xuất": tác giả ghi KHÔNG có vòng đo lại vì không sửa code — ĐÚNG lệnh ("đề xuất cần sửa code thì chỉ viết, không sửa") và đúng vì chưa áp dụng đề xuất nào; quy trình đo lại khi áp dụng đã viết sẵn, khả thi.
- Mục bóc `.elf` (text/data/bss, chênh text +66604 B ≈ 95% chênh flash do TinyUSB+USBHID): số học nội tại nhất quán (66604/69868 ≈ 95,3%); cảnh báo "BSS thô gồm cả vùng ngoài DRAM nên số arduino-cli mới là căn cứ ngưỡng" thể hiện hiểu đúng công cụ — điểm cộng chuyên môn, không trừ.
- Thứ tự ưu tiên tổng thể (không-sửa-code trước, sửa-code sau, đổi partition/cờ cuối) là ĐÚNG cho bài toán dự phòng dưới ngưỡng.

### 4. Kết luận kiểm chéo

- [KIEM-DINH] đạt — số liệu tái hiện từng byte qua 2 build độc lập; mọi %/dư/headroom tôi tính lại khớp 100%; kết luận dưới ngưỡng 70% đúng với biên an toàn lớn; 6 đề xuất dự phòng hợp lý, xếp hạng đúng, tham chiếu code chính xác, không cần cắt giảm bắt buộc.
- Tự kiểm: tính toán bằng lệnh pwsh riêng (exit 0, output ở mục 1); đọc 4 file nguồn; repo chỉ nối thêm chính sổ này; không git commit.
- Thảo luận lại: không. Họp hội đồng: không.

### 5. Unresolved

1. Không có unresolved chuyên môn: cả hai bản còn dư lớn (thấp nhất 71,57% flash OTG), ngưỡng 70% còn xa.
2. Thẻ Kanzo 207 (xem mục 6): comment kiểm định đã lên (id 119), nhưng move sang `done` kẹt HTTP 500 cả 3 lần — nhờ Viện trưởng vá cột khi Kanzo ổn định.

## 2026-11-21 03:35 — đồng bộ Kanzo thẻ 207 (comment OK, move kẹt 500)

- `GET /api/board?project=esp32-securitykey` (timeout 30s): lần 1 OK ngay — 69 thẻ (tăng từ 64 thẻ lúc NCKH-045 tra cứu, bảng đã được bổ sung), tìm thấy `id=207 status=todo title="[firmware] Rà soát RAM/flash hai bản build (NCKH-045)"` — ĐÚNG thẻ của NCKH-045 (được tạo sau phiên của tác giả, giải thích vì sao tác giả "không thấy thẻ của mình"). Thẻ id 203 vẫn là của NCKH-052, không động vào.
- LƯU Ý TRẠNG THÁI: thẻ 207 đang ở `todo`, không phải `review` như lệnh kiểm chéo giả định (thẻ tạo sau, chưa ai chuyển doing/review). Vì kết luận là đạt và việc gốc đã xong, tôi chuyển thẳng sang `done` thay vì quay `doing`.
- Cách 5s. `POST /api/tasks/207/comments` (nội dung `[KIEM-DINH] dat...` không dấu, kèm lý do + trỏ sổ này): OK lần 1 — `id=119, task_id=207, author=me`, response echo đủ body.
- Cách 5s. `POST /api/tasks/207/move {done}`: lần 1 HTTP 500 → cách 5s lần 2 HTTP 500 → cách 5s lần 3 HTTP 500. Hết quota (tối đa 2 thử lại), dừng.
- Xác minh: `GET /api/tasks/207` trả 200 nhưng thân rỗng (đúng bệnh NCKH-045 từng gặp ở thẻ 203); `GET board` lần 1 HTTP 500, lần 2 OK → `id=207 status=todo` — KHẲNG ĐỊNH cả 3 move đều không áp dụng (toàn HTTP 500, không phải timeout).
- Kết luận: comment kiểm định đã lên bảng; cột thẻ vẫn `todo` — nhờ Viện trưởng khi Kanzo ổn định vá 207 sang `done` (nội dung kiểm định đủ trong mục trên và comment id 119).
