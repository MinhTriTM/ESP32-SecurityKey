# Sổ cái NCKH-055 — Hoàng Cường (nhóm PQC, đợt 2C)

Nhiệm vụ (từ phan-cong.json): "Cài liboqs trên môi trường sạch — Thử cài theo
requirements-pqc trên venv mới, ghi mọi lỗi gặp và cách sửa." Loại: t1-tay-chon.

Quy tắc áp dụng: shell pwsh, không git commit, không chạm (không ghi/sửa) `.tooling/`
(chỉ đọc để đối chiếu), giới hạn 20 phút — hết giờ thì dừng, không build từ source.

## 2026-11-21 03:09 — nhận việc, đọc tài liệu
- Đã đọc: `vien-nghien-cuu/HIEN-CHUONG.md`, mục NCKH-055 trong
  `vien-nghien-cuu/phan-cong.json`, `vien-nghien-cuu/so-cai/README.md`,
  `tools/requirements-pqc.txt` (nội dung: `liboqs-python>=0.16`), `tools/pqc.py`.
- Kế hoạch: tạo venv sạch trong `$env:TEMP/nckh055-venv`, pip install theo
  requirements-pqc, thử `import oqs`, ghi mọi lỗi + cách sửa.
- Môi trường: Windows, Python 3.12.0, pip 26.2.1 (system).

## 2026-11-21 03:10 — tạo venv sạch (OK, không lỗi)
- Lệnh: `python -m venv "$env:TEMP/nckh055-venv"`
- Kết quả: thành công, `Scripts/python.exe` + pip 23.2.1 có mặt.
- Nâng pip trong venv lên 26.3: thành công, không lỗi.

## 2026-11-21 03:11 — pip install requirements-pqc (OK, không lỗi)
- Lệnh: `venv/Scripts/python.exe -m pip install -r tools/requirements-pqc.txt`
- Kết quả: `Successfully installed liboqs-python-0.16.0.2` (lấy từ cache wheel,
  không cần build, không lỗi, không cần sửa gì).

## 2026-11-21 03:12 — import oqs thuần (THẤT BẠI đúng như dự kiến: thiếu DLL native)
- Lệnh: `venv/Scripts/python.exe -c "import oqs; ..."`
- Hiện tượng:
  - `liboqs not found, installing it in C:\Users\user\_oqs`, đếm ngược 5s,
    `git clone --depth 1 --branch=0.16.0 https://github.com/open-quantum-safe/liboqs`
    thành công (thấy log "Updating files: 100%").
  - Sau đó crash: `FileNotFoundError: [WinError 2] The system cannot find the file
    specified` tại `oqs/oqs.py:242` trong `_install_liboqs` (vòng lặp chạy
    clone -> configure -> build -> install). Clone đã xong nên lệnh chết là
    `configure_cmd = ["cmake", "-S", ...]` — tức thiếu `cmake`.
- Nguyên nhân gốc (đã kiểm chứng từng món):
  - `git`: CÓ (`C:\Program Files\Git\cmd\git.exe`).
  - `cmake`: KHÔNG có (`Get-Command cmake` trống) → nguyên nhân trực tiếp.
  - `cl`/MSVC: KHÔNG có (`Get-Command cl`, `msbuild` trống; `vswhere` tồn tại
    nhưng truy vấn `VC.Tools` không trả về bản cài nào) → kể cả có cmake thì
    build vẫn sẽ hỏng ở bước biên dịch C.
  - `ninja`: có (`Python313\Scripts\ninja.exe`) nhưng không đủ thay MSVC.
  - `$HOME/_oqs`: chưa được tạo (build chết trước bước install). Thư mục
    clone tạm đã tự xóa theo `TemporaryDirectory`.
- Cách sửa (đề xuất, KHÔNG thực hiện vì vượt giới hạn 20 phút / cấm build source):
  1. Cài CMake (winget `Kitware.CMake`) + Visual Studio Build Tools workload
     "Desktop development with C++", rồi `import oqs` một lần để nó tự build
     vào `%USERPROFILE%\_oqs`; hoặc
  2. Lấy DLL liboqs build sẵn và trỏ `OQS_INSTALL_PATH` tới thư mục chứa `bin/oqs.dll`
     trước khi `import oqs` (đã kiểm chứng ở mục dưới).

## 2026-11-21 03:14 — test chẩn đoán bổ sung: import oqs với DLL có sẵn (THÀNH CÔNG)
- Mục đích: chứng minh venv sạch + wrapper Python là tốt, chỉ thiếu DLL native.
  Chỉ ĐỌC `.tooling/oqs/bin/oqs.dll` (16.666.405 byte), không ghi/sửa `.tooling/`.
- Lệnh: `$env:OQS_INSTALL_PATH = "<repo>/.tooling/oqs"`,
  `venv/Scripts/python.exe -c "import oqs; ..."`.
- Kết quả:
  - `oqs_version: 0.16.0`, `oqs_python: 0.16.0.2`
  - `enabled_kems: 38`, `ML-KEM-768 enabled: True`
- Kết luận: **CÓ, `import oqs` bắt buộc cần DLL native.** `pip install
  liboqs-python` chỉ cài wrapper ctypes; không có `oqs.dll` thì import thất bại.

## 2026-11-21 03:20 — đồng bộ Kanzo (KHÔNG thấy thẻ của mình, không tạo thẻ)
- `GET /api/board?project=esp32-securitykey` (timeout 30s): lần 1 → 500
  Internal Server Error; đợi 5s thử lại lần 2 → OK (62 tasks); lần 3 (lọc chặt)
  → 500; đợi 5s thử lại lần 4 → OK. Đúng tính chất chập chờn đã báo trước.
- Lọc `NCKH-055` / `Hoàng Cường`: chỉ trúng 1 thẻ id 201
  "[ML] Benchmark CPU vs GPU (NCKH-050)", trạng thái `todo`, chủ là Hà Bình
  (NCKH-050, nhóm ML) — trong mô tả ghi "Người kiểm chéo: NCKH-055 (khác nhóm)".
- Kết luận: không có thẻ nào mà NCKH-055 là chủ. Thẻ 201 còn ở `todo` (việc của
  NCKH-050 chưa xong, chưa tới `review`) nên chưa có gì để kiểm chéo lúc này.
- Hành động: KHÔNG move, KHÔNG comment vào thẻ 201 (việc của agent khác, chưa
  tới lượt review), KHÔNG tự tạo thẻ — đúng chỉ thị "hỏng hoặc không thấy thẻ
  thì ghi sổ và tiếp tục".
- Ghi nhận cho Viện trưởng: khi thẻ 201 sang `review`, gọi NCKH-055 kiểm chéo.

## 2026-11-21 03:21 — báo cáo cuối
- Đã làm: cài sạch liboqs-python trên venv mới trong `$env:TEMP`, tái hiện lỗi
  thiếu DLL native, xác định thiếu cmake (+MSVC), kiểm chứng DLL có sẵn cứu được.
- Tự kiểm: 4 lệnh trên, output ghi đầy đủ ở từng mục; không sửa file repo nào
  ngoài sổ này; không chạm `.tooling/`.
- Unresolved: (1) máy thiếu CMake + MSVC nên không thể hoàn tất `import oqs`
  thuần túy trên môi trường sạch; (2) chưa chạy `tools/pqc.py --self-test` trên
  venv sạch (ngoài phạm vi: nhiệm vụ chỉ yêu cầu tới `import oqs`).
- Kanzo: không có thẻ chủ NCKH-055 (chỉ có thẻ 201 của NCKH-050 chỉ định mình
  kiểm chéo, còn ở `todo`); đã ghi sổ, không tạo thẻ, không move/comment.
- Venv sạch giữ nguyên tại `$env:TEMP/nckh055-venv` để Viện trưởng/người kiểm
  tra lại; không xóa.

## 2026-11-21 — kiểm chéo đợt 2C: công việc NCKH-050 Hà Bình (bench CPU)

Vai: NCKH-055 Hoàng Cường, kiểm độc lập bằng ĐƯỜNG KHÁC. Đã đọc toàn bộ
`vien-nghien-cuu/so-cai/NCKH-050.md`. Mọi lệnh shell dùng `shell="pwsh"`;
không git commit; không sửa file repo nào ngoài chính sổ này.

### Kết luận: ĐẠT

- Môi trường: torch CPU-only được xác nhận độc lập; "không có số CUDA" là
  đúng và có lý do chính đáng (ngân sách cấm cài nặng + tool numpy thuần).
- Số liệu: cấu hình nhẹ chạy độc lập khớp từng chữ số accuracy với sổ
  NCKH-050; thời gian cùng bậc.
- Phát hiện slow path OpenBLAS: tái hiện độc lập cùng hướng trên cấu hình
  khác, kiểm chứng threads=1 hết chậm → kết luận có logic và đúng.

### Kiểm tra độc lập (lệnh + output thật)

1. torch CPU-only (đường khác: gọi trực tiếp, không qua script của NCKH-050):
   - `torch: 2.14.1+cpu`, `cuda_available: False`, `device_count: 0`
   - numpy BLAS: `scipy-openblas 0.3.34.106.0, Haswell, MAX_THREADS=24,
     NO_AFFINITY` — khớp từng chi tiết với sổ NCKH-050.
   - → Xác nhận: không có đường CUDA nào khả dụng trong Python.
2. Tool numpy thuần (đường khác: grep source thay vì tin mô tả):
   - `Select-String -Pattern 'torch|cuda|device|batch' tools/ml_distinguisher.py`
     → không có import torch/cuda/device (chỉ 1 dòng comment nhắc torch);
     có cờ `--batch` mặc định 256. → "Cùng cấu hình trên CUDA" đúng là
     không khả thi nếu không port mô hình; phương án dự phòng (bench CPU
     đa cấu hình) hợp lệ.
3. Cấu hình nhẹ độc lập (R=5, 2k train/2k test, 3 epoch, seed 1337,
   batch 256 mặc định):
   - Output tool: `accuracy=0.5070 (0.2s)`; wall toàn tiến trình ~0.8s
     (gồm khởi động Python).
   - Đối chiếu sổ NCKH-050 §5 dòng "nhẹ 2k/3ep": acc **0.5070 khớp từng
     chữ số**, train 0.2s vs ~0.055–0.2s cùng bậc (sai khác do máy chia
     sẻ tải, đúng cảnh báo "số tuyệt đối dao động" của NCKH-050).
   - → Pipeline chạy được, số cùng bậc. ĐẠT.
4. Đối chứng slow path batch lớn (cấu hình nhẹ khác hẳn sweep gốc 6k/5ep):
   - Cùng cấu hình nhẹ + `--batch 1024`: `accuracy=0.4865 (1.6s)` —
     chậm hơn batch 256 (0.2s) **~8 lần**, cùng hướng với ~15 lần của
     NCKH-050 ở cấu hình chuẩn. Acc đổi theo batch (0.5070 → 0.4865),
     phù hợp nhận định "batch ảnh hưởng accuracy".
   - Kiểm chứng quyết định: `$env:OPENBLAS_NUM_THREADS='1';
     $env:OMP_NUM_THREADS='1'` + batch 1024 → `accuracy=0.4865 (0.1s)`:
     nhanh hơn **~16 lần**, acc không đổi. → Tái hiện độc lập cơ chế
     gốc (threading OpenBLAS), không chỉ copy số.
   - Đánh giá logic: kết luận slow path CÓ LOGIC — (a) ngược lý thuyết
     FLOPs nhưng giải thích được bằng overhead thread trên ma trận nhỏ;
     (b) profile tách op chỉ ra `X.T @ D` non-contiguous, test threads=1
     triệt tiêu hiện tượng (cả của NCKH-050 lẫn kiểm chéo này); (c) hiệu
     ứng phụ thuộc ngưỡng batch, đúng đặc trưng pathology threading chứ
     không phải lỗi đo ngẫu nhiên.

### Đồng bộ Kanzo (thẻ 201 "[ML] Benchmark CPU vs GPU (NCKH-050)")

- `GET /api/board`: lần 1 OK ngay (69 tasks), thấy `id=201 status=review`.
  Không tự tạo thẻ.
- `POST /api/tasks/201/comments` (`[KIEM-DINH] đạt...`): lần 1 HTTP 500,
  thử lại lần 2 HTTP 500, thử lại lần 3 (rút gọn) HTTP 500 → hết ngân
  sách, comment KHÔNG lên được. Toàn văn kiểm định nằm ở mục này.
- Cách 5s. `POST /api/tasks/201/move {done}`: OK lần 1 (`status=done`).
- Cách 5s. GET xác minh: lần 1 HTTP 500, lần 2 OK →
  `id=201 status=done` ĐÃ XÁC MINH trên bảng.
- Trạng thái thẻ: review -> done (đã áp dụng).

### Unresolved

1. Comment `[KIEM-DINH]` không POST được sau 3 lần (Kanzo 500 liên tục ở
   endpoint comments) — nhờ Viện trưởng khi Kanzo ổn định kiểm tra/coppy
   tay nội dung mục này vào thẻ 201.
2. Không đo lại toàn bộ sweep của NCKH-050 (ngoài phạm vi kiểm chéo 1 cấu
   hình + đối chứng slow path); các bảng §2–§5 của NCKH-050 được tin cậy
   gián tiếp qua 2 điểm khớp độc lập + cơ chế tái hiện được.
