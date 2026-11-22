#!/usr/bin/env python3
"""Cụm từ khôi phục kiểu ví lạnh, tương thích chuẩn BIP-39.

Mã hóa 128-256 bit bí mật thành 12-24 từ tiếng Anh để ghi ra giấy hoặc thép.
Mất hết thiết bị vẫn khôi phục được bằng cụm từ này. Wordlist là bảng
BIP-39 tiếng Anh chính thức (file bip39_english.txt cạnh tool).

Cách dùng:
    python mnemonic.py new --words 24                 # sinh bí mật mới
    python mnemonic.py from-entropy --from-file s.bin # bytes -> cụm từ
    python mnemonic.py to-entropy abandon ... about   # cụm từ -> hex
    python mnemonic.py seed abandon ... about         # lấy seed 64 byte
    python mnemonic.py --self-test

Cần Python 3.10 trở lên. Không cần cài thêm thư viện.
"""
import argparse
import hashlib
import secrets
import sys
import unicodedata
from pathlib import Path

try:
    import secureio
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import secureio

WORDLIST_PATH = Path(__file__).with_name("bip39_english.txt")
VALID_BITS = {128: 12, 160: 15, 192: 18, 224: 21, 256: 24}


def load_wordlist() -> list[str]:
    words = WORDLIST_PATH.read_text(encoding="utf-8").split()
    if len(words) != 2048:
        raise ValueError(f"bảng từ phải có 2048 từ, thấy {len(words)}")
    return words


def _to_bits(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)


def entropy_to_mnemonic(entropy: bytes, words: list[str]) -> str:
    """Bytes bí mật -> chuỗi từ. Độ dài entropy phải là 16/20/24/28/32 byte."""
    ent = len(entropy) * 8
    if ent not in VALID_BITS:
        raise ValueError(f"entropy phải dài {sorted(VALID_BITS)} bit, nhận {ent}")
    checksum = _to_bits(hashlib.sha256(entropy).digest())[: ent // 32]
    bits = _to_bits(entropy) + checksum
    return " ".join(words[int(bits[i:i + 11], 2)] for i in range(0, len(bits), 11))


def normalize_mnemonic(text: str) -> str:
    """Chuẩn hóa như BIP-39: NFKD, chữ thường, một khoảng trắng."""
    return " ".join(unicodedata.normalize("NFKD", text).lower().split())


def mnemonic_to_entropy(mnemonic: str, words: list[str]) -> bytes:
    """Chuỗi từ -> bytes bí mật. Ném ValueError nếu sai từ hoặc sai checksum."""
    cleaned = [w for w in normalize_mnemonic(mnemonic).split(" ") if w]
    total = len(cleaned) * 11
    ent = total * 32 // 33
    if ent not in VALID_BITS or ent * 33 // 32 != total:
        raise ValueError(f"số từ phải là {sorted(VALID_BITS.values())}, nhận {len(cleaned)}")
    try:
        bits = "".join(f"{words.index(w):011b}" for w in cleaned)
    except ValueError:
        bad = next(w for w in cleaned if w not in words)
        raise ValueError(f"từ lạ không có trong bảng BIP-39: {bad}")
    body, checksum = bits[:ent], bits[ent:]
    entropy = int(body, 2).to_bytes(ent // 8, "big")
    good = _to_bits(hashlib.sha256(entropy).digest())[: ent // 32]
    if checksum != good:
        raise ValueError("sai checksum: gõ nhầm từ hoặc sai thứ tự")
    return entropy


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """Seed 64 byte theo BIP-39: PBKDF2-HMAC-SHA512, 2048 vòng."""
    password = unicodedata.normalize("NFKD", normalize_mnemonic(mnemonic))
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"),
                               salt.encode("utf-8"), 2048, dklen=64)


# --- Lệnh CLI ---

def lay_cum_tu(args: argparse.Namespace) -> tuple[str | None, int]:
    """Lấy cụm từ từ --from-file, đối số, hoặc stdin. Trả về (text, exit_code).

    Đối số dòng lệnh lộ vào shell history và danh sách tiến trình nên chỉ là
    đường cuối cùng; --from-file và stdin an toàn hơn.
    """
    if getattr(args, "from_file", None):
        try:
            return Path(args.from_file).read_text(encoding="utf-8"), 0
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Không đọc được file cụm từ: {exc}")
            return None, 1
    if args.words:
        return " ".join(args.words), 0
    if not sys.stdin.isatty():
        return sys.stdin.read(), 0
    print("Thiếu cụm từ: đưa các từ làm đối số, --from-file, hoặc stdin.")
    return None, 2


def cmd_new(args: argparse.Namespace, words: list[str]) -> int:
    if args.words not in VALID_BITS.values():
        print(f"--words phải là một trong {sorted(VALID_BITS.values())}")
        return 2
    entropy = secrets.token_bytes(args.words * 11 * 32 // 33 // 8)
    print(entropy_to_mnemonic(entropy, words))
    if args.out:
        try:
            secureio.write_secret_file(args.out, entropy)
        except OSError as exc:
            print(f"Không ghi được {args.out}: {exc}")
            return 1
        print(f"Đã ghi {len(entropy)} byte entropy ra {args.out} (xóa sau khi chia share!).")
    print("Ghi cụm từ ra giấy NGAY, theo đúng thứ tự. Đây là đường khôi phục cuối cùng.")
    return 0


def cmd_from_entropy(args: argparse.Namespace, words: list[str]) -> int:
    try:
        print(entropy_to_mnemonic(Path(args.from_file).read_bytes(), words))
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}")
        return 1
    return 0


def cmd_to_entropy(args: argparse.Namespace, words: list[str]) -> int:
    text, code = lay_cum_tu(args)
    if text is None:
        return code
    try:
        entropy = mnemonic_to_entropy(text, words)
    except ValueError as exc:
        print(f"Cụm từ sai: {exc}")
        return 1
    if args.out:
        try:
            secureio.write_secret_file(args.out, entropy)
        except OSError as exc:
            print(f"Không ghi được {args.out}: {exc}")
            return 1
    else:
        print(f"Entropy ({len(entropy)} byte): {entropy.hex()}")
    return 0


def cmd_seed(args: argparse.Namespace, words: list[str]) -> int:
    text, code = lay_cum_tu(args)
    if text is None:
        return code
    try:
        mnemonic_to_entropy(text, words)
    except ValueError as exc:
        print(f"CẢNH BÁO: {exc}. Seed dưới đây có thể không khớp ví của bạn.")
    print(mnemonic_to_seed(text, args.passphrase).hex())
    return 0


# --- Tự kiểm tra ---

def self_test() -> int:
    words = load_wordlist()

    # 1. Bảng từ nguyên vẹn: đủ 2048, đầu/cuối đúng, tiền tố 4 chữ phân biệt.
    assert words[0] == "abandon" and words[3] == "about" and words[2047] == "zoo"
    assert len(set(words)) == 2048, "bảng từ trùng từ"
    assert len({w[:4] for w in words}) == 2048, "tiền tố 4 chữ không phân biệt"

    # 2. Vector chuẩn BIP-39: entropy 16 byte 0 -> 11 từ abandon + about.
    zero12 = "abandon " * 11 + "about"
    assert entropy_to_mnemonic(bytes(16), words) == zero12
    assert mnemonic_to_entropy(zero12, words) == bytes(16)

    # 3. Round-trip ngẫu nhiên mọi độ dài hợp lệ.
    for ent_bytes in (16, 20, 24, 28, 32):
        entropy = secrets.token_bytes(ent_bytes)
        text = entropy_to_mnemonic(entropy, words)
        assert len(text.split(" ")) == VALID_BITS[ent_bytes * 8]
        assert mnemonic_to_entropy(text, words) == entropy

    # 4. Cụm từ hỏng bị từ chối (thay từ cuối của vector 0 bằng abandon).
    try:
        mnemonic_to_entropy("abandon " * 12, words)
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối checksum sai")
    for bad in ["abandon từ-lạ " + "abandon " * 10, "abandon abandon"]:
        try:
            mnemonic_to_entropy(bad, words)
        except ValueError:
            pass
        else:
            raise AssertionError(f"đáng lẽ phải từ chối: {bad[:30]}")

    # 5. Seed ổn định, dài 64 byte, nhạy với passphrase.
    s1 = mnemonic_to_seed(zero12, "TREZOR")
    assert len(s1) == 64 and s1 == mnemonic_to_seed(zero12, "TREZOR")
    assert mnemonic_to_seed(zero12, "") != s1

    # 6. Input rỗng đếm đúng 0 từ; seed cụm hỏng cảnh báo nhưng vẫn tính;
    # --from-file đọc được cụm từ.
    try:
        mnemonic_to_entropy("", words)
    except ValueError as exc:
        assert "nhận 0" in str(exc), f"đếm sai input rỗng: {exc}"
    else:
        raise AssertionError("đáng lẽ phải từ chối input rỗng")
    import contextlib
    import io
    import tempfile
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cmd_seed(argparse.Namespace(words=["abandon"] * 12, from_file=None,
                                         passphrase=""), words)
    assert rc == 0 and "CẢNH BÁO" in buf.getvalue(), "seed cụm hỏng phải cảnh báo"
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "cum.txt"
        f.write_text(zero12, encoding="utf-8")
        text, code = lay_cum_tu(argparse.Namespace(words=[], from_file=str(f)))
        assert code == 0 and mnemonic_to_entropy(text, words) == bytes(16)

    print("self-test ok: bảng BIP-39 nguyên vẹn, vector chuẩn đúng, checksum bắt lỗi.")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv or "-t" in argv:
        return self_test()
    parser = argparse.ArgumentParser(description="Cụm từ khôi phục kiểu ví lạnh (BIP-39).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_new = sub.add_parser("new", help="sinh bí mật mới và in cụm từ")
    p_new.add_argument("--words", type=int, default=24, help="số từ (mặc định 24)")
    p_new.add_argument("--out", help="ghi entropy thô ra file để chia share")
    p_from = sub.add_parser("from-entropy", help="bytes bí mật -> cụm từ")
    p_from.add_argument("--from-file", required=True)
    p_to = sub.add_parser("to-entropy", help="cụm từ -> entropy (kiểm checksum)")
    p_to.add_argument("words", nargs="*", help="các từ theo đúng thứ tự (lộ vào shell history!)")
    p_to.add_argument("--from-file", help="đọc cụm từ từ file (an toàn hơn gõ đối số)")
    p_to.add_argument("--out", help="ghi entropy ra file thay vì in hex")
    p_seed = sub.add_parser("seed", help="cụm từ -> seed 64 byte")
    p_seed.add_argument("words", nargs="*")
    p_seed.add_argument("--from-file", help="đọc cụm từ từ file (an toàn hơn gõ đối số)")
    p_seed.add_argument("--passphrase", default="", help="cụm mật khẩu phụ (tùy chọn)")
    p_qr = sub.add_parser("qr", help="vẽ cụm từ thành ảnh QR")
    p_qr.add_argument("words", nargs="*", help="các từ theo đúng thứ tự (lộ vào shell history!)")
    p_qr.add_argument("--from-file", help="đọc cụm từ từ file (an toàn hơn gõ đối số)")
    p_qr.add_argument("--out", default="mnemonic.png", help="file ảnh PNG")
    args = parser.parse_args(argv)
    try:
        words = load_wordlist()
    except (OSError, ValueError) as exc:
        print(f"Bảng từ lỗi: {exc}")
        return 1
    if args.cmd == "new":
        return cmd_new(args, words)
    if args.cmd == "from-entropy":
        return cmd_from_entropy(args, words)
    if args.cmd == "to-entropy":
        return cmd_to_entropy(args, words)
    if args.cmd == "qr":
        return cmd_qr(args, words)
    return cmd_seed(args, words)


def cmd_qr(args: argparse.Namespace, words: list[str]) -> int:
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
    except ImportError:
        print("Thiếu thư viện QR. Chạy: pip install -r requirements-qr.txt")
        return 2
    text, code = lay_cum_tu(args)
    if text is None:
        return code
    text = normalize_mnemonic(text)
    try:
        mnemonic_to_entropy(text, words)
    except ValueError as exc:
        print(f"Cụm từ sai: {exc}")
        return 1
    try:
        secureio.ensure_parent(args.out)
        qrcode.make(text, error_correction=ERROR_CORRECT_M).save(args.out)
    except OSError as exc:
        print(f"Không vẽ được QR ra {args.out}: {exc}")
        return 1
    print(f"Đã vẽ QR ra {args.out}. Quét xong thì xóa file ảnh.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
