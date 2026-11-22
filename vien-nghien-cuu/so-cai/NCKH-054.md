# Sổ cái NCKH-054 — Phạm Cường (nhóm kiemdinh, đợt 2C)

- Nhiệm vụ (phan-cong.json): "Cài lib trên venv sạch — Thử mọi requirements trên venv mới, ghi lỗi."
- Quy tắc tuân thủ: REPO CHỈ ĐỌC (chỉ ghi đúng file này), shell pwsh, không git commit,
  venv sạch trong $env:TEMP, KHÔNG chạm .tooling/ và system python, KHÔNG build liboqs.

## 2026-11-21 03:05 — nhận việc
- Việc: tạo venv sạch trong $env:TEMP, cài lần lượt mọi tools/requirements*.txt, ghi lỗi + cách sửa.
- Môi trường: Windows 11, system python 3.12.0 (đạt yêu cầu >= 3.10 trong requirements.txt).
- Venv: C:\Users\user\AppData\Local\Temp\nckh054-venv (python 3.12.0, pip 23.2.1).

## 2026-11-21 03:19 — báo cáo cài đặt
- Đã làm: tạo venv sạch + cài thử cả 4 file requirements, mỗi file một lệnh pip install riêng.
- Bảng cài đặt:

| File | Gói cài được (pip freeze) | Kết quả | Lỗi | Cách sửa |
|------|---------------------------|---------|-----|----------|
| tools/requirements.txt | hidapi 0.15.0 | OK (exit 0) | Không | Không cần |
| tools/requirements-vault.txt | cryptography 50.0.2, cffi 2.1.1, pycparser 3.12 | OK (exit 0) | Không | Không cần |
| tools/requirements-qr.txt | qrcode 8.2, pillow 13.0.0, colorama 0.4.6 | OK (exit 0) | Không | Không cần |
| tools/requirements-pqc.txt | liboqs-python 0.16.0.2 (wheel wrapper) | OK pip install (exit 0); BỎ QUA build native, xem dưới | Không (ở bước pip) | Không cần |

- Tự kiểm (chạy bằng python trong venv, KHÔNG chạm system python):
  - `pip freeze` -> 8 gói như bảng trên.
  - `import hid` -> OK (hid.cp312-win_amd64.pyd trong venv).
  - `import cryptography` -> OK, 50.0.2.
  - `qrcode.make('nckh054-smoke')` -> OK, ảnh 290x290; PIL 13.0.0.
  - Ghi chú nhỏ: module `qrcode` không có thuộc tính `__version__` (phải lấy qua
    importlib.metadata) — đây là đặc tính của thư viện, không phải lỗi repo.
- KHÔNG build liboqs — lý do bỏ qua (theo đúng lệnh nhiệm vụ):
  1. Nhiệm vụ cấm build liboqs.
  2. Lần đầu `import oqs` sẽ tự build native vào %USERPROFILE%\_oqs, tức ghi ra ngoài
     cả venv lẫn repo — vượt phạm vi "venv sạch trong TEMP" và cần CMake + Visual Studio C++.
  3. Vì vậy chỉ kiểm tới bước `pip install liboqs-python` (thành công) và KHÔNG `import oqs`.
  4. Xác nhận sau khi xong: `Test-Path $env:USERPROFILE\_oqs` -> False (chưa hề build).
- Cam kết không chạm vùng cấm:
  - .tooling/: không có lệnh nào đọc/ghi tới thư mục này.
  - system python: chỉ dùng `python -m venv` để tạo venv (đọc interpreter), không hề
    `pip install` ra system site-packages; mọi gói nằm trong venv TEMP.
  - repo: chỉ đọc + ghi đúng file sổ cái này; không git commit.
- Log chi tiết từng lần cài (ngoài repo, trong TEMP):
  - nckh054-req-base.log, nckh054-req-vault.log, nckh054-req-qr.log, nckh054-req-pqc.log
- Unresolved: (1) pip trong venv là 23.2.1, PyPI nhắc có 26.3 — chỉ là notice, không nâng cấp
  để giữ venv đúng trạng thái "sạch" tái hiện được; (2) liboqs native chưa được kiểm chứng
  trên máy này (bị cấm build) — cần một nhiệm vụ riêng có quyền build + CMake/VS C++ để kiểm.

## 2026-11-21 03:25 — đồng bộ Kanzo (thẻ 205, file trước bảng sau)
- Thẻ: [kiemdinh] Cài lib trên venv sạch (NCKH-054), id 205. GET board: thử 1 lỗi 500,
  thử 2 OK (66 thẻ). Mỗi thao tác ghi cách nhau 5s, timeout 30s, tối đa 2 thử lại.
- MOVE todo -> doing: OK ngay thử 1.
- COMMENT nhận việc: thử 1 timeout 30s, thử 2 lỗi 500, thử 3 OK.
- MOVE doing -> review: OK ngay thử 1.
- COMMENT báo cáo: thử 1 timeout 30s, thử 2 lỗi 500, thử 3 lỗi 500 -> GHI NHẬN THẤT BẠI.
- Đối chiếu lại bảng sau đợt ghi: status=review, comments=3 (lạ: chỉ 1 comment báo OK
  nhưng đếm được 3 — đúng cảnh báo Hiến chương: timeout/500 không đồng nghĩa server chưa ghi,
  có thể comment bị trùng do thử lại; nội dung chuẩn nằm ở file sổ cái này).
- Trạng thái: todo -> doing -> review. Chờ kiểm chéo NCKH-047.
- Unresolved thêm: (3) comment báo cáo trên Kanzo có thể thiếu/trùng do Kanzo chập chờn —
  Viện trưởng đối chiếu bằng file này khi Kanzo sống lại.

## 2026-11-21 03:28 — kiểm chéo NCKH-049 (đợt 2C, Phạm Cường kiểm Tạ Bình)
- Đối tượng: `vien-nghien-cuu/so-cai/NCKH-049.md` (Tạ Bình): so sánh chữ ký
  ML-DSA-65 3309B vs SLH-DSA-192s/f, khuyến nghị ML-DSA-65 cho ký firmware.
- Đường kiểm ĐỘC LẬP (không ăn theo nguồn của 049): tra web riêng
  (RFC 9909 IETF, Go pkg slhdsa, starkquantum, lamarrlabs, quantakrypto,
  encse/quantumize), tính lại mọi tỉ lệ bằng python qua pwsh, đánh giá logic
  khuyến nghị với flash ESP32-S3 16MB.
- Đối chiếu kích thước (byte) — TẤT CẢ KHỚP:
  - ML-DSA-44: 049 ghi 1312/2560/2420 — web khớp (1312/2560/2420).
  - ML-DSA-65: 049 ghi 1952/4032/3309 — web khớp; nhiều nguồn ghi đây là
    bộ được khuyên dùng mặc định (recommended default).
  - ML-DSA-87: 049 ghi 2592/4896/4627 — web khớp.
  - SLH-DSA-128s/f: 32/64/7856 và 32/64/17088 — web khớp.
  - SLH-DSA-192s/f: 48/96/16224 và 48/96/35664 — web khớp (RFC 9909 + Go docs).
  - SLH-DSA-256s/f: 64/128/29792 và 64/128/49856 — web khớp.
  - "Kích thước không phụ thuộc SHA2 hay SHAKE" — ĐÚNG (RFC 9909 liệt kê
    cùng size cho cả hai họ băm).
  - Level: ML-DSA 44=L2/65=L3/87=L5, SLH 128=L1/192=L3/256=L5 — đúng.
    Lưu ý nhỏ: cặp "Level 1/2" gộp ML-DSA-44 (L2) với SLH-128 (L1) không cùng
    level tuyệt đối, nhưng 049 đã ghi nhãn rõ nên không sai — chỉ là so sánh
    lân cận hợp lý vì không tồn tại ML-DSA level 1.
- Tính lại tỉ lệ bằng python (qua pwsh) — TẤT CẢ ĐÚNG:
  - 7856/2420=3,246 → "3,2 lần" đúng.
  - 16224/3309=4,903 → "4,9 lần" đúng.
  - 35664/3309=10,778 → "10,8 lần" đúng.
  - 29792/4627=6,439 → "6,4 lần" đúng.
  - 49856/4627=10,775 → "10,8 lần" đúng.
  - 1312/32=41 → "~40 lần" đúng.
- Đánh giá khuyến nghị ML-DSA-65 với flash ESP32-S3 16MB — LOGIC:
  - pk 1952B = 0,0116% flash 16MB → "dư chỗ nhúng khóa" đúng, loại bỏ lý do
    duy nhất để chê ML-DSA.
  - sig 3309B = 0,32% image 1MB; SLH cùng level 1,55%–3,40% → gọn hơn 5–11
    lần, đúng và có ý nghĩa cho manifest/kênh phân phối.
  - Tốc độ theo bậc độ lớn (ML-DSA sub-ms, SLH-s chậm 10–100ms) khớp kiến
    thức công khai; 049 đã ghi rõ là bậc độ lớn x86-64, không mạo nhận số đo
    repo, và U1 tự thừa nhận chưa đo liboqs — trung thực.
  - Định vị NIST (ML-DSA chuẩn chính, SLH-DSA dự phòng bảo thủ) — đúng.
  - Điều kiện "lai cổ điển+PQC, CHỜ Espressif, không tự vá bootloader" nhất
    quán với ràng buộc repo mà 049 đã trích; phương án B SLH-DSA khi "không
    tin lattice" là hợp lý.
- KẾT LUẬN: ĐẠT. Toàn bộ 9 bộ tham số khớp FIPS 204/205, 6 tỉ lệ tính lại
  đúng, khuyến nghị ML-DSA-65 logic với ràng buộc flash và định vị NIST.
- Kanzo http://100.101.100.100:4242/api (mỗi lệnh cách 5s, timeout 30s):
  - GET board lần 1: 500. Lần 2: 200 OK nhưng parse sai field nên rỗng.
    Lần 3: 200 OK, 39514 bytes, project esp32-securitykey total 69/open 24,
    cấu trúc `tasks[]` (id/project/title/status) — chưa kịp lọc NCKH-049.
  - GET lọc NCKH-049 lần 4–6: cả 3 đều 500 (hết 2 thử lại).
  - Không xác định được id thẻ → KHÔNG comment, KHÔNG move, KHÔNG tạo thẻ
    (đúng luật). Nếu Kanzo sống lại, Viện trưởng comment '[KIEM-DINH] đạt —
    9/9 bộ tham số khớp FIPS 204/205, tỉ lệ đúng, ML-DSA-65 hợp flash 16MB'
    và move review->done.
- Tự kiểm: mọi lệnh shell dùng shell='pwsh'; repo chỉ đọc ngoài file này;
  không git commit.
- Unresolved thêm: (4) chưa lan tỏa kết quả kiểm định lên Kanzo do Kanzo
  chập chờn — Viện trưởng đối chiếu bằng file này; (5) lượt này không đọc lại
  `docs/de-doa-luong-tu.md`, tin trích dẫn ưu tiên 4 của 049 — cần chặt chẽ
  tuyệt đối thì đối chiếu thêm 1 dòng.
