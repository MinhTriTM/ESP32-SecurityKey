# qgac-distinguisher

Bộ phân biệt nơ-ron kiểu Gohr trên Speck32/64 rút gọn vòng:
**sinh dữ liệu bằng Rust nhanh** + **huấn luyện bằng PyTorch**.

Port từ `tools/ml_distinguisher.py` của repo mẹ: giữ nguyên mật mã
(Speck32/64, chênh lệch bản rõ `(0x0040, 0x0000)`, tập cân bằng, MLP
64 → 128 → 64 → 1, Adam lr=0.002, BCE), chỉ thay phần sinh dữ liệu
numpy chậm bằng Rust (seeded, xác định) và thay MLP numpy bằng PyTorch.

## Kiến trúc

```
qgac-distinguisher/
├── crates/nd-data/      # Rust: Speck32/64 + sinh dataset + đọc/ghi .ndd
│   ├── src/lib.rs       #   thư viện (encrypt/decrypt/tao_dataset/ndd)
│   ├── src/main.rs      #   binary nd-gen (CLI sinh dataset)
│   └── tests/           #   kiểm vector Speck từ fixture Python
├── python/
│   ├── ndd.py           # đọc/ghi .ndd bằng numpy (đối chiếu + nạp train)
│   └── train.py         # huấn luyện MLP PyTorch từ file .ndd
├── tests/fixtures/      # speck.json: vector kiểm do bản Python mẹ sinh ra
└── docs/THIET-KE.md     # đặc tả byte .ndd + ánh xạ với bản Python
```

Hai bên giao tiếp qua file dataset nhị phân `.ndd`.

## Định dạng file `.ndd` (tóm tắt)

- Header 20 byte: magic `NDD1`, version u16, rounds u16,
  n_samples u32, seed u64 (tất cả little-endian).
- Mỗi mẫu 9 byte: 4 từ u16 LE `(c0.x, c0.y, c1.x, c1.y)` + 1 byte nhãn (0/1).
- Đặc trưng huấn luyện: 64 bit MSB-first của 4 từ.

Đặc tả đầy đủ xem [docs/THIET-KE.md](docs/THIET-KE.md).

## Cách chạy end-to-end

Yêu cầu: Rust (cargo), Python 3.12, `pip install -r python/requirements.txt`.

```powershell
# 1. Sinh dataset bằng Rust (nhanh, xác định theo seed)
cargo run -p nd-data --bin nd-gen -- --rounds 5 --samples 6000 --seed 1 --out train-R5.ndd
cargo run -p nd-data --bin nd-gen -- --rounds 5 --samples 2000 --seed 2 --out test-R5.ndd

# 2. Huấn luyện bằng PyTorch
python python/train.py --data train-R5.ndd --test-data test-R5.ndd --epochs 5

# Kiểm tra nhanh (không cần dữ liệu)
cargo test -p nd-data
python python/train.py --self-test
```

Lưu ý: chạy các lệnh `cargo` từ thư mục `qgac-distinguisher/crates/nd-data`
(nếu chưa có workspace), hoặc từ `qgac-distinguisher` sau khi thêm
`Cargo.toml` workspace. Lệnh mẫu ở trên giả định crate `nd-data` đã tham
chiếu được; cách đơn giản nhất:

```powershell
cd qgac-distinguisher/crates/nd-data
cargo test
cargo run --bin nd-gen -- --rounds 5 --samples 1000 --seed 1 --out train-R5.ndd
cd ../../..
python qgac-distinguisher/python/train.py --data train-R5.ndd --epochs 1
```
