# Thiết kế qgac-distinguisher

Tài liệu kỹ thuật: đặc tả byte của file `.ndd` và ánh xạ với bản Python mẹ
(`tools/ml_distinguisher.py`).

## 1. Mục tiêu

Thay phần **sinh dữ liệu numpy chậm** bằng **Rust nhanh** (seeded, xác định),
giữ phần **huấn luyện bằng PyTorch** (thay MLP numpy). Hai bên giao tiếp qua
file dataset nhị phân `.ndd` (neural-distinguisher data).

## 2. Đặc tả byte của file `.ndd`

Mọi số nguyên đa byte đều **little-endian**. Kích thước file:

```
len = 20 + n_samples * 9  (byte)
```

### 2.1. Header (20 byte)

| Offset | Kích thước | Kiểu | Tên       | Ý nghĩa                          |
|--------|------------|------|-----------|----------------------------------|
| 0      | 4          | byte | magic     | Luôn là `4E 44 44 31` ("NDD1")   |
| 4      | 2          | u16  | version   | Phiên bản định dạng (hiện là 1)  |
| 6      | 2          | u16  | rounds    | Số vòng Speck đã dùng (1..=22)   |
| 8      | 4          | u32  | n_samples | Số mẫu trong file                |
| 12     | 8          | u64  | seed      | Seed RNG đã dùng để sinh         |

Ví dụ header của file R=5, 1000 mẫu, seed=1 (hex):

```
4E 44 44 31  01 00  05 00  E8 03 00 00  01 00 00 00 00 00 00 00
|--- magic --| |-ver-| |-R--| |----- n -----| |----- seed ------|
```

### 2.2. Thân file: từng mẫu 9 byte

Mẫu thứ `i` (đếm từ 0) nằm ở offset `20 + i * 9`:

| Offset trong mẫu | Kích thước | Kiểu | Tên     | Ý nghĩa                                    |
|------------------|------------|------|---------|--------------------------------------------|
| 0                | 2          | u16  | c0.x    | Nửa trái của bản mã thứ nhất               |
| 2                | 2          | u16  | c0.y    | Nửa phải của bản mã thứ nhất               |
| 4                | 2          | u16  | c1.x    | Nửa trái của bản mã thứ hai                |
| 6                | 2          | u16  | c1.y    | Nửa phải của bản mã thứ hai                |
| 8                | 1          | u8   | label   | Nhãn: 1 = bản mã thật, 0 = ngẫu nhiên     |

- Mẫu nhãn 1: `(c0, c1)` là cặp bản mã của cặp bản rõ lệch nhau
  `(FIXED_DX, FIXED_DY) = (0x0040, 0x0000)` dưới cùng một khóa ngẫu nhiên.
- Mẫu nhãn 0: 4 từ hoàn toàn ngẫu nhiên (tương đương 64 bit ngẫu nhiên
  trong bản Python).

Quy tắc kiểm tra khi đọc: magic phải là `NDD1`, version phải là 1,
label chỉ được 0/1, độ dài file phải khớp đúng công thức trên.

### 2.3. Từ mẫu `.ndd` ra đặc trưng huấn luyện

Đặc trưng là **64 bit MSB-first** của 4 từ, giống hệt `words_to_bits`:

```
bit[j*16 + b] = (tu[j] >> (15 - b)) & 1   (j = 0..3, b = 0..15)
```

- Rust: `nd_data::tu_thanh_bit` (để đối chiếu/tài liệu).
- Python: `ndd.tu_thanh_bit` (dùng thật trong `train.py`).

## 3. Ánh xạ với `make_dataset` của bản Python

Hàm `nd_data::tao_dataset(vong, so_mau, seed)` port trực tiếp
`make_dataset(rounds, n_samples, seed)`:

| Bản Python (`tools/ml_distinguisher.py`) | Bản Rust (`crates/nd-data`)        |
|------------------------------------------|------------------------------------|
| `rotr16` / `rotl16`                      | `rotr16` / `rotl16` (dùng `rotate_*`) |
| `expand_key` (ALPHA=7, BETA=2)           | `expand_key`, hằng `ALPHA`/`BETA`  |
| `encrypt` / `decrypt`                    | `encrypt` / `decrypt`              |
| `FIXED_DX=0x0040`, `FIXED_DY=0x0000`     | `FIXED_DX`, `FIXED_DY`             |
| `n_on = half + (n % 2)` mẫu nhãn 1 trước | Vòng lặp sinh nhãn 1 trước, cùng công thức |
| `rng.integers(0, 2, size=64)` nhãn 0     | 4 từ `u16` ngẫu nhiên (= 64 bit)   |
| `rng.permutation(n)` trộn               | `SliceRandom::shuffle` (Fisher–Yates) |
| `np.random.default_rng(seed)`            | `ChaCha8Rng::seed_from_u64(seed)`  |

**Lưu ý về RNG:** numpy `default_rng` (PCG64) và ChaCha8 là hai thuật toán
khác nhau, nên cùng một seed thì hai bản cho hai dataset khác nhau nhưng
**cùng phân phối và cùng tính chất** (cân bằng, xác định, trộn đều).
Mọi logic mật mã (Speck, chênh lệch, nhãn, trộn) đều giữ nguyên.

## 4. Ánh xạ huấn luyện: MLP numpy → MLP PyTorch

| Bản Python mẹ (`MLP`)              | `python/train.py` (`MLP`)        |
|------------------------------------|----------------------------------|
| 64 → 128 → 64 → 1                  | `Linear(64,128) → Linear(128,64) → Linear(64,1)` |
| ReLU + sigmoid, BCE                | ReLU + `BCEWithLogitsLoss`       |
| Khởi tạo He / Xavier (normal)      | `kaiming_normal_` / `xavier_normal_` |
| Adam lr=0.002, beta 0.9/0.999      | `torch.optim.Adam(lr=0.002)`     |
| Trộn lại mỗi epoch, batch          | Trộn lại mỗi epoch, batch        |
| Ngưỡng 0.5                        | Ngưỡng 0.5                       |
