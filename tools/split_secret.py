#!/usr/bin/env python3
"""Chia một bí mật thành N phần (share), chỉ cần K phần là ghép lại được.

Thuật toán Shamir trên trường GF(256). Mục đích: mật khẩu mở bản sao lưu
(recovery codes, két mật khẩu...) được chia ra nhiều USB/ổ cứng. Mất bớt ổ
vẫn khôi phục được, một ổ rơi vào tay kẻ xấu cũng không đủ để mở.

Cách dùng:
    python split_secret.py split --shares 3 --threshold 2 --out E:\\backup
    python split_secret.py combine E:\\s1\\share-1-of-3.txt F:\\s2\\share-3-of-3.txt
    python split_secret.py --self-test

Cần Python 3.10 trở lên. Không cần cài thêm thư viện.
"""
import argparse
import getpass
import secrets
import sys
from pathlib import Path

try:
    import secureio
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import secureio

HEADER_MAGIC = "SHAMIR-SHARE-V1"

# --- Số học trên GF(256) với đa thức AES x^8 + x^4 + x^3 + x + 1 ---

_GF_EXP = [0] * 512
_GF_LOG = [0] * 256


def _xtime(a: int) -> int:
    a <<= 1
    if a & 0x100:
        a ^= 0x11B
    return a & 0xFF


def _build_tables() -> None:
    # Dựng bảng bằng lũy thừa của 0x03 (phần tử sinh, chu kỳ đủ 255).
    # Không dùng 0x02 vì chu kỳ của nó chỉ 51, bảng sẽ thiếu giá trị.
    x = 1
    for i in range(255):
        _GF_EXP[i] = x
        _GF_LOG[x] = i
        x = _xtime(x) ^ x  # nhân với 0x03
    if len(set(_GF_EXP[:255])) != 255:
        raise ValueError("0x03 không sinh đủ trường GF(256)")
    for i in range(255, 512):
        _GF_EXP[i] = _GF_EXP[i - 255]


_build_tables()


def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _GF_EXP[_GF_LOG[a] + _GF_LOG[b]]


def _gf_div(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("chia cho 0 trong GF(256)")
    if a == 0:
        return 0
    return _GF_EXP[(_GF_LOG[a] - _GF_LOG[b]) % 255]


def _eval_poly(coeffs: list[int], x: int) -> int:
    """Tính đa thức tại x theo Horner. coeffs[0] là hệ số tự do."""
    y = 0
    for c in reversed(coeffs):
        y = _gf_mul(y, x) ^ c
    return y


# --- Chia và ghép Shamir ---

def split(secret: bytes, n: int, k: int) -> list[tuple[int, bytes]]:
    """Chia secret thành n share (x, y), cần k share để ghép. x chạy 1..n."""
    if not secret:
        raise ValueError("bí mật rỗng, không có gì để chia")
    if not 1 <= k <= n <= 255:
        raise ValueError(f"cần 1 <= threshold <= shares <= 255, nhận k={k} n={n}")
    out: list[bytearray] = [bytearray() for _ in range(n)]
    for byte in secret:
        # Mỗi byte là hệ số tự do của một đa thức ngẫu nhiên bậc k-1.
        coeffs = [byte] + [secrets.randbelow(256) for _ in range(k - 1)]
        for i in range(n):
            out[i].append(_eval_poly(coeffs, i + 1))
    return [(i + 1, bytes(out[i])) for i in range(n)]


def _lagrange_at_zero(xs: list[int], ys: list[int]) -> int:
    """Nội suy Lagrange tại x=0. Trong GF(2^8), trừ chính là xor."""
    total = 0
    for i in range(len(xs)):
        num, den = 1, 1
        for j in range(len(xs)):
            if i == j:
                continue
            num = _gf_mul(num, xs[j])
            den = _gf_mul(den, xs[i] ^ xs[j])
        total ^= _gf_mul(ys[i], _gf_div(num, den))
    return total


def _check_coords(n: int, k: int, x: int) -> None:
    """Biên tọa độ share: chặn x âm (bí mật SAI LẶNG), x=0, x>255, k/n sai."""
    if not 1 <= k <= n <= 255:
        raise ValueError(f"cần 1 <= threshold <= shares <= 255, nhận k={k} n={n}")
    if not 1 <= x <= 255:
        raise ValueError(f"chỉ số share phải trong 1..255, nhận {x}")


def combine(shares: list[tuple[int, bytes]]) -> bytes:
    """Ghép các share (x, y) thành secret. Mọi share phải cùng độ dài."""
    if not shares:
        raise ValueError("không có share nào để ghép")
    xs = [x for x, _ in shares]
    if len(set(xs)) != len(xs):
        raise ValueError("share trùng chỉ số x, kiểm tra lại file")
    for x in xs:
        if not 1 <= x <= 255:
            raise ValueError(f"chỉ số x phải trong 1..255, nhận {x}")
    length = len(shares[0][1])
    if any(len(y) != length for _, y in shares):
        raise ValueError("các share không cùng độ dài, lẫn lộn hai lần chia?")
    return bytes(
        _lagrange_at_zero(xs, [y[pos] for _, y in shares])
        for pos in range(length)
    )


# --- Định dạng file share ---

def format_share(n: int, k: int, x: int, y: bytes) -> str:
    return f"{HEADER_MAGIC} shares={n} threshold={k} index={x} len={len(y)}\n{y.hex()}\n"


def parse_share(text: str) -> tuple[int, int, int, bytes]:
    """Trả về (n, k, x, y). Ném ValueError nếu file sai định dạng."""
    lines = text.strip().splitlines()
    if len(lines) != 2 or not lines[0].startswith(HEADER_MAGIC):
        raise ValueError("file không phải share Shamir của tool này")
    params: dict[str, int] = {}
    for part in lines[0].split()[1:]:
        key, sep, val = part.partition("=")
        if not sep:
            raise ValueError(f"header lạ: {part}")
        if key in params:
            raise ValueError(f"header trùng tham số: {key}")
        try:
            params[key] = int(val)
        except ValueError:
            raise ValueError(f"tham số {key} không phải số: {val}")
    for need in ("shares", "threshold", "index", "len"):
        if need not in params:
            raise ValueError(f"header thiếu tham số: {need}")
    n, k, x = params["shares"], params["threshold"], params["index"]
    _check_coords(n, k, x)
    try:
        y = bytes.fromhex(lines[1])
    except ValueError:
        raise ValueError("phần dữ liệu không phải hex hợp lệ")
    if y.hex() != lines[1].lower() or len(y) != params["len"]:
        raise ValueError("độ dài dữ liệu không khớp header")
    return n, k, x, y


# --- Lệnh CLI ---

def cmd_split(args: argparse.Namespace) -> int:
    if args.from_file:
        try:
            secret = secureio.read_capped(args.from_file)
        except (OSError, ValueError) as exc:
            print(f"Không đọc được file bí mật: {exc}")
            return 1
    else:
        first = getpass.getpass("Nhập bí mật cần chia: ").encode("utf-8")
        second = getpass.getpass("Nhập lại để xác nhận: ").encode("utf-8")
        if first != second or not first:
            print("Hai lần nhập không khớp hoặc rỗng.")
            return 1
        secret = first
    try:
        shares = split(secret, args.shares, args.threshold)
    except ValueError as exc:
        print(f"Sai tham số: {exc}")
        return 2
    out_dir = Path(args.out)
    for x, y in shares:
        path = out_dir / f"share-{x}-of-{args.shares}.txt"
        try:
            secureio.write_secret_file(path, format_share(args.shares, args.threshold, x, y))
        except OSError as exc:
            print(f"Không ghi được {path}: {exc}")
            return 1
        print(f"Đã ghi {path}")
    print(f"Xong: {args.shares} share, cần {args.threshold} share để ghép.")
    print("Chép mỗi file sang một USB khác nhau, cất ở nơi khác nhau.")
    return 0


def cmd_combine(args: argparse.Namespace) -> int:
    parsed = []
    for name in args.shares:
        try:
            parsed.append(parse_share(Path(name).read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            print(f"File {name} lỗi: {exc}")
            return 1
    heads = {(n, k, len(y)) for n, k, _, y in parsed}
    if len(heads) != 1:
        print("Các share không cùng một lần chia (shares/threshold/len khác nhau).")
        return 1
    n, k, _ = heads.pop()
    if len(parsed) < k:
        print(f"Thiếu share: cần ít nhất {k} trong {n}, mới đưa {len(parsed)}.")
        return 2
    try:
        secret = combine([(x, y) for _, _, x, y in parsed])
    except ValueError as exc:
        print(f"Không ghép được: {exc}")
        return 1
    if args.out:
        Path(args.out).write_bytes(secret)
        print(f"Đã ghi bí mật ra {args.out}")
    else:
        try:
            print(f"Bí mật: {secret.decode('utf-8')}")
        except UnicodeDecodeError:
            print(f"Bí mật (hex): {secret.hex()}")
    return 0


# --- Tự kiểm tra ---

def self_test() -> int:
    # 1. Bảng phải đủ 255 giá trị khác nhau, rồi mới kiểm vector AES (FIPS-197).
    assert len(set(_GF_EXP[:255])) == 255, "bảng exp thiếu giá trị"
    assert _GF_LOG[1] == 0 and _GF_LOG[0x53] != 0, "bảng log sai"
    assert _gf_mul(0x53, 0xCA) == 0x01, "phép nhân GF(256) sai"
    assert _gf_div(0x01, 0xCA) == 0x53, "phép chia GF(256) sai"

    # 2. Round-trip ngẫu nhiên với nhiều ngưỡng, mọi tập con K share đều ghép đúng.
    import itertools

    cases = [(3, 2), (5, 3), (5, 5), (8, 2)]
    for n, k in cases:
        secret = secrets.token_bytes(16)
        shares = split(secret, n, k)
        assert [x for x, _ in shares] == list(range(1, n + 1))
        for subset in itertools.combinations(shares, k):
            assert combine(list(subset)) == secret, f"ghép sai với n={n} k={k}"
        # Thừa share vẫn ghép đúng.
        assert combine(shares) == secret

    # 3. Thiếu share cho ra kết quả khác (xác suất trùng chỉ 2^-128 với secret 16 byte).
    s = secrets.token_bytes(16)
    assert combine(split(s, 3, 2)[:1]) != s

    # 4. File share hỏng bị từ chối.
    assert parse_share(format_share(3, 2, 1, b"abcdefgh"))[2] == 1
    for bad in ["rác", f"{HEADER_MAGIC} shares=3\nzzzz",
                format_share(3, 2, 1, b"abcdefgh").replace("len=8", "len=7")]:
        try:
            parse_share(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"đáng lẽ phải từ chối: {bad[:40]}")

    # 5. Share trùng x và khác độ dài bị từ chối.
    try:
        combine([(1, b"aa"), (1, b"bb")])
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối share trùng x")
    try:
        combine([(1, b"aa"), (2, b"bbb")])
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối share khác độ dài")

    # 6. Biên tọa độ: index -1/0/300, thiếu param, k/n sai, trùng param,
    # param không phải số — tất cả bị từ chối sạch bằng ValueError.
    data_line = format_share(3, 2, 1, b"abcdefgh").splitlines()[1]
    bad_headers = [
        f"{HEADER_MAGIC} shares=3 threshold=2 index=-1 len=8",
        f"{HEADER_MAGIC} shares=3 threshold=2 index=0 len=8",
        f"{HEADER_MAGIC} shares=3 threshold=2 index=300 len=8",
        f"{HEADER_MAGIC} shares=3 threshold=2 len=8",
        f"{HEADER_MAGIC} shares=3 threshold=5 index=1 len=8",
        f"{HEADER_MAGIC} shares=3 threshold=2 index=1 index=2 len=8",
        f"{HEADER_MAGIC} shares=3 threshold=x index=1 len=8",
    ]
    for h in bad_headers:
        try:
            parse_share(h + "\n" + data_line + "\n")
        except ValueError:
            pass
        else:
            raise AssertionError(f"đáng lẽ phải từ chối: {h}")
    for bad_x in (-1, 0, 300):
        try:
            combine([(bad_x, b"aa"), (2, b"bb")])
        except ValueError:
            pass
        else:
            raise AssertionError(f"đáng lẽ combine phải từ chối x={bad_x}")

    print("self-test ok: GF(256) đúng vector AES, chia/ghép đúng mọi ngưỡng thử.")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv or "-t" in argv:
        return self_test()
    parser = argparse.ArgumentParser(description="Chia/ghép bí mật Shamir K-trên-N.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_split = sub.add_parser("split", help="chia bí mật thành N share")
    p_split.add_argument("--shares", type=int, required=True, help="số share N (tối đa 255)")
    p_split.add_argument("--threshold", type=int, required=True, help="số share tối thiểu K để ghép")
    p_split.add_argument("--from-file", help="đọc bí mật từ file thay vì gõ")
    p_split.add_argument("--out", required=True, help="thư mục ghi các file share")
    p_combine = sub.add_parser("combine", help="ghép các share thành bí mật")
    p_combine.add_argument("shares", nargs="+", help="file share (ít nhất K file)")
    p_combine.add_argument("--out", help="ghi bí mật ra file thay vì in màn hình")
    p_qr = sub.add_parser("qr", help="vẽ file share thành ảnh QR để quét sang điện thoại")
    p_qr.add_argument("share", help="file share cần vẽ")
    p_qr.add_argument("--out", help="file ảnh PNG (mặc định cùng tên, đuôi .png)")
    args = parser.parse_args(argv)
    if args.cmd == "split":
        return cmd_split(args)
    if args.cmd == "qr":
        return cmd_qr(args)
    return cmd_combine(args)


def cmd_qr(args: argparse.Namespace) -> int:
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
    except ImportError:
        print("Thiếu thư viện QR. Chạy: pip install -r requirements-qr.txt")
        return 2
    try:
        text = Path(args.share).read_text(encoding="utf-8")
        parse_share(text)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"File share lỗi: {exc}")
        return 1
    out = args.out or str(Path(args.share).with_suffix(".png"))
    try:
        secureio.ensure_parent(out)
        qrcode.make(text.strip(), error_correction=ERROR_CORRECT_M).save(out)
    except OSError as exc:
        print(f"Không vẽ được QR ra {out}: {exc}")
        return 1
    print(f"Đã vẽ QR ra {out}. Quét xong thì xóa file ảnh.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
